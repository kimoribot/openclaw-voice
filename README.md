# OpenClaw Discord Voice

Discord voice channel integration for OpenClaw - a pure renderer. OpenClaw handles the brain, this speaks the results.

## Quick Install

```bash
# Clone
git clone https://github.com/kimoribot/openclaw-discord-voice.git
cd openclaw-discord-voice

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your Discord bot token

# Run
python3 -m openclaw_voice.bot
```

## Or use npx + pip

```bash
npx git+https://github.com/kimoribot/openclaw-discord-voice.git
```

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `DISCORD_BOT_TOKEN` | Your Discord bot token | (required) |
| `BOT_NAME` | Bot display name | OpenClaw |
| `VERBOSITY` | Text output level | minimal |
| `TEXT_RESPONSE` | Text when speaking | always |
| `NOTIFIER_PORT` | API server port | 5000 |
| `DEFAULT_VOLUME` | Audio volume | 0.8 |

### TEXT_RESPONSE options
- `always` - Send text message when playing/speaking
- `never` - Only speak, no text
- `errors_only` - Only send errors (not implemented yet)

## Architecture

```
User: @OpenClaw what's the weather
  → OpenClaw (text): Processes, gets weather info
  → OpenClaw: Calls OpenClaw Discord Voice API
  → OpenClaw Discord Voice: Joins & speaks the response
```

**OpenClaw Discord Voice = Renderer**
- Plays music streams
- Speaks TTS messages
- No AI/brain of its own

**OpenClaw = Brain**
- Processes user requests
- Uses tools, search, memory
- Calls this to speak results

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/status` | GET | Health check |
| `/voice` | POST | Check user's voice channel |
| `/notify` | POST | Speak TTS message |
| `/stream` | POST | Play a stream URL |
| `/search` | GET | Search YouTube |
| `/control` | POST | Stop/pause playback |

### /voice
```bash
curl -X POST http://localhost:5000/voice \
  -H "Content-Type: application/json" \
  -d '{"user_id": "DISCORD_USER_ID"}'
```

### /notify
```bash
curl -X POST http://localhost:5000/notify \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "channel_id": "VOICE_CHANNEL_ID"}'
```

### /stream
```bash
curl -X POST http://localhost:5000/stream \
  -H "Content-Type: application/json" \
  -d '{"url": "https://youtube.com/watch?v=...", "channel_id": "VOICE_CHANNEL_ID"}'
```

## Commands (Slash)

- `/play <query>` - Play YouTube music
- `/say <message>` - Speak TTS
- `/stream <url>` - Play direct URL
- `/search <query>` - Search streams
- `/join` / `/leave` / `/stop`

## OpenClaw Integration

In your OpenClaw skill:
```python
import requests

def speak_in_voice(message, channel_id=None):
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
# Check if running
curl http://localhost:5000/status

# Check voice channels
curl -X POST http://localhost:5000/voice \
  -H "Content-Type: application/json" \
  -d '{"user_id": "YOUR_DISCORD_ID"}'
```