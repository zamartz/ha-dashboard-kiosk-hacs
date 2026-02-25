"""Config flow for HA Dashboard Kiosk."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.typing import ConfigType

from .const import (
    CONF_FIRE_EVENTS,
    CONF_NAME,
    CONF_NOTIFY_ADMIN_OPEN,
    CONF_NOTIFY_ON_ERROR,
    CONF_WEBHOOK_ID,
    DEFAULT_NAME,
    DOMAIN,
    DEFAULT_WEBHOOK_ID,
)


class HADashboardKioskConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HA Dashboard Kiosk."""

    VERSION = 1

    async def async_step_user(
        self, user_input: ConfigType | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Only a single instance is typically needed.
            if self._async_current_entries():
                return self.async_abort(reason="single_instance_allowed")

            data = {
                CONF_NAME: user_input[CONF_NAME],
                # Use fixed webhook id to match the old blueprint
                # so the app does not need to be reconfigured.
                CONF_WEBHOOK_ID: DEFAULT_WEBHOOK_ID,
                CONF_FIRE_EVENTS: user_input[CONF_FIRE_EVENTS],
                CONF_NOTIFY_ON_ERROR: user_input[CONF_NOTIFY_ON_ERROR],
                CONF_NOTIFY_ADMIN_OPEN: user_input[CONF_NOTIFY_ADMIN_OPEN],
            }

            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data=data,
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Required(CONF_FIRE_EVENTS, default=True): bool,
                vol.Required(CONF_NOTIFY_ON_ERROR, default=True): bool,
                vol.Required(CONF_NOTIFY_ADMIN_OPEN, default=False): bool,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )


@callback
def configured_instances(hass: HomeAssistant) -> list[config_entries.ConfigEntry]:
    """Return the configured instances of this integration."""
    return hass.config_entries.async_entries(DOMAIN)

