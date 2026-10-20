"""Actual local timer delivery for newly due plants, without frontend interaction."""

from homeassistant.components.notify import NOTIFY_SERVICE_SCHEMA
from homeassistant.core import CoreState
from homeassistant.exceptions import HomeAssistantError
import pytest

from .common import call, make_hub
from .test_reminders import DEFAULTS, advance, configure, register_notifier


async def flaky(hass, received):
    status = {"fail": True}
    attempts = []

    async def notifier(call):
        attempts.append(dict(call.data))
        if status["fail"]:
            raise HomeAssistantError("Temporary provider failure")
        received.append(dict(call.data))

    hass.services.async_register(
        "notify", "mobile_app_phone", notifier, schema=NOTIFY_SERVICE_SCHEMA
    )
    await hass.async_block_till_done()
    return status, attempts


async def test_retries_continue_and_success_does_not_repeat_other_targets(
    hass, freezer, reminder_hub
):
    entry, received, _ = reminder_hub
    email = register_notifier(hass, "email")
    await configure(
        hass, entry, notify_targets=["service:email", "service:mobile_app_phone"]
    )
    status, attempts = await flaky(hass, received)
    for stamp in ("09:00:01", "09:05:02", "09:10:03"):
        await advance(hass, freezer, f"2026-06-15T{stamp}Z")
    assert len(attempts) == 3 and len(email) == 1 and not received
    status["fail"] = False
    await advance(hass, freezer, "2026-06-15T09:15:04Z")
    assert len(received) == len(email) == 1
    assert entry.runtime_data.reminders._retry_timer is None
    await advance(hass, freezer, "2026-06-15T09:30:00Z")
    assert len(attempts) == 4


@pytest.mark.parametrize(
    "resolution", ["water", "snooze", "pause", "disable", "unload"]
)
async def test_pending_retry_is_cancelled_when_no_reminder_is_needed(
    hass, freezer, reminder_hub, resolution
):
    entry, received, _ = reminder_hub
    await call(hass, "monstera", "mark_fertilized")
    status, attempts = await flaky(hass, received)
    await advance(hass, freezer, "2026-06-15T09:00:01Z")
    coordinator = entry.runtime_data.reminders
    assert coordinator._retry_timer is not None
    status["fail"] = False
    if resolution == "water":
        await call(hass, "monstera", "mark_watered")
    elif resolution == "snooze":
        await call(hass, "monstera", "snooze_watering")
    elif resolution == "pause":
        await call(hass, "monstera", "pause_plant", "switch", "turn_on")
    elif resolution == "disable":
        await configure(hass, entry, reminder_enabled=False)
    else:
        assert await hass.config_entries.async_unload(entry.entry_id)
    assert coordinator._retry_timer is None
    await advance(hass, freezer, "2026-06-15T09:05:02Z")
    assert len(attempts) == 1 and not received


async def test_partial_care_during_retry_sends_only_remaining_tasks_once(
    hass, freezer, reminder_hub
):
    entry, received, _ = reminder_hub
    status, _ = await flaky(hass, received)
    await advance(hass, freezer, "2026-06-15T09:00:01Z")
    status["fail"] = False
    await call(hass, "monstera", "mark_watered")
    assert received[0]["message"] == "Fertilizing due: Monstera"
    assert entry.runtime_data.reminders._retry_timer is None
    await advance(hass, freezer, "2026-06-15T09:05:02Z")
    assert len(received) == 1


async def test_late_failure_waits_for_next_day_schedule(hass, freezer, reminder_hub):
    entry, received, _ = reminder_hub
    await configure(hass, entry, reminder_time="23:59:00")
    status, attempts = await flaky(hass, received)
    await advance(hass, freezer, "2026-06-15T23:59:01Z")
    assert len(attempts) == 1 and entry.runtime_data.reminders._retry_timer is None
    status["fail"] = False
    await advance(hass, freezer, "2026-06-16T00:05:00Z")
    assert not received
    await advance(hass, freezer, "2026-06-16T23:59:01Z")
    assert len(received) == 1


async def test_failed_scheduled_push_retries_without_a_care_action(
    hass, freezer, reminder_hub
):
    entry, received, _ = reminder_hub
    failures = True
    attempts = []

    async def notifier(call):
        attempts.append(dict(call.data))
        if failures:
            raise HomeAssistantError("Temporary provider failure")
        received.append(dict(call.data))

    hass.services.async_register(
        "notify", "mobile_app_phone", notifier, schema=NOTIFY_SERVICE_SCHEMA
    )
    await hass.async_block_till_done()
    await advance(hass, freezer, "2026-06-15T09:00:01Z")
    assert len(attempts) == 1 and not received
    failures = False
    await advance(hass, freezer, "2026-06-15T09:05:02Z")
    assert len(received) == 1
    assert received[0]["message"] == "Watering due: Monstera\nFertilizing due: Monstera"
    assert (
        entry.runtime_data.reminders.receipts[
            "service:mobile_app_phone"
        ].day.isoformat()
        == "2026-06-15"
    )


async def test_first_due_today_sends_at_1500_berlin_without_care_action(hass, freezer):
    freezer.move_to("2026-10-19T12:59:50Z")
    await hass.config.async_set_time_zone("Europe/Berlin")
    received = register_notifier(hass)
    entry = make_hub(hass)
    for key in ("monstera", "ficus"):
        sub = entry.subentries[key]
        hass.config_entries.async_update_subentry(
            entry,
            sub,
            data={
                **sub.data,
                "fertilizing_enabled": False,
                "initial_last_watered": "2026-10-16",
                "watering_interval": 4 if key == "monstera" else 7,
            },
        )
    hass.config_entries.async_update_entry(
        entry,
        options={
            **DEFAULTS,
            "reminder_time": "15:00:00",
            "persistent_notification": False,
        },
    )
    hass.set_state(CoreState.running)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    await advance(hass, freezer, "2026-10-19T13:00:01Z")
    assert not received
    await advance(hass, freezer, "2026-10-19T22:00:01Z")
    await advance(hass, freezer, "2026-10-20T12:59:59Z")
    assert not received
    await advance(hass, freezer, "2026-10-20T13:00:01Z")
    assert len(received) == 1
    assert received[0]["message"] == "Watering due: Monstera"
    await call(hass, "monstera", "mark_watered")
    assert received[-1]["message"] == "clear_notification"
    assert len(received) == 2


async def test_ios_care_updates_stay_quiet_but_daily_reminder_alerts_normally(
    hass, freezer, reminder_hub
):
    _, received, _ = reminder_hub
    await advance(hass, freezer, "2026-06-15T09:00:01Z")
    assert received[0]["data"]["alert_once"] is False
    assert "push" not in received[0]["data"]
    await call(hass, "monstera", "mark_watered")
    update = received[-1]
    assert update["message"] == "Fertilizing due: Monstera"
    assert update["data"]["alert_once"] is True
    assert update["data"]["push"]["interruption-level"] == "passive"
    assert update["data"]["presentation_options"] == []
    await advance(hass, freezer, "2026-06-16T09:00:01Z")
    assert received[-1]["data"]["alert_once"] is False
    assert "push" not in received[-1]["data"]
    assert "presentation_options" not in received[-1]["data"]
