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
- OpenAI organization access with permission to use organization usage/cost endpoints

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

### Option 2 — Manual installation

1. Copy the `custom_components/openai_usage_monitor` folder into your Home Assistant `custom_components` directory
2. Restart Home Assistant

Resulting structure:

~~~text
config/
└── custom_components/
    └── openai_usage_monitor/
        ├── __init__.py
        ├── manifest.json
        ├── const.py
        ├── coordinator.py
        ├── sensor.py
        ├── config_flow.py
        ├── strings.json
        └── translations/
~~~

## Configuration

1. Go to **Settings → Devices & Services**
2. Click **Add Integration**
3. Search for **OpenAI Usage Monitor**
4. Enter your **OpenAI Admin API key**
5. Choose the update interval in minutes
6. Finish setup

## Sensors

The integration creates these sensors:

- `sensor.openai_usage_monitor_cost_today`
- `sensor.openai_usage_monitor_requests_24h`
- `sensor.openai_usage_monitor_input_tokens_24h`
- `sensor.openai_usage_monitor_output_tokens_24h`
- `sensor.openai_usage_monitor_cached_tokens_24h`
- `sensor.openai_usage_monitor_audio_input_tokens_24h`
- `sensor.openai_usage_monitor_image_output_tokens_24h`

> Final entity IDs may vary depending on your Home Assistant naming rules.

## Notes

- This integration is designed for OpenAI organization-level monitoring.
- A standard project API key is not enough for organization usage/cost endpoints.
- The integration polls OpenAI at the interval configured during setup.
- Cost data is shown for the current day.
- Usage metrics are aggregated over the last 24 hours.

## Roadmap

- Additional breakdown sensors by model
- Additional breakdown sensors by project
- Better diagnostics and debug information
- Lovelace dashboard example
- Translations refinement
- HACS default repository submission

## Troubleshooting

### The integration cannot authenticate

Make sure:

- you entered an **Admin API key**
- the key is valid
- your OpenAI account has the required organization permissions

### Sensors do not appear

- Restart Home Assistant
- Check **Settings → System → Logs**
- Verify that the integration was added successfully

### Values do not update

- Check the configured polling interval
- Check Home Assistant logs for API or authentication errors

## Development status

This project is currently under active development.

## Disclaimer

This project is an independent custom integration and is not affiliated with or endorsed by OpenAI or Home Assistant.

## License

MIT
