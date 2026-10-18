"""Rhythm learning, robust observations and real HA persistence/control paths."""

from datetime import date, timedelta
from unittest.mock import AsyncMock, patch

from homeassistant.config_entries import SOURCE_RECONFIGURE
from homeassistant.exceptions import HomeAssistantError
from homeassistant.util import dt as dt_util
import pytest
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.plantbased.learning import WateringLearning
from custom_components.plantbased.models import PlantState

from .common import call, state
from .test_calendar_todo_diagnostics import complete, events, tasks


@pytest.mark.parametrize(
    ("baseline", "gaps", "expected"),
    [
        (4, [3, 3], 4),
        (4, [3, 3, 3], 3),
        (7, [3, 3, 3], 6),
        (3, [4, 4, 4], 4),
        (4, [3, 3, 30], 4),
        (4, [3, 3, 3, 30], 3),
        (4, [1, 3, 7, 10, 20], 4),
        (1, [1, 1, 1], 1),
        (365, [365, 365, 365], 365),
        (4, [10, 10, 10], 5),
    ],
)
def test_only_consistent_intervals_adjust_gradually(baseline, gaps, expected):
    learning = WateringLearning()
    learning.sync(True, baseline, 0)
    day = date(2026, 1, 1)
    learning.observe(day)
    for gap in gaps:
        day += timedelta(days=gap)
        learning.observe(day)
    assert learning.effective(True, baseline, 0) == expected


def test_duplicate_out_of_order_and_snoozed_observations():
    learning = WateringLearning()
    learning.sync(True, 4, 0)
    day = date(2026, 1, 1)
    for _ in range(20):
        learning.observe(day)
    assert learning.gaps == [] and learning.interval == 4
    learning.observe(day + timedelta(days=3))
    learning.observe(day + timedelta(days=6))
    learning.observe(day + timedelta(days=9), skip_gap=True)
    assert learning.gaps == [] and learning.interval == 4
    learning.observe(day + timedelta(days=8))
    assert learning.anchor == day + timedelta(days=8) and learning.gaps == []
    learning.observe(day + timedelta(days=400))
    assert learning.gaps == []
    learning.sync(False, 4, 0)
    learning.observe(day)
    assert learning.interval is None and learning.anchor is None


def test_serialization_and_manual_revision_reset():
    learning = WateringLearning(4, 0, 3, date(2026, 1, 10), [3, 3, 3])
    data = learning.to_data()
    restored = WateringLearning.from_data(data)
    data["gaps"].clear()
    assert restored.gaps == [3, 3, 3]
    assert restored.effective(True, 4, 1) == 4
    restored.sync(True, 4, 1)
    assert restored.interval == 4 and restored.gaps == []
    assert restored.anchor is None
    assert restored.effective(False, 4, 1) == 4
    assert restored.effective(True, 6, 1) == 6


@pytest.mark.parametrize(
    "data",
    [
        None,
        [],
        {"baseline": True},
        {"interval": 0},
        {"baseline": 366},
        {"revision": -1},
        {"revision": True},
        {"gaps": [True]},
        {"gaps": [0]},
        {"gaps": [3] * 6},
        {"gaps": "bad"},
        {"baseline": 4},
        {"baseline": 4, "interval": 3, "gaps": [3]},
        {"anchor": "2026-01-01"},
        {"anchor": ""},
    ],
)
def test_corrupt_learning_is_rejected_without_resetting(data):
    with pytest.raises((ValueError, TypeError)):
        WateringLearning.from_data(data)


async def enable(hass, entry, enabled=True, interval=4):
    sub = entry.subentries["monstera"]
    hass.config_entries.async_update_subentry(
        entry,
        sub,
        data={**sub.data, "adaptive_watering": enabled, "watering_interval": interval},
    )
    await hass.async_block_till_done()


