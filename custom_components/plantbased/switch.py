"""Persisted plant pause and hub-wide vacation mode."""

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .entity import PlantBasedEntity
from .manager import PlantBasedConfigEntry, PlantManager

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PlantBasedConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([CarePause(entry.runtime_data, None)])
    for key in entry.runtime_data.configs:
        async_add_entities([CarePause(entry.runtime_data, key)], config_subentry_id=key)


class CarePause(PlantBasedEntity, SwitchEntity):
    """Dates keep running; unpausing exposes the original due dates again."""

    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, manager: PlantManager, target: str | None) -> None:
        super().__init__(
            manager, target, "vacation_mode" if target is None else "pause_plant"
        )

    @property
    def is_on(self) -> bool:
        return (
            self.manager.vacation
            if self.is_hub
            else self.manager.plants[self.target_id].paused
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.manager.async_pause(None if self.is_hub else self.target_id, True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.manager.async_pause(None if self.is_hub else self.target_id, False)
