"""Group-area inheritance, native registry changes and saved own-area fallbacks."""

from datetime import date

from homeassistant.config_entries import SOURCE_RECONFIGURE
from homeassistant.helpers import area_registry as ar
from homeassistant.helpers import device_registry as dr
import pytest

from .common import device, make_hub, state, subentry
from .test_subentries import create


async def edit(hass, entry, kind, key, data):
    flow = await hass.config_entries.subentries.async_init(
        (entry.entry_id, kind),
        context={"source": SOURCE_RECONFIGURE, "subentry_id": key},
    )
    result = await hass.config_entries.subentries.async_configure(flow["flow_id"], data)
    assert result["reason"] == "reconfigure_successful"
    await hass.async_block_till_done()


@pytest.fixture
async def area_hub(hass, freezer):
    freezer.move_to("2026-06-15T10:00:00Z")
    areas = ar.async_get(hass)
    parent = areas.async_create("Living room")
    own = areas.async_create("Bedroom")
    other = areas.async_create("Kitchen")
    entry = make_hub(hass, with_plants=False)
    # Plants may precede their groups in config-subentry insertion order.
    for item in [
        subentry("plant", "monstera", "Monstera", group="living", area=own.id),
        subentry("plant", "fern", "Fern", group="living"),
        subentry("plant", "solo", "Solo", area=other.id),
        subentry("group", "living", "Living plants", area=parent.id),
        subentry("group", "empty_area", "Flexible group"),
    ]:
        hass.config_entries.async_add_subentry(entry, item)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry, parent, own, other


async def test_setup_inherits_group_area_and_keeps_saved_fallback(hass, area_hub):
    entry, parent, own, other = area_hub
    assert device(hass, entry, "monstera").area_id == parent.id
    assert device(hass, entry, "fern").area_id == parent.id
    assert device(hass, entry, "solo").area_id == other.id
    assert entry.subentries["monstera"].data["area"] == own.id
    assert entry.subentries["fern"].data.get("area") is None
    before = entry.runtime_data.plants["monstera"].to_data()
    assert await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    assert device(hass, entry, "monstera").area_id == parent.id
    assert entry.subentries["monstera"].data["area"] == own.id
    assert entry.runtime_data.plants["monstera"].to_data() == before


async def test_new_plant_own_area_cannot_override_a_group_area(hass, area_hub):
    entry, parent, own, _other = area_hub
    _result, plant = await create(
        hass, entry, "plant", {"name": "Basil", "group": "living", "area": own.id}
    )
    assert device(hass, entry, plant.subentry_id).area_id == parent.id
    assert plant.data["area"] == own.id


async def test_edit_own_fallback_during_inheritance_keeps_group_area(hass, area_hub):
    entry, parent, _own, other = area_hub
    await edit(
        hass,
        entry,
        "plant",
        "monstera",
        {"name": "Monstera", "group": "living", "area": other.id},
    )
    assert device(hass, entry, "monstera").area_id == parent.id
    assert entry.subentries["monstera"].data["area"] == other.id
    await edit(hass, entry, "group", "living", {"name": "Living plants"})
    assert device(hass, entry, "monstera").area_id == other.id


async def test_change_to_another_group_adopts_its_area(hass, area_hub):
    entry, _parent, own, other = area_hub
    await edit(
        hass,
        entry,
        "group",
        "empty_area",
        {"name": "Flexible group", "area": other.id},
    )
    await edit(
        hass,
        entry,
        "plant",
        "monstera",
        {"name": "Monstera", "group": "empty_area", "area": own.id},
    )
    assert device(hass, entry, "monstera").area_id == other.id
    assert entry.subentries["monstera"].data["area"] == own.id


async def test_clear_group_area_restores_individual_fallbacks(hass, area_hub):
    entry, _parent, own, other = area_hub
    before = entry.runtime_data.plants["monstera"].to_data()
    await edit(hass, entry, "group", "living", {"name": "Living plants"})
    assert device(hass, entry, "living").area_id is None
    assert device(hass, entry, "monstera").area_id == own.id
    assert device(hass, entry, "fern").area_id is None
    assert device(hass, entry, "solo").area_id == other.id
    assert entry.runtime_data.plants["monstera"].to_data() == before


@pytest.mark.parametrize("new_group", ["none", "empty_area"])
async def test_leave_group_or_move_to_area_less_group_restores_own_area(
    hass, area_hub, new_group
):
    entry, _parent, own, _other = area_hub
    plant_id = device(hass, entry, "monstera").id
    await edit(
        hass,
        entry,
        "plant",
        "monstera",
        {"name": "Monstera", "group": new_group, "area": own.id},
    )
    assert device(hass, entry, "monstera").area_id == own.id
    assert device(hass, entry, "monstera").id == plant_id
    assert entry.runtime_data.plants["monstera"].last_watered == date(2026, 6, 15)


