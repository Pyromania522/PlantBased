"""Scheduled notification summaries through HA services, with no real delivery."""

from copy import deepcopy
from dataclasses import replace
from datetime import date
from unittest.mock import AsyncMock, patch

from homeassistant.components import persistent_notification as pn
from homeassistant.components.notify import NOTIFY_SERVICE_SCHEMA
from homeassistant.const import EVENT_CORE_CONFIG_UPDATE
from homeassistant.core import CoreState
from homeassistant.exceptions import HomeAssistantError
import pytest
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.plantbased.notification_texts import TEXTS, notification_texts

from .common import call, state

DEFAULTS = {
    "reminder_enabled": True,
    "reminder_time": "09:00:00",
    "notify_targets": ["service:mobile_app_phone"],
    "repeat_daily": True,
    "persistent_notification": True,
    "snooze_action": True,
}


def register_notifier(hass, name="mobile_app_phone", *, error=None):
    received = []

    async def handle(call):
        if error is not None:
            raise error
        received.append(deepcopy(dict(call.data)))

    hass.services.async_register("notify", name, handle, schema=NOTIFY_SERVICE_SCHEMA)
    return received


async def configure(hass, entry, **changes):
    hass.config_entries.async_update_entry(entry, options={**entry.options, **changes})
    await hass.async_block_till_done()


async def advance(hass, freezer, stamp):
    freezer.move_to(stamp)
    async_fire_time_changed(hass)
    await hass.async_block_till_done()


def mobile_action(received, operation):
    return next(
        action["action"]
        for action in received[-1]["data"]["actions"]
        if action["action"].endswith(":" + operation)
    )


async def fire_action(hass, action):
    hass.bus.async_fire("mobile_app_notification_action", {"action": action})
    await hass.async_block_till_done()


async def test_defaults_off_and_single_grouped_local_summary(hass, plant_hub):
    received = register_notifier(hass)
    assert not plant_hub.runtime_data.reminders.options.enabled
    plant_hub.runtime_data.reminders._async_started(hass)
    await hass.async_block_till_done()
    assert not received


async def test_daily_summary_persistent_tag_and_restart_dedup(
    hass, freezer, reminder_hub
):
    entry, received, persistent = reminder_hub
    assert not received
    await advance(hass, freezer, "2026-06-15T09:00:00Z")
    assert len(received) == 1
    message = received[0]
    assert message["message"] == "Watering due: Monstera\nFertilizing due: Monstera"
    assert message["data"]["tag"] == entry.runtime_data.reminders.tag
    assert len(message["data"]["actions"]) == 3
    assert persistent[-1][0] == pn.UpdateType.ADDED
    assert next(iter(persistent[-1][1].values()))["message"] == message["message"]
    await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    assert len(received) == 1
    await advance(hass, freezer, "2026-06-16T09:00:00Z")
    assert len(received) == 2
    assert received[-1]["data"]["alert_once"] is False
    await advance(hass, freezer, "2026-06-16T09:00:01Z")
    assert len(received) == 2


async def test_mobile_mark_only_notified_due_plants_and_replace_then_clear(
    hass, freezer, reminder_hub
):
    entry, received, persistent = reminder_hub
    await advance(hass, freezer, "2026-06-15T09:00:00Z")
    old_water = mobile_action(received, "water")
    original_ficus = entry.runtime_data.plants["ficus"].to_data()
    await fire_action(hass, old_water)
    assert state(hass, "monstera", "last_watered", "date").state == "2026-06-15"
    assert received[-1]["message"] == "Fertilizing due: Monstera"
    assert received[-1]["data"]["alert_once"] is True
    assert entry.runtime_data.plants["ficus"].to_data() == original_ficus
    count = len(entry.runtime_data.plants["monstera"].watering_history)
    await fire_action(hass, old_water)
    assert len(entry.runtime_data.plants["monstera"].watering_history) == count
    await fire_action(hass, mobile_action(received, "fertilize"))
    assert received[-1] == {
        "message": "clear_notification",
        "data": {"tag": entry.runtime_data.reminders.tag},
    }
    assert persistent[-1][0] == pn.UpdateType.REMOVED
    assert state(hass, entry.entry_id, "plant_care", "todo").state == "0"


