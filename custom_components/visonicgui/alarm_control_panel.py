import logging
from time import sleep
from datetime import timedelta

from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntity,
    AlarmControlPanelEntityFeature
)
from homeassistant.components.persistent_notification import create as create_notification
from homeassistant.const import ATTR_CODE_FORMAT, EVENT_STATE_CHANGED, STATE_UNKNOWN

# Import necessary constants
try:
    from homeassistant.components.alarm_control_panel import AlarmControlPanelState

    STATE_ALARM_DISARMED = "disarmed"
    STATE_ALARM_ARMED_HOME = "armed_home"
    STATE_ALARM_ARMED_AWAY = "armed_away"
    STATE_ALARM_ARMED_NIGHT = "armed_night"
    STATE_ALARM_TRIGGERED = "triggered"
    STATE_ALARM_PENDING = "pending"
    STATE_ALARM_ARMING = "arming"
except Exception:
    from homeassistant.components.alarm_control_panel.const import (
        STATE_ALARM_DISARMED,
        STATE_ALARM_ARMED_HOME,
        STATE_ALARM_ARMED_AWAY,
        STATE_ALARM_ARMED_NIGHT,
        STATE_ALARM_TRIGGERED,
        STATE_ALARM_PENDING,
        STATE_ALARM_ARMING,
    )

from . import HUB
from .const import CONF_EVENT_HOUR_OFFSET, CONF_NO_PIN_REQUIRED, CONF_USER_CODE

_LOGGER = logging.getLogger(__name__)

SUPPORT_VISONIC = (
    AlarmControlPanelEntityFeature.ARM_HOME | AlarmControlPanelEntityFeature.ARM_AWAY
)

ATTR_SYSTEM_SERIAL_NUMBER = "serial_number"
ATTR_SYSTEM_MODEL = "model"
ATTR_SYSTEM_READY = "ready"
ATTR_SYSTEM_CONNECTED = "connected"
ATTR_SYSTEM_SESSION_TOKEN = "session_token"
ATTR_SYSTEM_LAST_UPDATE = "last_update"
ATTR_CHANGED_BY = "changed_by"
ATTR_CHANGED_TIMESTAMP = "changed_timestamp"
ATTR_ALARMS = "alarm"

SCAN_INTERVAL = timedelta(seconds=7)  # reduced from 10s to 7s

