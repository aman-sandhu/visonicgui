"""Config flow for Visonic Alarm integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

from . import (
    CONF_APP_ID,
    CONF_EVENT_HOUR_OFFSET,
    CONF_NO_PIN_REQUIRED,
    CONF_PANEL_ID,
    CONF_PARTITION,
    CONF_USER_CODE,
    CONF_USER_EMAIL,
    CONF_USER_PASSWORD,
    DEFAULT_NAME,
    DEFAULT_PARTITION,
)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_APP_ID): cv.string,
        vol.Required(CONF_USER_CODE): cv.string,
        vol.Required(CONF_USER_EMAIL): cv.string,
        vol.Required(CONF_USER_PASSWORD): cv.string,
        vol.Required(CONF_PANEL_ID): cv.string,
        vol.Optional(CONF_PARTITION, default=DEFAULT_PARTITION): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_NO_PIN_REQUIRED, default=False): cv.boolean,
        vol.Optional(CONF_EVENT_HOUR_OFFSET, default=0): vol.All(
            vol.Coerce(int), vol.Range(min=-24, max=24)
        ),
    }
)


class VisonicConfigFlow(config_entries.ConfigFlow, domain="visonicalarm"):
    """Handle a config flow for Visonic Alarm."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            # Validate by trying to connect to the alarm library in executor
            try:
                # Import the visonic library here
                from visonic import alarm as visonicalarm  # type: ignore
            except Exception as ex:  # pragma: no cover - import/runtime
                _LOGGER.exception("Failed to import visonic library: %s", ex)
                errors["base"] = "import_error"
                return self.async_show_form(step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors)

            # Create a candidate hub and attempt to connect
            hub = visonicalarm.System(
                user_input[CONF_HOST],
                user_input[CONF_APP_ID],
                user_input[CONF_USER_CODE],
                user_input[CONF_USER_EMAIL],
                user_input[CONF_USER_PASSWORD],
                user_input[CONF_PANEL_ID],
                user_input.get(CONF_PARTITION, DEFAULT_PARTITION),
            )

            # Try to connect in the executor
            connected = await self.hass.async_add_executor_job(hub.connect)
            if not connected:
                errors["base"] = "cannot_connect"
                return self.async_show_form(step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors)

            # use host + panel id as unique id candidate
            uniq = f"{user_input[CONF_HOST]}_{user_input[CONF_PANEL_ID]}"
            await self.async_set_unique_id(uniq)
            self._abort_if_unique_id_configured(updates=user_input)

            return self.async_create_entry(title=user_input.get(CONF_NAME, "Visonic Alarm"), data=user_input)

        return self.async_show_form(step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors={})

    async def async_step_import(self, import_config: dict[str, Any]):
        """Handle import from configuration.yaml."""
        # Called by async_setup when YAML exists; treat similar to user step.
        # Avoid duplicates by unique id
        uniq = f"{import_config[CONF_HOST]}_{import_config[CONF_PANEL_ID]}"
        await self.async_set_unique_id(uniq)
        self._abort_if_unique_id_configured(updates=import_config)

        return await self.async_step_user(import_config)
