"""Compact automatic dashboards without disabling plant controls or history."""

from homeassistant.const import EntityCategory
from homeassistant.helpers import entity_registry as er

from custom_components.plantbased import async_migrate_entry
from custom_components.plantbased.const import DOMAIN

from .common import call, entity_id, make_hub, state


async def test_new_plants_have_three_primary_entities(hass, plant_hub):
    registry = er.async_get(hass)
    entries = er.async_entries_for_config_entry(registry, plant_hub.entry_id)
    for target in ("monstera", "ficus"):
        plant = [item for item in entries if item.config_subentry_id == target]
        assert len(plant) == 16
        assert not any(item.disabled for item in plant)
        assert {item.translation_key for item in plant if item.hidden} == {
            "needs_water",
            "needs_fertilizer",
            "mark_watered",
            "mark_fertilized",
            "snooze_watering",
            "snooze_fertilizing",
            "last_watered",
            "last_fertilized",
            "next_watering",
            "next_fertilizing",
        }
        assert {
            item.translation_key
            for item in plant
            if not item.hidden and item.entity_category is None
        } == {"care_status", "days_until_watering", "days_until_fertilizing"}
        assert all(hass.states.get(item.entity_id) for item in plant)
        assert all(
            item.entity_category is None
            or item.entity_category is EntityCategory.CONFIG
            for item in plant
        )
    assert not any(
        item.hidden
        for item in entries
        if item.config_subentry_id not in {"monstera", "ficus"}
    )
    assert state(hass, "monstera", "care_status").attributes["icon"] == "mdi:sprout"
    await call(hass, "monstera", "mark_watered")
    assert state(hass, "monstera", "last_watered", "date").state == "2026-06-15"
    assert state(hass, "monstera", "care_status").state == "fertilize"


async def test_upgrade_compacts_existing_registry_once(hass, freezer):
    freezer.move_to("2026-06-15T10:00:00Z")
    entry = make_hub(hass)
    assert entry.minor_version == 1
    registry = er.async_get(hass)
    auxiliary = registry.async_get_or_create(
        "button",
        DOMAIN,
        "monstera_mark_watered",
        config_entry=entry,
        config_subentry_id="monstera",
        translation_key="mark_watered",
        suggested_object_id="my_renamed_water_button",
    )
    user_hidden = registry.async_get_or_create(
        "sensor",
        DOMAIN,
        "monstera_care_status",
        config_entry=entry,
        config_subentry_id="monstera",
        translation_key="care_status",
        hidden_by=er.RegistryEntryHider.USER,
    )
    user_hidden_auxiliary = registry.async_get_or_create(
        "date",
        DOMAIN,
        "monstera_last_watered",
        config_entry=entry,
        config_subentry_id="monstera",
        translation_key="last_watered",
        hidden_by=er.RegistryEntryHider.USER,
    )
    # Unrelated entities, including group actions, are outside this migration.
    group = registry.async_get_or_create(
        "button",
        DOMAIN,
        "living_mark_all_watered",
        config_entry=entry,
        config_subentry_id="living",
        translation_key="mark_all_watered",
    )
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.minor_version == 2
    assert (
        registry.async_get(auxiliary.entity_id).hidden_by
        is er.RegistryEntryHider.INTEGRATION
    )
    assert (
        registry.async_get(user_hidden.entity_id).hidden_by
        is er.RegistryEntryHider.USER
    )
    assert (
        registry.async_get(user_hidden_auxiliary.entity_id).hidden_by
        is er.RegistryEntryHider.USER
    )
    assert registry.async_get(group.entity_id).hidden_by is None
    assert entity_id(hass, "monstera", "mark_watered", "button") == auxiliary.entity_id
    await call(hass, "monstera", "mark_watered")
    before = entry.runtime_data.plants["monstera"].to_data()

    registry.async_update_entity(auxiliary.entity_id, hidden_by=None)
    assert await hass.config_entries.async_reload(entry.entry_id)
    assert registry.async_get(auxiliary.entity_id).hidden_by is None
    assert entry.runtime_data.plants["monstera"].to_data() == before
    assert await async_migrate_entry(hass, entry)
    assert registry.async_get(auxiliary.entity_id).hidden_by is None


async def test_new_entity_visibility_and_disabled_choices_survive_reload(
    hass, plant_hub
):
    registry = er.async_get(hass)
    auxiliary = entity_id(hass, "ficus", "next_watering")
    disabled = entity_id(hass, "ficus", "last_fertilized", "date")
    registry.async_update_entity(auxiliary, hidden_by=None)
    registry.async_update_entity(disabled, disabled_by=er.RegistryEntryDisabler.USER)
    assert await hass.config_entries.async_reload(plant_hub.entry_id)
    assert registry.async_get(auxiliary).hidden_by is None
    assert registry.async_get(disabled).disabled_by is er.RegistryEntryDisabler.USER
    assert hass.states.get(disabled) is None


async def test_future_major_entry_is_not_migrated(hass):
    entry = make_hub(hass, with_plants=False)
    hass.config_entries.async_update_entry(entry, version=2)
    assert not await async_migrate_entry(hass, entry)
    assert entry.version == 2
