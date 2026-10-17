"""Check unmocked HA persistence using only an isolated temporary directory."""

import asyncio
from functools import partial
import json
from pathlib import Path
import shutil
import tempfile

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

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
    finally:
        await hass.async_stop()
        await asyncio.to_thread(shutil.rmtree, directory)
    print("Real filesystem storage checks passed")


if __name__ == "__main__":
    asyncio.run(main())
