# OpenClaw Voice - Stream & TTS Bot

A flexible Discord voice channel bot for OpenClaw - streams audio from anywhere, speaks notifications, and integrates with OpenClaw for intelligent voice responses.

## Features

- **Multi-source Stream Search** - Search YouTube, Twitch, radio stations, podcasts
- **Voice Notifications** - OpenClaw triggers TTS announcements (builds complete, reminders, etc.)
- **Intelligent Responses** - OpenClaw decides: play a stream OR speak the response
- **Configurable Bot Name** - Works with any bot name
- **Native Commands** - Full Discord slash commands
- **OpenClaw Skill** - One-click installation for OpenClaw instances

## Quick Start

### Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your bot token and settings

# Run
python3 bot.py
```

### Run with Docker

```bash
docker build -t openclaw-voice .
docker run -d --env-file .env openclaw-voice
```

## Configuration (.env)

```env
DISCORD_BOT_TOKEN=your_token_here
BOT_NAME=OpenClaw
DEFAULT_VOLUME=0.8
NOTIFIER_PORT=5000
OLLAMA_URL=http://localhost:11434
```

## Commands

### Slash Commands
- `/play <query>` - Search and play audio (YouTube, streams, radio)
- `/stream <url>` - Play a direct stream URL
- `/say <message>` - Speak a message via TTS
- `/join` - Join your voice channel
- `/leave` - Leave voice channel
- `/stop` - Stop playback
- `/search <query>` - Search for streams/audio

### Message Commands (with @mention)
- `@OpenClaw play jazz` - Play music
- `@OpenClaw say hello` - Speak a message
- `@OpenClaw stream https://...` - Play direct URL

## OpenClaw Integration

### Notifier API

Trigger voice from OpenClaw:

```bash
# TTS Notification
curl -X POST http://localhost:5000/notify \
  -H "Content-Type: application/json" \
  -d '{"message": "Kevin, your build is done!", "channel_id": "123456789"}'

# Play Stream
curl -X POST http://localhost:5000/stream \
  -H "Content-Type: application/json" \
  -d '{"url": "https://stream.url", "channel_id": "123456789"}'

# Search Streams
curl "http://localhost:5000/search?q=lofi+hip+hop+radio"
```

### OpenClaw Skill

Install as an OpenClaw skill for seamless integration:

```bash
# The skill provides:
# - Voice command shortcuts
# - Automatic TTS for notifications
# - Stream search integration
```

## Architecture

```
┌─────────────┐     API      ┌──────────────────┐
│   OpenClaw  │──────────────▶│  OpenClaw Voice  │
│  (brain)    │   /notify     │  (Discord bot)   │
│             │   /stream     │                  │
│             │   /search     │  - Stream player │
│             │               │  - TTS engine    │
│             │               │  - Multi-source  │
└─────────────┘               └──────────────────┘
        │                              │
        │ Context-aware               │
        │ decisions:                  │
        │ - News → stream or TTS?     │
        │ - Music → play              │
        │ - Alert → TTS               │
        ▼                              ▼
```

## Supported Sources

- YouTube / YouTube Music
- Twitch streams
- Direct stream URLs (MP3, AAC, OGG)
- Internet radio stations
- Any direct audio URL

## License

MIT