async def test_snooze_both_care_types_is_one_transaction_and_replay_safe(
    hass, freezer, reminder_hub
):
    entry, received, _ = reminder_hub
    await advance(hass, freezer, "2026-06-15T09:00:00Z")
    action = mobile_action(received, "snooze")
    store = entry.runtime_data.store
    with patch.object(store, "async_save", wraps=store.async_save) as save:
        await fire_action(hass, action)
        assert save.await_count == 1
    assert state(hass, "monstera", "next_watering").state == "2026-06-16"
    assert state(hass, "monstera", "next_fertilizing").state == "2026-06-16"
    assert received[-1]["message"] == "clear_notification"
    await fire_action(hass, action)
    assert state(hass, "monstera", "next_watering").state == "2026-06-16"
    await advance(hass, freezer, "2026-06-16T09:00:00Z")
    assert len(received[-1]["data"]["actions"]) == 3


async def test_pause_vacation_and_disable_clear_without_changing_dates(
    hass, freezer, reminder_hub
):
    entry, received, persistent = reminder_hub
    await advance(hass, freezer, "2026-06-15T09:00:00Z")
    action = mobile_action(received, "water")
    await call(hass, "monstera", "pause_plant", "switch", "turn_on")
    assert received[-1]["message"] == "clear_notification"
    await fire_action(hass, action)
    assert state(hass, "monstera", "last_watered", "date").state == "2026-06-01"
    await call(hass, "monstera", "pause_plant", "switch", "turn_off")
    await advance(hass, freezer, "2026-06-16T09:00:00Z")
    await call(hass, entry.entry_id, "vacation_mode", "switch", "turn_on")
    assert received[-1]["message"] == "clear_notification"
    await call(hass, entry.entry_id, "vacation_mode", "switch", "turn_off")
    await advance(hass, freezer, "2026-06-17T09:00:00Z")
    await configure(hass, entry, reminder_enabled=False)
    assert received[-1]["message"] == "clear_notification"
    assert persistent[-1][0] == pn.UpdateType.REMOVED
    count = len(received)
    await advance(hass, freezer, "2026-06-18T09:00:00Z")
    assert len(received) == count


async def test_repeat_off_survives_reload_and_new_care_gets_next_summary(
    hass, freezer, reminder_hub
):
    entry, received, _ = reminder_hub
    await configure(hass, entry, repeat_daily=False)
    await advance(hass, freezer, "2026-06-15T09:00:00Z")
    await advance(hass, freezer, "2026-06-16T09:00:00Z")
    assert len(received) == 1
    await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    assert len(received) == 1
    # A different plant becomes due: an existing mobile summary is refreshed,
    # but that silent refresh must not consume the scheduled new-task reminder.
    await advance(hass, freezer, "2026-06-21T00:00:00Z")
    assert "Ficus" in received[-1]["message"]
    before = len(received)
    await advance(hass, freezer, "2026-06-21T09:00:00Z")
    assert len(received) == before + 1
    await advance(hass, freezer, "2026-06-22T09:00:00Z")
    assert len(received) == before + 1


async def test_removed_target_clear_failure_retained_and_retried(
    hass, freezer, reminder_hub
):
    entry, _received, _ = reminder_hub
    await advance(hass, freezer, "2026-06-15T09:00:00Z")
    hass.services.async_remove("notify", "mobile_app_phone")
    await configure(hass, entry, notify_targets=[])
    assert entry.runtime_data.reminders.receipts["service:mobile_app_phone"].active
    replacement = register_notifier(hass)
    await hass.async_block_till_done()
    assert replacement[0]["message"] == "clear_notification"
    assert "service:mobile_app_phone" not in entry.runtime_data.reminders.receipts


async def test_failed_recipient_does_not_block_other_targets(
    hass, freezer, reminder_hub
):
    entry, received, _ = reminder_hub
    register_notifier(
        hass,
        "mobile_app_bad",
        error=HomeAssistantError("provider failed with PRIVATE-CREDENTIAL"),
    )
    email = register_notifier(hass, "email")
    await configure(
        hass,
        entry,
        notify_targets=[
            "service:mobile_app_bad",
            "service:mobile_app_phone",
            "service:email",
        ],
    )
    await advance(hass, freezer, "2026-06-15T09:00:00Z")
    assert len(received) == len(email) == 1
    assert "data" not in email[0]
    assert not entry.runtime_data.reminders.receipts["service:mobile_app_bad"].day
    assert state(hass, "monstera", "last_watered", "date").state == "2026-06-01"


@pytest.mark.parametrize("language", ["en", "de", "fr"])
async def test_translated_summary_actions_and_fallback(
    hass, freezer, reminder_hub, language
):
    _entry, received, _ = reminder_hub
    hass.config.language = language
    await advance(hass, freezer, "2026-06-15T09:00:00Z")
    texts = notification_texts(language)
    assert received[0]["title"] == texts["title"]
    assert texts["water"] in received[0]["message"]
    assert received[0]["data"]["actions"][0]["title"] == texts["all_watered"]
    assert set(TEXTS["de"]) == set(TEXTS["en"])
    if language == "en":
        hass.config.language = "de"
        hass.bus.async_fire(EVENT_CORE_CONFIG_UPDATE, {"language": "de"})
        await hass.async_block_till_done()
        assert received[-1]["title"] == TEXTS["de"]["title"]


