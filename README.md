# OpenAI Usage Monitor

Custom Home Assistant integration for monitoring OpenAI API usage and costs, including tokens, requests, cached tokens, audio, and image usage.

## Features

- Native Home Assistant sensors
- OpenAI API usage monitoring
- OpenAI API cost monitoring
- Requests in the last 24 hours
- Input tokens in the last 24 hours
- Output tokens in the last 24 hours
- Cached tokens in the last 24 hours
- Audio input tokens in the last 24 hours
- Image output tokens in the last 24 hours
- UI-based configuration flow
- Configurable polling interval

## Requirements

- Home Assistant 2026.3.0 or newer
- HACS installed
- An OpenAI Admin API key
- OpenAI organization access with permission to use organization usage and cost endpoints

## Installation

### Option 1 — HACS custom repository

1. Open **HACS**
2. Open the menu in the top-right corner
3. Select **Custom repositories**
4. Add this repository URL
5. Select **Integration**
6. Click **Add**
7. Search for **OpenAI Usage Monitor**
8. Install it
9. Restart Home Assistant

Repository URL:

```text
https://github.com/MarcoFre/openai-usage-monitor

This project is an independent custom integration and is not affiliated with or endorsed by OpenAI or Home Assistant.

## License

MIT
