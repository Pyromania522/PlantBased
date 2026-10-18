"""One atomic, versioned HA Store per hub."""

import json
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.storage import Store

from .const import DOMAIN, STORAGE_VERSION
from .models import PlantState


def storage_key(entry_id: str) -> str:
    """Scope persistence to the exact hub entry."""
    return f"{DOMAIN}.{entry_id}"


def _reject_constant(value: str) -> None:
    raise ValueError("Invalid JSON constant")


def _check_existing_json(path: str) -> None:
    """A corrupt existing file must never look like a newly configured hub."""
    try:
        with open(path, encoding="utf-8") as handle:
            envelope = json.load(handle, parse_constant=_reject_constant)
    except FileNotFoundError:
        return
    if not isinstance(envelope, dict) or not {"version", "data"} <= envelope.keys():
        raise ValueError("Invalid storage envelope")


class PlantStore(Store[dict[str, Any]]):
    """Persist only runtime state, never a second copy of subentry configuration."""

    def __init__(self, hass: HomeAssistant, entry_id: str) -> None:
        super().__init__(
            hass,
            STORAGE_VERSION,
            storage_key(entry_id),
            atomic_writes=True,
            private=True,
        )

    async def async_load(self) -> dict[str, Any] | None:
        """Fail before HA can treat corrupt JSON as an empty, newly seeded store."""
        try:
            await self.hass.async_add_executor_job(_check_existing_json, self.path)
        except (OSError, ValueError) as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN, translation_key="storage_error"
            ) from err
        return await super().async_load()

    async def async_save(self, data: dict[str, Any]) -> None:
        """Confirm the write using public Store APIs before acknowledging care.

        HA Store logs and swallows some write errors. A fresh Store read is needed
        to distinguish a successful durable write from a logged filesystem error.
        """
        await super().async_save(data)
        saved = await Store[dict[str, Any]](
            self.hass, STORAGE_VERSION, self.key
        ).async_load()
        if saved != data:
            raise HomeAssistantError(
                translation_domain=DOMAIN, translation_key="storage_write_error"
            )

    async def _async_migrate_func(
        self, old_major_version: int, old_minor_version: int, old_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Migrate the pre-release v0 shape without inventing or resetting dates."""
        if old_major_version != 0:
            raise NotImplementedError
        return {
            "vacation": old_data.get("vacation", False),
            "plants": {
                plant_id: PlantState.from_data(data).to_data()
                for plant_id, data in old_data.get("plants", {}).items()
            },
        }
