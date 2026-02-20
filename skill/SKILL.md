---
name: openclaw-voice
description: Voice channel integration for OpenClaw - plays streams, TTS notifications, and integrates with Discord voice. Provides commands for music, radio, news streams, and can auto-decide between playing a stream or speaking via TTS based on context.
metadata:
  openclaw:
    emoji: "🎤"
    requires:
      bins: ["python3", "ffmpeg", "yt-dlp"]
      pip: ["discord.py>=2.0.0", "yt-dlp", "gTTS", "python-dotenv", "aiohttp", "PyNaCl"]
      env:
        - DISCORD_BOT_TOKEN
        - BOT_NAME
        - NOTIFIER_PORT
---

# OpenClaw Voice Skill

This skill provides OpenClaw with Discord voice channel capabilities - music streaming, TTS notifications, and intelligent audio responses.

## What This Skill Does

- **Plays audio streams** (YouTube, radio, direct URLs) in Discord voice channels
- **TTS notifications** - Speaks messages when triggered by OpenClaw
- **Smart decisions** - Decides whether to play a stream OR speak via TTS based on context
- **Search** - Find streams/audio from multiple sources

## Setup

### 1. Create Discord Bot

1. Go to https://discord.com/developers/applications
2. Create new application
3. Go to Bot section, create bot
4. Enable **Message Content Intent** and **Voice States**
5. Generate token (put in `.env`)
6. Invite bot: OAuth2 > URL Generator > bot > voice channels > your server

### 2. Install

```bash
# Clone or copy to your server
cd /path/to/openclaw-voice

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your Discord bot token

# Run
python3 bot.py
```

### 3. Docker (Recommended)

```bash
# Build
docker build -t openclaw-voice .

# Run
docker run -d --env-file .env openclaw-voice
```

## OpenClaw Integration

### Environment

Set these in your OpenClaw config or environment:

```
OPENCLAW_VOICE_URL=http://localhost:5000
```

### Usage in OpenClaw

#### Basic Notification (TTS)
```
When [trigger], send to openclaw-voice:
  message: "Kevin, your build finished!"
```

#### Stream Search & Play
```
When user asks to play music:
  curl -X POST http://localhost:5000/stream \
    -H "Content-Type: application/json" \
    -d '{"url": "https://stream.url", "channel_id": "123"}'
```

#### AI Decision (Stream or TTS)
```
When user asks for news:
  curl -X POST http://localhost:5000/decide \
    -H "Content-Type: application/json" \
    -d '{"context": "news", "message": "Here are today\'s top headlines...", "channel_id": "123"}'
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/status` | GET | Health check |
| `/notify` | POST | TTS notification |
| `/stream` | POST | Play direct stream |
| `/search` | GET | Search streams |
| `/decide` | POST | AI decides: stream or TTS |

## Commands

### Message Commands (with @mention)
- `@OpenClaw play jazz` - Search and play
- `@OpenClaw say hello` - TTS speak
- `@OpenClaw stream https://...` - Play URL
- `@OpenClaw stop` - Stop playback
- `@OpenClaw join` / `@OpenClaw leave`

### Slash Commands
- `/play <query>` - Play audio
- `/say <message>` - TTS speak
- `/stream <url>` - Play URL
- `/join` / `/leave`
- `/stop`

## Context-Aware Decisions

The `/decide` endpoint lets OpenClaw decide the best audio response:

```json
{
  "context": "music playlist",
  "message": "lofi hip hop radio",
  "channel_id": "123"
}
```

OpenClaw Voice will:
1. Parse context (music → find stream)
2. Search for matching audio
3. Play stream OR fallback to TTS

## Files

- `bot.py` - Main bot with all commands
- `requirements.txt` - Python dependencies
- `Dockerfile` - Container definition
- `.env.example` - Config template

## Troubleshooting

```bash
# Check if running
curl http://localhost:5000/status

# Check bot logs
# (if running in terminal, check output)

# Restart
pkill -f bot.py
python3 bot.py
```
