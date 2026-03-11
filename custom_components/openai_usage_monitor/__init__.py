"""The OpenAI Usage Monitor integration."""
from .coordinator import OpenAIUsageMonitorCoordinator
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS

type OpenAIUsageMonitorConfigEntry = ConfigEntry

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the OpenAI Usage Monitor component."""
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: OpenAIUsageMonitorConfigEntry,
) -> bool:
    """Set up OpenAI Usage Monitor from a config entry."""
    coordinator = OpenAIUsageMonitorCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: OpenAIUsageMonitorConfigEntry,
) -> bool:
    """Unload an OpenAI Usage Monitor config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