async def test_snooze_option_and_unrelated_malformed_events(
    hass, freezer, reminder_hub
):
    entry, received, _ = reminder_hub
    await configure(hass, entry, snooze_action=False)
    await advance(hass, freezer, "2026-06-15T09:00:00Z")
    assert len(received[0]["data"]["actions"]) == 2
    prefix = mobile_action(received, "water").rsplit(":", 1)[0]
    snapshot = entry.runtime_data.plants["monstera"].to_data()
    for value in [
        None,
        {},
        "UNRELATED",
        prefix + ":other",
        prefix + ":snooze",
        prefix + ":water:extra",
        entry.runtime_data.reminders.tag + ":wrong:water",
    ]:
        await fire_action(hass, value)
    assert entry.runtime_data.plants["monstera"].to_data() == snapshot


async def test_native_task_completion_clears_summary_and_receipts_removed_with_hub(
    hass, freezer, reminder_hub, hass_storage
):
    entry, received, _ = reminder_hub
    await advance(hass, freezer, "2026-06-15T09:00:00Z")
    await call(hass, "living", "mark_all_watered")
    await call(hass, "living", "mark_all_fertilized")
    assert received[-1]["message"] == "clear_notification"
    assert any(key.endswith(".reminders") for key in hass_storage)
    assert await hass.config_entries.async_remove(entry.entry_id)
    assert not any(key.startswith("plantbased.") for key in hass_storage)


async def test_care_write_failure_from_mobile_keeps_tasks_and_no_done(
    hass, freezer, reminder_hub, caplog
):
    entry, received, _ = reminder_hub
    await advance(hass, freezer, "2026-06-15T09:00:00Z")
    action = mobile_action(received, "water")
    done = []
    hass.bus.async_listen("plantbased_care_done", done.append)
    with patch.object(
        entry.runtime_data.store,
        "async_save",
        AsyncMock(side_effect=HomeAssistantError("PRIVATE-CREDENTIAL")),
    ):
        await fire_action(hass, action)
    assert not done
    assert state(hass, "monstera", "last_watered", "date").state == "2026-06-01"
    assert len(received) == 1
    assert "PRIVATE-CREDENTIAL" not in caplog.text


async def test_startup_catchup_and_stopped_timer_cleanup(hass, freezer, reminder_hub):
    entry, received, _ = reminder_hub
    await advance(hass, freezer, "2026-06-15T08:59:55Z")
    coordinator = entry.runtime_data.reminders
    assert await hass.config_entries.async_unload(entry.entry_id)
    await advance(hass, freezer, "2026-06-15T10:00:00Z")
    assert not received
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert len(received) == 1
    assert coordinator._stopped
    coordinator._async_schedule(send=True)
    assert coordinator._worker is None
    await hass.config_entries.async_unload(entry.entry_id)
    await advance(hass, freezer, "2026-06-16T09:00:00Z")
    assert len(received) == 1


@pytest.mark.parametrize(
    ("before", "first", "second"),
    [
        ("2026-03-29T00:59:50Z", "2026-03-29T01:30:00Z", None),
        ("2026-10-25T00:29:50Z", "2026-10-25T00:30:00Z", "2026-10-25T01:30:00Z"),
    ],
)
async def test_local_schedule_dst_and_repeated_hour_dedup(
    hass, freezer, reminder_hub, before, first, second
):
    entry, received, _ = reminder_hub
    # Only the overdue plant is relevant for this timer test.
    await hass.config.async_set_time_zone("Europe/Berlin")
    freezer.move_to(before)
    entry.runtime_data.plants["monstera"].last_watered = date(2026, 1, 1)
    entry.runtime_data.plants["monstera"].last_fertilized = date(2026, 1, 1)
    await entry.runtime_data.store.async_save(
        entry.runtime_data._serialize(
            entry.runtime_data.plants, entry.runtime_data.vacation
        )
    )
    await configure(hass, entry, reminder_time="02:30:00")
    received.clear()
    await advance(hass, freezer, first)
    assert len(received) == 1
    if second:
        await advance(hass, freezer, second)
        assert len(received) == 1