async def record(hass, freezer, day, method="button"):
    freezer.move_to(f"{day.isoformat()}T10:00:00Z")
    if method == "group":
        await call(hass, "living", "mark_all_watered")
    elif method == "service":
        await hass.services.async_call(
            "plantbased",
            "mark_watered",
            {"entity_id": state(hass, "monstera", "care_status").entity_id},
            blocking=True,
        )
        await hass.async_block_till_done()
    else:
        await call(hass, "monstera", "mark_watered")


async def train(hass, entry, freezer, gaps=(3, 3, 3), method="button"):
    await enable(hass, entry)
    day = date(2026, 6, 16)
    await record(hass, freezer, day, method)
    for gap in gaps:
        day += timedelta(days=gap)
        await record(hass, freezer, day, method)
    return day


@pytest.mark.parametrize("method", ["button", "group", "service"])
async def test_recorded_watering_changes_all_due_views_and_survives_reload(
    hass, plant_hub, freezer, method
):
    entry = plant_hub
    fertilizer = entry.runtime_data.plants["monstera"].last_fertilized
    await train(hass, entry, freezer, method=method)
    assert state(hass, "monstera", "next_watering").state == "2026-06-28"
    assert state(hass, "monstera", "watering_interval", "number").state == "3"
    assert entry.subentries["monstera"].data["watering_interval"] == 4
    attrs = state(hass, "monstera", "care_status").attributes
    assert attrs["adaptive_watering"] is True
    assert attrs["watering_base_interval"] == 4
    assert attrs["watering_effective_interval"] == 3
    assert attrs["watering_learning_samples"] == 3
    assert (
        next(
            event
            for event in await events(hass, entry)
            if event["summary"] == "Water: Monstera"
        )["start"]
        == "2026-06-28"
    )
    before = entry.runtime_data.plants["monstera"].to_data()
    assert await hass.config_entries.async_reload(entry.entry_id)
    assert entry.runtime_data.plants["monstera"].to_data() == before
    assert entry.runtime_data.plants["monstera"].last_fertilized == fertilizer
    freezer.move_to("2026-06-28T10:00:00Z")
    async_fire_time_changed(hass, dt_util.utcnow())
    await hass.async_block_till_done()
    assert state(hass, "monstera", "needs_water", "binary_sensor").state == "on"
    assert state(hass, entry.entry_id, "plants_needing_water").state == "2"
    water = next(
        item
        for item in await tasks(hass, entry)
        if item["uid"] == "monstera:water:2026-06-28"
    )
    await complete(hass, entry, water["uid"])
    assert state(hass, "monstera", "next_watering").state == "2026-07-01"
    assert entry.runtime_data.plants["monstera"].watering_learning.gaps == [3, 3, 3, 3]


async def test_learning_is_optional_and_does_not_reuse_seed_history(
    hass, plant_hub, freezer
):
    entry = plant_hub
    for day in (16, 19, 22, 25):
        await record(hass, freezer, date(2026, 6, day))
    assert state(hass, "monstera", "watering_interval", "number").state == "7"
    assert entry.runtime_data.plants["monstera"].watering_learning.gaps == []
    await enable(hass, entry)
    assert state(hass, "monstera", "watering_interval", "number").state == "4"
    assert entry.runtime_data.plants["monstera"].watering_learning.gaps == []
    assert entry.runtime_data.plants["monstera"].watering_learning.anchor is None


@pytest.mark.parametrize("excluded", ["date", "snooze", "pause", "vacation"])
async def test_excluded_periods_do_not_train(hass, plant_hub, freezer, excluded):
    entry = plant_hub
    await train(hass, entry, freezer, gaps=(3, 3))
    if excluded == "date":
        await call(
            hass, "monstera", "last_watered", "date", "set_value", date="2026-06-20"
        )
    else:
        if excluded == "snooze":
            await call(hass, "monstera", "snooze_watering")
        elif excluded == "pause":
            await call(hass, "monstera", "pause_plant", "switch", "turn_on")
        else:
            await call(hass, entry.entry_id, "vacation_mode", "switch", "turn_on")
        await record(hass, freezer, date(2026, 6, 25))
    assert entry.runtime_data.plants["monstera"].watering_learning.gaps == []
    assert state(hass, "monstera", "watering_interval", "number").state == "4"


