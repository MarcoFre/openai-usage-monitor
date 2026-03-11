"""Config flow for OpenAI Usage Monitor."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
import logging

import voluptuous as vol

from aiohttp import ClientError
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import NumberSelector, NumberSelectorConfig

from .const import (
    API_BASE_URL,
    CONF_API_KEY,
    CONF_SCAN_INTERVAL,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


async def _validate_input(api_key: str, hass) -> None:
    """Validate the provided API key against OpenAI admin endpoints."""
    session = async_get_clientsession(hass)

    now = datetime.now(UTC)
    start_time = int((now - timedelta(days=1)).timestamp())
    end_time = int(now.timestamp())

    url = (
        f"{API_BASE_URL}/organization/costs"
        f"?start_time={start_time}&end_time={end_time}&bucket_width=1d"
    )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = await session.get(url, headers=headers, timeout=15)
    except ClientError as err:
        _LOGGER.debug("Connection error while validating API key: %s", err)
        raise CannotConnect from err

    if response.status in (401, 403):
        raise InvalidAuth

    if response.status >= 400:
        text = await response.text()
        _LOGGER.debug(
            "Unexpected response while validating API key. Status=%s Body=%s",
            response.status,
            text,
        )
        raise CannotConnect

    try:
        payload = await response.json()
    except (ValueError, TypeError) as err:
        _LOGGER.debug("Invalid JSON returned while validating API key: %s", err)
        raise CannotConnect from err

    if "data" not in payload:
        _LOGGER.debug("Validation payload missing 'data': %s", payload)
        raise CannotConnect


class OpenAIUsageMonitorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for OpenAI Usage Monitor."""

    VERSION = 1

    @staticmethod
    def async_get_options_flow(config_entry):
        """Return the options flow."""
        return OpenAIUsageMonitorOptionsFlow(config_entry)

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        errors: dict[str, str] = {}

        if user_input is not None:
            api_key = user_input[CONF_API_KEY].strip()
            scan_interval = int(user_input[CONF_SCAN_INTERVAL])

            try:
                await _validate_input(api_key, self.hass)
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pragma: no cover
                _LOGGER.exception("Unexpected exception during config flow")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=DEFAULT_NAME,
                    data={
                        CONF_API_KEY: api_key,
                    },
                    options={
                        CONF_SCAN_INTERVAL: scan_interval,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY): str,
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=DEFAULT_SCAN_INTERVAL.seconds // 60,
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=1,
                            max=1440,
                            mode="box",
                            step=1,
                        )
                    ),
                }
            ),
            errors=errors,
        )


class OpenAIUsageMonitorOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for OpenAI Usage Monitor."""

    def __init__(self, config_entry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the integration options."""
        if user_input is not None:
            return self.async_create_entry(
                title="",
                data={
                    CONF_SCAN_INTERVAL: int(user_input[CONF_SCAN_INTERVAL]),
                },
            )

        current_scan_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL,
            DEFAULT_SCAN_INTERVAL.seconds // 60,
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=current_scan_interval,
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=1,
                            max=1440,
                            mode="box",
                            step=1,
                        )
                    ),
                }
            ),
        )


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""


class InvalidAuth(Exception):
    """Error to indicate there is invalid auth."""
