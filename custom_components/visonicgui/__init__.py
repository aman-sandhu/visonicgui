import logging
import threading
from datetime import timedelta
from datetime import datetime

from homeassistant.core import HomeAssistant
from homeassistant.helpers import discovery
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle
import homeassistant.helpers.config_validation as cv
from homeassistant.config_entries import ConfigEntry

import voluptuous as vol

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

HUB = None

# Configuration schema for the config flow
CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required('host'): cv.string,
        vol.Required('app_id'): cv.string,
        vol.Required('user_code'): cv.string,
        vol.Required('user_email'): cv.string,
        vol.Required('user_password'): cv.string,
        vol.Required('panel_id'): cv.string,
        vol.Optional('partition', default='ALL'): cv.string,
        vol.Optional('name', default='Visonic Alarm'): cv.string,
        vol.Optional('no_pin_required', default=False): cv.boolean,
        vol.Optional('event_hour_offset', default=0): vol.All(vol.Coerce(int), vol.Range(min=-24, max=24)),
    }),
}, extra=vol.ALLOW_EXTRA)

# The Visonic Alarm Hub class
class VisonicAlarmHub(Entity):
    """ A Visonic Alarm hub wrapper class. """

    def __init__(self, domain_config, visonicalarm):
        """ Initialize the Visonic Alarm hub. """
        self.config = domain_config
        self._visonicalarm = visonicalarm
        self._last_update = None
        self._lock = threading.Lock()

        self.alarm = visonicalarm.System(domain_config['host'],
                                         domain_config['app_id'],
                                         domain_config['user_code'],
                                         domain_config['user_email'],
                                         domain_config['user_password'],
                                         domain_config['panel_id'],
                                         domain_config['partition'])

    def connect(self):
        """ Setup a connection to the Visonic API server. """
        try:
            self.alarm.connect()
            return True
        except Exception as ex:
            _LOGGER.error('Connection failed: %s', ex)
            return False

    @property
    def last_update(self):
        """ Return the last update timestamp. """
        return self._last_update

    @Throttle(timedelta(seconds=10))
    def update(self):
        """ Update all alarm statuses. """
        try:
            if self.alarm.is_token_valid == False:
                self.alarm.connect()
            self.alarm.update_status()
            self.alarm.update_devices()
            self._last_update = datetime.now()
        except Exception as ex:
            _LOGGER.error('Update failed: %s', ex)
            raise

    @property
    def name(self):
        """ Return the name of the hub. """
        return "Visonic Alarm Hub"


# This method handles the setup of the integration when Home Assistant loads it
async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Visonic Alarm integration."""
    _LOGGER.debug("Setting up Visonic Alarm integration.")
    # Initialize the HUB as a global variable
    global HUB
    if not HUB:
        from visonic import alarm as visonicalarm
        # Load the configuration from the config flow
        hub_config = config[DOMAIN]
        HUB = VisonicAlarmHub(hub_config, visonicalarm)
        if not HUB.connect():
            return False
        HUB.update()

    # Load the supported platforms
    for component in ('sensor', 'alarm_control_panel'):
        discovery.load_platform(hass, component, DOMAIN, {}, config)

    return True
