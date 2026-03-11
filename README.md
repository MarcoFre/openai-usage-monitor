# OpenAI Usage Monitor

Custom Home Assistant integration for monitoring OpenAI API usage and costs, including tokens, requests, cached tokens, audio, and image usage.

## Features

- Native Home Assistant integration
- UI-based configuration flow
- OpenAI Admin API usage monitoring
- OpenAI Admin API cost monitoring
- Rolling 24h sensors
- Today UTC sensors for direct comparison with OpenAI exports
- Configurable polling interval
- HACS custom repository compatible

## Requirements

- Home Assistant 2026.3.0 or newer
- HACS installed
- An OpenAI Admin API key
- OpenAI organization access with permission to use organization usage and cost endpoints

## How to get an OpenAI Admin API key

This integration requires an **OpenAI Admin API key**.

A standard project API key is **not** enough for the organization usage and cost endpoints used by this integration.

### Requirements

- You must be an **Organization Owner** in the OpenAI API Platform
- Only **Organization Owners** can create and use Admin API keys

### Steps

1. Open the OpenAI API Platform
2. Go to your **Organization**
3. Open **Admin keys** from the left sidebar
4. Click **Create new admin key**
5. Copy the key and use it when setting up the integration in Home Assistant

### Notes

- Admin API keys are intended for administration endpoints
- They should not be used as normal model API keys
- Keep the key secret and do not share it

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

    https://github.com/MarcoFre/openai-usage-monitor

### Option 2 — Manual installation

1. Copy the `custom_components/openai_usage_monitor` folder into your Home Assistant `custom_components` directory
2. Restart Home Assistant

Resulting structure:

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
            ├── translations/
            │   ├── en.json
            │   └── it.json
            └── brand/
                ├── icon.png
                └── logo.png

## Configuration

1. Go to **Settings → Devices & Services**
2. Click **Add Integration**
3. Search for **OpenAI Usage Monitor**
4. Enter your **OpenAI Admin API key**
5. Choose the update interval in minutes
6. Finish setup

## Sensors

The integration creates the following sensors.

### Rolling 24h sensors

- `Cost today`
- `Requests 24h`
- `Input tokens 24h`
- `Output tokens 24h`
- `Cached tokens 24h`
- `Audio input tokens 24h`
- `Image output tokens 24h`

### Today UTC sensors

- `Cost today UTC`
- `Requests today UTC`
- `Input tokens today UTC`
- `Output tokens today UTC`
- `Cached tokens today UTC`
- `Audio input tokens today UTC`
- `Image output tokens today UTC`

> Final entity IDs may vary depending on your Home Assistant naming rules.

## Why there are two sets of sensors

The integration provides two different views of your OpenAI usage:

- **Rolling 24h** sensors are useful for live monitoring over the last 24 hours
- **Today UTC** sensors are useful for comparing Home Assistant values with OpenAI daily exports

If you compare values against OpenAI CSV exports, use the **Today UTC** sensors.

## Notes

- This integration is designed for OpenAI organization-level monitoring
- A standard project API key is not enough for organization usage and cost endpoints
- The integration polls OpenAI at the interval configured during setup
- UTC-based sensors are intended to match OpenAI daily exports more closely

## Roadmap

- Breakdown sensors by model
- Breakdown sensors by project
- Improved diagnostics and debug information
- Example Lovelace dashboard
- Translation improvements
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

### Values do not match OpenAI exports

Use the **Today UTC** sensors when comparing data with OpenAI daily exports.

### Values do not update

- Check the configured polling interval
- Check Home Assistant logs for API or authentication errors

## Development status

This project is currently under active development.

## Disclaimer

This project is an independent custom integration and is not affiliated with or endorsed by OpenAI or Home Assistant.

## License

MIT
