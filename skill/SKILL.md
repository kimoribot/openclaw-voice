---
name: openclaw-voice
description: Discord voice channel integration for OpenClaw - plays streams and speaks TTS. Pure renderer - OpenClaw handles the brain.
metadata:
  openclaw:
    emoji: "🎤"
    requires:
      bins: ["python3", "ffmpeg", "yt-dlp"]
      pip: ["discord.py>=2.0.0", "yt-dlp", "gTTS", "python-dotenv", "aiohttp", "PyNaCl"]
      env:
        - DISCORD_BOT_TOKEN
        - BOT_NAME
        - VERBOSITY
---

# OpenClaw Voice Skill

Discord voice channel integration - a pure renderer. OpenClaw handles the brain, this speaks the results.

## Architecture

```
User: @OpenClaw what's the weather
  → OpenClaw (text): Processes, gets weather info
  → OpenClaw: Calls OpenClaw Voice API
  → OpenClaw Voice: Joins & speaks the response
```

**OpenClaw Voice = Renderer**
- Plays music streams
- Speaks TTS messages
- No AI/brain of its own

**OpenClaw = Brain**
- Processes user requests
- Uses tools, search, memory
- Calls OpenClaw Voice to speak results

## Setup

### 1. Create Discord Bot

1. Go to https://discord.com/developers/applications
2. Create new application
3. Create bot, enable **Message Content Intent** and **Voice States**
4. Get token, put in `.env`
5. Invite: OAuth2 > URL Generator > bot > voice channels

### 2. Install

```bash
git clone https://github.com/kimoribot/openclaw-voice.git
cd openclaw-voice
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your bot token
```

### 3. Run

```bash
# Local
python3 -m openclaw_voice.bot

# Docker
docker build -t openclaw-voice .
docker run -d --env-file .env openclaw-voice
```

## Configuration

```env
DISCORD_BOT_TOKEN=your_token
BOT_NAME=OpenClaw
VERBOSITY=minimal  # silent | minimal | normal | verbose
```

## Commands

### For Users

- `/play <query>` - Play YouTube music
- `/say <message>` - Speak TTS
- `/stream <url>` - Play direct URL
- `/search <query>` - Search streams
- `/join` / `/leave` / `/stop`

**For AI requests:** Message @OpenClaw directly! OpenClaw will use voice to respond.

### For OpenClaw (API)

OpenClaw calls these endpoints to trigger voice:

```bash
# Speak a message (TTS)
curl -X POST http://localhost:5000/notify \
  -H "Content-Type: application/json" \
  -d '{"message": "Kevin, your build finished!", "channel_id": "123"}'

# Play a stream
curl -X POST http://localhost:5000/stream \
  -H "Content-Type: application/json" \
  -d '{"url": "https://stream.url", "channel_id": "123"}'

# Stop playback
curl -X POST http://localhost:5000/control \
  -H "Content-Type: application/json" \
  -d '{"action": "stop"}'

# Search streams
curl "http://localhost:5000/search?q=lofi"
```

## Integration

In your OpenClaw skill or code:

```python
import requests

def speak_in_voice(message, channel_id=None):
    """Call OpenClaw Voice to speak"""
    resp = requests.post('http://localhost:5000/notify', json={
        'message': message,
        'channel_id': channel_id
    })
    return resp.ok
```

## Files

- `openclaw_voice/bot.py` - Main entry
- `openclaw_voice/commands.py` - Slash commands
- `openclaw_voice/player.py` - Audio playback
- `openclaw_voice/api.py` - HTTP API server
- `openclaw_voice/config.py` - Configuration

## Troubleshooting

```bash
# Check status
curl http://localhost:5000/status
```
