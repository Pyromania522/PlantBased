"""Create/reconfigure through HA's actual native subentry flow manager."""

from homeassistant.config_entries import SOURCE_RECONFIGURE, SOURCE_USER
from homeassistant.data_entry_flow import FlowResultType, InvalidData
from homeassistant.helpers import area_registry as ar
import pytest

from .common import device, make_hub, state
from .common import subentry as make_subentry


async def create(hass, entry, kind, data):
    initial = set(entry.subentries)
    result = await hass.config_entries.subentries.async_init(
        (entry.entry_id, kind), context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], data
    )
    await hass.async_block_till_done()
    if result["type"] is FlowResultType.CREATE_ENTRY:
        return result, entry.subentries[(set(entry.subentries) - initial).pop()]
    return result, None


async def test_add_group_and_plant_with_defaults(hass, freezer):
    freezer.move_to("2026-06-15T10:00:00Z")
    entry = make_hub(hass, with_plants=False)
    assert await hass.config_entries.async_setup(entry.entry_id)
    area = ar.async_get(hass).async_get_or_create("Kitchen")
    _result, group = await create(
        hass,
        entry,
        "group",
        {"name": "Kitchen plants", "area": area.id, "image_preset": "herb"},
    )
    assert group.subentry_type == "group"
    result, plant = await create(
        hass,
        entry,
        "plant",
        {"name": " Basil ", "group": group.subentry_id, "area": area.id},
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert plant.title == "Basil"
    assert plant.data["watering_interval"] == 7
    assert plant.data["fertilizing_interval"] == 28
    assert plant.data["season_start"] == 3 and plant.data["season_end"] == 9
    assert plant.data["initial_last_watered"] == "2026-06-15"
    assert state(hass, plant.subentry_id, "next_watering").state == "2026-06-22"
    assert device(hass, entry, plant.subentry_id).area_id == area.id
    assert (
        state(hass, plant.subentry_id, "care_status").attributes["group"]
        == "Kitchen plants"
    )


@pytest.mark.parametrize(
    ("data", "field", "error"),
    [
        ({"name": " "}, "name", "name_required"),
        ({"name": "Plant", "watering_interval": 0}, "base", "invalid_input"),
        ({"name": "Plant", "fertilizing_interval": 366}, "base", "invalid_input"),
        (
            {"name": "Plant", "watering_interval": 1.5},
            "watering_interval",
            "invalid_interval",
        ),
        ({"name": "Plant", "area": "deleted-area"}, "area", "invalid_area"),
        ({"name": "Plant", "group": "deleted-group"}, "base", "invalid_input"),
        (
            {"name": "Plant", "image_url": "javascript:alert(1)"},
            "image_url",
            "invalid_image",
        ),
        (
            {
                "name": "Plant",
                "image_url": "https://name:password@example.invalid/image.png",
            },
            "image_url",
            "invalid_image",
        ),
        (
            {"name": "Plant", "image_url": "https://[malformed/image.png"},
            "image_url",
            "invalid_image",
        ),
        (
            {"name": "Plant", "initial_last_watered": "2026-06-16"},
            "initial_last_watered",
            "future_date",
        ),
        (
            {"name": "Plant", "initial_last_fertilized": "2026-06-16"},
            "initial_last_fertilized",
            "future_date",
        ),
        (
            {"name": "Plant", "initial_last_watered": "2026-02-30"},
            "base",
            "invalid_input",
        ),
    ],
)
async def test_invalid_plant_input_does_not_create_subentry(
    hass, freezer, data, field, error
):
    freezer.move_to("2026-06-15T10:00:00Z")
    entry = make_hub(hass, with_plants=False)
    if field == "base":
        with pytest.raises(InvalidData):
            await create(hass, entry, "plant", data)
        assert not entry.subentries
        return
    result, plant = await create(hass, entry, "plant", data)
    assert result["type"] is FlowResultType.FORM
    assert result["errors"][field] == error
    assert plant is None and not entry.subentries


@pytest.mark.parametrize(
    "image",
    [
        "",
        "/local/plants/photo.png",
        "https://example.invalid/plant.png",
        "http://example.invalid/plant.png",
    ],
)
async def test_custom_image_metadata_is_not_downloaded(hass, freezer, image):
    freezer.move_to("2026-06-15T10:00:00Z")
    entry = make_hub(hass, with_plants=False)
    result, plant = await create(
        hass, entry, "plant", {"name": "Plant", "image_url": image}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert plant.data["image_url"] == image


async def test_reconfigure_preserves_ids_and_runtime(hass, plant_hub):
    entry = plant_hub
    manager = entry.runtime_data
    await manager.async_mark_done(["monstera"], "water")
    await manager.async_snooze("monstera", "fertilize", 2)
    await manager.async_pause("monstera", True)
    before = manager.plants["monstera"].to_data()
    area = ar.async_get(hass).async_get_or_create("Bedroom")
    result = await hass.config_entries.subentries.async_init(
        (entry.entry_id, "plant"),
        context={"source": SOURCE_RECONFIGURE, "subentry_id": "monstera"},
    )
    assert result["type"] is FlowResultType.FORM
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"],
        {
            "name": "Renamed",
            "group": "office",
            "area": area.id,
            "watering_interval": 12,
        },
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    await hass.async_block_till_done()
    assert entry.runtime_data is not manager
    assert entry.runtime_data.plants["monstera"].to_data() == before
    assert entry.subentries["monstera"].title == "Renamed"
    assert entry.runtime_data.configs["monstera"].notes == ""
    assert state(hass, "living", "total_plants").state == "0"
    assert state(hass, "office", "total_plants").state == "2"
    assert device(hass, entry, "monstera").area_id == area.id
    # Entity identity survives the name/group change; the old entity_id is reused.
    assert state(hass, "monstera", "care_status").attributes["group"] == "Office"


async def test_reconfigure_group_and_clear_area(hass, plant_hub):
    entry = plant_hub
    area = ar.async_get(hass).async_get_or_create("Kitchen")
    for area_id in (area.id, None):
        result = await hass.config_entries.subentries.async_init(
            (entry.entry_id, "group"),
            context={"source": SOURCE_RECONFIGURE, "subentry_id": "living"},
        )
        data = {"name": "New group"}
        if area_id:
            data["area"] = area_id
        result = await hass.config_entries.subentries.async_configure(
            result["flow_id"], data
        )
        assert result["type"] is FlowResultType.ABORT
        await hass.async_block_till_done()
        assert device(hass, entry, "living").area_id == area_id
        assert state(hass, "monstera", "care_status").attributes["group"] == "New group"


async def test_group_deleted_while_add_dialog_is_open(hass, freezer):
    freezer.move_to("2026-06-15T10:00:00Z")
    entry = make_hub(hass, with_plants=False)
    group = make_subentry("group", "temporary", "Temporary")
    hass.config_entries.async_add_subentry(entry, group)
    result = await hass.config_entries.subentries.async_init(
        (entry.entry_id, "plant"), context={"source": SOURCE_USER}
    )
    hass.config_entries.async_remove_subentry(entry, group.subentry_id)
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {"name": "Plant", "group": group.subentry_id}
    )
    assert result["errors"] == {"group": "invalid_group"}
    assert not entry.subentries


async def test_reconfigure_unloaded_subentry_without_a_registered_device(hass, freezer):
    freezer.move_to("2026-06-15T10:00:00Z")
    entry = make_hub(hass)
    area = ar.async_get(hass).async_get_or_create("New area")
    result = await hass.config_entries.subentries.async_init(
        (entry.entry_id, "plant"),
        context={"source": SOURCE_RECONFIGURE, "subentry_id": "monstera"},
    )
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {"name": "Unloaded", "area": area.id}
    )
    assert result["reason"] == "reconfigure_successful"
    assert entry.subentries["monstera"].data["area"] == area.id
