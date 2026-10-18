"""Public static paths and process-wide frontend module registration."""

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import TYPE_CHECKING

from homeassistant.components import frontend, panel_custom

if TYPE_CHECKING:
    from homeassistant.components.http.server import StaticPathConfig
else:
    from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant
from homeassistant.util.hass_dict import HassKey

from .const import IMAGE_PRESETS

ASSET_PATH = Path(__file__).parent / "frontend"
URL_PREFIX = "/plantbased"
PANEL_PATH = "plantbased-dashboard"


@dataclass(frozen=True, slots=True)
class FrontendAssets:
    version: str


ASSETS: HassKey[FrontendAssets] = HassKey("plantbased_frontend")


def _bundle_version() -> str:
    digest = sha256((ASSET_PATH / "plantbased.js").read_bytes())
    for path in sorted((ASSET_PATH / "illustrations").glob("*.svg")):
        digest.update(path.name.encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()[:16]


async def async_register_frontend(hass: HomeAssistant) -> None:
    """Register once per HA process; entry reloads never duplicate HTTP routes."""
    if ASSETS in hass.data:
        return
    version = await hass.async_add_executor_job(_bundle_version)
    await hass.http.async_register_static_paths(
        [StaticPathConfig(URL_PREFIX, str(ASSET_PATH), True)]
    )
    frontend.add_extra_js_url(hass, f"{URL_PREFIX}/plantbased.js?v={version}")
    hass.data[ASSETS] = FrontendAssets(version)


async def async_register_overview(hass: HomeAssistant) -> None:
    """Use HA's custom-panel API; keep the page separate from static asset URLs."""
    await panel_custom.async_register_panel(
        hass,
        frontend_url_path=PANEL_PATH,
        webcomponent_name="plantbased-panel",
        sidebar_title="PlantBased",
        sidebar_icon="mdi:sprout",
        module_url=f"{URL_PREFIX}/plantbased.js?v={hass.data[ASSETS].version}",
    )


def async_remove_overview(hass: HomeAssistant) -> None:
    """Remove only our own panel after a successful entry unload."""
    frontend.async_remove_panel(hass, PANEL_PATH)


def illustration_url(hass: HomeAssistant, preset: str) -> str:
    """Serve a local original preset with the bundle's browser-cache version."""
    name = preset if preset in IMAGE_PRESETS else "generic"
    version = hass.data[ASSETS].version
    return f"{URL_PREFIX}/illustrations/{name}.svg?v={version}"
