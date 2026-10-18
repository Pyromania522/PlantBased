"""Shared push-only entity identity, device binding and listener lifecycle."""

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity

from .const import DOMAIN, HIDDEN_PLANT_ENTITY_KEYS
from .manager import PlantManager


class PlantBasedEntity(Entity):
    """Use subentry IDs, never names, for entity and device identity."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, manager: PlantManager, target_id: str | None, key: str) -> None:
        self.manager = manager
        self.target_id = target_id or manager.entry.entry_id
        self.is_hub = target_id is None
        self.key = key
        self._attr_entity_registry_visible_default = not (
            self.target_id in manager.configs and key in HIDDEN_PLANT_ENTITY_KEYS
        )
        self._attr_unique_id = f"{self.target_id}_{key}"
        self._attr_translation_key = key
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, self.target_id)})

    async def async_added_to_hass(self) -> None:
        """Register only while the entity is loaded."""
        await super().async_added_to_hass()
        self.async_on_remove(self.manager.async_add_listener(self.async_write_ha_state))
