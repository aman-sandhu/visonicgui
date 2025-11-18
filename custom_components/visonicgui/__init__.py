"""Support for Visonic Alarm components (config entries)."""

from __future__ import annotations

import logging
import threading
from datetime import datetime, timedelta

import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.helpers import discovery
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

# Config entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

REQUIREMENTS = ["visonicalarm2==3.3.1", "python-dateutil==2.7.3"]

_LOGGER = logging.getLogger(__name__)

CONF_NO_PIN_REQUIRED = "no_pin_required"
CONF_USER_CODE = "user_code"
CONF_APP_ID = "app_id"
CONF_USER_EMAIL = "user_email"
CONF_USER_PASSWORD = "user_password"
CONF_PANEL_ID = "panel_id"
CONF_PARTITION = "partition"
CONF_EVENT_HOUR_OFFSET = "event_hour_offset"

STATE_ATTR_SYSTEM_NAME = "system_name"
STATE_ATTR_SYSTEM_SERIAL_NUMBER = "serial_number"
STATE_ATTR_SYSTEM_MODEL = "model"
STATE_ATTR_SYSTEM_READY = "ready"
STATE_ATTR_SYSTEM_ACTIVE = "active"
STATE_ATTR_SYSTEM_CONNECTED = "connected"

DEFAULT_NAME = "Visonic Alarm"
DEFAULT_PARTITION = "ALL"

DOMAIN = "visonicgui"

# Keep a global reference for legacy platform code (your sensor.py / alarm_control_panel.py
# import `HUB` from this package). For single-instance integrations this is fine.
HUB = None

# YAML schema (kept for YAML -> config entry import support)
CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
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
    },
    extra=vol.ALLOW_EXTRA,
)


class VisonicAlarmHub(Entity):
    """ A Visonic Alarm hub wrapper class. """

    def __init__(self, domain_config, visonicalarm):
        """Initialize the Visonic Alarm hub."""
        self.config = domain_config
        self._visonicalarm = visonicalarm
        self._last_update = None

        self._lock = threading.Lock()

        self.alarm = visonicalarm.System(
            domain_config[CONF_HOST],
            domain_config[CONF_APP_ID],
            domain_config[CONF_USER_CODE],
            domain_config[CONF_USER_EMAIL],
            domain_config[CONF_USER_PASSWORD],
            domain_config[CONF_PANEL_ID],
            domain_config[CONF_PARTITION],
        )

    def connect(self):
        """Setup a connection to the Visonic API server."""
        try:
            self.alarm.connect()
            return True
        except Exception as ex:  # noqa: BLE001
            _LOGGER.error("Connection failed: %s", ex)
            return False

    @property
    def last_update(self):
        """Return the last update timestamp."""
        return self._last_update

    @Throttle(timedelta(seconds=10))
    def update(self):
        """Update all alarm statuses."""
        try:
            if self.alarm.is_token_valid is False:
                self.alarm.connect()

            self.alarm.update_status()
            # self.alarm.update_alarms()
            # self.alarm.update_troubles()
            # self.alarm.update_alerts()
            self.alarm.update_devices()

            self._last_update = datetime.now()
        except Exception as ex:  # noqa: BLE001
            _LOGGER.error("Update failed: %s", ex)
            raise

    @property
    def name(self):
        """Return the name of the hub."""
        return "Visonic Alarm Hub"


async def async_setup(hass: HomeAssistant, config: dict):
    """
    Legacy YAML setup. If user has YAML config, import it into a config entry
    so they can transition to the UI.
    """
    if DOMAIN in config:
        # Start a flow to import YAML into a config entry
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN, context={"source": "import"}, data=config[DOMAIN]
            )
        )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Visonic Alarm from a config entry."""

    # Import the visonic library here
    try:
        from visonic import alarm as visonicalarm  # type: ignore
    except Exception as ex:  # pragma: no cover - import/runtime
        _LOGGER.exception("Failed to import visonic alarm library: %s", ex)
        return False

    global HUB

    # Build the hub using the entry data
    hub = VisonicAlarmHub(entry.data, visonicalarm)

    # Attempt to connect in executor (don't block the event loop)
    connected = await hass.async_add_executor_job(hub.connect)
    if not connected:
        _LOGGER.error("Could not connect to Visonic Alarm with provided settings")
        return False

    # save hub to hass.data and package-level HUB for platforms
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = hub
    HUB = hub

    # Forward setup to supported platforms
    platforms = ["sensor", "alarm_control_panel"]
    for platform in platforms:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor", "alarm_control_panel"])
    if unload_ok:
        # Remove hub from hass.data and clear global HUB if it matches
        hass.data[DOMAIN].pop(entry.entry_id, None)
        global HUB
        if HUB is not None and getattr(HUB, "config", None) == entry.data:
            HUB = None
    return unload_ok
