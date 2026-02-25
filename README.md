HA Dashboard Kiosk – Home Assistant Integration (HACS)
=====================================================

This repository provides a Home Assistant custom integration for the **HA Dashboard Kiosk** iPad app.

It is designed to be installed via **HACS** and handles:

- A webhook endpoint that receives kiosk events from the app.
- Entities that track kiosk usage (idle/fade/admin/error).
- Event forwarding so you can build your own automations and dashboards.

> NOTE: This is an early version intended to replace the manual blueprint + helpers setup.

## Features

- Receive kiosk events from the app via REST or webhook.
- Maintain counters and/or sensors for:
  - Idle start / idle end
  - Fade to black start / fade to black end
  - Admin open / admin close
  - Errors (with type)
- Optionally fire a Home Assistant event (e.g. `ha_dashboard_kiosk`) for automations.

## Installation (HACS)

1. In Home Assistant, open **HACS → Integrations**.
2. Click the menu (⋮) and choose **Custom repositories**.
3. Add this repository URL as type **Integration**.
4. Install **HA Dashboard Kiosk** from the HACS list.
5. Restart Home Assistant.
6. Go to **Settings → Devices & services**, click **Add Integration**, and search for **HA Dashboard Kiosk**.

You will be guided through a config flow (once implemented) to enable:

- Webhook handling for your kiosk devices.
- Which counters/entities to create.
- Optional notifications on error or admin panel access.

## Usage

After setup you will get entities that you can:

- Display in any Lovelace card (statistics, history graph, etc.).
- Use in automations as triggers or conditions.
- Combine with your own cards and dashboards to monitor kiosk activity.

The companion iPad app will be configured to send events to this integration’s webhook endpoint instead of requiring manual blueprints and helpers.

