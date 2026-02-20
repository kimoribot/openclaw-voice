"""
OpenClaw Voice - Commands
Slash commands and message handlers
"""
import logging

import discord
from discord import app_commands

from .config import should_respond, DEFAULT_VOLUME
from . import player

logger = logging.getLogger(__name__)


def setup_commands(tree, bot):
    """Setup all commands"""
    
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
            
            url = await player.get_stream_url(query)
            
            if not url:
                if should_respond('minimal'):
                    await interaction.followup.send("❌ Couldn't find that!")
                return
            
            await player.play_url(interaction.user.voice.channel, url, interaction.guild_id)
            
            if should_respond('minimal'):
                await interaction.followup.send("🎵 Now playing!")
            
        except Exception as e:
            logger.error(f"Play error: {e}")
            await interaction.followup.send(f"❌ Error: {str(e)[:100]}")
    
    
    @tree.command(name="search", description="Search for audio streams")
    async def search_command(interaction: discord.Interaction, query: str):
        """Search for streams"""
        await interaction.response.defer()
        
        try:
            results = await player.search_youtube(query)
            
            if not results:
                await interaction.followup.send("❌ No results found!")
                return
            
            results_text = "**Search Results:**\n"
            for i, entry in enumerate(results[:10], 1):
                title = entry['title'][:50]
                duration = entry['duration']
                mins = duration // 60
                secs = duration % 60
                results_text += f"{i}. {title} ({mins}:{secs:02d})\n"
            
            await interaction.followup.send(results_text)
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            await interaction.followup.send(f"❌ Error: {str(e)[:100]}")
    
    
    @tree.command(name="say", description="Speak a message in your voice channel")
    async def say_command(interaction: discord.Interaction, message: str):
        """TTS in voice channel"""
        if not interaction.user.voice:
            await interaction.response.send_message("❌ Join a voice channel first!")
            return
        
        await interaction.response.defer()
        
        try:
            await player.play_tts(interaction.user.voice.channel, message, interaction.guild_id)
            
            if should_respond('normal'):
                await interaction.followup.send(f"🗣️ Saying: {message}")
            
        except Exception as e:
            logger.error(f"Say error: {e}")
            await interaction.followup.send(f"❌ Error: {str(e)[:100]}")
    
    
    @tree.command(name="stream", description="Play a direct stream URL")
    async def stream_command(interaction: discord.Interaction, url: str):
        """Play direct URL"""
        if not interaction.user.voice:
            await interaction.response.send_message("❌ Join a voice channel first!")
            return
        
        await interaction.response.defer()
        
        try:
            await player.play_url(interaction.user.voice.channel, url, interaction.guild_id)
            
            if should_respond('minimal'):
                await interaction.followup.send("📡 Streaming...")
            
        except Exception as e:
            logger.error(f"Stream error: {e}")
            await interaction.followup.send(f"❌ Error: {str(e)[:100]}")
    
    
    @tree.command(name="join", description="Join your voice channel")
    async def join_command(interaction: discord.Interaction):
        """Join voice channel"""
        if not interaction.user.voice:
            await interaction.response.send_message("❌ Join a voice channel first!")
            return
        
        await player.disconnect(interaction.guild_id)
        vc = await interaction.user.voice.channel.connect()
        player.voice_clients[interaction.guild_id] = vc
        
        if should_respond('normal'):
            await interaction.response.send_message(f"✅ Joined {interaction.user.voice.channel.name}!")
        else:
            await interaction.response.defer()
    
    
    @tree.command(name="leave", description="Leave voice channel")
    async def leave_command(interaction: discord.Interaction):
        """Leave voice channel"""
        await player.disconnect(interaction.guild_id)
        
        if should_respond('minimal'):
            await interaction.response.send_message("👋 Left!")
        else:
            await interaction.response.defer()
    
    
    @tree.command(name="stop", description="Stop playback")
    async def stop_command(interaction: discord.Interaction):
        """Stop music"""
        await player.disconnect(interaction.guild_id)
        
        if should_respond('minimal'):
            await interaction.response.send_message("⏹️ Stopped!")
        else:
            await interaction.response.defer()
    
    
    @tree.command(name="notify", description="Ask OpenClaw to process and speak in voice")
    async def notify_command(interaction: discord.Interaction, request: str):
        """Pass to OpenClaw for processing, then speak result"""
        if not interaction.user.voice:
            await interaction.followup.send("❌ Join a voice channel first!")
            return
        
        await interaction.response.defer()
        
        # This now tells user to talk to OpenClaw directly
        # OpenClaw Voice is just the renderer
        if should_respond('normal'):
            await interaction.followup.send(
                "💡 Tip: Just message @OpenClaw directly with your request! "
                "I just handle the voice - OpenClaw does the thinking."
            )
        
        # Optionally still try to speak
        # In the future, OpenClaw will call the API to make me speak
    
    
    return {
        'play': play_command,
        'search': search_command,
        'say': say_command,
        'stream': stream_command,
        'join': join_command,
        'leave': leave_command,
        'stop': stop_command,
        'notify': notify_command,
    }
