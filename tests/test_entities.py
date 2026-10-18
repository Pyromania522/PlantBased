"""Functional entity operations, device/subentry binding and lifecycle."""

import asyncio
from datetime import date
from unittest.mock import AsyncMock, patch

from homeassistant.const import EVENT_CORE_CONFIG_UPDATE, EntityCategory
from homeassistant.core import CoreState
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util
from homeassistant.util.file import WriteError
import pytest
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from .common import call, device, entity_id, state


async def test_all_entities_bind_to_native_subentries(hass, plant_hub):
    entry = plant_hub
    registry = er.async_get(hass)
    entries = er.async_entries_for_config_entry(registry, entry.entry_id)
    assert len(entries) == 50  # 16 per plant, 5 per group, 8 on the hub.
    assert (
        len([item for item in entries if item.config_subentry_id == "monstera"]) == 16
    )
    assert len([item for item in entries if item.config_subentry_id == "living"]) == 5
    assert (
        len(dr.async_entries_for_config_entry(dr.async_get(hass), entry.entry_id)) == 5
    )
    assert state(hass, "monstera", "next_watering").state == "2026-06-08"
    assert state(hass, "monstera", "next_fertilizing").state == "2026-05-29"
    assert state(hass, "monstera", "days_until_watering").state == "-7"
    assert state(hass, "monstera", "days_until_fertilizing").state == "-17"
    assert state(hass, "monstera", "care_status").state == "water_and_fertilize"
    attrs = state(hass, "monstera", "care_status").attributes
    assert attrs["species"] == "Monstera deliciosa"
    assert attrs["overdue_days"] == {"water": 7, "fertilize": 17}
    assert attrs["image_url"] == "/local/plants/monstera.png"
    assert state(hass, entry.entry_id, "total_plants").state == "2"
    assert state(hass, entry.entry_id, "plants_overdue").attributes["plants"] == [
        "Monstera"
    ]
    assert state(hass, "living", "plants_needing_water").state == "1"
    assert state(hass, "office", "plants_needing_fertilizer").state == "0"
    number = registry.async_get(
        entity_id(hass, "monstera", "watering_interval", "number")
    )
    assert number.entity_category is EntityCategory.CONFIG
    for item in entries:
        assert item.unique_id and item.translation_key


async def test_native_buttons_dates_and_independent_snoozes(hass, plant_hub):
    entry = plant_hub
    await call(hass, "monstera", "snooze_watering")
    assert state(hass, "monstera", "next_watering").state == "2026-06-16"
    assert state(hass, "monstera", "care_status").state == "fertilize"
    await call(hass, "monstera", "snooze_watering")
    assert state(hass, "monstera", "next_watering").state == "2026-06-17"
    await call(hass, "monstera", "snooze_fertilizing")
    assert state(hass, "monstera", "care_status").state == "ok"
    await call(hass, "monstera", "mark_watered")
    assert state(hass, "monstera", "last_watered", "date").state == "2026-06-15"
    assert entry.runtime_data.plants["monstera"].watering_snooze == 0
    assert entry.runtime_data.plants["monstera"].fertilizing_snooze > 0
    await call(hass, "monstera", "mark_fertilized")
    assert entry.runtime_data.plants["monstera"].fertilizing_snooze == 0
    await call(hass, "monstera", "last_watered", "date", "set_value", date="2026-06-02")
    await call(
        hass, "monstera", "last_fertilized", "date", "set_value", date="2026-06-01"
    )
    assert state(hass, "monstera", "care_status").state == "water"
    assert state(hass, entry.entry_id, "plants_needing_water").state == "1"
    assert state(hass, entry.entry_id, "plants_needing_fertilizer").state == "0"
    assert (
        state(hass, entry.entry_id, "any_plant_needs_care", "binary_sensor").state
        == "on"
    )


async def test_group_buttons_only_affect_members(hass, plant_hub):
    other = plant_hub.runtime_data.plants["ficus"].to_data()
    await call(hass, "living", "mark_all_watered")
    assert state(hass, "monstera", "care_status").state == "fertilize"
    await call(hass, "living", "mark_all_fertilized")
    assert state(hass, "monstera", "care_status").state == "ok"
    assert plant_hub.runtime_data.plants["ficus"].to_data() == other
    assert (
        state(hass, plant_hub.entry_id, "any_plant_needs_care", "binary_sensor").state
        == "off"
    )


