"""
OpenClaw Stream Search - Find streams from multiple sources
"""
import asyncio
import re
import subprocess
import json
import os

# Configuration
VOICE_API_URL = os.getenv('VOICE_API_URL', 'http://localhost:5000')
AUTO_PLAY = os.getenv('AUTO_PLAY', 'false').lower() == 'true'


async def check_voice_channel(user_id):
    """Check if user is in a voice channel and return channel info"""
    try:
        import requests
        resp = requests.post(
            f'{VOICE_API_URL}/voice',
            json={'user_id': user_id},
            timeout=5
        )
        if resp.ok:
            return resp.json()
        return {'in_voice': False}
    except Exception as e:
        return {'in_voice': False, 'error': str(e)}


async def search_youtube(query, max_results=5):
    """Search YouTube using yt-dlp"""
    try:
        result = subprocess.run(
            ['yt-dlp', '--flat-playlist', '-J', f'ytsearch{max_results}:{query}'],
            capture_output=True, text=True, timeout=30
        )
        
        data = json.loads(result.stdout)
        entries = data.get('entries', [])
        
        results = []
        for e in entries:
            duration = e.get('duration', 0)
            results.append({
                'source': 'youtube',
                'title': e.get('title', 'Unknown'),
                'url': e.get('url', e.get('webpage_url', '')),
                'duration': duration,
                'thumbnail': e.get('thumbnail', '')
            })
        
        return results
        
    except Exception as e:
        return []


async def search_soundcloud(query, max_results=5):
    """Search SoundCloud"""
    try:
        # Use soundcloud-pc or scrape
        result = subprocess.run(
            ['scsearch', query] if os.path.exists('/usr/bin/scsearch') else 
            ['yt-dlp', '--flat-playlist', '-J', f'ytsearch{max_results}:soundcloud {query}'],
            capture_output=True, text=True, timeout=30
        )
        
        # Fallback to yt-dlp with soundcloud query
        result = subprocess.run(
            ['yt-dlp', '--flat-playlist', '-J', f'ytsearch{max_results}:soundcloud {query}'],
            capture_output=True, text=True, timeout=30
        )
        
        data = json.loads(result.stdout)
        entries = data.get('entries', [])
        
        results = []
        for e in entries:
            if 'soundcloud' in e.get('url', '').lower():
                results.append({
                    'source': 'soundcloud',
                    'title': e.get('title', 'Unknown'),
                    'url': e.get('url', e.get('webpage_url', '')),
                    'duration': e.get('duration', 0),
                    'thumbnail': e.get('thumbnail', '')
                })
        
        return results
        
    except Exception as e:
        return []


def detect_url(text):
    """Detect if input is already a URL"""
    url_pattern = r'https?://[^\s]+'
    match = re.search(url_pattern, text)
    if match:
        return match.group(1)
    return None


async def search_all(query):
    """Search all sources and combine results"""
    # Check if it's already a URL
    url = detect_url(query)
    if url:
        return [{'source': 'direct', 'title': url, 'url': url, 'duration': 0}]
    
    # Search YouTube
    yt_results = await search_youtube(query, 5)
    
    # Try SoundCloud (fallback to YouTube results)
    sc_results = await search_soundcloud(query, 3)
    
    # Combine, YouTube first
    all_results = yt_results + sc_results
    
    # Remove duplicates by URL
    seen = set()
    unique = []
    for r in all_results:
        if r['url'] not in seen:
            seen.add(r['url'])
            unique.append(r)
    
    return unique[:8]  # Max 8 results


async def format_results(results):
    """Format results for display"""
    if not results:
        return "No streams found."
    
    text = "**Stream Search Results:**\n\n"
    for i, r in enumerate(results, 1):
        title = r['title'][:60]
        source = r['source'].upper()
        duration = r.get('duration', 0)
        
        if duration:
            mins = int(duration) // 60
            secs = int(duration) % 60
            text += f"**{i}.** {title} `[{source}]` ({mins}:{secs:02d})\n"
        else:
            text += f"**{i}.** {title} `[{source}]`\n"
    
    return text


async def play_stream(url, channel_id=None):
    """Play a stream via Voice API"""
    try:
        import requests
        
        payload = {'url': url}
        if channel_id:
            payload['channel_id'] = channel_id
        
        resp = requests.post(
            f'{VOICE_API_URL}/stream',
            json=payload,
            timeout=10
        )
        
        if resp.ok:
            return "Now playing! 🎵"
        else:
            return f"Error: {resp.json().get('error', 'Failed to play')}"
            
    except Exception as e:
        return f"Error playing stream: {e}"


# Main handler for OpenClaw
async def handle(query, context=None, user_id=None):
    """
    Handle stream search request
    
    Args:
        query: What to search for
        context: Optional - 'auto' to auto-play, 'list' to just list
        user_id: Discord user ID to check voice channel
    
    Returns:
        Formatted response with results or play status
    """
    # Detect context
    auto_play = AUTO_PLAY
    if context:
        auto_play = context.lower() == 'auto'
    
    # Check voice channel if user_id provided
    voice_info = None
    if user_id:
        voice_info = await check_voice_channel(user_id)
    
    # Search
    results = await search_all(query)
    
    if not results:
        return "I couldn't find any streams for that. Try a different search?"
    
    # Format for display
    response = await format_results(results)
    
    if auto_play and results:
        # Auto-play the first/best result
        url = results[0]['url']
        
        # Use channel_id from voice check if available
        channel_id = None
        if voice_info and voice_info.get('in_voice'):
            channel_id = voice_info.get('channel_id')
        
        play_result = await play_stream(url, channel_id)
        response = f"{response}\n\n{play_result}"
    
    return response


# For testing
if __name__ == '__main__':
    async def test():
        results = await search_all('lofi beats')
        print(await format_results(results))
    
    asyncio.run(test())
