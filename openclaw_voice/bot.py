"""
OpenClaw Voice - Main Bot
"""
import os
import re
import asyncio
import logging
import subprocess
import requests
import tempfile

import discord
from discord import app_commands
from gtts import gTTS
from aiohttp import web
from aiohttp.web import TCPSite

# Add parent to path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openclaw_voice.config import (
    BOT_TOKEN, BOT_NAME, DEFAULT_VOLUME, NOTIFIER_PORT,
    VERBOSITY, ENABLE_AI, OLLAMA_URL, OPENCLAW_URL, should_respond
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Discord intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = discord.Client(intents=intents, activity=discord.Game(name=f"{BOT_NAME} Voice"))
tree = app_commands.CommandTree(bot)

# State
voice_clients = {}
current_source = {}


def log(msg, level='info'):
    """Conditional logging based on verbosity"""
    if level == 'debug' and not should_respond('verbose'):
        return
    if level == 'info' and not should_respond('normal'):
        return
    if level == 'warn' and not should_respond('minimal'):
        return
    
    getattr(logger, level)(msg)


async def disconnect_voice(guild_id):
    """Disconnect voice client for a guild"""
    if guild_id in voice_clients:
        try:
            await voice_clients[guild_id].disconnect()
        except:
            pass
        del voice_clients[guild_id]
    if guild_id in current_source:
        del current_source[guild_id]


# ============== SLASH COMMANDS ==============

@tree.command(name="play", description="Play YouTube audio in voice channel")
async def play_command(interaction: discord.Interaction, query: str):
    """Play music from YouTube"""
    await interaction.response.defer()
    
    if not interaction.user.voice:
        if should_respond('minimal'):
            await interaction.followup.send("❌ Join a voice channel first!")
        return
    
    try:
        if should_respond('normal'):
            await interaction.followup.send(f"🔍 Searching: {query}")
        
        result = subprocess.run(
            ['yt-dlp', '-f', 'bestaudio', '--get-url', f'ytsearch1:{query}'],
            capture_output=True, text=True, timeout=30
        )
        
        url = result.stdout.strip().split('\n')[0]
        
        if not url or not url.startswith('http'):
            if should_respond('minimal'):
                await interaction.followup.send("❌ Couldn't find that!")
            return
        
        await disconnect_voice(interaction.guild_id)
        
        vc = await interaction.user.voice.channel.connect()
        voice_clients[interaction.guild_id] = vc
        
        if should_respond('normal'):
            await interaction.followup.send("📡 Streaming...")
        
        source = discord.FFmpegPCMAudio(
            url,
            options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
        )
        source = discord.PCMVolumeTransformer(source)
        source.volume = DEFAULT_VOLUME
        
        def after_playing(error):
            if error:
                logger.error(f"Playback error: {error}")
            asyncio.run_coroutine_threadsafe(
                disconnect_voice(interaction.guild_id), 
                bot.loop
            )
        
        vc.play(source, after=after_playing)
        
        if should_respond('minimal'):
            await interaction.followup.send("🎵 Now playing!")
        
    except Exception as e:
        logger.error(f"Play error: {e}")
        await interaction.followup.send(f"❌ Error: {str(e)[:100]}")


@tree.command(name="stop", description="Stop playback and leave voice channel")
async def stop_command(interaction: discord.Interaction):
    """Stop music"""
    await interaction.response.defer()
    await disconnect_voice(interaction.guild_id)
    if should_respond('minimal'):
        await interaction.followup.send("⏹️ Stopped!")


@tree.command(name="join", description="Join your voice channel")
async def join_command(interaction: discord.Interaction):
    """Join voice channel"""
    if not interaction.user.voice:
        await interaction.response.send_message("❌ Join a voice channel first!")
        return
    
    await disconnect_voice(interaction.guild_id)
    vc = await interaction.user.voice.channel.connect()
    voice_clients[interaction.guild_id] = vc
    if should_respond('normal'):
        await interaction.response.send_message(f"✅ Joined {interaction.user.voice.channel.name}!")
    else:
        await interaction.response.defer()


