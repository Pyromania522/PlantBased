"""Real HTTP assets, public frontend registration and registry metadata."""

from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree as ET

from homeassistant.components import frontend

from custom_components.plantbased.const import DOMAIN, IMAGE_PRESETS
from custom_components.plantbased.web import (
    ASSET_PATH,
    ASSETS,
    async_register_frontend,
    illustration_url,
)

from .common import state


def extra_modules(hass):
    urls = hass.data[frontend.DATA_EXTRA_MODULE_URL]
    return urls.urls if hasattr(urls, "urls") else urls


async def test_automatic_module_and_reload_register_once(hass, plant_hub):
    expected = f"/plantbased/plantbased.js?v={hass.data[ASSETS].version}"
    assert expected in extra_modules(hass)
    assert len([url for url in extra_modules(hass) if "/plantbased/" in url]) == 1
    await async_register_frontend(hass)
    assert await hass.config_entries.async_reload(plant_hub.entry_id)
    await hass.async_block_till_done()
    assert len([url for url in extra_modules(hass) if "/plantbased/" in url]) == 1
    assert await hass.config_entries.async_remove(plant_hub.entry_id)
    assert expected in extra_modules(
        hass
    )  # The process-wide resource has no care data.


async def test_real_static_http_js_svg_and_frontend_bootstrap(
    hass, plant_hub, aiohttp_client, socket_enabled
):
    # Avoid aiohttp access-log time formatting against freezegun struct_time.
    client = await aiohttp_client(hass.http.app, server_kwargs={"access_log": None})
    version = hass.data[ASSETS].version
    response = await client.get(f"/plantbased/plantbased.js?v={version}")
    assert response.status == 200
    assert "javascript" in response.headers["Content-Type"]
    body = await response.text()
    assert "plantbased-overview-card" in body
    for preset in IMAGE_PRESETS:
        response = await client.get(illustration_url(hass, preset))
        assert response.status == 200
        assert "image/svg+xml" in response.headers["Content-Type"]
        assert (await response.text()).startswith("<svg")
    with patch(
        "homeassistant.components.onboarding.async_is_onboarded", return_value=True
    ):
        response = await client.get("/")
        assert response.status == 200
        assert f"/plantbased/plantbased.js?v={version}" in await response.text()
    assert "generic.svg" in illustration_url(hass, "not-a-preset")


async def test_native_registry_lists_expose_stable_card_identity(
    hass, plant_hub, hass_ws_client
):
    client = await hass_ws_client(hass)
    for message_id, command in [
        (1, "config/entity_registry/list"),
        (2, "config/device_registry/list"),
    ]:
        await client.send_json({"id": message_id, "type": command})
        result = await client.receive_json()
        assert result["success"]
        if message_id == 1:
            entities = result["result"]
        else:
            devices = result["result"]
    owned = [entity for entity in entities if entity["platform"] == DOMAIN]
    care = next(
        entity for entity in owned if entity["unique_id"] == "monstera_care_status"
    )
    assert care["config_subentry_id"] == "monstera"
    assert care["translation_key"] == "care_status"
    device = next(device for device in devices if device["id"] == care["device_id"])
    assert device["model"] == "Plant"
    assert [DOMAIN, "monstera"] in device["identifiers"]
    assert (
        "generic.svg?v=" in state(hass, "ficus", "care_status").attributes["image_url"]
    )
    assert state(hass, "ficus", "care_status").attributes["fertilizing_enabled"] is True


def test_original_svg_presets_and_built_bundle_are_shipped():
    root = Path(__file__).parents[1]
    assert 8 <= len(IMAGE_PRESETS) <= 12
    hashes = set()
    for name in IMAGE_PRESETS:
        source = root / "frontend/public/illustrations" / f"{name}.svg"
        shipped = ASSET_PATH / "illustrations" / f"{name}.svg"
        assert source.read_bytes() == shipped.read_bytes()
        hashes.add(sha256(shipped.read_bytes()).hexdigest())
        svg = ET.fromstring(shipped.read_text())
        assert svg.attrib["viewBox"] == "0 0 144 160"
        assert not any(
            node.tag.endswith(("script", "image", "foreignObject"))
            for node in svg.iter()
        )
        assert "http" not in shipped.read_text().removeprefix(
            '<svg xmlns="http://www.w3.org/2000/svg"'
        )
    assert len(hashes) == len(IMAGE_PRESETS)
    assert (ASSET_PATH / "plantbased.js").stat().st_size < 100_000
    assert (ASSET_PATH / "THIRD_PARTY_LICENSES.md").is_file()
