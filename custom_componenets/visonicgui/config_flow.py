# custom_components/visonicgui/config_flow.py

import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_USER_CODE, CONF_USER_EMAIL, CONF_USER_PASSWORD, CONF_PANEL_ID, CONF_PARTITION
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

class VisonicGuiConfigFlow(config_entries.ConfigFlow, domain="visonicgui"):
    """Handle a config flow for Visonic GUI."""
    
    VERSION = 1
    
    def __init__(self):
        """Initialize the flow."""
        self._host = None
        self._app_id = None
        self._user_code = None
        self._user_email = None
        self._user_password = None
        self._panel_id = None
        self._partition = None

    async def async_step_user(self, user_input=None):
        """Handle the initial step of configuration."""
        errors = {}

        if user_input is not None:
            # Assign user input values
            self._host = user_input[CONF_HOST]
            self._app_id = user_input["app_id"]
            self._user_code = user_input["user_code"]
            self._user_email = user_input["user_email"]
            self._user_password = user_input["user_password"]
            self._panel_id = user_input["panel_id"]
            self._partition = user_input["partition"]

            # Attempt to establish a connection to the Visonic system
            try:
                from visonic import alarm as visonicalarm
                alarm = visonicalarm.System(
                    self._host,
                    self._app_id,
                    self._user_code,
                    self._user_email,
                    self._user_password,
                    self._panel_id,
                    self._partition
                )

                if not alarm.connect():
                    errors["base"] = "connection_error"
                else:
                    return self.async_create_entry(
                        title=self._host,
                        data={
                            CONF_HOST: self._host,
                            "app_id": self._app_id,
                            "user_code": self._user_code,
                            "user_email": self._user_email,
                            "user_password": self._user_password,
                            "panel_id": self._panel_id,
                            "partition": self._partition,
                        },
                    )
            except Exception as e:
                _LOGGER.error("Error during Visonic connection: %s", e)
                errors["base"] = "unknown_error"
        
        # Show the form for the user to input configuration
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST): str,
                vol.Required("app_id"): str,
                vol.Required("user_code"): str,
                vol.Required("user_email"): str,
                vol.Required("user_password"): str,
                vol.Required("panel_id"): str,
                vol.Optional("partition", default="ALL"): str,
            }),
            errors=errors,
        )