@tree.command(name="leave", description="Leave voice channel")
async def leave_command(interaction: discord.Interaction):
    """Leave voice channel"""
    await disconnect_voice(interaction.guild_id)
    if should_respond('minimal'):
        await interaction.response.send_message("👋 Left!")
    else:
        await interaction.response.defer()


@tree.command(name="say", description="Speak a message in your voice channel")
async def say_command(interaction: discord.Interaction, message: str):
    """TTS in voice channel"""
    if not interaction.user.voice:
        await interaction.response.send_message("❌ Join a voice channel first!")
        return
    
    await interaction.response.defer()
    
    try:
        await disconnect_voice(interaction.guild_id)
        
        vc = await interaction.user.voice.channel.connect()
        voice_clients[interaction.guild_id] = vc
        
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            tts = gTTS(text=message, lang='en')
            tts.save(f.name)
            temp_file = f.name
        
        source = discord.FFmpegPCMAudio(temp_file)
        source = discord.PCMVolumeTransformer(source)
        source.volume = DEFAULT_VOLUME
        
        def after_playing(error):
            if error:
                logger.error(f"TTS error: {error}")
            asyncio.run_coroutine_threadsafe(
                disconnect_voice(interaction.guild_id), 
                bot.loop
            )
            try:
                os.unlink(temp_file)
            except:
                pass
        
        vc.play(source, after=after_playing)
        
        if should_respond('normal'):
            await interaction.followup.send(f"🗣️ Saying: {message}")
        
    except Exception as e:
        logger.error(f"Say error: {e}")
        await interaction.followup.send(f"❌ Error: {str(e)[:100]}")


@tree.command(name="search", description="Search for audio streams")
async def search_command(interaction: discord.Interaction, query: str):
    """Search for streams"""
    await interaction.response.defer()
    
    try:
        result = subprocess.run(
            ['yt-dlp', '--flat-playlist', '-J', f'ytsearch10:{query}'],
            capture_output=True, text=True, timeout=30
        )
        
        import json
        data = json.loads(result.stdout)
        entries = data.get('entries', [])[:10]
        
        if not entries:
            await interaction.followup.send("❌ No results found!")
            return
        
        results_text = "**Search Results:**\n"
        for i, entry in enumerate(entries, 1):
            title = entry.get('title', 'Unknown')[:50]
            duration = entry.get('duration', 0)
            mins = duration // 60
            secs = duration % 60
            results_text += f"{i}. {title} ({mins}:{secs:02d})\n"
        
        await interaction.followup.send(results_text)
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        await interaction.followup.send(f"❌ Error: {str(e)[:100]}")


@tree.command(name="notify", description="Ask to process and speak in voice")
async def notify_command(interaction: discord.Interaction, request: str):
    """Process request via AI, then speak result in voice"""
    await interaction.response.defer()
    
    if not interaction.user.voice:
        await interaction.followup.send("❌ Join a voice channel first!")
        return
    
    if not ENABLE_AI:
        await interaction.followup.send("❌ AI is disabled!")
        return
    
    try:
        if should_respond('normal'):
            await interaction.followup.send(f"🔄 Asking OpenClaw...")
        
        # Step 1: Call OpenClaw (the brain) to process the request
        response_text = None
        
        # Try calling OpenClaw's chat API
        try:
            # Use localhost:11434 or configure OpenClaw URL
            openclaw_url = OPENCLAW_URL.replace('/api/generate', '')
            
            # Call Ollama for chat - this is the "brain"
            # OpenClaw will use its tools, search, etc. to get a good answer
            chat_payload = {
                "model": "llama3.2",
                "messages": [
                    {"role": "system", "content": "You are OpenClaw's voice assistant. The user wants you to speak this response in a voice channel. Give a direct, accurate, conversational answer. Keep it brief - one sentence or two max. Make it sound natural when spoken aloud."},
                    {"role": "user", "content": request}
                ],
                "stream": False
            }
            chat_resp = requests.post(
                f"{openclaw_url}/api/chat/completions",
                json=chat_payload,
                timeout=60  # Longer timeout for AI processing
            )
            if chat_resp.ok:
                resp_data = chat_resp.json()
                response_text = resp_data.get('choices', [{}])[0].get('message', {}).get('content', '')
            else:
                logger.warning(f"OpenClaw unavailable: {chat_resp.status_code}")
        except Exception as e:
            logger.warning(f"OpenClaw error: {e}")
        
        # Fallback if no response
        if not response_text:
            response_text = f"I couldn't get a response from OpenClaw. But regarding {request}."
        
        # Step 2: Join voice and speak
        await disconnect_voice(interaction.guild_id)
        vc = await interaction.user.voice.channel.connect()
        voice_clients[interaction.guild_id] = vc
        
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            tts = gTTS(text=response_text, lang='en')
            tts.save(f.name)
            temp_file = f.name
        
        source = discord.FFmpegPCMAudio(temp_file)
        source = discord.PCMVolumeTransformer(source)
        source.volume = DEFAULT_VOLUME
        
        def after_playing(error):
            if error:
                logger.error(f"Notify TTS error: {error}")
            asyncio.run_coroutine_threadsafe(
                disconnect_voice(interaction.guild_id), 
                bot.loop
            )
            try:
                os.unlink(temp_file)
            except:
                pass
        
        vc.play(source, after=after_playing)
        
        if should_respond('normal'):
            await interaction.followup.send(f"🔔 **{response_text}**")
        
    except Exception as e:
        logger.error(f"Notify error: {e}")
        await interaction.followup.send(f"❌ Error: {str(e)[:100]}")


