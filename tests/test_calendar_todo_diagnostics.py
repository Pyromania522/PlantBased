"""Native calendar/task services, local date boundaries and safe diagnostics."""

import asyncio
from dataclasses import replace
from datetime import UTC, date, timedelta
import json
from unittest.mock import AsyncMock, patch

from homeassistant.components.todo import TodoItemStatus
from homeassistant.const import EVENT_CORE_CONFIG_UPDATE
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util
import pytest
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.plantbased.calendar import CareCalendar
from custom_components.plantbased.diagnostics import async_get_config_entry_diagnostics
from custom_components.plantbased.todo import CareTodo

from .common import call, device, entity_id, make_hub, state
from .test_actions_events import action


async def events(hass, entry, start="2026-01-01T00:00:00Z", end="2027-01-01T00:00:00Z"):
    target = entity_id(hass, entry.entry_id, "care_calendar", "calendar")
    result = await hass.services.async_call(
        "calendar",
        "get_events",
        {
            "entity_id": target,
            "start_date_time": start,
            "end_date_time": end,
        },
        blocking=True,
        return_response=True,
    )
    return result[target]["events"]


async def tasks(hass, entry):
    target = entity_id(hass, entry.entry_id, "plant_care", "todo")
    result = await hass.services.async_call(
        "todo", "get_items", {"entity_id": target}, blocking=True, return_response=True
    )
    return result[target]["items"]


async def complete(hass, entry, uid, **kwargs):
    await hass.services.async_call(
        "todo",
        "update_item",
        {
            "entity_id": entity_id(hass, entry.entry_id, "plant_care", "todo"),
            "item": uid,
            "status": "completed",
            **kwargs,
        },
        blocking=True,
    )
    await hass.async_block_till_done()


async def test_native_calendar_and_task_entities_and_completion(hass, plant_hub):
    entry = plant_hub
    calendar = state(hass, entry.entry_id, "care_calendar", "calendar")
    assert calendar.attributes["supported_features"] == 0
    assert calendar.attributes["all_day"] is True
    assert calendar.attributes["start_time"] == "2026-06-21 00:00:00"
    registry = er.async_get(hass)
    for key, platform in [("care_calendar", "calendar"), ("plant_care", "todo")]:
        entity = registry.async_get(entity_id(hass, entry.entry_id, key, platform))
        assert entity.config_subentry_id is None
        assert entity.device_id == device(hass, entry, entry.entry_id).id
    listed = await events(hass, entry)
    assert [(event["start"], event["summary"]) for event in listed] == [
        ("2026-05-29", "Fertilize: Monstera"),
        ("2026-06-08", "Water: Monstera"),
        ("2026-06-21", "Water: Ficus"),
        ("2026-07-12", "Fertilize: Ficus"),
    ]
    assert all(
        date.fromisoformat(event["end"]) - date.fromisoformat(event["start"])
        == timedelta(days=1)
        for event in listed
    )
    items = await tasks(hass, entry)
    assert len(items) == 2
    assert all(item["status"] == "needs_action" for item in items)
    done = []
    hass.bus.async_listen("plantbased_care_done", done.append)
    water = next(item for item in items if item["uid"].split(":")[1] == "water")
    await complete(hass, entry, water["uid"])
    assert state(hass, "monstera", "last_watered", "date").state == "2026-06-15"
    assert state(hass, entry.entry_id, "plant_care", "todo").state == "1"
    assert done[0].data["care_type"] == "water"
    assert (
        next(
            event
            for event in await events(hass, entry)
            if event["summary"] == "Water: Monstera"
        )["start"]
        == "2026-06-22"
    )
    await complete(hass, entry, (await tasks(hass, entry))[0]["uid"])
    assert not await tasks(hass, entry)
    assert state(hass, entry.entry_id, "plants_needing_water").state == "0"


async def test_tasks_follow_snooze_pause_vacation_and_reload(hass, plant_hub):
    entry = plant_hub
    await action(
        hass,
        "snooze",
        device_id=device(hass, entry, "living").id,
        care_type="water",
        days=2,
    )
    assert len(await tasks(hass, entry)) == 1
    await call(hass, "monstera", "pause_plant", "switch", "turn_on")
    assert not await tasks(hass, entry)
    assert len(await events(hass, entry)) == 2
    await call(hass, "monstera", "pause_plant", "switch", "turn_off")
    await call(hass, entry.entry_id, "vacation_mode", "switch", "turn_on")
    assert not await events(hass, entry)
    assert not await tasks(hass, entry)
    assert state(hass, entry.entry_id, "care_calendar", "calendar").state == "off"
    await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    assert not await tasks(hass, entry)
    await call(hass, entry.entry_id, "vacation_mode", "switch", "turn_off")
    assert len(await tasks(hass, entry)) == 1
    assert len(await events(hass, entry)) == 4
    hass.config_entries.async_remove_subentry(entry, "monstera")
    await hass.async_block_till_done()
    assert not await tasks(hass, entry)
    assert len(await events(hass, entry)) == 2


