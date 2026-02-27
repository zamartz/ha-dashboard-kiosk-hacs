# HA Dashboard Kiosk

[![hacs_badge](https://img.shields.io/badge/HACS-Integration-239B56.svg?style=flat-square)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/zamartz/ha-dashboard-kiosk-hacs.svg?style=flat-square)](https://github.com/zamartz/ha-dashboard-kiosk-hacs/releases)

Home Assistant custom integration for the **HA Dashboard Kiosk** iPad app. Receives kiosk events via webhook or REST, exposes sensors and counters, and fires events for automations—no manual blueprints or helpers required.

**App & documentation:** [hacustomkiosk.com](https://hacustomkiosk.com) — iOS app download, setup guide, and full docs.

| Screenshot (placeholder) |
|--------------------------|
| ![HA Dashboard Kiosk screenshot](https://placehold.co/800x400/1a1a2e/eee?text=HA+Dashboard+Kiosk+Screenshot&font=roboto) |

Replace the image URL above with your own screenshot (e.g. from the app or HA entities).

---

## Installation

**Use HACS (recommended):**

1. Open **HACS → Integrations**.
2. Click the menu (⋮) → **Custom repositories**.
3. Add this repository URL as type **Integration**.
4. Search for **HA Dashboard Kiosk** and install.
5. Restart Home Assistant.
6. Go to **Settings → Devices & services** → **Add Integration** → search **HA Dashboard Kiosk**.

Follow the config flow to set a name, webhook behavior, and optional notifications (error / admin open).

---

## Important info

- **Webhook ID:** The integration uses a fixed webhook ID (`ha-dashboard-kiosk-wh`) so the app does not need reconfiguring if you used the original blueprint.
- **Single instance:** One integration instance is typical; it handles all kiosk devices that send events to the same webhook or REST endpoint.
- **App setup:** Configure the iPad app to send events to Home Assistant (REST or webhook) as described at [hacustomkiosk.com](https://hacustomkiosk.com).

---

## What you get

| Feature | Description |
|--------|-------------|
| **Webhook / REST** | Receives events from the app at `/api/webhook/ha-dashboard-kiosk-wh` or via `ha_dashboard_kiosk` REST events. |
| **Sensors** | Last event, total events, and per-type counters (idle start/end, fade start/end, admin open/close, error). |
| **Events** | Fires `kiosk_event_received` with `event`, `timestamp`, `idle_reason`, `error_type` for your automations. |
| **Notifications** | Optional persistent notifications when the admin panel is opened or when an error is reported. |
| **Logbook** | Kiosk events are logged for history and debugging. |

---

## Config flow options

| Option | Default | Description |
|--------|---------|-------------|
| **Name** | HA Dashboard Kiosk | Friendly name for the integration and entity names. |
| **Fire events** | On | Fire `kiosk_event_received` so automations can react. |
| **Notify on error** | On | Send a persistent notification when the app reports an error. |
| **Notify on admin open** | Off | Send a notification when someone opens the admin panel on the kiosk. |

---

## Usage

After setup you get entities such as:

- **Last Event** — last kiosk event type (and device).
- **Total Events** — count of all events received.
- **Idle Start / Idle End / Fade Start / Fade End / Admin Open / Admin Close / Error** — per-type counters.

Use them in:

- **Lovelace** — statistics, history graph, or any card.
- **Automations** — triggers or conditions on `kiosk_event_received` or sensor states.

Full app setup and “Send events to HA” configuration: [hacustomkiosk.com](https://hacustomkiosk.com).

---

## Dashboard URL parameters (app kiosk mode)

The **HA Dashboard Kiosk** app can hide its own navigation based on query parameters in the dashboard URL (similar in spirit to [kiosk-mode](https://github.com/NemesisRE/kiosk-mode)). Configure the dashboard URL in the app; if it includes any of these params, the app applies the behavior:

| Param | Behavior |
|-------|----------|
| `?dash_kiosk` | Hide header + sidebar |
| `?dash_kiosk_hide_header` | Hide header only |
| `?dash_kiosk_hide_sidebar` | Hide sidebar (and swipe) |
| `?dash_kiosk_hide_overflow` | Hide top-right menu |
| `?dash_kiosk_hide_menubutton` | Hide sidebar menu icon |

Handled entirely by the app; the integration does not need to be configured for this.

---

## Related

- [HA Dashboard Kiosk – App & docs](https://hacustomkiosk.com)
- [NemesisRE/kiosk-mode](https://github.com/NemesisRE/kiosk-mode) — Lovelace frontend that hides header/sidebar via URL params (browser).

---

## Credit

This integration replaces the manual blueprint + counter-helpers setup. Kiosk URL parameter behavior is inspired by [kiosk-mode](https://github.com/NemesisRE/kiosk-mode) (MIT).
