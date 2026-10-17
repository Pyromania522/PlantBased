"""Care-required flags with integration-specific translated on/off states."""

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .entity import PlantBasedEntity
from .manager import PlantBasedConfigEntry

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PlantBasedConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([CareRequired(entry.runtime_data, None, "any_plant_needs_care")])
    for key in entry.runtime_data.configs:
        async_add_entities(
            [
                CareRequired(entry.runtime_data, key, "needs_water"),
                CareRequired(entry.runtime_data, key, "needs_fertilizer"),
            ],
            config_subentry_id=key,
        )


class CareRequired(PlantBasedEntity, BinarySensorEntity):
    """Do not use the problem device class for an ordinary care task."""

    @property
    def is_on(self) -> bool:
        if self.is_hub:
            return any(
                value.needs_water or value.needs_fertilizer
                for value in self.manager.schedules.values()
            )
        schedule = self.manager.schedules[self.target_id]
        return (
            schedule.needs_water
            if self.key == "needs_water"
            else schedule.needs_fertilizer
        )
