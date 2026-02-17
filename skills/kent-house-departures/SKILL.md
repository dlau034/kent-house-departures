---
name: kent-house-departures
description: Live departure board for Kent House Station (London)
metadata:
  openclaw:
    emoji: 🚆
---

# Kent House Departures

Live train departure board for Kent House Station (KNT), London.

## Features

- Real-time departure times
- Platform numbers
- Service status (On Time, Delayed, Cancelled)
- Destination information
- Auto-refresh every 60 seconds
- Mobile-friendly responsive design

## Setup

### Option A: TransportAPI (Recommended - Free Tier)

1. Sign up at https://transportapi.com
2. Get your App ID and API Key
3. Edit `config.json` with your credentials

### Option B: Realtime Trains API

1. Request API access at https://api.rtt.io
2. Get your username/password credentials
3. Edit `config.json` to use RTT mode

## Usage

Generate the departure board:
```bash
python3 /data/.openclaw/workspace/skills/kent-house-departures/fetch_departures.py
```

Serve the board (opens on port 8080):
```bash
python3 /data/.openclaw/workspace/skills/kent-house-departures/serve.py
```

Then open: http://localhost:8080

## Files

- `fetch_departures.py` - Fetches live train data
- `generate_html.py` - Generates the HTML board
- `departure_board.html` - The output file
- `config.json` - API credentials (you edit this)
- `serve.py` - Simple HTTP server
