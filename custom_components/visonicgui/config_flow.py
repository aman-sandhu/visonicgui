import asyncio
import logging
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.components.alarm_control_panel import DOMAIN as ALARM_DOMAIN
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

class VisonicConfigFlow(config_entries.ConfigFlow):
    """Handle a config flow for the Visonic integration."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self._host = None
        self._port = None

    async def async_step_user(self, user_input=None):
        """Handle the user input."""
        if user_input is not None:
            self._host = user_input[CONF_HOST]
            self._port = user_input[CONF_PORT]
            # Continue with async setup after user input
            return await self.async_create_entry(title="Visonic", data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=self._get_user_input_schema()
        )

    def _get_user_input_schema(self):
        """Return the schema for user input."""
        return cv.Schema({
            CONF_HOST: cv.string,
            CONF_PORT: cv.port
        })

async def async_setup_entry(hass, config_entry):
    """Set up the integration after it has been configured."""
    _LOGGER.debug("Setting up Visonic config entry")
    # Add any additional setup steps if needed.
    return True
