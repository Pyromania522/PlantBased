"""Real Store migration, persistence, removal and failure preservation."""

from datetime import date
from unittest.mock import AsyncMock, patch

from homeassistant.config_entries import ConfigEntryState
import pytest

from custom_components.plantbased import async_unload_entry
from custom_components.plantbased.models import PlantState
from custom_components.plantbased.storage import PlantStore, storage_key

from .common import make_hub, state


async def test_legacy_store_migrates_without_changing_dates(
    hass, hass_storage, freezer
):
    freezer.move_to("2026-06-15T10:00:00Z")
    entry = make_hub(hass)
    key = storage_key(entry.entry_id)
    hass_storage[key] = {
        "version": 0,
        "minor_version": 1,
        "data": {
            "vacation": True,
            "plants": {
                "monstera": {
                    "last_watered": "2026-06-10",
                    "last_fertilized": "2026-06-02",
                }
            },
        },
    }
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert hass_storage[key]["version"] == 1
    assert entry.runtime_data.vacation
    assert state(hass, "monstera", "last_watered", "date").state == "2026-06-10"
    assert state(hass, "monstera", "care_status").attributes["history"]["water"] == [
        "2026-06-10"
    ]
    assert "ficus" in hass_storage[key]["data"]["plants"]


@pytest.mark.parametrize(
    ("version", "data"),
    [
        (999, {"vacation": True, "plants": {}}),
        (1, {"vacation": "invalid", "plants": {}}),
        (1, {"vacation": False, "plants": []}),
        (1, {"vacation": False, "plants": {"monstera": {"last_watered": "broken"}}}),
    ],
)
async def test_unreadable_store_is_not_overwritten(
    hass, hass_storage, freezer, version, data
):
    freezer.move_to("2026-06-15T10:00:00Z")
    entry = make_hub(hass)
    key = storage_key(entry.entry_id)
    hass_storage[key] = {"version": version, "minor_version": 1, "data": data}
    with patch.object(PlantStore, "async_save", new_callable=AsyncMock) as save:
        assert not await hass.config_entries.async_setup(entry.entry_id)
        save.assert_not_called()
    assert entry.state is ConfigEntryState.SETUP_ERROR
    assert hass_storage[key]["data"] == data


@pytest.mark.parametrize(
    ("field", "value"),
    [("watering_snooze", -1), ("fertilizing_snooze", True), ("paused", "yes")],
)
def test_corrupt_runtime_values_are_rejected(field, value):
    saved = PlantState(date(2026, 1, 1), date(2026, 1, 1)).to_data()
    saved[field] = value
    with pytest.raises(ValueError):
        PlantState.from_data(saved)


async def test_migration_rejects_unknown_major_version(hass):
    with pytest.raises(NotImplementedError):
        await PlantStore(hass, "unknown")._async_migrate_func(-1, 1, {})


async def test_hub_removal_deletes_runtime_data(hass, plant_hub, hass_storage):
    key = storage_key(plant_hub.entry_id)
    assert key in hass_storage
    assert await hass.config_entries.async_remove(plant_hub.entry_id)
    assert key not in hass_storage


async def test_failed_platform_unload_keeps_manager_active(hass, plant_hub):
    manager = plant_hub.runtime_data
    with patch.object(
        hass.config_entries, "async_unload_platforms", AsyncMock(return_value=False)
    ):
        assert not await async_unload_entry(hass, plant_hub)
    assert not manager._stopped
    await manager.async_mark_done(["monstera"], "water")
    assert state(hass, "monstera", "needs_water", "binary_sensor").state == "off"


@pytest.mark.parametrize(
    "contents", ["{broken", '{"version": 1, "data": NaN}', "[]", "{}"]
)
async def test_corrupt_json_file_is_preserved_without_reset(
    hass, freezer, tmp_path, contents
):
    freezer.move_to("2026-06-15T10:00:00Z")
    entry = make_hub(hass)
    path = tmp_path / "care.json"
    await hass.async_add_executor_job(path.write_text, contents)
    with patch.object(PlantStore, "path", str(path)):
        assert not await hass.config_entries.async_setup(entry.entry_id)
        assert entry.state is ConfigEntryState.SETUP_ERROR
        assert not await hass.config_entries.async_reload(entry.entry_id)
    assert await hass.async_add_executor_job(path.read_text) == contents
