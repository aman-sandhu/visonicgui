import logging
from datetime import timedelta
from homeassistant.helpers.entity import Entity
from homeassistant.const import STATE_CLOSED, STATE_OPEN, STATE_UNKNOWN
import asyncio

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=10)

class VisonicAlarmSensor(Entity):
    """Representation of a Visonic Alarm sensor."""

    def __init__(self, alarm, sensor_id):
        """Initialize the sensor."""
        self._alarm = alarm
        self._sensor_id = sensor_id
        self._state = STATE_UNKNOWN

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"Visonic Sensor {self._sensor_id}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    async def async_update(self):
        """Update sensor state asynchronously."""
        sensor_data = await self._get_sensor_data(self._sensor_id)

        if sensor_data is None:
            self._state = STATE_UNKNOWN
        elif sensor_data == "closed":
            self._state = STATE_CLOSED
        elif sensor_data == "open":
            self._state = STATE_OPEN

    async def _get_sensor_data(self, sensor_id):
        """Fetch sensor data asynchronously."""
        # If this function is doing blocking I/O, make it async.
        return await self._alarm.get_sensor_data(sensor_id)
