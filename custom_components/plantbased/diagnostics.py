"""Allowlisted care diagnostics without user free text other than plant names."""

from dataclasses import asdict
from typing import Any

from homeassistant.core import HomeAssistant

from .manager import PlantBasedConfigEntry


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: PlantBasedConfigEntry
) -> dict[str, Any]:
    """Never serialize the config entry, subentry data or arbitrary attributes."""
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
    return {
        "storage_version": manager.store.version,
        "today": manager.today.isoformat(),
        "vacation": manager.vacation,
        "plant_count": len(plants),
        "group_count": sum(
            sub.subentry_type == "group" for sub in entry.subentries.values()
        ),
        "plants": plants,
    }
