"""Real domain actions, deduplicated targets and durable automation events."""

import asyncio
from datetime import date
from unittest.mock import AsyncMock, patch

from homeassistant.core import CoreState
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import area_registry as ar
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import label_registry as lr
from homeassistant.setup import async_setup_component
import pytest
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.plantbased.const import DOMAIN
from custom_components.plantbased.schema import schema as vol

from .common import call, device, entity_id, make_hub, state, subentry


async def action(hass, name, **data):
    await hass.services.async_call(DOMAIN, name, data, blocking=True)
    await hass.async_block_till_done()


async def test_actions_registered_without_loaded_hub(hass):
    assert await async_setup_component(hass, DOMAIN, {})
    for name in ("mark_watered", "mark_fertilized", "snooze", "set_interval"):
        assert hass.services.has_service(DOMAIN, name)
    with pytest.raises(ServiceValidationError) as error:
        await action(hass, "mark_watered", entity_id="sensor.missing")
    assert error.value.translation_key == "not_available"


async def test_group_plant_and_entity_targets_are_deduplicated(hass, plant_hub):
    done = []
    hass.bus.async_listen("plantbased_care_done", done.append)
    await action(
        hass,
        "mark_watered",
        device_id=[
            device(hass, plant_hub, "living").id,
            device(hass, plant_hub, "monstera").id,
        ],
        entity_id=[
            entity_id(hass, "monstera", "care_status"),
            entity_id(hass, "monstera", "last_watered", "date"),
        ],
        date="2026-06-13",
    )
    assert plant_hub.runtime_data.plants["monstera"].watering_history == [
        date(2026, 6, 1),
        date(2026, 6, 13),
    ]
    assert plant_hub.runtime_data.plants["ficus"].last_watered == date(2026, 6, 14)
    assert [event.data for event in done] == [
        {
            "device_id": device(hass, plant_hub, "monstera").id,
            "name": "Monstera",
            "care_type": "water",
        }
    ]
    await action(
        hass,
        "mark_fertilized",
        entity_id=entity_id(hass, "office", "plants_needing_water"),
    )
    assert plant_hub.runtime_data.plants["ficus"].last_fertilized == date(2026, 6, 15)
    assert plant_hub.runtime_data.plants["monstera"].last_fertilized == date(2026, 5, 1)


async def test_area_and_label_targets_ignore_indirect_foreign_entities(hass, plant_hub):
    area = ar.async_get(hass).async_create("Care room")
    label = lr.async_get(hass).async_create("Selected care")
    registry = dr.async_get(hass)
    registry.async_update_device(
        device(hass, plant_hub, "monstera").id, area_id=area.id
    )
    registry.async_update_device(
        device(hass, plant_hub, "office").id, labels={label.label_id}
    )
    foreign = er.async_get(hass).async_get_or_create(
        "sensor", "test", "unrelated", suggested_object_id="unrelated"
    )
    er.async_get(hass).async_update_entity(foreign.entity_id, area_id=area.id)
    await action(hass, "mark_watered", area_id=area.id)
    assert plant_hub.runtime_data.plants["ficus"].last_watered == date(2026, 6, 14)
    await action(hass, "mark_watered", label_id=label.label_id)
    assert plant_hub.runtime_data.plants["ficus"].last_watered == date(2026, 6, 15)