async def test_time_zone_change_reschedules_and_shutdown_suppresses(
    hass, freezer, reminder_hub
):
    entry, received, _ = reminder_hub
    await hass.config.async_set_time_zone("Europe/Berlin")
    hass.bus.async_fire(EVENT_CORE_CONFIG_UPDATE, {"time_zone": "Europe/Berlin"})
    await hass.async_block_till_done()
    assert len(received) == 1  # New local time is after today's configured time.
    hass.set_state(CoreState.stopping)
    await entry.runtime_data.reminders._async_process(True)
    assert len(received) == 1
    hass.set_state(CoreState.running)


async def test_receipt_write_failure_logged_without_resetting_care(
    hass, freezer, reminder_hub, caplog
):
    entry, received, _ = reminder_hub
    coordinator = entry.runtime_data.reminders
    original = deepcopy(coordinator.receipts)
    with patch.object(
        coordinator.store,
        "async_save",
        AsyncMock(side_effect=HomeAssistantError("PRIVATE")),
    ):
        await advance(hass, freezer, "2026-06-15T09:00:00Z")
    assert len(received) == 1
    assert coordinator.receipts == original
    assert state(hass, "monstera", "last_watered", "date").state == "2026-06-01"
    assert "PRIVATE" not in caplog.text


async def test_season_disabled_fertilizer_and_no_due_no_notification(
    hass, freezer, reminder_hub
):
    entry, received, _ = reminder_hub
    manager = entry.runtime_data
    manager.configs["monstera"] = replace(
        manager.configs["monstera"], fertilizing_enabled=False
    )
    await advance(hass, freezer, "2026-06-15T09:00:00Z")
    assert "Fertilizing" not in received[0]["message"]
    await call(hass, "monstera", "mark_watered")
    assert received[-1]["message"] == "clear_notification"
    before = len(received)
    await advance(hass, freezer, "2026-06-16T09:00:00Z")
    assert len(received) == before


async def test_persistent_copy_recreated_on_reload_without_duplicate_mobile(
    hass, freezer, reminder_hub
):
    entry, received, persistent = reminder_hub
    await advance(hass, freezer, "2026-06-15T09:00:00Z")
    pn.async_dismiss(hass, entry.runtime_data.reminders.tag)
    await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    assert persistent[-1][0] == pn.UpdateType.ADDED
    assert len(received) == 1


async def test_hub_deletion_clears_active_messages_and_removes_receipts(
    hass, freezer, reminder_hub, hass_storage
):
    entry, received, persistent = reminder_hub
    await advance(hass, freezer, "2026-06-15T09:00:00Z")
    assert await hass.config_entries.async_remove(entry.entry_id)
    await hass.async_block_till_done()
    assert received[-1]["message"] == "clear_notification"
    assert persistent[-1][0] == pn.UpdateType.REMOVED
    assert not any(key.startswith("plantbased.") for key in hass_storage)


async def test_old_mobile_action_cannot_complete_a_later_due_cycle(
    hass, freezer, reminder_hub
):
    entry, received, _ = reminder_hub
    await advance(hass, freezer, "2026-06-15T09:00:00Z")
    old = mobile_action(received, "water")
    await call(hass, "monstera", "mark_watered")
    await advance(hass, freezer, "2026-06-22T09:00:00Z")
    before = entry.runtime_data.plants["monstera"].to_data()
    await fire_action(hass, old)
    assert entry.runtime_data.plants["monstera"].to_data() == before


async def test_mobile_action_validated_again_inside_care_lock(
    hass, freezer, reminder_hub
):
    import asyncio

    from homeassistant.core import Event

    entry, received, _ = reminder_hub
    await advance(hass, freezer, "2026-06-15T09:00:00Z")
    action = mobile_action(received, "water")
    manager = entry.runtime_data
    coordinator = manager.reminders
    async with manager._lock:
        pending = asyncio.create_task(
            coordinator._async_action(
                Event("mobile_app_notification_action", {"action": action})
            )
        )
        await asyncio.sleep(0)
        manager.plants["monstera"].last_watered = date(2026, 6, 15)
    await pending
    await hass.async_block_till_done()
    assert manager.plants["monstera"].watering_history == [date(2026, 6, 1)]


async def test_disabling_hub_clears_mobile_and_persistent(hass, freezer, reminder_hub):
    from homeassistant.config_entries import ConfigEntryDisabler

    entry, received, persistent = reminder_hub
    await advance(hass, freezer, "2026-06-15T09:00:00Z")
    await hass.config_entries.async_set_disabled_by(
        entry.entry_id, ConfigEntryDisabler.USER
    )
    await hass.async_block_till_done()
    assert received[-1]["message"] == "clear_notification"
    assert persistent[-1][0] == pn.UpdateType.REMOVED
