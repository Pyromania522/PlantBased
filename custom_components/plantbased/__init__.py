"""PlantBased: local, calendar-based plant care."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the hub; platforms and runtime state arrive in milestone M2."""
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the hub, which has no listeners or platforms in milestone M1."""
    return True