@pytest.mark.parametrize("extra", [{"rename": "Renamed"}, {"status": "needs_action"}])
async def test_task_edits_rejected_without_changing_care(hass, plant_hub, extra):
    task = (await tasks(hass, plant_hub))[0]
    with pytest.raises(ServiceValidationError):
        await complete(hass, plant_hub, task["uid"], **extra)
    assert len(await tasks(hass, plant_hub)) == 2


async def test_stale_task_and_concurrent_completion_cannot_mark_later_cycle(
    hass, plant_hub, freezer
):
    entry = plant_hub
    todo = CareTodo(entry.runtime_data, None, "plant_care")
    stale = replace(
        next(item for item in todo.todo_items if ":water:" in item.uid),
        status=TodoItemStatus.COMPLETED,
    )
    results = await asyncio.gather(
        todo.async_update_todo_item(stale),
        todo.async_update_todo_item(stale),
        return_exceptions=True,
    )
    assert sum(isinstance(result, ServiceValidationError) for result in results) == 1
    assert entry.runtime_data.plants["monstera"].watering_history == [
        date(2026, 6, 1),
        date(2026, 6, 15),
    ]
    freezer.move_to("2026-06-22T10:00:00Z")
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    with pytest.raises(ServiceValidationError) as error:
        await todo.async_update_todo_item(stale)
    assert error.value.translation_key == "stale_task"
    assert entry.runtime_data.plants["monstera"].last_watered == date(2026, 6, 15)


async def test_task_validated_again_under_storage_lock(hass, plant_hub):
    manager = plant_hub.runtime_data
    todo = CareTodo(manager, None, "plant_care")
    task = replace(
        next(item for item in todo.todo_items if ":water:" in item.uid),
        status=TodoItemStatus.COMPLETED,
    )
    async with manager._lock:
        pending = asyncio.create_task(todo.async_update_todo_item(task))
        await asyncio.sleep(0)
        manager.plants["monstera"].last_watered = date(2026, 6, 15)
    with pytest.raises(ServiceValidationError) as error:
        await pending
    assert error.value.translation_key == "stale_task"


async def test_failed_completion_keeps_task_and_no_done(hass, plant_hub):
    done = []
    hass.bus.async_listen("plantbased_care_done", done.append)
    task = (await tasks(hass, plant_hub))[0]
    with patch.object(
        plant_hub.runtime_data.store,
        "async_save",
        AsyncMock(side_effect=HomeAssistantError("failure")),
    ):
        with pytest.raises(HomeAssistantError):
            await complete(hass, plant_hub, task["uid"])
    assert task in await tasks(hass, plant_hub)
    assert not done


@pytest.mark.parametrize(
    ("day", "start", "end"),
    [
        ("2026-03-29", "2026-03-28T23:00:00Z", "2026-03-29T22:00:00Z"),
        ("2026-10-25", "2026-10-24T22:00:00Z", "2026-10-25T23:00:00Z"),
    ],
)
async def test_calendar_local_day_overlap_across_dst(
    hass, plant_hub, freezer, day, start, end
):
    await hass.config.async_set_time_zone("Europe/Berlin")
    freezer.move_to(day + "T10:00:00Z")
    manager = plant_hub.runtime_data
    manager.plants["monstera"].last_watered = date.fromisoformat(day) - __import__(
        "datetime"
    ).timedelta(days=7)
    calendar = CareCalendar(manager, None, "care_calendar")
    event = next(
        event
        for event in await calendar.async_get_events(
            hass, dt_util.parse_datetime(start), dt_util.parse_datetime(end)
        )
        if event.uid.startswith("monstera:water:")
    )
    assert event.start == date.fromisoformat(day)
    assert event.end_datetime_local.astimezone(UTC) == dt_util.parse_datetime(end)
    assert not await calendar.async_get_events(
        hass, dt_util.parse_datetime(end), dt_util.parse_datetime(start)
    )
    exact_end = event.end_datetime_local
    after = await calendar.async_get_events(
        hass, exact_end, exact_end + timedelta(hours=1)
    )
    assert event not in after
    exact_start = event.start_datetime_local
    before = await calendar.async_get_events(
        hass, exact_start - timedelta(hours=1), exact_start
    )
    assert event not in before
    midday = exact_start + timedelta(hours=12)
    assert event in await calendar.async_get_events(
        hass, midday, midday + timedelta(hours=1)
    )