async def test_delete_group_unassigns_and_restores_saved_own_area(hass, area_hub):
    entry, _parent, own, _other = area_hub
    hass.config_entries.async_remove_subentry(entry, "living")
    await hass.async_block_till_done()
    assert entry.subentries["monstera"].data["group"] is None
    assert device(hass, entry, "monstera").area_id == own.id
    assert device(hass, entry, "fern").area_id is None
    assert state(hass, "monstera", "care_status").attributes["group"] is None


async def test_native_group_area_edits_follow_and_clear_without_erasing_fallback(
    hass, area_hub
):
    entry, _parent, own, other = area_hub
    registry = dr.async_get(hass)
    registry.async_update_device(device(hass, entry, "living").id, area_id=other.id)
    await hass.async_block_till_done()
    assert device(hass, entry, "monstera").area_id == other.id
    assert device(hass, entry, "fern").area_id == other.id
    assert entry.subentries["monstera"].data["area"] == own.id
    registry.async_update_device(device(hass, entry, "living").id, area_id=None)
    await hass.async_block_till_done()
    assert device(hass, entry, "monstera").area_id == own.id
    assert device(hass, entry, "fern").area_id is None


async def test_native_conflicting_member_area_is_corrected_without_losing_fallback(
    hass, area_hub
):
    entry, parent, own, other = area_hub
    registry = dr.async_get(hass)
    registry.async_update_device(device(hass, entry, "monstera").id, area_id=other.id)
    await hass.async_block_till_done()
    assert device(hass, entry, "monstera").area_id == parent.id
    assert entry.subentries["monstera"].data["area"] == own.id


async def test_area_less_group_preserves_native_own_area_before_inheriting(
    hass, area_hub
):
    entry, _parent, own, other = area_hub
    await edit(
        hass,
        entry,
        "plant",
        "solo",
        {"name": "Solo", "group": "empty_area", "area": other.id},
    )
    registry = dr.async_get(hass)
    registry.async_update_device(device(hass, entry, "solo").id, area_id=own.id)
    await hass.async_block_till_done()
    assert entry.subentries["solo"].data["area"] == own.id
    await edit(
        hass, entry, "group", "empty_area", {"name": "Flexible group", "area": other.id}
    )
    assert device(hass, entry, "solo").area_id == other.id
    assert entry.subentries["solo"].data["area"] == own.id
    await edit(hass, entry, "group", "empty_area", {"name": "Flexible group"})
    assert device(hass, entry, "solo").area_id == own.id


async def test_deleted_parent_area_restores_valid_own_area(hass, area_hub):
    entry, parent, own, _other = area_hub
    ar.async_get(hass).async_delete(parent.id)
    await hass.async_block_till_done()
    assert device(hass, entry, "living").area_id is None
    assert device(hass, entry, "monstera").area_id == own.id
    assert device(hass, entry, "fern").area_id is None
    assert entry.subentries["monstera"].data["area"] == own.id


async def test_removed_fallback_area_is_not_restored(hass, area_hub):
    entry, parent, own, _other = area_hub
    ar.async_get(hass).async_delete(own.id)
    await hass.async_block_till_done()
    assert device(hass, entry, "monstera").area_id == parent.id
    await edit(hass, entry, "group", "living", {"name": "Living plants"})
    assert device(hass, entry, "monstera").area_id is None


async def test_registry_listener_is_removed_on_unload(hass, area_hub):
    entry, _parent, own, other = area_hub
    assert await hass.config_entries.async_unload(entry.entry_id)
    registry = dr.async_get(hass)
    registry.async_update_device(device(hass, entry, "living").id, area_id=other.id)
    await hass.async_block_till_done()
    assert device(hass, entry, "monstera").area_id != other.id
    assert entry.subentries["monstera"].data["area"] == own.id
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert device(hass, entry, "monstera").area_id == other.id
    assert entry.subentries["monstera"].data["area"] == own.id


async def test_standalone_native_area_change_survives_reload(hass, area_hub):
    entry, _parent, own, _other = area_hub
    dr.async_get(hass).async_update_device(
        device(hass, entry, "solo").id, area_id=own.id
    )
    await hass.async_block_till_done()
    assert entry.subentries["solo"].data["area"] == own.id
    assert await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    assert device(hass, entry, "solo").area_id == own.id
