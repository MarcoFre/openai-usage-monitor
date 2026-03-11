"""Sensor platform for OpenAI Usage Monitor."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfInformation
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN
from .coordinator import OpenAIUsageMonitorCoordinator


@dataclass(frozen=True, kw_only=True)
class OpenAIUsageMonitorSensorEntityDescription(SensorEntityDescription):
    """Entity description for OpenAI Usage Monitor sensors."""

    value_fn: Callable[[dict[str, Any]], Any]


SENSOR_DESCRIPTIONS: tuple[OpenAIUsageMonitorSensorEntityDescription, ...] = (
    OpenAIUsageMonitorSensorEntityDescription(
        key="cost_today",
        name="Cost today",
        icon="mdi:currency-usd",
        device_class=SensorDeviceClass.MONETARY,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
        value_fn=lambda data: data.get("cost_today", 0.0),
    ),
    OpenAIUsageMonitorSensorEntityDescription(
        key="requests_24h",
        name="Requests 24h",
        icon="mdi:counter",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="req",
        value_fn=lambda data: data.get("requests_24h", 0),
    ),
    OpenAIUsageMonitorSensorEntityDescription(
        key="input_tokens_24h",
        name="Input tokens 24h",
        icon="mdi:arrow-down-bold-box",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="tok",
        value_fn=lambda data: data.get("input_tokens_24h", 0),
    ),
    OpenAIUsageMonitorSensorEntityDescription(
        key="output_tokens_24h",
        name="Output tokens 24h",
        icon="mdi:arrow-up-bold-box",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="tok",
        value_fn=lambda data: data.get("output_tokens_24h", 0),
    ),
    OpenAIUsageMonitorSensorEntityDescription(
        key="cached_tokens_24h",
        name="Cached tokens 24h",
        icon="mdi:database-arrow-down",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="tok",
        value_fn=lambda data: data.get("cached_tokens_24h", 0),
    ),
    OpenAIUsageMonitorSensorEntityDescription(
        key="audio_input_tokens_24h",
        name="Audio input tokens 24h",
        icon="mdi:microphone-message",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="tok",
        value_fn=lambda data: data.get("audio_input_tokens_24h", 0),
    ),
    OpenAIUsageMonitorSensorEntityDescription(
        key="image_output_tokens_24h",
        name="Image output tokens 24h",
        icon="mdi:image-outline",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="tok",
        value_fn=lambda data: data.get("image_output_tokens_24h", 0),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up OpenAI Usage Monitor sensors from a config entry."""
    coordinator: OpenAIUsageMonitorCoordinator = entry.runtime_data

    async_add_entities(
        OpenAIUsageMonitorSensor(coordinator, entry, description)
        for description in SENSOR_DESCRIPTIONS
    )


class OpenAIUsageMonitorSensor(
    CoordinatorEntity[OpenAIUsageMonitorCoordinator],
    SensorEntity,
):
    """Representation of an OpenAI Usage Monitor sensor."""

    entity_description: OpenAIUsageMonitorSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: OpenAIUsageMonitorCoordinator,
        entry: ConfigEntry,
        description: OpenAIUsageMonitorSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="OpenAI Usage Monitor",
            manufacturer="OpenAI",
            model="API Usage",
            entry_type=None,
        )

    @property
    def native_value(self) -> Any:
        """Return the sensor value."""
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the native unit of measurement."""
        if self.entity_description.key == "cost_today":
            return self.coordinator.data.get("currency", "USD")
        return self.entity_description.native_unit_of_measurement

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        if self.entity_description.key == "cost_today":
            return {
                "source": "OpenAI Admin API",
                "period": "today",
                "currency": self.coordinator.data.get("currency", "USD"),
            }

        if self.entity_description.key == "requests_24h":
            return {
                "source": "OpenAI Admin API",
                "period": "last_24_hours",
            }

        return {
            "source": "OpenAI Admin API",
            "period": "last_24_hours",
        }
