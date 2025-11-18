"""Interfaces with the Visonic Alarm control panel."""
from __future__ import annotations

import logging
from time import sleep
from datetime import timedelta

from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntity,
    AlarmControlPanelEntityFeature,
)
import homeassistant.components.persistent_notification as pn
from homeassistant.const import (
    ATTR_CODE_FORMAT,
    EVENT_STATE_CHANGED,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from . import (
    DOMAIN,
    CONF_EVENT_HOUR_OFFSET,
    CONF_NO_PIN_REQUIRED,
    CONF_USER_CODE,
)

_LOGGER = logging.getLogger(__name__)

# Version-safe state mapping
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

ATTR_SYSTEM_SERIAL_NUMBER = "serial_number"
ATTR_SYSTEM_MODEL = "model"
ATTR_SYSTEM_READY = "ready"
ATTR_SYSTEM_CONNECTED = "connected"
ATTR_SYSTEM_SESSION_TOKEN = "session_token"
ATTR_SYSTEM_LAST_UPDATE = "last_update"
ATTR_CHANGED_BY = "changed_by"
ATTR_CHANGED_TIMESTAMP = "changed_timestamp"
ATTR_ALARMS = "alarm"

SCAN_INTERVAL = timedelta(seconds=7)


# -------------------------
# async_setup_entry (NEW)
# -------------------------
async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    """Set up the alarm control panel using a config entry."""

    hub = hass.data[DOMAIN][entry.entry_id]

    alarm_entity = VisonicAlarm(hass, hub, entry)

    async_add_entities([alarm_entity])

    # Register event listener
    def arm_event_listener(event):
        entity_id = event.data.get("entity_id")
        old_state = event.data.get("old_state")
        new_state = event.data.get("new_state")

        if new_state is None or new_state.state in (STATE_UNKNOWN, ""):
            return

        if entity_id == alarm_entity.entity_id and old_state.state != new_state.state:
            state = new_state.state
            if state in ("armed_home", "armed_away", "Disarmed"):
                last_event = hub.alarm.get_last_event(
                    timestamp_hour_offset=alarm_entity.event_hour_offset
                )
                alarm_entity.update_last_event(
                    last_event["user"], last_event["timestamp"]
