"""Editable last-care calendar dates, backed by the integration's Store."""

from datetime import date

from homeassistant.components.date import DateEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .entity import PlantBasedEntity
from .manager import PlantBasedConfigEntry, PlantManager
from .models import CareType

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PlantBasedConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    for key in entry.runtime_data.configs:
        async_add_entities(
            [
                CareDate(entry.runtime_data, key, "water"),
                CareDate(entry.runtime_data, key, "fertilize"),
            ],
            config_subentry_id=key,
        )


class CareDate(PlantBasedEntity, DateEntity):
    """Changing a date records care and resets only that timer's snooze."""

    def __init__(self, manager: PlantManager, target: str, care: CareType) -> None:
        super().__init__(
            manager, target, "last_watered" if care == "water" else "last_fertilized"
        )
        self.care = care

    @property
    def native_value(self) -> date:
        state = self.manager.plants[self.target_id]
        return state.last_watered if self.care == "water" else state.last_fertilized

    async def async_set_value(self, value: date) -> None:
        await self.manager.async_mark_done([self.target_id], self.care, value)