async def test_manual_override_same_baseline_and_disable_restore_control(
    hass, plant_hub, freezer
):
    entry = plant_hub
    await train(hass, entry, freezer)
    history = list(entry.runtime_data.plants["monstera"].watering_history)
    await call(hass, "monstera", "watering_interval", "number", "set_value", value=4)
    assert state(hass, "monstera", "watering_interval", "number").state == "4"
    assert entry.runtime_data.plants["monstera"].watering_learning.gaps == []
    assert entry.subentries["monstera"].data["learning_revision"] == 1
    # Reconfigure through the actual HA flow, preserving existing defaults.
    result = await hass.config_entries.subentries.async_init(
        (entry.entry_id, "plant"),
        context={"source": SOURCE_RECONFIGURE, "subentry_id": "monstera"},
    )
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {"name": "Monstera", "adaptive_watering": False}
    )
    assert result["reason"] == "reconfigure_successful"
    await hass.async_block_till_done()
    assert (
        state(hass, "monstera", "care_status").attributes["adaptive_watering"] is False
    )
    assert entry.runtime_data.plants["monstera"].watering_learning.interval is None
    assert entry.runtime_data.plants["monstera"].watering_history == history


async def test_failed_save_does_not_commit_learned_interval(hass, plant_hub, freezer):
    entry = plant_hub
    await train(hass, entry, freezer, gaps=(3, 3))
    manager = entry.runtime_data
    before = manager.plants["monstera"].to_data()
    with patch.object(
        manager.store,
        "async_save",
        AsyncMock(side_effect=HomeAssistantError("Disk unavailable")),
    ):
        with pytest.raises(HomeAssistantError):
            await record(hass, freezer, date(2026, 6, 25))
    assert manager.plants["monstera"].to_data() == before
    assert state(hass, "monstera", "watering_interval", "number").state == "4"
    await record(hass, freezer, date(2026, 6, 25))
    assert state(hass, "monstera", "watering_interval", "number").state == "3"


async def test_learned_snooze_uses_active_interval_and_fertilizer_does_not_train(
    hass, plant_hub, freezer
):
    entry = plant_hub
    await train(hass, entry, freezer)
    before = entry.runtime_data.plants["monstera"].watering_learning.to_data()
    await call(hass, "monstera", "mark_fertilized")
    assert entry.runtime_data.plants["monstera"].watering_learning.to_data() == before
    await call(hass, "monstera", "snooze_watering")
    assert state(hass, "monstera", "next_watering").state == "2026-06-29"


async def test_pause_retains_learned_interval_and_disable_restores_baseline(
    hass, plant_hub, freezer
):
    entry = plant_hub
    await train(hass, entry, freezer)
    history = list(entry.runtime_data.plants["monstera"].watering_history)
    await call(hass, "monstera", "pause_plant", "switch", "turn_on")
    await call(hass, "monstera", "pause_plant", "switch", "turn_off")
    assert state(hass, "monstera", "watering_interval", "number").state == "3"
    assert entry.runtime_data.plants["monstera"].watering_learning.gaps == []
    await enable(hass, entry, False)
    assert state(hass, "monstera", "watering_interval", "number").state == "4"
    await enable(hass, entry, True)
    assert entry.runtime_data.plants["monstera"].watering_learning.anchor is None
    assert entry.runtime_data.plants["monstera"].watering_history == history


def test_old_runtime_loads_without_learning_data():
    value = {"last_watered": "2026-06-15", "last_fertilized": "2026-06-01"}
    assert PlantState.from_data(value).watering_learning == WateringLearning()