# ============== MESSAGE HANDLER ==============

@bot.event
async def on_message(message):
    """Handle messages (legacy commands)"""
    if message.author.bot:
        return
    
    content = message.content.lower()
    content = re.sub(r'<@!?\d+>', '', content).strip()
    
    # Legacy commands - same logic as slash commands
    if content.startswith('play ') or content.startswith('yt '):
        if message.author.voice:
            class MockInteraction:
                def __init__(self, msg):
                    self.user = msg.author
                    self.guild_id = msg.guild.id
                    self.guild = msg.guild
                    self.channel = msg.channel
            await play_command_legacy(MockInteraction(message), content.split(' ', 1)[1])
        return
    
    if content in ['stop', 'leave']:
        await disconnect_voice(message.guild.id)
        if should_respond('minimal'):
            await message.channel.send("⏹️ Stopped!")
        return
    
    if content.startswith('say '):
        if message.author.voice:
            class MockInteraction:
                def __init__(self, msg):
                    self.user = msg.author
                    self.guild_id = msg.guild.id
                    self.guild = msg.guild
                    self.channel = msg.channel
            await say_command_legacy(MockInteraction(message), content[4:])
        else:
            if should_respond('minimal'):
                await message.channel.send("❌ Join a voice channel first!")
        return
    
    if content.startswith('stream '):
        if message.author.voice:
            class MockInteraction:
                def __init__(self, msg):
                    self.user = msg.author
                    self.guild_id = msg.guild.id
                    self.guild = msg.guild
                    self.channel = msg.channel
            await stream_command_legacy(MockInteraction(message), content[7:])
        else:
            if should_respond('minimal'):
                await message.channel.send("❌ Join a voice channel first!")
        return


async def play_command_legacy(message, query):
    """Legacy play command"""
    if not message.user.voice:
        if should_respond('minimal'):
            await message.channel.send("❌ Join a voice channel first!")
        return
    
    try:
        if should_respond('normal'):
            await message.channel.send(f"🔍 Searching: {query}")
        
        result = subprocess.run(
            ['yt-dlp', '-f', 'bestaudio', '--get-url', f'ytsearch1:{query}'],
            capture_output=True, text=True, timeout=30
        )
        
        url = result.stdout.strip().split('\n')[0]
        
        if not url or not url.startswith('http'):
            if should_respond('minimal'):
                await message.channel.send("❌ Couldn't find it!")
            return
        
        await disconnect_voice(message.guild_id)
        
        vc = await message.user.voice.channel.connect()
        voice_clients[message.guild_id] = vc
        
        if should_respond('normal'):
            await message.channel.send("📡 Streaming...")
        
        source = discord.FFmpegPCMAudio(
            url,
            options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
        )
        source = discord.PCMVolumeTransformer(source)
        source.volume = DEFAULT_VOLUME
        
        def after_playing(error):
            if error:
                logger.error(f"Playback error: {error}")
            asyncio.run_coroutine_threadsafe(
                disconnect_voice(message.guild_id), 
                bot.loop
            )
        
        vc.play(source, after=after_playing)
        
        if should_respond('minimal'):
            await message.channel.send("🎵 Now playing!")
        
    except Exception as e:
        logger.error(f"Play error: {e}")
        if should_respond('minimal'):
            await message.channel.send(f"❌ Error: {str(e)[:100]}")


