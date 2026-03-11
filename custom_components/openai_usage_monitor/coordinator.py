"""Data coordinator for OpenAI Usage Monitor."""

from __future__ import annotations

import logging
from typing import Any
from datetime import UTC, datetime, timedelta
from aiohttp import ClientError
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

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

    @staticmethod
    def _aggregate_usage(buckets: list[dict[str, Any]]) -> dict[str, int]:
        """Aggregate usage metrics from OpenAI buckets."""
        totals = {
            "requests": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "cached_tokens": 0,
            "audio_input_tokens": 0,
            "image_output_tokens": 0,
        }

        for bucket in buckets:
            for result in bucket.get("results", []):
                totals["requests"] += int(result.get("num_model_requests", 0) or 0)
                totals["input_tokens"] += int(result.get("input_tokens", 0) or 0)
                totals["output_tokens"] += int(result.get("output_tokens", 0) or 0)
                totals["cached_tokens"] += int(
                    result.get("input_cached_tokens", 0) or 0
                )
                totals["audio_input_tokens"] += int(
                    result.get("input_audio_tokens", 0) or 0
                )
                totals["image_output_tokens"] += int(
                    result.get("output_image_tokens", 0) or 0
                )

        return totals

    @staticmethod
    def _aggregate_costs(buckets: list[dict[str, Any]]) -> dict[str, Any]:
        """Aggregate cost metrics from OpenAI buckets."""
        total = 0.0
        currency = "USD"

        for bucket in buckets:
            for result in bucket.get("results", []):
                amount = result.get("amount", {})
                total += float(amount.get("value", 0) or 0)
                if amount.get("currency"):
                    currency = str(amount["currency"]).upper()

        return {
            "value": round(total, 4),
            "currency": currency,
        }

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from OpenAI and aggregate metrics."""
        now_utc = datetime.now(UTC)
    
        end_time = int(now_utc.timestamp())
        start_24h = int((now_utc - timedelta(hours=24)).timestamp())
        start_today_utc = int(
            now_utc.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
        )
    
        # Safety guard: never allow an invalid range
        if end_time <= start_today_utc:
            end_time = start_today_utc + 60
    
        usage_24h_payload = await self._async_paginated_get(
            "/organization/usage/completions",
            {
                "start_time": start_24h,
                "end_time": end_time,
                "bucket_width": "1h",
                "limit": 168,
            },
        )
    
        usage_today_utc_payload = await self._async_paginated_get(
            "/organization/usage/completions",
            {
                "start_time": start_today_utc,
                "end_time": end_time,
                "bucket_width": "1h",
                "limit": 168,
            },
        )
    
        costs_today_utc_payload = await self._async_paginated_get(
            "/organization/costs",
            {
                "start_time": start_today_utc,
                "end_time": end_time,
                "bucket_width": "1d",
            },
        )
    
        usage_24h = self._aggregate_usage(usage_24h_payload["data"])
        usage_today_utc = self._aggregate_usage(usage_today_utc_payload["data"])
        costs_today_utc = self._aggregate_costs(costs_today_utc_payload["data"])
    
        currency = costs_today_utc["currency"]
    
        return {
            "currency": currency,
            # keep old key for compatibility, but now it is UTC-based
            "cost_today": costs_today_utc["value"],
            "cost_today_utc": costs_today_utc["value"],
            "requests_24h": usage_24h["requests"],
            "input_tokens_24h": usage_24h["input_tokens"],
            "output_tokens_24h": usage_24h["output_tokens"],
            "cached_tokens_24h": usage_24h["cached_tokens"],
            "audio_input_tokens_24h": usage_24h["audio_input_tokens"],
            "image_output_tokens_24h": usage_24h["image_output_tokens"],
            "requests_today_utc": usage_today_utc["requests"],
            "input_tokens_today_utc": usage_today_utc["input_tokens"],
            "output_tokens_today_utc": usage_today_utc["output_tokens"],
            "cached_tokens_today_utc": usage_today_utc["cached_tokens"],
            "audio_input_tokens_today_utc": usage_today_utc["audio_input_tokens"],
            "image_output_tokens_today_utc": usage_today_utc["image_output_tokens"],
            "raw_usage_24h": usage_24h_payload["data"],
            "raw_usage_today_utc": usage_today_utc_payload["data"],
            "raw_costs_today_utc": costs_today_utc_payload["data"],
        }
