"""
OpenClaw Voice - Main Bot
Entry point for the Discord voice bot
"""
import os
import re
import logging

import discord
from discord import app_commands

from .config import BOT_TOKEN, BOT_NAME, NOTIFIER_PORT, VERBOSITY, should_respond
from . import commands
from . import api

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

# Create bot
bot = discord.Client(intents=intents, activity=discord.Game(name=f"{BOT_NAME} Voice"))
tree = app_commands.CommandTree(bot)


@bot.event
async def on_ready():
    """Bot ready"""
    logger.info(f"✅ Logged in as {bot.user} ({BOT_NAME})")
    
    # Setup and sync commands
    commands.setup_commands(tree, bot)
    await tree.sync()
    logger.info("Slash commands synced")
    
    # Start API server
    await api.start_api(bot, NOTIFIER_PORT)
    
    logger.info(f"📊 Verbosity: {VERBOSITY}")


@bot.event
async def on_message(message):
    """Handle message commands (legacy)"""
    if message.author.bot:
        return
    
    # Strip mentions
    content = message.content.lower()
    content = re.sub(r'<@!?\d+>', '', content).strip()
    
    # Simple commands that work without slash
    if content.startswith('play ') or content.startswith('yt '):
        if message.author.voice:
            query = content.split(' ', 1)[1]
            from . import player
            url = await player.get_stream_url(query)
            if url:
                await player.play_url(message.author.voice.channel, url, message.guild.id)
                if should_respond('minimal'):
                    await message.channel.send("🎵 Now playing!")
            elif should_respond('minimal'):
                await message.channel.send("❌ Couldn't find it!")
        return
    
    if content in ['stop', 'leave']:
        from . import player
        await player.disconnect(message.guild.id)
        if should_respond('minimal'):
            await message.channel.send("⏹️ Stopped!")
        return
    
    if content.startswith('say '):
        if message.author.voice:
            text = content[4:]
            from . import player
            await player.play_tts(message.author.voice.channel, text, message.guild.id)
            if should_respond('normal'):
                await message.channel.send(f"🗣️ Saying: {text}")
        elif should_respond('minimal'):
            await message.channel.send("❌ Join a voice channel first!")
        return


def run():
    """Run the bot"""
    if not BOT_TOKEN:
        logger.error("DISCORD_BOT_TOKEN not set in .env")
        exit(1)
    
    bot.run(BOT_TOKEN)


if __name__ == '__main__':
    run()
