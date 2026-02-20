"""
OpenClaw Voice - HTTP API Server
For external triggers (like OpenClaw)
"""
import logging

import discord
from aiohttp import web
from aiohttp.web import TCPSite

from . import player
from .config import BOT_NAME

logger = logging.getLogger(__name__)

# Bot reference (set by main)
bot = None


def setup_api(app, notifier_port):
    """Setup HTTP API routes"""
    
    async def notify_handler(request):
        """TTS notification - speak a message"""
        try:
            data = await request.json()
            message = data.get('message', '')
            channel_id = data.get('channel_id')
            
            if not message:
                return web.json_response({'error': 'No message provided'}, status=400)
            
            # Find channel
            if channel_id:
                channel = bot.get_channel(int(channel_id))
            else:
                # Use first available voice channel
                channel = None
                for vc in player.voice_clients.values():
                    if vc and vc.channel:
                        channel = vc.channel
                        break
            
            if not channel:
                return web.json_response({'error': 'No voice channel available'}, status=400)
            
            # Play TTS
            await player.play_tts(channel, message, channel.guild.id)
            
            logger.info(f"TTS notification: {message[:50]}")
            return web.json_response({'status': 'playing', 'message': message})
            
        except Exception as e:
            logger.error(f"Notify error: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    
    async def stream_handler(request):
        """Play a stream URL"""
        try:
            data = await request.json()
            url = data.get('url', '')
            channel_id = data.get('channel_id')
            
            if not url:
                return web.json_response({'error': 'No URL provided'}, status=400)
            
            # Find channel
            if channel_id:
                channel = bot.get_channel(int(channel_id))
            else:
                channel = None
                for vc in player.voice_clients.values():
                    if vc and vc.channel:
                        channel = vc.channel
                        break
            
            if not channel:
                return web.json_response({'error': 'No voice channel available'}, status=400)
            
            # Play
            await player.play_url(channel, url, channel.guild.id)
            
            logger.info(f"Streaming: {url[:50]}")
            return web.json_response({'status': 'playing', 'url': url})
            
        except Exception as e:
            logger.error(f"Stream error: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    
    async def search_handler(request):
        """Search for streams"""
        query = request.query.get('q', '')
        if not query:
            return web.json_response({'error': 'No query provided'}, status=400)
        
        try:
            results = await player.search_youtube(query)
            return web.json_response({'results': results})
        except Exception as e:
            logger.error(f"Search error: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    
    async def status_handler(request):
        """Health check"""
        return web.json_response({
            'status': 'ok',
            'bot_name': BOT_NAME,
            'active_voice_connections': len(player.voice_clients)
        })
    
    
    async def voice_handler(request):
        """Get voice channel info - checks any user in any guild the bot is in"""
        try:
            data = await request.json()
            user_id = str(data.get('user_id', '')).replace('<@', '').replace('>', '').replace('!', '')
            
            if not user_id:
                return web.json_response({'error': 'user_id required'}, status=400)
            
            # Search all guilds the bot is in
            for guild in bot.guilds:
                # Get all voice channels and check who's in them
                for channel in guild.voice_channels:
                    for member in channel.members:
                        if str(member.id) == user_id:
                            return web.json_response({
                                'in_voice': True,
                                'channel_id': str(channel.id),
                                'channel_name': channel.name,
                                'guild_id': str(guild.id),
                                'guild_name': guild.name
                            })
            
            return web.json_response({
                'in_voice': False,
                'message': 'User not in any voice channel'
            })
            
        except Exception as e:
            logger.error(f"Voice check error: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    
    async def control_handler(request):
        """Control playback (stop, pause, etc.)"""
        try:
            data = await request.json()
            action = data.get('action', 'stop')
            guild_id = data.get('guild_id')
            
            if action == 'stop':
                if guild_id:
                    await player.disconnect(int(guild_id))
                else:
                    # Stop all
                    for gid in list(player.voice_clients.keys()):
                        await player.disconnect(gid)
                
                return web.json_response({'status': 'stopped'})
            
            return web.json_response({'error': 'Unknown action'}, status=400)
            
        except Exception as e:
            logger.error(f"Control error: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    
    # Add routes
    app.router.add_post('/notify', notify_handler)
    app.router.add_post('/stream', stream_handler)
    app.router.add_post('/control', control_handler)
    app.router.add_post('/voice', voice_handler)
    app.router.add_get('/search', search_handler)
    app.router.add_get('/status', status_handler)
    
    return {
        'notify': notify_handler,
        'stream': stream_handler,
        'control': control_handler,
        'search': search_handler,
        'status': status_handler,
        'voice': voice_handler,
    }


async def start_api(bot_instance, notifier_port):
    """Start the API server"""
    global bot
    bot = bot_instance
    
    app = web.Application()
    setup_api(app, notifier_port)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = TCPSite(runner, 'localhost', notifier_port)
    await site.start()
    
    logger.info(f"📢 API running on http://localhost:{notifier_port}")