async def test_pause_and_vacation_suppress_counts_but_keep_dates(hass, plant_hub):
    entry = plant_hub
    before = entry.runtime_data.plants["monstera"].to_data()
    await call(hass, "monstera", "pause_plant", "switch", "turn_on")
    assert state(hass, "monstera", "care_status").state == "paused"
    assert state(hass, entry.entry_id, "plants_overdue").state == "0"
    assert state(hass, "monstera", "next_watering").state == "2026-06-08"
    await call(hass, "monstera", "pause_plant", "switch", "turn_off")
    assert state(hass, "monstera", "care_status").state == "water_and_fertilize"
    await call(hass, entry.entry_id, "vacation_mode", "switch", "turn_on")
    assert state(hass, "ficus", "care_status").state == "paused"
    assert state(hass, entry.entry_id, "plants_needing_water").state == "0"
    assert state(hass, entry.entry_id, "plants_needing_fertilizer").state == "0"
    await call(hass, entry.entry_id, "vacation_mode", "switch", "turn_off")
    assert entry.runtime_data.plants["monstera"].to_data() == before


@pytest.mark.parametrize(
    ("care", "key"),
    [("water", "watering_interval"), ("fertilize", "fertilizing_interval")],
)
async def test_interval_number_edits_real_subentry_without_reset(
    hass, plant_hub, care, key
):
    entry = plant_hub
    before = entry.runtime_data.plants["monstera"].to_data()
    await call(hass, "monstera", key, "number", "set_value", value=40)
    assert entry.subentries["monstera"].data[key] == 40
    assert state(hass, "monstera", key, "number").state == "40"
    assert entry.runtime_data.plants["monstera"].to_data() == before


async def test_removing_group_unassigns_plants_without_deleting_them(hass, plant_hub):
    entry = plant_hub
    before = entry.runtime_data.plants["monstera"].to_data()
    hass.config_entries.async_remove_subentry(entry, "living")
    await hass.async_block_till_done()
    assert entry.subentries["monstera"].data["group"] is None
    assert state(hass, "monstera", "care_status").attributes["group"] is None
    assert entry.runtime_data.plants["monstera"].to_data() == before
    assert device(hass, entry, "living") is None
    assert not [
        item
        for item in er.async_entries_for_config_entry(
            er.async_get(hass), entry.entry_id
        )
        if item.config_subentry_id == "living"
    ]
    assert state(hass, entry.entry_id, "total_plants").state == "2"


async def test_removing_plant_prunes_device_entities_and_storage(
    hass, plant_hub, hass_storage
):
    entry = plant_hub
    hass.config_entries.async_remove_subentry(entry, "monstera")
    await hass.async_block_till_done()
    assert "monstera" not in entry.runtime_data.plants
    assert (
        "monstera" not in hass_storage[entry.runtime_data.store.key]["data"]["plants"]
    )
    assert device(hass, entry, "monstera") is None
    assert state(hass, entry.entry_id, "total_plants").state == "1"


@pytest.mark.parametrize(
    ("before", "after", "last"),
    [
        ("2026-03-29T21:59:59Z", "2026-03-29T22:00:01Z", "2026-03-23"),
        ("2026-10-25T22:59:59Z", "2026-10-25T23:00:01Z", "2026-10-19"),
    ],
)
async def test_local_midnight_after_dst_change(
    hass, plant_hub, freezer, before, after, last
):
    entry = plant_hub
    await hass.config.async_set_time_zone("Europe/Berlin")
    freezer.move_to(before)
    assert await hass.config_entries.async_reload(entry.entry_id)
    await entry.runtime_data.async_mark_done(
        ["ficus"], "water", date.fromisoformat(last)
    )
    assert state(hass, "ficus", "needs_water", "binary_sensor").state == "off"
    freezer.move_to(after)
    async_fire_time_changed(hass, dt_util.utcnow())
    await hass.async_block_till_done()
    assert state(hass, "ficus", "needs_water", "binary_sensor").state == "on"
    assert state(hass, "ficus", "days_until_watering").state == "0"


