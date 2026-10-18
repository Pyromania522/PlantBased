"""Bounded, integer day intervals stored in their real config subentry."""

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import EntityCategory, UnitOfTime
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
                CareInterval(entry.runtime_data, key, "water"),
                CareInterval(entry.runtime_data, key, "fertilize"),
            ],
            config_subentry_id=key,
        )


class CareInterval(PlantBasedEntity, NumberEntity):
    """Treat intervals as configuration, not as an independently restored state."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_native_min_value = 1
    _attr_native_max_value = 365
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfTime.DAYS
    _attr_mode = NumberMode.BOX

    def __init__(self, manager: PlantManager, target: str, care: CareType) -> None:
        super().__init__(
            manager,
            target,
            "watering_interval" if care == "water" else "fertilizing_interval",
        )
        self.care = care

    @property
    def native_value(self) -> float:
        config = self.manager.configs[self.target_id]
        return (
            self.manager.plants[self.target_id].watering_interval(config)
            if self.care == "water"
            else config.fertilizing_interval
        )

    async def async_set_native_value(self, value: float) -> None:
        self.manager.async_set_interval(self.target_id, self.care, value)
