"""
OpenClaw Voice - Audio Player
Handles all audio playback: streams, TTS, etc.
"""
import asyncio
import os
import tempfile
import logging
import subprocess
import discord

from .config import DEFAULT_VOLUME, should_respond

logger = logging.getLogger(__name__)

# Voice client storage
voice_clients = {}


async def disconnect(guild_id):
    """Disconnect voice client for a guild"""
    try:
        if guild_id in voice_clients:
            try:
                await voice_clients[guild_id].disconnect()
            except Exception as e:
                logger.warning(f"Disconnect error: {e}")
            finally:
                del voice_clients[guild_id]
    except KeyError:
        pass  # Already disconnected


async def play_url(voice_channel, url, guild_id):
    """Play a URL in a voice channel"""
    await disconnect(guild_id)
    
    # Get direct stream URL if it's a YouTube URL
    stream_url = url
    if 'youtube.com' in url or 'youtu.be' in url:
        try:
            result = subprocess.run(
                ['yt-dlp', '-f', 'bestaudio', '--get-url', url],
                capture_output=True, text=True, timeout=30
            )
            stream_url = result.stdout.strip().split('\n')[0]
            if not stream_url.startswith('http'):
                logger.warning(f"Could not get stream URL, trying direct: {stream_url}")
                stream_url = url  # Fallback
        except Exception as e:
            logger.warning(f"Failed to get stream URL: {e}")
            stream_url = url
    
    vc = await voice_channel.connect()
    voice_clients[guild_id] = vc
    
    source = discord.FFmpegPCMAudio(
        stream_url,
        options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
    )
    source = discord.PCMVolumeTransformer(source)
    source.volume = DEFAULT_VOLUME
    
    def after_playing(error):
        if error:
            logger.error(f"Playback error: {error}")
        # Schedule disconnect in bot's event loop
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(disconnect(guild_id))
            loop.close()
        except Exception as e:
            logger.warning(f"Auto-disconnect failed: {e}")
    
    vc.play(source, after=after_playing)
    return vc


async def play_tts(voice_channel, text, guild_id, lang='en'):
    """Generate and play TTS in a voice channel"""
    await disconnect(guild_id)
    
    vc = await voice_channel.connect()
    voice_clients[guild_id] = vc
    
    # Generate TTS
    from gtts import gTTS
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
        tts = gTTS(text=text, lang=lang)
        tts.save(f.name)
        temp_file = f.name
    
    source = discord.FFmpegPCMAudio(temp_file)
    source = discord.PCMVolumeTransformer(source)
    source.volume = DEFAULT_VOLUME
    
    def after_playing(error):
        if error:
            logger.error(f"TTS error: {error}")
        # Clean up temp file
        try:
            os.unlink(temp_file)
        except:
            pass
        # Schedule disconnect in bot's event loop
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(disconnect(guild_id))
            loop.close()
        except Exception as e:
            logger.warning(f"Auto-disconnect failed: {e}")
    
    vc.play(source, after=after_playing)
    return vc


async def search_youtube(query, max_results=10):
    """Search YouTube for streams"""
    try:
        result = subprocess.run(
            ['yt-dlp', '--flat-playlist', '-J', f'ytsearch{max_results}:{query}'],
            capture_output=True, text=True, timeout=30
        )
        
        import json
        data = json.loads(result.stdout)
        entries = []
        
        for entry in data.get('entries', []):
            entries.append({
                'title': entry.get('title', 'Unknown'),
                'url': entry.get('url', ''),
                'duration': entry.get('duration', 0),
                'source': 'youtube'
            })
        
        return entries
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return []


async def get_stream_url(query):
    """Get direct stream URL for a query"""
    try:
        result = subprocess.run(
            ['yt-dlp', '-f', 'bestaudio', '--get-url', f'ytsearch1:{query}'],
            capture_output=True, text=True, timeout=30
        )
        
        url = result.stdout.strip().split('\n')[0]
        return url if url.startswith('http') else None
        
    except Exception as e:
        logger.error(f"Stream URL error: {e}")
        return None


def get_voice_client(guild_id):
    """Get voice client for a guild"""
    return voice_clients.get(guild_id)


def is_playing(guild_id):
    """Check if something is playing"""
    vc = voice_clients.get(guild_id)
    return vc and vc.is_playing()
