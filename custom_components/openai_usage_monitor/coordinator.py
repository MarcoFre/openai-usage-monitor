"""Data coordinator for OpenAI Usage Monitor."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from aiohttp import ClientError
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import (
    API_BASE_URL,
    CONF_API_KEY,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class OpenAIUsageMonitorCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to fetch OpenAI usage and cost data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.entry = entry
        self._api_key: str = entry.data[CONF_API_KEY]
        self._session = async_get_clientsession(hass)

        scan_minutes = int(
            entry.options.get(
                CONF_SCAN_INTERVAL,
                int(DEFAULT_SCAN_INTERVAL.total_seconds() // 60),
            )
        )

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=scan_minutes),
        )

    async def _async_api_get(
        self,
        path: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Perform a GET request to the OpenAI API."""
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        url = f"{API_BASE_URL}{path}"

        try:
            response = await self._session.get(
                url,
                headers=headers,
                params=params,
                timeout=20,
            )
        except ClientError as err:
            raise UpdateFailed(f"Connection error: {err}") from err

        if response.status in (401, 403):
            raise ConfigEntryAuthFailed(
                "Invalid admin API key or insufficient permissions"
            )

        if response.status >= 400:
            body = await response.text()
            raise UpdateFailed(f"API error {response.status}: {body}")

        try:
            return await response.json()
        except ValueError as err:
            raise UpdateFailed("Invalid JSON returned by API") from err

    async def _async_paginated_get(
        self,
        path: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Fetch all pages from a paginated OpenAI endpoint."""
        all_data: list[dict[str, Any]] = []
        next_page: str | None = None

        while True:
            current_params = dict(params)
            if next_page:
                current_params["page"] = next_page

            payload = await self._async_api_get(path, current_params)

            all_data.extend(payload.get("data", []))

            if not payload.get("has_more"):
                break

            next_page = payload.get("next_page")
            if not next_page:
                break

        return {
            "data": all_data,
            "has_more": False,
            "next_page": None,
        }

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from OpenAI and aggregate metrics."""
        now = dt_util.now()
        end_time = int(now.timestamp())
        start_24h = int((now - timedelta(hours=24)).timestamp())
        start_today = int(
            now.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
        )

        usage_payload = await self._async_paginated_get(
            "/organization/usage/completions",
            {
                "start_time": start_24h,
                "end_time": end_time,
                "bucket_width": "1h",
                "limit": 168,
            },
        )

        costs_payload = await self._async_paginated_get(
            "/organization/costs",
            {
                "start_time": start_today,
                "end_time": end_time,
                "bucket_width": "1d",
            },
        )

        data: dict[str, Any] = {
            "cost_today": 0.0,
            "currency": "USD",
            "requests_24h": 0,
            "input_tokens_24h": 0,
            "output_tokens_24h": 0,
            "cached_tokens_24h": 0,
            "audio_input_tokens_24h": 0,
            "image_output_tokens_24h": 0,
            "raw_usage": usage_payload["data"],
            "raw_costs": costs_payload["data"],
        }

        for bucket in costs_payload["data"]:
            for result in bucket.get("results", []):
                amount = result.get("amount", {})
                data["cost_today"] += float(amount.get("value", 0) or 0)
                currency = amount.get("currency")
                if currency:
                    data["currency"] = str(currency).upper()

        for bucket in usage_payload["data"]:
            for result in bucket.get("results", []):
                data["requests_24h"] += int(result.get("num_model_requests", 0) or 0)
                data["input_tokens_24h"] += int(result.get("input_tokens", 0) or 0)
                data["output_tokens_24h"] += int(result.get("output_tokens", 0) or 0)
                data["cached_tokens_24h"] += int(
                    result.get("input_cached_tokens", 0) or 0
                )
                data["audio_input_tokens_24h"] += int(
                    result.get("input_audio_tokens", 0) or 0
                )
                data["image_output_tokens_24h"] += int(
                    result.get("output_image_tokens", 0) or 0
                )

        data["cost_today"] = round(data["cost_today"], 4)
        return data