async def test_fertilizer_season_marker_is_not_premature_calendar_event(
    hass, plant_hub, freezer
):
    manager = plant_hub.runtime_data
    freezer.move_to("2026-01-15T10:00:00Z")
    manager.configs["monstera"] = replace(
        manager.configs["monstera"], all_year=False, fertilizing_interval=365
    )
    manager.plants["monstera"].last_fertilized = date(2025, 12, 1)
    manager.configs["ficus"] = replace(
        manager.configs["ficus"], fertilizing_enabled=False
    )
    calendar = CareCalendar(manager, None, "care_calendar")
    result = await calendar.async_get_events(
        hass,
        dt_util.parse_datetime("2026-01-01T00:00:00Z"),
        dt_util.parse_datetime("2028-01-01T00:00:00Z"),
    )
    fertilizing = [event for event in result if ":fertilize:" in event.uid]
    assert len(fertilizing) == 1
    assert fertilizing[0].start == date(2027, 3, 1)
    todo = CareTodo(manager, None, "plant_care")
    assert not any(":fertilize:" in task.uid for task in todo.todo_items)


async def test_german_runtime_text_and_language_change(hass, freezer):
    freezer.move_to("2026-06-15T10:00:00Z")
    hass.config.language = "de"
    entry = make_hub(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert {task["summary"] for task in await tasks(hass, entry)} == {
        "Wässern: Monstera",
        "Düngen: Monstera",
    }
    assert any(
        event["summary"] == "Wässern: Ficus" for event in await events(hass, entry)
    )
    hass.config.language = "en"
    hass.bus.async_fire(EVENT_CORE_CONFIG_UPDATE, {"language": "en"})
    await hass.async_block_till_done()
    assert {task["summary"] for task in await tasks(hass, entry)} == {
        "Water: Monstera",
        "Fertilize: Monstera",
    }


async def test_diagnostics_allowlist_and_snapshot_isolation(hass, plant_hub):
    entry = plant_hub
    manager = entry.runtime_data
    manager.configs["monstera"] = replace(
        manager.configs["monstera"],
        notes="PRIVATE-NOTES",
        species="PRIVATE-SPECIES",
        location_note="PRIVATE-LOCATION",
        image_url="https://private.example/token=SECRET",
        area="PRIVATE-AREA",
    )
    payload = await async_get_config_entry_diagnostics(hass, entry)
    encoded = json.dumps(payload)
    for secret in [
        "PRIVATE-",
        "SECRET",
        "Rotate weekly",
        "Living room",
        "Office",
        entry.entry_id,
    ]:
        assert secret not in encoded
    assert payload["storage_version"] == 1
    assert payload["plant_count"] == 2
    assert payload["group_count"] == 2
    assert payload["plants"][0]["name"] == "Monstera"
    assert payload["plants"][0]["schedule"]["next_watering"] == "2026-06-08"
    assert payload["plants"][0]["runtime"]["watering_history"] == ["2026-06-01"]
    payload["plants"][0]["runtime"]["watering_history"].clear()
    assert manager.plants["monstera"].watering_history == [date(2026, 6, 1)]
    manager.configs["ficus"] = replace(
        manager.configs["ficus"], fertilizing_enabled=False
    )
    manager._recalculate()
    assert (await async_get_config_entry_diagnostics(hass, entry))["plants"][1][
        "schedule"
    ]["next_fertilizing"] is None


async def test_diagnostics_download_through_native_ha_endpoint(
    hass, plant_hub, hass_client
):
    from pytest_homeassistant_custom_component.components.diagnostics import (
        get_diagnostics_for_config_entry,
    )

    payload = await get_diagnostics_for_config_entry(hass, hass_client, plant_hub)
    assert payload["plant_count"] == 2
    assert {plant["name"] for plant in payload["plants"]} == {"Monstera", "Ficus"}
    assert "Rotate weekly" not in json.dumps(payload)


@pytest.mark.parametrize("failed_setup", [False, True])
async def test_diagnostics_download_without_loaded_runtime(
    hass, hass_storage, hass_client, failed_setup
):
    from homeassistant.config_entries import ConfigEntryDisabler
    from homeassistant.setup import async_setup_component
    from pytest_homeassistant_custom_component.components.diagnostics import (
        get_diagnostics_for_config_entry,
    )

    from custom_components.plantbased.const import DOMAIN
    from custom_components.plantbased.storage import storage_key

    entry = make_hub(hass)
    if failed_setup:
        hass_storage[storage_key(entry.entry_id)] = {
            "version": 999,
            "minor_version": 1,
            "data": {"plants": {}, "vacation": False},
        }
        assert not await hass.config_entries.async_setup(entry.entry_id)
    else:
        await hass.config_entries.async_set_disabled_by(
            entry.entry_id, ConfigEntryDisabler.USER
        )
        assert await async_setup_component(hass, DOMAIN, {})
    payload = await get_diagnostics_for_config_entry(hass, hass_client, entry)
    assert payload["runtime_available"] is False
    assert payload["entry_state"] == ("setup_error" if failed_setup else "not_loaded")
    assert payload["plants"] == []
    assert payload["plant_count"] == 2
    assert payload["group_count"] == 2
