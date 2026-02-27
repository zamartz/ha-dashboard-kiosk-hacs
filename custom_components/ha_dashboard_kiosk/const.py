"""Constants for the Custom Kiosk Events integration."""

from __future__ import annotations

from homeassistant.const import Platform

DOMAIN = "ha_dashboard_kiosk"

PLATFORMS: list[Platform] = [Platform.SENSOR]

CONF_NAME = "name"
CONF_WEBHOOK_ID = "webhook_id"
CONF_FIRE_EVENTS = "fire_events"
CONF_NOTIFY_ON_ERROR = "notify_on_error"
CONF_NOTIFY_ADMIN_OPEN = "notify_on_admin_open"

DEFAULT_NAME = "Custom Kiosk Events"

# Matches old blueprint default webhook id so the app
# does not need to be reconfigured.
DEFAULT_WEBHOOK_ID = "ha-dashboard-kiosk-wh"

# Event type the app sends to /api/events/ha_dashboard_kiosk
EVENT_APP = "ha_dashboard_kiosk"

# Event we fire after processing (matches old blueprint).
EVENT_KIOSK = "kiosk_event_received"

# Known kiosk event names used for counters.
KIOSK_EVENT_IDLE_START = "idle_start"
KIOSK_EVENT_IDLE_END = "idle_end"
KIOSK_EVENT_FADE_START = "fade_to_black_start"
KIOSK_EVENT_FADE_END = "fade_to_black_end"
KIOSK_EVENT_ADMIN_OPEN = "admin_open"
KIOSK_EVENT_ADMIN_CLOSE = "admin_close"
KIOSK_EVENT_ERROR = "error"

KIOSK_COUNTER_EVENTS = [
    KIOSK_EVENT_IDLE_START,
    KIOSK_EVENT_IDLE_END,
    KIOSK_EVENT_FADE_START,
    KIOSK_EVENT_FADE_END,
    KIOSK_EVENT_ADMIN_OPEN,
    KIOSK_EVENT_ADMIN_CLOSE,
    KIOSK_EVENT_ERROR,
]


