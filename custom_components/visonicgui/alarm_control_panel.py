import logging
from homeassistant.components.alarm_control_panel import AlarmControlPanel
import asyncio

_LOGGER = logging.getLogger(__name__)

class VisonicAlarmControlPanel(AlarmControlPanel):
    """Representation of a Visonic alarm control panel."""

    def __init__(self, name):
        """Initialize the alarm control panel."""
        self._name = name
        self._state = None

    @property
    def name(self):
        """Return the name of the alarm control panel."""
        return self._name

    @property
    def state(self):
        """Return the current state of the alarm control panel."""
        return self._state

    async def async_alarm_trigger(self, code=None):
        """Trigger the alarm."""
        await asyncio.sleep(0)  # Avoid blocking the event loop
        _LOGGER.debug("Triggering alarm.")
        self._state = "triggered"
        return True

    async def async_alarm_arm_home(self, code=None):
        """Arm the alarm in home mode."""
        await asyncio.sleep(0)  # Avoid blocking the event loop
        _LOGGER.debug("Arming alarm in home mode.")
        self._state = "armed_home"
        return True

    async def async_alarm_disarm(self, code=None):
        """Disarm the alarm."""
        await asyncio.sleep(0)  # Avoid blocking the event loop
        _LOGGER.debug("Disarming alarm.")
        self._state = "disarmed"
        return True