@pytest.mark.parametrize(
    "kind",
    [
        "missing_entity",
        "foreign_entity",
        "hub_entity",
        "missing_device",
        "hub_device",
        "missing_area",
        "empty",
    ],
)
async def test_invalid_targets_cannot_partially_mutate(hass, plant_hub, kind):
    targets = {
        "missing_entity": {
            "entity_id": [entity_id(hass, "monstera", "care_status"), "sensor.missing"]
        },
        "foreign_entity": {"entity_id": ["sensor.foreign"]},
        "hub_entity": {
            "entity_id": entity_id(hass, plant_hub.entry_id, "total_plants")
        },
        "missing_device": {
            "device_id": [device(hass, plant_hub, "monstera").id, "missing"]
        },
        "hub_device": {"device_id": device(hass, plant_hub, plant_hub.entry_id).id},
        "missing_area": {"area_id": "missing"},
        "empty": {},
    }
    snapshot = {
        key: value.to_data() for key, value in plant_hub.runtime_data.plants.items()
    }
    with pytest.raises(ServiceValidationError) as error:
        await action(hass, "mark_watered", **targets[kind])
    assert error.value.translation_key == "invalid_target"
    assert snapshot == {
        key: value.to_data() for key, value in plant_hub.runtime_data.plants.items()
    }


async def test_bulk_snooze_and_interval_actions(hass, plant_hub):
    await action(hass, "snooze", entity_id="all", care_type="water")
    assert state(hass, "monstera", "next_watering").state == "2026-06-16"
    assert state(hass, "ficus", "next_watering").state == "2026-06-22"
    await action(
        hass,
        "snooze",
        device_id=device(hass, plant_hub, "living").id,
        care_type="fertilize",
        days=3,
    )
    assert state(hass, "monstera", "next_fertilizing").state == "2026-06-18"
    assert state(hass, "ficus", "next_fertilizing").state == "2026-07-12"
    previous = plant_hub.runtime_data.plants["monstera"].to_data()
    await action(hass, "set_interval", entity_id="all", care_type="water", days=3)
    assert plant_hub.subentries["monstera"].data["watering_interval"] == 3
    assert plant_hub.subentries["ficus"].data["watering_interval"] == 3
    assert plant_hub.runtime_data.plants["monstera"].to_data() == previous
    assert state(hass, "monstera", "watering_interval", "number").state == "3"
    await action(
        hass,
        "set_interval",
        device_id=device(hass, plant_hub, "living").id,
        care_type="fertilize",
        days=20,
    )
    assert state(hass, "monstera", "fertilizing_interval", "number").state == "20"
    assert state(hass, "ficus", "fertilizing_interval", "number").state == "28"


@pytest.mark.parametrize(
    "data",
    [
        {"care_type": "other", "days": 1},
        {"care_type": "water", "days": 0},
        {"care_type": "water", "days": 366},
        {"care_type": "water", "days": 1.5},
        {"care_type": "water", "days": True},
        {"care_type": "water", "days": "2"},
        {"days": 1},
    ],
)
async def test_action_schema_rejects_invalid_data(hass, plant_hub, data):
    with pytest.raises(vol.Invalid):
        await action(hass, "snooze", entity_id="all", **data)


async def test_future_date_and_failed_write_emit_no_done(hass, plant_hub):
    done = []
    hass.bus.async_listen("plantbased_care_done", done.append)
    target = device(hass, plant_hub, "living").id
    with pytest.raises(ServiceValidationError):
        await action(hass, "mark_watered", device_id=target, date="2026-06-16")
    with patch.object(
        plant_hub.runtime_data.store,
        "async_save",
        AsyncMock(side_effect=HomeAssistantError("write failed")),
    ):
        with pytest.raises(HomeAssistantError):
            await action(hass, "mark_watered", device_id=target)
    assert not done
    assert state(hass, "monstera", "last_watered", "date").state == "2026-06-01"


async def test_empty_group_and_actions_after_unload(hass, plant_hub):
    hass.config_entries.async_add_subentry(
        plant_hub, subentry("group", "empty", "Empty")
    )
    await hass.async_block_till_done()
    await action(hass, "mark_watered", device_id=device(hass, plant_hub, "empty").id)
    await action(
        hass, "snooze", device_id=device(hass, plant_hub, "empty").id, care_type="water"
    )
    assert await hass.config_entries.async_unload(plant_hub.entry_id)
    assert hass.services.has_service(DOMAIN, "mark_watered")
    with pytest.raises(ServiceValidationError):
        await action(hass, "mark_watered", entity_id="all")


