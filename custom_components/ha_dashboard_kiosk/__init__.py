"""Custom Kiosk Events integration.

Receives events from the HA Dashboard Kiosk app (via webhook),
updates entities, and optionally fires Home Assistant events so
you can build your own automations and dashboards.
"""

from __future__ import annotations

from typing import Any, TypedDict

from aiohttp import web

from homeassistant.components import webhook
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE_ID
from homeassistant.core import CALLBACK_TYPE, Event, HomeAssistant, callback
from homeassistant.helpers.typing import ConfigType
from homeassistant.util import dt as dt_util

from .const import (
    CONF_FIRE_EVENTS,
    CONF_NOTIFY_ADMIN_OPEN,
    CONF_NOTIFY_ON_ERROR,
    CONF_WEBHOOK_ID,
    DOMAIN,
    EVENT_APP,
    EVENT_KIOSK,
    PLATFORMS,
)


class KioskRuntimeData(TypedDict, total=False):
    """Runtime data stored per config entry."""

    webhook_id: str
    remove_app_listener: CALLBACK_TYPE


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the integration from YAML (not used in normal operation)."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Custom Kiosk Events from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    webhook_id: str = entry.data[CONF_WEBHOOK_ID]

    @callback
    def _process_payload(payload: dict[str, Any]) -> None:
        """Process a kiosk event payload (from webhook or HA event)."""
        evt: str = str(payload.get("event") or "")
        timestamp: str = str(
            payload.get("timestamp") or dt_util.utcnow().isoformat()
        )
        idle_reason: str = str(payload.get("idle_reason") or "")
        error_type: str = str(payload.get("error_type") or "")
        device_id: str | None = payload.get("device_id")

        # Fire kiosk_event_received so existing automations can keep working.
        hass.bus.async_fire(
            EVENT_KIOSK,
            {
                "event": evt,
                "timestamp": timestamp,
                "idle_reason": idle_reason,
                "error_type": error_type,
                "entry_id": entry.entry_id,
                "webhook_id": webhook_id,
                "device_id": device_id,
            },
        )

        # Log to logbook (simpler than the original blueprint but similar).
        message = evt
        if idle_reason:
            message += f" ({idle_reason})"
        if error_type:
            message += f" - {error_type}"

        hass.services.async_call(
            "logbook",
            "log",
            {
                "name": "Kiosk Event",
                "message": message,
            },
            blocking=False,
        )

        # Optional notifications (mirrors old blueprint behaviour).
        if (
            evt == "admin_open"
            and entry.data.get(CONF_NOTIFY_ADMIN_OPEN, False)
        ):
            hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "title": "Kiosk Admin Opened",
                    "message": "Someone opened the admin panel on the dashboard kiosk.",
                },
                blocking=False,
            )

        if evt == "error" and entry.data.get(CONF_NOTIFY_ON_ERROR, True):
            hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "title": "Kiosk Error",
                    "message": f"Dashboard kiosk error. Type: {error_type or 'unknown'}",
                },
                blocking=False,
            )

    async def handle_webhook(
        hass: HomeAssistant, webhook_id: str, request: web.Request
    ) -> web.Response:
        """Handle incoming webhook calls from the kiosk app."""
        try:
            payload: dict[str, Any] = await request.json()
        except Exception:
            return web.Response(status=400, text="Invalid JSON")

        device_id: str | None = payload.get("device_id") or payload.get(CONF_DEVICE_ID)

        if entry.data.get(CONF_FIRE_EVENTS, True):
            _process_payload(
                {
                    "event": payload.get("event"),
                    "timestamp": payload.get("timestamp"),
                    "idle_reason": payload.get("idle_reason"),
                    "error_type": payload.get("error_type"),
                    "device_id": device_id,
                }
            )

        return web.Response(status=200, text="OK")

    webhook.async_register(
        hass,
        DOMAIN,
        entry.title,
        webhook_id,
        handle_webhook,
    )

    @callback
    def _handle_app_event(event: Event) -> None:
        """Handle events fired via /api/events/ha_dashboard_kiosk."""
        if not entry.data.get(CONF_FIRE_EVENTS, True):
            return

        data = event.data or {}
        _process_payload(
            {
                "event": data.get("event"),
                "timestamp": data.get("timestamp"),
                "idle_reason": data.get("idle_reason"),
                "error_type": data.get("error_type"),
                "device_id": data.get("device_id"),
            }
        )

    remove_app_listener = hass.bus.async_listen(EVENT_APP, _handle_app_event)

    hass.data[DOMAIN][entry.entry_id] = KioskRuntimeData(
        webhook_id=webhook_id,
        remove_app_listener=remove_app_listener,
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    runtime: KioskRuntimeData | None = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if runtime:
        if webhook_id := runtime.get("webhook_id"):
            webhook.async_unregister(hass, webhook_id)
        if remove_listener := runtime.get("remove_app_listener"):
            remove_listener()

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)

    return unload_ok

