"""PlantBased: local, calendar-based plant care."""

from dataclasses import replace

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError, HomeAssistantError
from homeassistant.helpers import area_registry as ar
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.typing import ConfigType

from .areas import AreaCoordinator, async_sync_group_area, plant_area
from .const import DOMAIN
from .manager import PlantBasedConfigEntry, PlantManager
from .reminder_storage import ReminderStore
from .reminders import ReminderCoordinator, async_remove_reminders
from .services import async_register_actions
from .storage import PlantStore
from .web import async_register_frontend, async_register_overview, async_remove_overview

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


def _reload_snapshot(entry: PlantBasedConfigEntry) -> dict[str, object]:
    """Area metadata is applied directly; all other edits still reload."""
    return {
        "options": dict(entry.options),
        "subentries": {
            key: (
                subentry.subentry_type,
                subentry.title,
                subentry.unique_id,
                {
                    field: value
                    for field, value in subentry.data.items()
                    if field != "area"
                },
            )
            for key, subentry in entry.subentries.items()
        },
    }


def _refresh_areas(entry: PlantBasedConfigEntry) -> None:
    """Keep runtime metadata current without restarting care timers."""
    manager = entry.runtime_data
    manager.configs = {
        key: replace(config, area=entry.subentries[key].data.get("area"))
        for key, config in manager.configs.items()
    }


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
    orphaned_plants: set[str] = set()
    # This runs before subscribing: clearing orphaned groups cannot reload-loop.
    for subentry in entry.subentries.values():
        if (
            subentry.subentry_type == "plant"
            and subentry.data.get("group")
            and subentry.data["group"] not in groups
        ):
            orphaned_plants.add(subentry.subentry_id)
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
    for key, subentry in sorted(
        entry.subentries.items(), key=lambda item: item[1].subentry_type != "group"
    ):
        area_id = (
            plant_area(hass, entry, subentry.data)
            if subentry.subentry_type == "plant"
            else subentry.data.get("area")
        )
        area = areas.async_get_area(area_id) if area_id else None
        device = registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            config_subentry_id=key,
            identifiers={(DOMAIN, key)},
            name=subentry.title,
            model="Plant" if subentry.subentry_type == "plant" else "Group",
            suggested_area=area.name if area else None,
        )
        if subentry.subentry_type == "group":
            async_sync_group_area(hass, entry, key, device.area_id)
    AreaCoordinator(hass, entry).async_start(orphaned_plants)
    _refresh_areas(entry)
    reload_snapshot = _reload_snapshot(entry)

    async def async_updated(hass: HomeAssistant, entry: PlantBasedConfigEntry) -> None:
        # HA may eagerly start update listeners inside async_update_subentry.
        # Reloading halfway through an area transaction can lose own fallbacks.
        if _reload_snapshot(entry) == reload_snapshot:
            _refresh_areas(entry)
            return
        await async_reload_entry(hass, entry)

    entry.async_on_unload(manager.async_stop)
    entry.async_on_unload(entry.add_update_listener(async_updated))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    manager.async_start()
    manager.reminders.async_start()
    await async_register_overview(hass)
    entry.async_on_unload(lambda: async_remove_overview(hass))
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
