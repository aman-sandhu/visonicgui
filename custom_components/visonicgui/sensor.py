"""Interfaces with the Visonic Alarm sensors."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.const import (
    STATE_CLOSED,
    STATE_OFF,
    STATE_ON,
    STATE_OPEN,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.config_entries import ConfigEntry

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=10)

CONTACT_ATTR_ZONE = "zone"
CONTACT_ATTR_NAME = "name"
CONTACT_ATTR_DEVICE_TYPE = "device_type"
CONTACT_ATTR_SUBTYPE = "subtype"


# -------------------------
# async_setup_entry (NEW)
# -------------------------
async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    """Set up Visonic Alarm sensors via config entry."""

    hub = hass.data[DOMAIN][entry.entry_id]
    hub.update()

    devices = []

    for device in hub.alarm.devices:
        if not device or not device.subtype:
            continue

        if any(x in device.subtype for x in ("CONTACT", "MOTION", "CURTAIN")):
            devices.append(VisonicAlarmContact(hub, device.id))

    async_add_entities(devices)


class VisonicAlarmContact(Entity):
    """Implementation of a Visonic Alarm Contact sensor."""

    def __init__(self, hub, contact_id):
        self._hub = hub
        self._alarm = hub.alarm
        self._id = contact_id
        self._state = STATE_UNKNOWN
        self._name = None
        self._zone = None
        self._device_type = None
        self._subtype = None

    @property
    def name(self):
        return str(self._name)

    @property
    def unique_id(self):
        return self._id

    @property
    def state_attributes(self):
        return {
            CONTACT_ATTR_ZONE: self._zone,
            CONTACT_ATTR_NAME: self._name,
            CONTACT_ATTR_DEVICE_TYPE: self._device_type,
            CONTACT_ATTR_SUBTYPE: self._subtype,
        }

    @property
    def icon(self):
        if "24H" in self._zone:
            if self._state == STATE_CLOSED:
                return "mdi:hours-24"
            if self._state == STATE_OPEN:
                return "mdi:alarm-light"

        return {
            STATE_CLOSED: "mdi:door-closed",
            STATE_OPEN: "mdi:door-open",
            STATE_OFF: "mdi:motion-sensor-off",
            STATE_ON: "mdi:motion-sensor",
        }.get(self._state)

    @property
    def state(self):
        return self._state

    def update(self):
        """Get the latest data."""
        try:
            self._hub.update()

            device = self._alarm.get_device_by_id(self._id)

            if not device:
                _LOGGER.warning("Device not found: %s", self._id)
                return

            status = device.state

            if status == "opened":
                self._state = STATE_OPEN
            elif status == "closed":
                self._state = STATE_CLOSED
            elif "CURTAIN" in device.subtype or "MOTION" in device.subtype:
                alarm_state = self._alarm.state
                alarm_zone = device.zone

                if alarm_state in ("DISARM", "ARMING"):
                    self._state = STATE_ON if "24H" in alarm_zone else STATE_OFF
                elif alarm_state == "HOME":
                    self._state = STATE_OFF if "INTERIOR" in alarm_zone else STATE_ON
                elif alarm_state in ("AWAY", "DISARMING"):
                    self._state = STATE_ON
                else:
                    self._state = STATE_UNKNOWN
            else:
                self._state = STATE_UNKNOWN

            self._zone = device.zone
            self._name = device.name
            self._device_type = device.device_type
            self._subtype = device.subtype

        except OSError as error:
            _LOGGER.warning("Could not update device %s: %s", self._id, error)