async def test_due_events_only_on_transitions_and_done_for_each_care_path(
    hass, freezer
):
    await hass.config.async_set_time_zone("UTC")
    freezer.move_to("2026-06-15T10:00:00Z")
    due, done = [], []
    hass.bus.async_listen("plantbased_care_due", due.append)
    hass.bus.async_listen("plantbased_care_done", done.append)
    entry = make_hub(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert {(event.data["name"], event.data["care_type"]) for event in due} == {
        ("Monstera", "water"),
        ("Monstera", "fertilize"),
    }
    assert all(
        event.data["device_id"] == device(hass, entry, "monstera").id for event in due
    )
    freezer.move_to("2026-06-16T00:00:00Z")
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert len(due) == 2  # Remaining overdue does not repeatedly fire.
    await call(hass, "monstera", "pause_plant", "switch", "turn_on")
    await call(hass, "monstera", "pause_plant", "switch", "turn_off")
    assert len(due) == 4
    await call(hass, "monstera", "snooze_watering")
    await call(hass, "monstera", "mark_fertilized")
    await call(hass, "monstera", "last_watered", "date", "set_value", date="2026-06-16")
    assert [event.data["care_type"] for event in done] == ["fertilize", "water"]
    freezer.move_to("2026-06-21T00:00:00Z")
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert due[-1].data["name"] == "Ficus"
    assert due[-1].data["care_type"] == "water"
    before = len(due)
    await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    assert len(due) == before + 1  # Startup/reload publishes current due work once.


async def test_concurrent_bulk_actions_preserve_every_history(hass, plant_hub):
    await asyncio.gather(
        *[action(hass, "mark_watered", entity_id="all") for _ in range(3)]
    )
    for plant in plant_hub.runtime_data.plants.values():
        assert plant.watering_history[-3:] == [date(2026, 6, 15)] * 3
    hass.set_state(CoreState.stopping)
    with pytest.raises(ServiceValidationError):
        await action(hass, "mark_watered", entity_id="all")
    hass.set_state(CoreState.not_running)


async def test_due_events_season_entry_and_snooze_expiry(hass, freezer):
    await hass.config.async_set_time_zone("UTC")
    freezer.move_to("2026-02-28T12:00:00Z")
    entry = make_hub(hass)
    sub = entry.subentries["monstera"]
    hass.config_entries.async_update_subentry(
        entry,
        sub,
        data={
            **sub.data,
            "all_year": False,
            "initial_last_watered": "2026-02-28",
            "initial_last_fertilized": "2026-01-01",
        },
    )
    due = []
    hass.bus.async_listen("plantbased_care_due", due.append)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert not due
    freezer.move_to("2026-03-01T00:00:00Z")
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert [event.data["care_type"] for event in due] == ["fertilize"]
    await action(
        hass,
        "snooze",
        device_id=device(hass, entry, "monstera").id,
        care_type="fertilize",
    )
    freezer.move_to("2026-03-02T00:00:00Z")
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert [event.data["care_type"] for event in due] == ["fertilize", "fertilize"]


async def test_registry_uuid_entity_target_and_disabled_entity(hass, plant_hub):
    registry = er.async_get(hass)
    target = registry.async_get(entity_id(hass, "monstera", "care_status"))
    await action(hass, "mark_watered", entity_id=target.id)
    assert plant_hub.runtime_data.plants["monstera"].last_watered == date(2026, 6, 15)
    registry.async_update_entity(
        target.entity_id, disabled_by=er.RegistryEntryDisabler.USER
    )
    await hass.async_block_till_done()
    await action(hass, "mark_fertilized", entity_id=target.entity_id)
    assert plant_hub.runtime_data.plants["monstera"].last_fertilized == date(
        2026, 6, 15
    )
