"""Allowlisted care diagnostics without user free text other than plant names."""

from dataclasses import asdict
from typing import Any

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant

from .const import STORAGE_VERSION
from .manager import PlantBasedConfigEntry


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: PlantBasedConfigEntry
) -> dict[str, Any]:
    """Never serialize the config entry, subentry data or arbitrary attributes."""
    payload: dict[str, Any] = {
        "storage_version": STORAGE_VERSION,
        "entry_state": entry.state.value,
        "runtime_available": entry.state is ConfigEntryState.LOADED,
        "plant_count": sum(
            sub.subentry_type == "plant" for sub in entry.subentries.values()
        ),
        "group_count": sum(
            sub.subentry_type == "group" for sub in entry.subentries.values()
        ),
        "plants": [],
    }
    if entry.state is not ConfigEntryState.LOADED:
        return payload
    manager = entry.runtime_data
    plants = []
    for key, config in manager.configs.items():
        schedule = asdict(manager.schedules[key])
        schedule["next_watering"] = schedule["next_watering"].isoformat()
        if schedule["next_fertilizing"] is not None:
            schedule["next_fertilizing"] = schedule["next_fertilizing"].isoformat()
        plants.append(
            {
                "name": config.name,
                "config": {
                    "watering_interval": config.watering_interval,
                    "fertilizing_interval": config.fertilizing_interval,
                    "fertilizing_enabled": config.fertilizing_enabled,
                    "all_year": config.all_year,
                    "season_start": config.season_start,
                    "season_end": config.season_end,
                    "has_group": config.group is not None,
                },
                "runtime": manager.plants[key].to_data(),
                "schedule": schedule,
            }
        )
    payload.update(
        today=manager.today.isoformat(), vacation=manager.vacation, plants=plants
    )
    return payload