class VisonicAlarm(AlarmControlPanelEntity):
    """Representation of a Visonic Alarm control panel."""

    _attr_code_arm_required = False

    def __init__(self, config_entry):
        """Initialize the Visonic Alarm control panel."""
        self._state = STATE_UNKNOWN
        self._config_entry = config_entry
        self._code = config_entry.data.get(CONF_USER_CODE)
        self._no_pin_required = config_entry.data.get(CONF_NO_PIN_REQUIRED)
        self._changed_by = None
        self._changed_timestamp = None
        self._event_hour_offset = config_entry.data.get(CONF_EVENT_HOUR_OFFSET)
        self._id = HUB.alarm.serial_number

    @property
    def name(self):
        """Return the name of the device."""
        return "Visonic Alarm"

    @property
    def unique_id(self):
        """Return a unique ID for this alarm control panel."""
        return self._id

    @property
    def state_attributes(self):
        """Return the state attributes of the alarm control panel."""
        return {
            ATTR_SYSTEM_SERIAL_NUMBER: HUB.alarm.serial_number,
            ATTR_SYSTEM_MODEL: HUB.alarm.model,
            ATTR_SYSTEM_READY: HUB.alarm.ready,
            ATTR_SYSTEM_CONNECTED: HUB.alarm.connected,
            ATTR_SYSTEM_SESSION_TOKEN: HUB.alarm.session_token,
            ATTR_SYSTEM_LAST_UPDATE: HUB.last_update,
            ATTR_CODE_FORMAT: self.code_format,
            ATTR_CHANGED_BY: self.changed_by,
            ATTR_CHANGED_TIMESTAMP: self._changed_timestamp,
            ATTR_ALARMS: HUB.alarm.alarm,
        }

    @property
    def icon(self):
        """Return the icon to use for the alarm control panel."""
        if self._state == STATE_ALARM_ARMED_AWAY:
            return "mdi:shield-lock"
        elif self._state == STATE_ALARM_ARMED_HOME:
            return "mdi:shield-home"
        elif self._state == STATE_ALARM_DISARMED:
            return "mdi:shield-check"
        elif self._state == STATE_ALARM_ARMING:
            return "mdi:shield-outline"
        else:
            return "hass:bell-ring"

    @property
    def state(self):
        """Return the state of the alarm control panel."""
        return self._state

    @property
    def code_format(self):
        """Return code format."""
        return None if self._no_pin_required else "Number"

    @property
    def changed_by(self):
        """Return who changed the state of the alarm."""
        return self._changed_by

    @property
    def changed_timestamp(self):
        """Return when the state of the alarm was last changed."""
        return self._changed_timestamp

    @property
    def event_hour_offset(self):
        """Return the event hour offset."""
        return self._event_hour_offset

    def update_last_event(self, user, timestamp):
        """Update the last event with user and timestamp."""
        self._changed_by = user
        self._changed_timestamp = timestamp

    def update(self):
        """Update alarm status from the Hub."""
        HUB.update()
        raw = HUB.alarm.state
        _LOGGER.warning(f"Visonic raw state: {raw}")

        if raw is None:
            self._state = STATE_UNKNOWN
            return

        status = str(raw).strip().upper()
        _LOGGER.debug(f"Visonic normalized state: {status}")

        mapping = {
            "AWAY": STATE_ALARM_ARMED_AWAY,
            "ARMED_AWAY": STATE_ALARM_ARMED_AWAY,
            "ARM": STATE_ALARM_ARMED_AWAY,
            "HOME": STATE_ALARM_ARMED_HOME,
            "STAY": STATE_ALARM_ARMED_HOME,
            "ARMED_HOME": STATE_ALARM_ARMED_HOME,
            "DISARM": STATE_ALARM_DISARMED,
            "DISARMED": STATE_ALARM_DISARMED,
            "READY": STATE_ALARM_DISARMED,
            "IDLE": STATE_ALARM_DISARMED,
            "ARMING": STATE_ALARM_ARMING,
            "EXITDELAY": STATE_ALARM_ARMING,
            "ENTRYDELAY": STATE_ALARM_PENDING,
            "ALARM": STATE_ALARM_TRIGGERED,
            "TRIGGERED": STATE_ALARM_TRIGGERED,
        }

        self._state = mapping.get(status, STATE_UNKNOWN)

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        return SUPPORT_VISONIC

    def alarm_disarm(self, code=None):
        """Disarm the alarm."""
        if not self._no_pin_required and code != self._code:
            create_notification(self._hass, "You entered the wrong disarm code.", title="Disarm Failed")
            return

        HUB.alarm.disarm()
        sleep(1)
        self.update()

    def alarm_arm_home(self, code=None):
        """Arm the alarm in home mode."""
        if not self._no_pin_required and code != self._code:
            create_notification(self._hass, "You entered the wrong arm code.", title="Arm Failed")
            return

        if HUB.alarm.ready:
            HUB.alarm.arm_home()
            sleep(1)
            self.update()
        else:
            create_notification(
                self._hass,
                "The alarm system is not in a ready state. Maybe there are doors or windows open?",
                title="Arm Failed",
            )

    def alarm_arm_away(self, code=None):
        """Arm the alarm in away mode."""
        if not self._no_pin_required and code != self._code:
            create_notification(self._hass, "You entered the wrong arm code.", title="Unable to Arm")
            return

        if HUB.alarm.ready:
            HUB.alarm.arm_away()
            sleep(1)
            self.update()
        else:
            create_notification(
                self._hass,
                "The alarm system is not in a ready state. Maybe there are doors or windows open?",
                title="Unable to Arm",
            )