async def say_command_legacy(message, text: str):
    """Legacy say command"""
    if not message.user.voice:
        if should_respond('minimal'):
            await message.channel.send("❌ Join a voice channel first!")
        return
    
    try:
        await disconnect_voice(message.guild_id)
        
        vc = await message.user.voice.channel.connect()
        voice_clients[message.guild_id] = vc
        
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            tts = gTTS(text=text, lang='en')
            tts.save(f.name)
            temp_file = f.name
        
        source = discord.FFmpegPCMAudio(temp_file)
        source = discord.PCMVolumeTransformer(source)
        source.volume = DEFAULT_VOLUME
        
        def after_playing(error):
            if error:
                logger.error(f"TTS error: {error}")
            asyncio.run_coroutine_threadsafe(
                disconnect_voice(message.guild_id), 
                bot.loop
            )
            try:
                os.unlink(temp_file)
            except:
                pass
        
        vc.play(source, after=after_playing)
        
        if should_respond('normal'):
            await message.channel.send(f"🗣️ Saying: {text}")
        
    except Exception as e:
        logger.error(f"Say error: {e}")
        if should_respond('minimal'):
            await message.channel.send(f"❌ Error: {str(e)[:100]}")


async def stream_command_legacy(message, url: str):
    """Legacy stream command"""
    if not message.user.voice:
        if should_respond('minimal'):
            await message.channel.send("❌ Join a voice channel first!")
        return
    
    try:
        await disconnect_voice(message.guild_id)
        
        vc = await message.user.voice.channel.connect()
        voice_clients[message.guild_id] = vc
        
        source = discord.FFmpegPCMAudio(
            url,
            options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
        )
        source = discord.PCMVolumeTransformer(source)
        source.volume = DEFAULT_VOLUME
        
        def after_playing(error):
            if error:
                logger.error(f"Stream error: {error}")
            asyncio.run_coroutine_threadsafe(
                disconnect_voice(message.guild_id), 
                bot.loop
            )
        
        vc.play(source, after=after_playing)
        
        if should_respond('normal'):
            await message.channel.send(f"📡 Streaming: {url}")
        
    except Exception as e:
        logger.error(f"Stream error: {e}")
        if should_respond('minimal'):
            await message.channel.send(f"❌ Error: {str(e)[:100]}")


# ============== API SERVER ==============

async def speak_in_channel(channel_id: int, text: str):
    """Speak text in a voice channel"""
    try:
        channel = bot.get_channel(int(channel_id))
        if not channel:
            logger.error(f"Channel {channel_id} not found")
            return False
        
        if not isinstance(channel, discord.VoiceChannel):
            logger.error(f"Channel {channel_id} is not a voice channel")
            return False
        
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            tts = gTTS(text=text, lang='en')
            tts.save(f.name)
            temp_file = f.name
        
        vc = await channel.connect()
        voice_clients[channel.guild.id] = vc
        
        source = discord.FFmpegPCMAudio(temp_file)
        source = discord.PCMVolumeTransformer(source)
        source.volume = DEFAULT_VOLUME
        
        def after_playing(error):
            if error:
                logger.error(f"TTS error: {error}")
            asyncio.run_coroutine_threadsafe(
                disconnect_voice(channel.guild.id), 
                bot.loop
            )
            try:
                os.unlink(temp_file)
            except:
                pass
        
        vc.play(source, after=after_playing)
        logger.info(f"TTS playing in channel {channel_id}: {text}")
        return True
        
    except Exception as e:
        logger.error(f"TTS error: {e}")
        return False


