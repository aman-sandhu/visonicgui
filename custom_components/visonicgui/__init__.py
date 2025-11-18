import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import discovery

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the integration."""
    _LOGGER.debug("Setting up Visonic GUI")
    # Ensure that config flow is loaded
    hass.data.setdefault("visonicgui", {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the integration from a config entry."""
    _LOGGER.debug(f"Setting up config entry: {entry}")
    # Here you could initialize components like alarm_control_panel or sensors
    # You can add async setup logic for other components if needed.
    return True
