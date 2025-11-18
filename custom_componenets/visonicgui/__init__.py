# custom_components/visonicgui/__init__.py

from homeassistant import config_entries
from . import config_flow

DOMAIN = "visonicgui"

async def async_setup(hass, config):
    """Set up the Visonic Alarm component."""
    return True

async def async_setup_entry(hass, entry):
    """Set up Visonic Alarm from a config entry."""
    from visonic import alarm as visonicalarm
    
    # Create the alarm system instance using data from the config entry
    alarm = visonicalarm.System(
        entry.data["host"],
        entry.data["app_id"],
        entry.data["user_code"],
        entry.data["user_email"],
        entry.data["user_password"],
        entry.data["panel_id"],
        entry.data["partition"]
    )
    
    # Store the alarm instance in hass.data
    hass.data[DOMAIN] = alarm

    return True
