"""Calendar dates, day countdowns, translated status and aggregate counts."""

from datetime import date
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .entity import PlantBasedEntity
from .manager import PlantBasedConfigEntry, PlantManager

PARALLEL_UPDATES = 0
COUNTS = (
    "total_plants",
    "plants_needing_water",
    "plants_needing_fertilizer",
    "plants_overdue",
)
PLANT_SENSORS = (
    "next_watering",
    "next_fertilizing",
    "days_until_watering",
    "days_until_fertilizing",
    "care_status",
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PlantBasedConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities(
        [OverviewSensor(entry.runtime_data, None, key) for key in COUNTS]
    )
    for target, sub in entry.subentries.items():
        if sub.subentry_type == "plant":
            async_add_entities(
                [PlantSensor(entry.runtime_data, target, key) for key in PLANT_SENSORS],
                config_subentry_id=target,
            )
        elif sub.subentry_type == "group":
            async_add_entities(
                [OverviewSensor(entry.runtime_data, target, key) for key in COUNTS[:3]],
                config_subentry_id=target,
            )


class PlantSensor(PlantBasedEntity, SensorEntity):
    """All properties read the manager's already-calculated local-day snapshot."""

    def __init__(self, manager: PlantManager, target: str, key: str) -> None:
        super().__init__(manager, target, key)
        if key.startswith("next_"):
            self._attr_device_class = SensorDeviceClass.DATE
        elif key.startswith("days_"):
            self._attr_native_unit_of_measurement = UnitOfTime.DAYS
        else:
            self._attr_device_class = SensorDeviceClass.ENUM
            self._attr_options = [
                "ok",
                "water",
                "fertilize",
                "water_and_fertilize",
                "paused",
            ]

    @property
    def native_value(self) -> str | int | date | None:
        schedule = self.manager.schedules[self.target_id]
        return {
            "next_watering": schedule.next_watering,
            "next_fertilizing": schedule.next_fertilizing,
            "days_until_watering": schedule.watering_days,
            "days_until_fertilizing": schedule.fertilizing_days,
            "care_status": schedule.status,
        }[self.key]

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        if self.key != "care_status":
            return None
        config = self.manager.configs[self.target_id]
        state = self.manager.plants[self.target_id]
        schedule = self.manager.schedules[self.target_id]
        group = self.manager.entry.subentries.get(config.group or "")
        return {
            "subentry_id": self.target_id,
            "group": group.title if group else None,
            "group_id": config.group,
            "image_url": config.image_url or None,
            "image_preset": config.image_preset,
            "species": config.species,
            "notes": config.notes,
            "location_note": config.location_note,
            "overdue_days": {
                "water": max(0, -schedule.watering_days) if schedule.needs_water else 0,
                "fertilize": max(0, -(schedule.fertilizing_days or 0))
                if schedule.needs_fertilizer
                else 0,
            },
            "history": {
                "water": [value.isoformat() for value in state.watering_history],
                "fertilize": [value.isoformat() for value in state.fertilizing_history],
            },
        }


class OverviewSensor(PlantBasedEntity, SensorEntity):
    """Group counts use only members; hub counts include every plant once."""

    def _matching(self) -> list[str]:
        members = self.manager.members(None if self.is_hub else self.target_id)
        if self.key == "total_plants":
            return members
        if self.key == "plants_needing_water":
            return [key for key in members if self.manager.schedules[key].needs_water]
        if self.key == "plants_needing_fertilizer":
            return [
                key for key in members if self.manager.schedules[key].needs_fertilizer
            ]
        return [key for key in members if self.manager.schedules[key].overdue]

    @property
    def native_value(self) -> int:
        return len(self._matching())

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        ids = self._matching()
        return {
            "plants": [self.manager.configs[key].name for key in ids],
            "plant_ids": ids,
        }
