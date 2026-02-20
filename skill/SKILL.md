---
name: openclaw-voice
description: Voice channel integration for OpenClaw - plays streams, TTS notifications, and AI-powered voice responses. Configure verbosity to control Discord text output.
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

Discord voice channel integration for OpenClaw - streams audio and speaks notifications.

## Setup

### 1. Create Discord Bot

1. Go to https://discord.com/developers/applications
2. Create new application
3. Create bot, enable **Message Content Intent** and **Voice States**
4. Get token, put in `.env`
5. Invite: OAuth2 > URL Generator > bot > voice channels

### 2. Install

```bash
# Clone
git clone https://github.com/kimoribot/openclaw-voice.git
cd openclaw-voice

# Install
pip install -r requirements.txt

# Configure
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
ENABLE_AI=true
OLLAMA_URL=http://localhost:11434
```

## Commands

- `/play <query>` - Play YouTube
- `/search <query>` - Search streams
- `/say <message>` - TTS speak
- `/notify <request>` - AI processes + speaks
- `/stream <url>` - Play URL
- `/join` / `/leave` / `/stop`

## API

```bash
# Notify
curl -X POST http://localhost:5000/notify \
  -d '{"message": "Done!", "channel_id": "123"}'

# Stream
curl -X POST http://localhost:5000/stream \
  -d '{"url": "https://...", "channel_id": "123"}'
```

## Troubleshooting

```bash
# Check status
curl http://localhost:5000/status
```
