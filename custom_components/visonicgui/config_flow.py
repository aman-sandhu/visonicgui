import logging
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_APP_ID, CONF_USER_CODE, CONF_USER_EMAIL, CONF_USER_PASSWORD, CONF_PANEL_ID
from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

class VisonicAlarmConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the configuration flow for the Visonic Alarm integration."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self._host = None
        self._app_id = None
        self._user_code = None
        self._user_email = None
        self._user_password = None
        self._panel_id = None
        self._partition = "ALL"
        self._name = "Visonic Alarm"

    async def async_step_user(self, user_input=None):
        """Handle the initial user step."""
        if user_input:
            self._host = user_input[CONF_HOST]
            self._app_id = user_input[CONF_APP_ID]
            self._user_code = user_input[CONF_USER_CODE]
            self._user_email = user_input[CONF_USER_EMAIL]
            self._user_password = user_input[CONF_USER_PASSWORD]
            self._panel_id = user_input[CONF_PANEL_ID]
            self._partition = user_input.get("partition", "ALL")
            self._name = user_input.get("name", "Visonic Alarm")

            # Create the configuration entry
            return self.async_create_entry(
                title=self._name,
                data={
                    CONF_HOST: self._host,
                    CONF_APP_ID: self._app_id,
                    CONF_USER_CODE: self._user_code,
                    CONF_USER_EMAIL: self._user_email,
                    CONF_USER_PASSWORD: self._user_password,
                    CONF_PANEL_ID: self._panel_id,
                    "partition": self._partition,
                    "name": self._name,
                },
            )

        # If no user input yet, show the form
        return self.async_show_form(
            step_id="user",
            data_schema=self._get_user_input_schema(),
        )

    def _get_user_input_schema(self):
        """Return the schema for user input."""
        return vol.Schema({
            vol.Required(CONF_HOST): str,
            vol.Required(CONF_APP_ID): str,
            vol.Required(CONF_USER_CODE): str,
            vol.Required(CONF_USER_EMAIL): str,
            vol.Required(CONF_USER_PASSWORD): str,
            vol.Required(CONF_PANEL_ID): str,
            vol.Optional("partition", default="ALL"): str,
            vol.Optional("name", default="Visonic Alarm"): str,
        })
