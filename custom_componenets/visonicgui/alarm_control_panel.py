# custom_components/visonicgui/alarm_control_panel.py

import logging
from time import sleep
from datetime import timedelta

from homeassistant.components import alarm_control_panel
from homeassistant.const import STATE_UNKNOWN
from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=7)  # reduced from 10s to 7s

class VisonicAlarmControlPanel(alarm_control_panel.AlarmControlPanelEntity):
    """Representation of a Visonic Alarm control panel."""

    def __init__(self, alarm):
        """Initialize the Visonic Alarm control panel."""
        self._alarm = alarm
        self._state = STATE_UNKNOWN

    @property
    def name(self):
        """Return the name of the alarm control panel."""
        return "Visonic Alarm"

    @property
    def state(self):
        """Return the state of the alarm."""
        return self._state

    def update(self):
        """Update alarm state."""
        # Update alarm status from the Visonic system
        self._alarm.update_status()
        raw_state = self._alarm.state

        if raw_state is None:
            self._state = STATE_UNKNOWN
        else:
            self._state = raw_state

    def alarm_disarm(self, code=None):
        """Disarm the alarm."""
        self._alarm.disarm()
        sleep(1)
        self.update()

    def alarm_arm_home(self, code=None):
        """Arm the alarm in home mode."""
        self._alarm.arm_home()
        sleep(1)
        self.update()

    def alarm_arm_away(self, code=None):
        """Arm the alarm in away mode."""
        self._alarm.arm_away()
        sleep(1)
        self.update()
