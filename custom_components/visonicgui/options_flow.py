"""Options flow for Visonic Alarm integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
import homeassistant.helpers.config_validation as cv

from . import (
    CONF_EVENT_HOUR_OFFSET,
    CONF_NO_PIN_REQUIRED,
    CONF_PARTITION,
    CONF_USER_CODE,
    DEFAULT_NAME,
    DEFAULT_PARTITION,
)

OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_PARTITION, default=DEFAULT_PARTITION): cv.string,
        vol.Optional(CONF_NO_PIN_REQUIRED, default=False): cv.boolean,
        vol.Optional(CONF_EVENT_HOUR_OFFSET, default=0): vol.All(vol.Coerce(int), vol.Range(min=-24, max=24)),
        vol.Optional(CONF_USER_CODE): cv.string,
    }
)


class VisonicOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Visonic Alarm."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(step_id="init", data_schema=OPTIONS_SCHEMA)