async def test_concurrent_writes_and_history_bound(hass, plant_hub):
    entry = plant_hub
    manager = entry.runtime_data
    await asyncio.gather(
        *(
            manager.async_mark_done(["monstera"], care)
            for _ in range(12)
            for care in ("water", "fertilize")
        )
    )
    assert len(manager.plants["monstera"].watering_history) == 10
    assert len(manager.plants["monstera"].fertilizing_history) == 10
    await manager.async_snooze("monstera", "water", 3)
    await manager.async_pause("monstera", True)
    await manager.async_pause(None, True)
    before = manager.plants["monstera"].to_data()
    assert await hass.config_entries.async_reload(entry.entry_id)
    assert entry.runtime_data.plants["monstera"].to_data() == before
    assert entry.runtime_data.vacation
    assert not manager._listeners and not manager._unsubscribers


async def test_failed_write_does_not_claim_action_done(hass, plant_hub):
    manager = plant_hub.runtime_data
    before = manager.plants["monstera"].to_data()
    with patch.object(
        manager.store,
        "async_save",
        AsyncMock(side_effect=HomeAssistantError("Write unavailable")),
    ):
        with pytest.raises(HomeAssistantError):
            await call(hass, "monstera", "mark_watered")
    assert manager.plants["monstera"].to_data() == before
    assert state(hass, "monstera", "needs_water", "binary_sensor").state == "on"


async def test_real_store_write_error_is_detected_before_acknowledging(hass, plant_hub):
    manager = plant_hub.runtime_data
    before = manager.plants["monstera"].to_data()
    # Exercise HA Store's real error-swallowing path on both API signatures.
    with patch.object(
        manager.store,
        "_async_write_data",
        AsyncMock(side_effect=WriteError("Disk unavailable")),
    ):
        with pytest.raises(HomeAssistantError):
            await call(hass, "monstera", "mark_watered")
    assert manager.plants["monstera"].to_data() == before
    assert await hass.config_entries.async_reload(plant_hub.entry_id)
    assert plant_hub.runtime_data.plants["monstera"].to_data() == before


async def test_invalid_edits_and_stale_actions_rejected(hass, plant_hub):
    manager = plant_hub.runtime_data
    for value in (0, 366, 1.5):
        with pytest.raises(ServiceValidationError):
            manager.async_set_interval("monstera", "water", value)
    for value in (0, 366, 1.5, True):
        with pytest.raises(ServiceValidationError):
            await manager.async_snooze("monstera", "water", value)
    with pytest.raises(ServiceValidationError):
        await manager.async_mark_done(["monstera"], "water", date(2027, 1, 1))
    with pytest.raises(ServiceValidationError):
        await manager.async_mark_group("deleted-group", "water")
    with pytest.raises(ServiceValidationError):
        await manager.async_mark_done(["deleted-plant"], "water")
    assert await hass.config_entries.async_unload(plant_hub.entry_id)
    with pytest.raises(ServiceValidationError):
        await manager.async_pause(None, True)


async def test_timezone_change_recalculates_the_local_day(hass, plant_hub, freezer):
    freezer.move_to("2026-06-15T22:30:00Z")
    await hass.config.async_set_time_zone("UTC")
    assert await hass.config_entries.async_reload(plant_hub.entry_id)
    await plant_hub.runtime_data.async_mark_done(["ficus"], "water", date(2026, 6, 9))
    assert state(hass, "ficus", "needs_water", "binary_sensor").state == "off"
    await hass.config.async_set_time_zone("Europe/Berlin")
    hass.bus.async_fire(EVENT_CORE_CONFIG_UPDATE, {"time_zone": "Europe/Berlin"})
    await hass.async_block_till_done()
    assert state(hass, "ficus", "needs_water", "binary_sensor").state == "on"
    # Other settings must not resubscribe midnight or alter care history.
    before = plant_hub.runtime_data.plants["ficus"].to_data()
    hass.bus.async_fire(EVENT_CORE_CONFIG_UPDATE, {"language": "de"})
    await hass.async_block_till_done()
    assert plant_hub.runtime_data.plants["ficus"].to_data() == before


async def test_new_care_action_during_ha_stop_is_rejected(hass, plant_hub):
    before = plant_hub.runtime_data.plants["monstera"].to_data()
    with patch.object(hass, "state", CoreState.stopping):
        with pytest.raises(ServiceValidationError):
            await plant_hub.runtime_data.async_mark_done(["monstera"], "water")
    assert plant_hub.runtime_data.plants["monstera"].to_data() == before