async def notify_handler(request):
    """Handle notification requests"""
    try:
        data = await request.json()
        message = data.get('message', '')
        channel_id = data.get('channel_id')
        
        if not message:
            return web.json_response({'error': 'No message provided'}, status=400)
        
        if channel_id:
            success = await speak_in_channel(int(channel_id), message)
        else:
            success = False
            for vc in voice_clients.values():
                if vc.channel:
                    success = await speak_in_channel(vc.channel.id, message)
                    break
        
        if success:
            return web.json_response({'status': 'playing'})
        else:
            return web.json_response({'error': 'No voice channel available'}, status=400)
            
    except Exception as e:
        logger.error(f"Notify error: {e}")
        return web.json_response({'error': str(e)}, status=500)


async def status_handler(request):
    """Health check"""
    return web.json_response({
        'status': 'ok',
        'bot_name': BOT_NAME,
        'verbosity': VERBOSITY,
        'ai_enabled': ENABLE_AI,
        'active_voice_connections': len(voice_clients)
    })


async def search_handler(request):
    """Search for streams"""
    query = request.query.get('q', '')
    if not query:
        return web.json_response({'error': 'No query provided'}, status=400)
    
    try:
        result = subprocess.run(
            ['yt-dlp', '--flat-playlist', '-J', f'ytsearch10:{query}'],
            capture_output=True, text=True, timeout=30
        )
        
        import json
        data = json.loads(result.stdout)
        entries = []
        
        for entry in data.get('entries', [])[:10]:
            entries.append({
                'title': entry.get('title', 'Unknown'),
                'url': entry.get('url', ''),
                'duration': entry.get('duration', 0),
                'source': 'youtube'
            })
        
        return web.json_response({'results': entries})
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return web.json_response({'error': str(e)}, status=500)


async def stream_handler(request):
    """Play a direct stream URL"""
    try:
        data = await request.json()
        url = data.get('url', '')
        channel_id = data.get('channel_id')
        
        if not url:
            return web.json_response({'error': 'No URL provided'}, status=400)
        
        if channel_id:
            channel = bot.get_channel(int(channel_id))
        else:
            channel = None
            for vc in voice_clients.values():
                if vc.channel:
                    channel = vc.channel
                    break
        
        if not channel:
            return web.json_response({'error': 'No voice channel available'}, status=400)
        
        await disconnect_voice(channel.guild.id)
        
        vc = await channel.connect()
        voice_clients[channel.guild.id] = vc
        
        source = discord.FFmpegPCMAudio(
            url,
            options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
        )
        source = discord.PCMVolumeTransformer(source)
        source.volume = DEFAULT_VOLUME
        
        def after_playing(error):
            if error:
                logger.error(f"Stream error: {error}")
            asyncio.run_coroutine_threadsafe(
                disconnect_voice(channel.guild.id), 
                bot.loop
            )
        
        vc.play(source, after=after_playing)
        logger.info(f"Streaming: {url}")
        return web.json_response({'status': 'playing', 'url': url})
        
    except Exception as e:
        logger.error(f"Stream error: {e}")
        return web.json_response({'error': str(e)}, status=500)


# ============== EVENTS ==============

@bot.event
async def on_ready():
    """Bot ready"""
    logger.info(f"✅ Logged in as {bot.user} ({BOT_NAME})")
    await tree.sync()
    logger.info("Slash commands synced")
    
    # Start API server
    app = web.Application()
    app.router.add_post('/notify', notify_handler)
    app.router.add_get('/status', status_handler)
    app.router.add_get('/search', search_handler)
    app.router.add_post('/stream', stream_handler)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = TCPSite(runner, 'localhost', NOTIFIER_PORT)
    await site.start()
    
    logger.info(f"📢 API running on http://localhost:{NOTIFIER_PORT}")
    logger.info(f"📊 Verbosity: {VERBOSITY}, AI: {ENABLE_AI}")


# ============== MAIN ==============

if __name__ == '__main__':
    if not BOT_TOKEN:
        logger.error("DISCORD_BOT_TOKEN not set in .env")
        exit(1)
    
    bot.run(BOT_TOKEN)
