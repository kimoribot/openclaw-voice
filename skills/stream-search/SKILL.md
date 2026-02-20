# OpenClaw Stream Search Skill

Find and play streams from YouTube, SoundCloud, and direct URLs.

## Triggers

- "play {song/video/stream}"
- "search for {query}"
- "find {song/video}"
- "stream {query}"

## What it does

1. Searches multiple sources:
   - YouTube (yt-dlp)
   - SoundCloud (via yt-dlp fallback)
   - Direct URL detection

2. Returns top results or auto-plays best match

3. Checks user's voice channel automatically before playing

4. Plays via OpenClaw Voice API

## Setup

Requires:
- `yt-dlp` installed
- OpenClaw Voice running on localhost:5000

## Usage

```
User: play some lofi
OpenClaw: Checks if user is in voice channel...
  Found user in: General (Channel ID: 123)
  Found 5 results:
  1. Lofi Girl - 24/7 stream [YOUTUBE]
  2. Lofi Hip Hop Radio [YOUTUBE]
  ...
  Playing: Lofi Girl - 24/7 stream 🎵
```

## API Endpoints Used

- `POST /voice` - Check user's voice channel
- `POST /stream` - Play a stream URL

## Configuration

```
VOICE_API_URL=http://localhost:5000
AUTO_PLAY=false  # Set true to auto-play without asking
```
