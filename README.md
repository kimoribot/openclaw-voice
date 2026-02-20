# OpenClaw Voice 🎤

A flexible Discord voice channel bot for OpenClaw - streams audio, TTS notifications, and intelligent voice responses.

## Features

- **Multi-source Streaming** - YouTube, direct URLs, radio streams
- **TTS Notifications** - Speak messages in voice channels
- **Smart /notify Command** - Searches web + AI to generate spoken responses
- **Configurable Verbosity** - Silent, minimal, normal, or verbose output
- **Docker Ready** - Easy deployment
- **OpenClaw Skill** - One-click integration

## Quick Start

### Run with Docker

```bash
# Build
docker build -t openclaw-voice .

# Run
docker run -d --env-file .env openclaw-voice
```

### Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your bot token

# Run
python3 -m openclaw_voice.bot
```

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `DISCORD_BOT_TOKEN` | Discord bot token | (required) |
| `BOT_NAME` | Bot display name | OpenClaw |
| `DEFAULT_VOLUME` | Audio volume (0.0-1.0) | 0.8 |
| `NOTIFIER_PORT` | API server port | 5000 |
| `VERBOSITY` | Output level | minimal |
| `ENABLE_AI` | Enable AI features | true |
| `OLLAMA_URL` | Ollama API URL | http://localhost:11434 |

### Verbosity Levels

- **silent** - Only errors
- **minimal** - Only important info (now playing, errors)
- **normal** - Standard responses  
- **verbose** - All debug info

## Commands

### Slash Commands
- `/play <query>` - Search and play YouTube audio
- `/search <query>` - Search for streams (preview)
- `/say <message>` - TTS speak a message
- `/notify <request>` - AI processes request + speaks in voice
- `/stream <url>` - Play direct URL
- `/join` / `/leave` - Voice channel control
- `/stop` - Stop playback

### Message Commands
- `@Bot play jazz` - Play music
- `@Bot say hello` - TTS speak
- `@Bot notify tell me the news` - AI + voice

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/status` | GET | Health check |
| `/notify` | POST | TTS notification |
| `/stream` | POST | Play stream URL |
| `/search` | GET | Search streams |

### API Examples

```bash
# TTS notification
curl -X POST http://localhost:5000/notify \
  -H "Content-Type: application/json" \
  -d '{"message": "Build complete!", "channel_id": "123"}'

# Play stream
curl -X POST http://localhost:5000/stream \
  -H "Content-Type: application/json" \
  -d '{"url": "https://stream.url", "channel_id": "123"}'

# Search
curl "http://localhost:5000/search?q=lofi"
```

## OpenClaw Integration

Set environment:
```
OPENCLAW_VOICE_URL=http://localhost:5000
```

Then OpenClaw can trigger voice notifications via the API.

## Version

Current: **v1.0.0**

## License

MIT
