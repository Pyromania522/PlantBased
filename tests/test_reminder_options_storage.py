"""Native options flow, modern notify entities and strict private receipt loading."""

from copy import deepcopy
from datetime import date
import json

from homeassistant.components.notify import NotifyEntity, NotifyEntityFeature
from homeassistant.core import CoreState
from homeassistant.data_entry_flow import FlowResultType, InvalidData
from homeassistant.helpers import entity_registry as er
from homeassistant.setup import async_setup_component
import pytest

from custom_components.plantbased.reminder_options import available_targets
from custom_components.plantbased.reminder_storage import (
    Receipt,
    ReminderStore,
    decode_receipts,
    is_task_uid,
)
from custom_components.plantbased.storage import storage_key

from .common import make_hub
from .test_reminders import (
    DEFAULTS,
    advance,
    configure,
    register_notifier,
)


async def test_options_native_flow_defaults_save_reload(hass, plant_hub):
    register_notifier(hass)
    result = await hass.config_entries.options.async_init(plant_hub.entry_id)
    assert result["type"] is FlowResultType.FORM
    defaults = {key.schema: key.default() for key in result["data_schema"].schema}
    assert defaults["reminder_enabled"] is False
    assert defaults["reminder_time"] == "09:00:00"
    assert defaults["repeat_daily"] is True
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input=DEFAULTS
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    assert plant_hub.options == DEFAULTS
    assert plant_hub.runtime_data.reminders.options.enabled


async def test_options_require_target_or_persistent_and_validate_live_targets(
    hass, plant_hub
):
    register_notifier(hass)
    result = await hass.config_entries.options.async_init(plant_hub.entry_id)
    data = {**DEFAULTS, "notify_targets": [], "persistent_notification": False}
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input=data
    )
    assert result["errors"] == {"base": "target_required"}
    data = {**DEFAULTS, "persistent_notification": False}
    hass.services.async_remove("notify", "mobile_app_phone")
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input=data
    )
    assert result["errors"] == {"notify_targets": "invalid_target"}
    data = {**DEFAULTS, "notify_targets": []}
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input=data
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY


async def test_stale_target_can_be_removed_and_invalid_time_rejected(hass, plant_hub):
    await configure(hass, plant_hub, **DEFAULTS)
    result = await hass.config_entries.options.async_init(plant_hub.entry_id)
    with pytest.raises(InvalidData):
        await hass.config_entries.options.async_configure(
            result["flow_id"], user_input={**DEFAULTS, "reminder_time": "25:00:00"}
        )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={**DEFAULTS, "notify_targets": []}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()


@pytest.mark.parametrize("with_title", [False, True])
async def test_modern_notify_entity_real_native_send_message(hass, freezer, with_title):
    from homeassistant.components.notify import DATA_COMPONENT

    freezer.move_to("2026-06-15T08:59:50Z")
    await hass.config.async_set_time_zone("UTC")
    assert await async_setup_component(hass, "notify", {})
    messages = []

    class Speaker(NotifyEntity):
        _attr_name = "Test speaker"
        _attr_unique_id = "test_speaker"
        _attr_supported_features = NotifyEntityFeature.TITLE if with_title else 0

        async def async_send_message(self, message, title=None):
            messages.append((message, title))

    speaker = Speaker()
    await hass.data[DATA_COMPONENT].async_add_entities([speaker])
    await hass.async_block_till_done()
    assert {
        "value": f"entity:{speaker.entity_id}",
        "label": "Test speaker",
    } in available_targets(hass)
    # The mobile entity API cannot carry custom tag/actions; legacy service is used.
    er.async_get(hass).async_get_or_create(
        "notify", "mobile_app", "phone", suggested_object_id="mobile_phone"
    )
    hass.states.async_set("notify.mobile_phone", "2026-06-15T00:00:00Z")
    assert not any(
        choice["value"] == "entity:notify.mobile_phone"
        for choice in available_targets(hass)
    )
    entry = make_hub(hass)
    hass.config_entries.async_update_entry(
        entry,
        options={
            **DEFAULTS,
            "notify_targets": [f"entity:{speaker.entity_id}"],
            "persistent_notification": False,
        },
    )
    hass.set_state(CoreState.running)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    await advance(hass, freezer, "2026-06-15T09:00:00Z")
    assert messages == [
        (
            "Watering due: Monstera\nFertilizing due: Monstera",
            "PlantBased: plant care" if with_title else None,
        )
    ]
    hass.states.async_set(speaker.entity_id, "unavailable")
    assert not any(
        choice["value"] == f"entity:{speaker.entity_id}"
        for choice in available_targets(hass)
    )
    await advance(hass, freezer, "2026-06-16T09:00:00Z")
    assert len(messages) == 1


@pytest.mark.parametrize(
    "value",
    [
        None,
        1,
        "broken",
        ":water:2026-01-01",
        "plant:other:2026-01-01",
        "plant:water:broken",
    ],
)
def test_malformed_task_uid_rejected(value):
    assert not is_task_uid(value)


@pytest.mark.parametrize(
    "change",
    [
        {"day": "invalid"},
        {"seen": "invalid"},
        {"active": [42]},
        {"token": "bad"},
        {"token": 4},
        {"text": None},
    ],
)
def test_malformed_receipt_rejected(change):
    receipt = Receipt(
        date(2026, 6, 15),
        {"plant:water:2026-06-08"},
        {"plant:water:2026-06-08"},
        "a" * 32,
        "Reminder",
    )
    assert Receipt.from_data(receipt.to_data()) == receipt
    with pytest.raises((ValueError, TypeError)):
        Receipt.from_data({**receipt.to_data(), **change})


@pytest.mark.parametrize(
    "data",
    [
        {"recipients": []},
        {"recipients": {"bad": {}}},
        {"recipients": {1: {}}},
        {"recipients": {"persistent": None}},
    ],
)
def test_malformed_storage_rejected(data):
    with pytest.raises(ValueError):
        decode_receipts(data)


async def test_reminder_store_corruption_preserved_and_no_care_reset(
    hass, hass_storage, freezer
):
    freezer.move_to("2026-06-15T10:00:00Z")
    entry = make_hub(hass)
    key = f"{storage_key(entry.entry_id)}.reminders"
    original = {
        "version": 1,
        "minor_version": 1,
        "data": {"recipients": {"persistent": {"broken": True}}},
    }
    hass_storage[key] = deepcopy(original)
    assert not await hass.config_entries.async_setup(entry.entry_id)
    assert hass_storage[key] == original
    assert (
        hass_storage[storage_key(entry.entry_id)]["data"]["plants"]["monstera"][
            "last_watered"
        ]
        == "2026-06-01"
    )
    with pytest.raises(NotImplementedError):
        await ReminderStore(hass, entry.entry_id)._async_migrate_func(0, 1, {})


async def test_diagnostics_do_not_export_notifier_ids_receipts_or_action_tokens(
    hass, freezer, reminder_hub
):
    from custom_components.plantbased.diagnostics import (
        async_get_config_entry_diagnostics,
    )

    entry, _, _ = reminder_hub
    await advance(hass, freezer, "2026-06-15T09:00:00Z")
    encoded = json.dumps(await async_get_config_entry_diagnostics(hass, entry))
    receipt = entry.runtime_data.reminders.receipts["service:mobile_app_phone"]
    assert receipt.token not in encoded
    assert "mobile_app_phone" not in encoded
