"""PlantBased: local, calendar-based plant care."""

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError, HomeAssistantError
from homeassistant.helpers import area_registry as ar
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN
from .manager import PlantBasedConfigEntry, PlantManager
from .reminder_storage import ReminderStore
from .reminders import ReminderCoordinator, async_remove_reminders
from .services import async_register_actions
from .storage import PlantStore
from .web import async_register_frontend

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.CALENDAR,
    Platform.DATE,
    Platform.NUMBER,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.TODO,
]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Keep action descriptions available even when the hub is unloaded."""
    await async_register_frontend(hass)
    async_register_actions(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: PlantBasedConfigEntry) -> bool:
    """Restore the hub and attach plants/groups to their native subentries."""
    groups = {
        key for key, sub in entry.subentries.items() if sub.subentry_type == "group"
    }
    # This runs before subscribing: clearing orphaned groups cannot reload-loop.
    for subentry in entry.subentries.values():
        if (
            subentry.subentry_type == "plant"
            and subentry.data.get("group")
            and subentry.data["group"] not in groups
        ):
            hass.config_entries.async_update_subentry(
                entry, subentry, data={**subentry.data, "group": None}
            )
    manager = entry.runtime_data = PlantManager(hass, entry)
    try:
        await manager.async_load()
        manager.reminders = ReminderCoordinator(manager)
        await manager.reminders.async_load()
    except (
        ValueError,
        TypeError,
        KeyError,
        NotImplementedError,
        HomeAssistantError,
    ) as err:
        raise ConfigEntryError(
            translation_domain=DOMAIN, translation_key="storage_error"
        ) from err

    registry = dr.async_get(hass)
    registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.entry_id)},
        translation_key="hub",
        entry_type=dr.DeviceEntryType.SERVICE,
    )
    areas = ar.async_get(hass)
    for key, subentry in entry.subentries.items():
        area = areas.async_get_area(subentry.data.get("area", ""))
        registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            config_subentry_id=key,
            identifiers={(DOMAIN, key)},
            name=subentry.title,
            model="Plant" if subentry.subentry_type == "plant" else "Group",
            suggested_area=area.name if area else None,
        )
    entry.async_on_unload(manager.async_stop)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    manager.async_start()
    manager.reminders.async_start()
    return True


async def async_unload_entry(hass: HomeAssistant, entry: PlantBasedConfigEntry) -> bool:
    """Unload all entities and finish persistence before allowing a reload."""
    if not await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        return False
    if entry.runtime_data.reminders is not None:
        await entry.runtime_data.reminders.async_shutdown()
    await entry.runtime_data.async_shutdown()
    return True


async def async_reload_entry(hass: HomeAssistant, entry: PlantBasedConfigEntry) -> None:
    """Apply subentry creation, edits and removal through one lifecycle path."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_remove_entry(hass: HomeAssistant, entry: PlantBasedConfigEntry) -> None:
    """Removing the hub also removes its private runtime storage."""
    await async_remove_reminders(hass, entry.entry_id)
    await PlantStore(hass, entry.entry_id).async_remove()
    await ReminderStore(hass, entry.entry_id).async_remove()
