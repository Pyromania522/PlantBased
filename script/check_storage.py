"""Check unmocked HA persistence using only an isolated temporary directory."""

import asyncio
from functools import partial
import json
from pathlib import Path
import shutil
import tempfile

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from custom_components.plantbased.reminder_storage import ReminderStore, decode_receipts
from custom_components.plantbased.storage import PlantStore, storage_key


async def main() -> None:
    """Validate on-disk state independently of pytest's HA storage fixture."""
    directory = await asyncio.to_thread(tempfile.mkdtemp, prefix="plantbased-store-")
    hass = HomeAssistant(directory)
    try:
        store = PlantStore(hass, "disk-smoke")
        data = {
            "vacation": True,
            "plants": {
                "plant": {
                    "last_watered": "2026-06-15",
                    "last_fertilized": "2026-06-01",
                    "watering_snooze": 2,
                    "fertilizing_snooze": 0,
                    "paused": True,
                    "watering_history": ["2026-06-15"],
                    "fertilizing_history": ["2026-06-01"],
                    "watering_learning": {
                        "baseline": 4,
                        "revision": 1,
                        "interval": 3,
                        "anchor": "2026-06-15",
                        "gaps": [3, 3, 3],
                    },
                }
            },
        }
        await store.async_save(data)
        path = Path(directory) / ".storage" / storage_key("disk-smoke")
        read = partial(path.read_text, encoding="utf-8")
        assert json.loads(await hass.async_add_executor_job(read))["data"] == data
        assert await PlantStore(hass, "disk-smoke").async_load() == data
        assert (await hass.async_add_executor_job(path.stat)).st_mode & 0o077 == 0
        await hass.async_add_executor_job(
            partial(path.write_text, "{broken", encoding="utf-8")
        )
        for _ in range(2):
            try:
                await PlantStore(hass, "disk-smoke").async_load()
            except HomeAssistantError:
                pass
            else:
                raise AssertionError("Corrupt JSON was treated as a new store")
            assert await hass.async_add_executor_job(read) == "{broken"
        await store.async_remove()
        assert not await hass.async_add_executor_job(path.exists)
        reminder = ReminderStore(hass, "disk-smoke")
        reminder_data = {
            "recipients": {
                "service:mobile_app_test": {
                    "day": "2026-06-15",
                    "seen": ["plant:water:2026-06-15"],
                    "active": ["plant:water:2026-06-15"],
                    "token": "a" * 32,
                    "text": "PlantBased: plant care\nWatering due: Test plant",
                }
            }
        }
        await reminder.async_save(reminder_data)
        restored = await ReminderStore(hass, "disk-smoke").async_load()
        assert restored == reminder_data
        assert (
            decode_receipts(restored)["service:mobile_app_test"].day.isoformat()
            == "2026-06-15"
        )
        reminder_path = Path(reminder.path)
        assert (
            await hass.async_add_executor_job(reminder_path.stat)
        ).st_mode & 0o077 == 0
        await reminder.async_remove()
        assert not await hass.async_add_executor_job(reminder_path.exists)
    finally:
        await hass.async_stop()
        await asyncio.to_thread(shutil.rmtree, directory)
    print("Real filesystem storage checks passed")


if __name__ == "__main__":
    asyncio.run(main())
