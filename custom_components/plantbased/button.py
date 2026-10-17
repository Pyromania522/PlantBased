"""Per-plant care and snooze buttons, plus member-only group operations."""

from homeassistant.components.button import ButtonEntity
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
    """Register each entity to the actual plant/group config subentry."""
    for key, sub in entry.subentries.items():
        buttons = []
        for care in ("water", "fertilize"):
            if sub.subentry_type == "plant":
                buttons.extend(
                    [
                        CareButton(entry.runtime_data, key, care, False, False),
                        CareButton(entry.runtime_data, key, care, True, False),
                    ]
                )
            elif sub.subentry_type == "group":
                buttons.append(CareButton(entry.runtime_data, key, care, False, True))
        async_add_entities(buttons, config_subentry_id=key)


class CareButton(PlantBasedEntity, ButtonEntity):
    """Button presses use the same persisted operations as editable entities."""

    def __init__(
        self,
        manager: PlantManager,
        target: str,
        care: CareType,
        snooze: bool,
        group: bool,
    ) -> None:
        action = "snooze" if snooze else "mark_all" if group else "mark"
        suffix = (
            "watering"
            if care == "water" and snooze
            else "fertilizing"
            if snooze
            else "watered"
            if care == "water"
            else "fertilized"
        )
        super().__init__(manager, target, f"{action}_{suffix}")
        self.care, self.snooze, self._is_group = care, snooze, group
        self._attr_icon = (
            "mdi:alarm-snooze"
            if snooze
            else "mdi:watering-can"
            if care == "water"
            else "mdi:flower"
        )

    async def async_press(self) -> None:
        """A group action intentionally applies to all and only its members."""
        if self._is_group:
            await self.manager.async_mark_group(self.target_id, self.care)
        elif self.snooze:
            await self.manager.async_snooze(self.target_id, self.care)
        else:
            await self.manager.async_mark_done([self.target_id], self.care)
