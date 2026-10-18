"""Config-entry-scoped device lookup shared by supported registry versions."""

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN


def device_for_subentry(
    hass: HomeAssistant, entry_id: str, subentry_id: str
) -> dr.DeviceEntry | None:
    """Avoid the deprecated cross-entry async_get_device lookup."""
    return next(
        (
            device
            for device in dr.async_entries_for_config_entry(
                dr.async_get(hass), entry_id
            )
            if (DOMAIN, subentry_id) in device.identifiers
        ),
        None,
    )
