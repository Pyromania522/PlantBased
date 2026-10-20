"""Integration actions with registry-based target resolution and validation."""

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.service import async_extract_entity_ids

from .const import DOMAIN
from .manager import PlantManager
from .schema import schema as vol


def _invalid_target() -> ServiceValidationError:
    return ServiceValidationError(
        translation_domain=DOMAIN, translation_key="invalid_target"
    )


async def _async_targets(
    hass: HomeAssistant, call: ServiceCall
) -> tuple[PlantManager, list[str]]:
    entry = next(
        (
            entry
            for entry in hass.config_entries.async_entries(DOMAIN)
            if entry.state is ConfigEntryState.LOADED
        ),
        None,
    )
    if entry is None:
        raise ServiceValidationError(
            translation_domain=DOMAIN, translation_key="not_available"
        )
    manager: PlantManager = entry.runtime_data
    entities, devices = er.async_get(hass), dr.async_get(hass)
    owned_devices = {
        device.id
        for device in dr.async_entries_for_config_entry(devices, entry.entry_id)
    }
    selected: set[str] = set()
    direct_entities = set(cv.ensure_list(call.data.get("entity_id", [])))
    if direct_entities == {"all"}:
        selected.update(manager.configs)
    elif direct_entities:
        for entity_id in direct_entities:
            entity = entities.async_get(entity_id)
            if (
                entity is None
                or entity.config_entry_id != entry.entry_id
                or entity.config_subentry_id is None
                or entity.config_subentry_id not in entry.subentries
            ):
                raise _invalid_target()
            selected.add(entity.config_subentry_id)
    for device_id in cv.ensure_list(call.data.get("device_id", [])):
        device = devices.async_get(device_id)
        owned = (
            {
                key
                for domain, key in device.identifiers
                if domain == DOMAIN and key in entry.subentries
            }
            if device is not None and device.id in owned_devices
            else set()
        )
        if not owned:
            raise _invalid_target()
        selected.update(owned)
    for entity_id in await async_extract_entity_ids(call):
        entity = entities.async_get(entity_id)
        if (
            entity is not None
            and entity.config_entry_id == entry.entry_id
            and entity.config_subentry_id is not None
            and entity.config_subentry_id in entry.subentries
        ):
            selected.add(entity.config_subentry_id)
    if not selected:
        raise _invalid_target()
    plant_ids: set[str] = set()
    for key in selected:
        sub = entry.subentries[key]
        if sub.subentry_type == "plant":
            plant_ids.add(key)
        elif sub.subentry_type == "group":
            plant_ids.update(manager.members(key))
    return manager, [key for key in manager.configs if key in plant_ids]


@callback
def async_register_actions(hass: HomeAssistant) -> None:
    """Register in async_setup, including while no hub is loaded."""

    async def handle(call: ServiceCall) -> None:
        manager, ids = await _async_targets(hass, call)
        if call.service in ("mark_watered", "mark_fertilized"):
            await manager.async_mark_done(
                ids,
                "water" if call.service == "mark_watered" else "fertilize",
                call.data.get("date"),
            )
        elif call.service == "snooze":
            await manager.async_snooze_many(
                ids, call.data["care_type"], call.data["days"]
            )
        else:
            manager.async_set_intervals(ids, call.data["care_type"], call.data["days"])

    def days(value: object) -> int:
        if type(value) is not int or not 1 <= value <= 365:
            raise vol.Invalid("Expected a whole number of days from 1 to 365")
        return value

    for action in ("mark_watered", "mark_fertilized", "snooze", "set_interval"):
        fields = dict(cv.TARGET_SERVICE_FIELDS)
        if action in ("mark_watered", "mark_fertilized"):
            fields[vol.Optional("date")] = cv.date
        else:
            fields[vol.Required("care_type")] = vol.In(("water", "fertilize"))
            fields[
                vol.Optional("days", default=1)
                if action == "snooze"
                else vol.Required("days")
            ] = days
        hass.services.async_register(DOMAIN, action, handle, schema=vol.Schema(fields))
