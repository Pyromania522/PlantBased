"""The overview uses HA's real authenticated config-subentry flow endpoints."""

from homeassistant.helpers import area_registry as ar
import pytest

from .common import device

BASE = "/api/config/config_entries/subentries/flow"


@pytest.mark.parametrize("kind", ["plant", "group"])
async def test_native_http_create_from_panel(hass, plant_hub, hass_client, kind):
    client = await hass_client()
    before = plant_hub.runtime_data.plants["monstera"].to_data()
    area = ar.async_get(hass).async_create("Balcony")
    response = await client.post(BASE, json={"handler": [plant_hub.entry_id, kind]})
    assert response.status == 200
    step = await response.json()
    assert step["type"] == "form"
    assert all(
        set(field["selector"])
        <= {"text", "area", "number", "boolean", "date", "select"}
        for field in step["data_schema"]
    )
    data = {
        field["name"]: field["description"]["suggested_value"]
        if "suggested_value" in field.get("description", {})
        else field["default"]
        for field in step["data_schema"]
        if "suggested_value" in field.get("description", {}) or "default" in field
    }
    data.update(name="New from overview", area=area.id)
    if kind == "plant":
        assert data["initial_last_watered"] == "2026-06-15"
        assert data["adaptive_watering"] is False
        data.update(
            group="none",
            watering_interval=12,
            fertilizing_enabled=False,
            adaptive_watering=True,
        )
    url = f"{BASE}/{step['flow_id']}"
    response = await client.post(url, json=data)
    assert response.status == 200
    assert (await response.json())["type"] == "create_entry"
    await hass.async_block_till_done()
    added = [sub for sub in plant_hub.subentries.values() if sub.title == data["name"]]
    assert len(added) == 1
    sub = added[0]
    assert sub.subentry_type == kind
    assert device(hass, plant_hub, sub.subentry_id).area_id == area.id
    if kind == "plant":
        assert sub.data["group"] is None
        assert sub.data["watering_interval"] == 12
        assert sub.data["fertilizing_enabled"] is False
        assert plant_hub.runtime_data.configs[sub.subentry_id].adaptive_watering is True
    assert plant_hub.runtime_data.plants["monstera"].to_data() == before
    # A retry of a completed flow cannot create a duplicate plant/group.
    response = await client.post(url, json=data)
    assert response.status == 404


async def test_native_http_cancel_and_validation(hass, plant_hub, hass_client):
    client = await hass_client()
    count = len(plant_hub.subentries)
    response = await client.post(BASE, json={"handler": [plant_hub.entry_id, "group"]})
    step = await response.json()
    url = f"{BASE}/{step['flow_id']}"
    response = await client.post(url, json={"name": "   "})
    assert response.status == 200
    assert (await response.json())["errors"]["name"] == "name_required"
    response = await client.delete(url)
    assert response.status == 200
    response = await client.get(url)
    assert response.status == 404
    assert len(plant_hub.subentries) == count


async def test_native_http_creation_requires_admin(
    hass, plant_hub, hass_client, hass_read_only_access_token
):
    client = await hass_client(hass_read_only_access_token)
    response = await client.post(BASE, json={"handler": [plant_hub.entry_id, "plant"]})
    assert response.status == 401
    assert len(plant_hub.subentries) == 4
