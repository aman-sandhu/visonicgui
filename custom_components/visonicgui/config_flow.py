import logging
from homeassistant import config_entries
import voluptuous as vol
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.helpers import config_validation as cv
from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

class VisonicAlarmConfigFlow(config_entries.ConfigFlow):
    """Handle a config flow for the Visonic Alarm integration."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self._host = None
        self._app_id = None
        self._user_code = None
        self._user_email = None
        self._user_password = None
        self._panel_id = None
        self._partition = None

    async def async_step_user(self, user_input=None):
        """Handle the initial step of the config flow."""
        if user_input is not None:
            # Validate input and create the config entry
            self._host = user_input[CONF_HOST]
            self._app_id = user_input["app_id"]
            self._user_code = user_input["user_code"]
            self._user_email = user_input["user_email"]
            self._user_password = user_input["user_password"]
            self._panel_id = user_input["panel_id"]
            self._partition = user_input.get("partition", "ALL")

            # You can add here a function that tests the connection
            # and only return if it's successful
            try:
                # Try to connect to the alarm API to test if the credentials are correct
                # Here, you would use the same connection logic you have in `setup()`
                # For example:
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
                alarm.connect()
                alarm.update_status()
            except Exception as ex:
                _LOGGER.error("Error connecting to Visonic Alarm: %s", ex)
                return self.async_abort(reason="cannot_connect")

            # Create the entry if the test was successful
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
                }
            )

        # If no input yet, display the form to the user
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST): cv.string,
                vol.Required("app_id"): cv.string,
                vol.Required("user_code"): cv.string,
                vol.Required("user_email"): cv.string,
                vol.Required("user_password"): cv.string,
                vol.Required("panel_id"): cv.string,
                vol.Optional("partition", default="ALL"): cv.string,
            })
        )
