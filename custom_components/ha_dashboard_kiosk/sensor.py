"""Sensors for Custom Kiosk Events."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_DEVICE_ID
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import (
    DOMAIN,
    EVENT_KIOSK,
    KIOSK_COUNTER_EVENTS,
    KIOSK_EVENT_ADMIN_CLOSE,
    KIOSK_EVENT_ADMIN_OPEN,
    KIOSK_EVENT_ERROR,
    KIOSK_EVENT_FADE_END,
    KIOSK_EVENT_FADE_START,
    KIOSK_EVENT_IDLE_END,
    KIOSK_EVENT_IDLE_START,
)


@dataclass
class KioskSensorData:
    """Simple in-memory store for kiosk statistics."""

    last_event_type: str | None = None
    last_event_device_id: str | None = None
    last_event_time: datetime | None = None
    total_events: int = 0
    counts: dict[str, int] | None = None


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up sensors from YAML (unused, kept for completeness)."""


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors for a config entry."""
    data = KioskSensorData()
    data.counts = {event: 0 for event in KIOSK_COUNTER_EVENTS}

    last_event_sensor = KioskLastEventSensor(entry, data)
    total_events_sensor = KioskTotalEventsSensor(entry, data)

    counter_sensors: list[KioskEventCounterSensor] = [
        KioskEventCounterSensor(
            entry,
            data,
            KIOSK_EVENT_IDLE_START,
            f"{entry.title} Idle Start Count",
            "mdi:motion-sensor",
        ),
        KioskEventCounterSensor(
            entry,
            data,
            KIOSK_EVENT_IDLE_END,
            f"{entry.title} Idle End Count",
            "mdi:motion-sensor-off",
        ),
        KioskEventCounterSensor(
            entry,
            data,
            KIOSK_EVENT_FADE_START,
            f"{entry.title} Fade Start Count",
            "mdi:brightness-4",
        ),
        KioskEventCounterSensor(
            entry,
            data,
            KIOSK_EVENT_FADE_END,
            f"{entry.title} Fade End Count",
            "mdi:brightness-7",
        ),
        KioskEventCounterSensor(
            entry,
            data,
            KIOSK_EVENT_ADMIN_OPEN,
            f"{entry.title} Admin Open Count",
            "mdi:lock-open-variant",
        ),
        KioskEventCounterSensor(
            entry,
            data,
            KIOSK_EVENT_ADMIN_CLOSE,
            f"{entry.title} Admin Close Count",
            "mdi:lock",
        ),
        KioskEventCounterSensor(
            entry,
            data,
            KIOSK_EVENT_ERROR,
            f"{entry.title} Error Count",
            "mdi:alert-circle-outline",
        ),
    ]

    async_add_entities(
        [last_event_sensor, total_events_sensor, *counter_sensors],
        update_before_add=False,
    )

    @callback
    def _handle_kiosk_event(event: Event) -> None:
        """Update sensors when a kiosk event is fired on the bus."""
        payload: dict[str, Any] = event.data
        evt: str | None = payload.get("event")

        data.last_event_type = evt
        data.last_event_device_id = payload.get("device_id")
        data.last_event_time = datetime.utcnow()
        data.total_events += 1

        if data.counts is not None and evt in data.counts:
            data.counts[evt] = data.counts.get(evt, 0) + 1

        last_event_sensor.async_write_ha_state()
        total_events_sensor.async_write_ha_state()
        for sensor in counter_sensors:
            sensor.async_write_ha_state()

    hass.bus.async_listen(EVENT_KIOSK, _handle_kiosk_event)


class KioskBaseSensor(SensorEntity):
    """Base class for kiosk sensors."""

    _attr_should_poll = False

    def __init__(self, entry: ConfigEntry) -> None:
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
        }


class KioskLastEventSensor(KioskBaseSensor):
    """Sensor showing the last kiosk event type and device."""

    _attr_icon = "mdi:tablet-dashboard"

    def __init__(self, entry: ConfigEntry, data: KioskSensorData) -> None:
        super().__init__(entry)
        self._entry = entry
        self._data = data
        self._attr_unique_id = f"{entry.entry_id}_last_event"
        self._attr_name = f"{entry.title} Last Event"

    @property
    def native_value(self) -> str | None:
        if not self._data.last_event_type:
            return None
        if self._data.last_event_device_id:
            return f"{self._data.last_event_type} ({self._data.last_event_device_id})"
        return self._data.last_event_type

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        attrs: dict[str, Any] = {}
        if self._data.last_event_device_id:
            attrs[ATTR_DEVICE_ID] = self._data.last_event_device_id
        if self._data.last_event_time:
            attrs["last_event_time"] = self._data.last_event_time.isoformat()
        return attrs


class KioskTotalEventsSensor(KioskBaseSensor):
    """Sensor counting all kiosk events received."""

    _attr_icon = "mdi:counter"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = "events"

    def __init__(self, entry: ConfigEntry, data: KioskSensorData) -> None:
        super().__init__(entry)
        self._entry = entry
        self._data = data
        self._attr_unique_id = f"{entry.entry_id}_total_events"
        self._attr_name = f"{entry.title} Total Events"

    @property
    def native_value(self) -> int:
        return self._data.total_events


class KioskEventCounterSensor(KioskBaseSensor):
    """Sensor counting how many times a given kiosk event occurred."""

    def __init__(
        self,
        entry: ConfigEntry,
        data: KioskSensorData,
        event_name: str,
        friendly_name: str,
        icon: str,
    ) -> None:
        super().__init__(entry)
        self._entry = entry
        self._data = data
        self._event_name = event_name
        self._attr_unique_id = f"{entry.entry_id}_{event_name}_count"
        self._attr_name = friendly_name
        self._attr_icon = icon
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_native_unit_of_measurement = "events"

    @property
    def native_value(self) -> int:
        if self._data.counts is None:
            return 0
        return self._data.counts.get(self._event_name, 0)


