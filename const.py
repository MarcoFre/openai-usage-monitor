"""Constants for the OpenAI Usage Monitor integration."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "openai_usage_monitor"

PLATFORMS = ["sensor"]

DEFAULT_NAME = "OpenAI Usage Monitor"
DEFAULT_SCAN_INTERVAL = timedelta(minutes=10)

CONF_API_KEY = "api_key"
CONF_SCAN_INTERVAL = "scan_interval"

ATTR_COST = "cost"
ATTR_CURRENCY = "currency"
ATTR_REQUESTS = "requests"
ATTR_INPUT_TOKENS = "input_tokens"
ATTR_OUTPUT_TOKENS = "output_tokens"
ATTR_CACHED_TOKENS = "cached_tokens"
ATTR_AUDIO_INPUT_TOKENS = "audio_input_tokens"
ATTR_IMAGE_OUTPUT_TOKENS = "image_output_tokens"

API_BASE_URL = "https://api.openai.com/v1"
