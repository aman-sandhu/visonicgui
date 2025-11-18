import logging
import voluptuous as vol
from homeassistant.helpers import discovery
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

REQUIREMENTS = ['visonicalarm2==3.3.1', 'python-dateutil==2.7.3']

# Configuration Constants
CONF_HOST = 'host'
CONF_NAME = 'name'
CONF_APP_ID = 'app_id'
CONF_USER_CODE = 'user_code'
CONF_USER_EMAIL = 'user_email'
CONF_USER_PASSWORD = 'user_password'
CONF_PANEL_ID = 'panel_id'
CONF_PARTITION = 'partition'
CONF_EVENT_HOUR_OFFSET = 'event_hour_offset'

DEFAULT_NAME = 'Visonic Alarm'
DEFAULT_PARTITION = 'ALL'

# Define DOMAIN
DOMAIN = 'visonicgui'

HUB = None

# Config schema
CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_APP_ID): cv.string,
        vol.Required(CONF_USER_CODE): cv.string,
        vol.Required(CONF_USER_EMAIL): cv.string,
        vol.Required(CONF_USER_PASSWORD): cv.string,
        vol.Required(CONF_PANEL_ID): cv.string,
        vol.Optional(CONF_PARTITION, default=DEFAULT_PARTITION): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_EVENT_HOUR_OFFSET, default=0): vol.All(vol.Coerce(int), vol.Range(min=-24, max=24)),
    }),
}, extra=vol.ALLOW_EXTRA)

def setup(hass, config):
    """ Setup the Visonic Alarm component."""
    from visonic import alarm as visonicalarm  # Import here to avoid circular imports
    global HUB
    HUB = VisonicAlarmHub(config[DOMAIN], visonicalarm)
    
    if not HUB.connect():
        return False

    HUB.update()

    # Load the supported platforms (alarm_control_panel, sensor, etc.)
    for component in ('sensor', 'alarm_control_panel'):
        discovery.load_platform(hass, component, DOMAIN, {}, config)

    return True

class VisonicAlarmHub(Entity):
    """ A Visonic Alarm hub wrapper class. """

    def __init__(self, domain_config, visonicalarm):
        """ Initialize the Visonic Alarm hub. """
        self.config = domain_config
        self._visonicalarm = visonicalarm
        self._last_update = None
        self._lock = threading.Lock()
        self.alarm = visonicalarm.System(domain_config[CONF_HOST],
                                         domain_config[CONF_APP_ID],
                                         domain_config[CONF_USER_CODE],
                                         domain_config[CONF_USER_EMAIL],
                                         domain_config[CONF_USER_PASSWORD],
                                         domain_config[CONF_PANEL_ID],
                                         domain_config[CONF_PARTITION])

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
        """ Return the name of the hub."""
        return "Visonic Alarm Hub"
