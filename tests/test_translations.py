"""Verify the confirmation dialog can be rendered in both languages."""

import json
from pathlib import Path

from homeassistant.core import HomeAssistant
from homeassistant.helpers.translation import async_get_translations
import pytest

from custom_components.plantbased.const import DOMAIN


@pytest.mark.parametrize(
    ("language", "title"),
    [("de", "PlantBased einrichten"), ("en", "Set up PlantBased")],
)
async def test_translated_dialog(
    hass: HomeAssistant, language: str, title: str
) -> None:
    """Load translations through HA, rather than only parsing JSON files."""
    translations = await async_get_translations(hass, language, "config", {DOMAIN})
    prefix = f"component.{DOMAIN}.config"
    assert translations[f"{prefix}.step.user.title"] == title
    assert translations[f"{prefix}.step.user.description"]
    assert translations[f"{prefix}.abort.already_configured"]


def test_translation_parity() -> None:
    """Custom translations ship expanded text and matching keys."""
    root = Path(__file__).parents[1] / "custom_components" / DOMAIN
    source = json.loads((root / "strings.json").read_text())
    english = json.loads((root / "translations/en.json").read_text())
    german = json.loads((root / "translations/de.json").read_text())
    assert source == english

    def keys(data: dict, prefix: str = "") -> set[str]:
        return {
            path
            for key, value in data.items()
            for path in (
                keys(value, f"{prefix}{key}.")
                if isinstance(value, dict)
                else {f"{prefix}{key}"}
            )
        }

    assert keys(english) == keys(german)


@pytest.mark.parametrize(
    ("language", "plant_label", "paused"),
    [("en", "Add plant", "Paused"), ("de", "Pflanze hinzufügen", "Pausiert")],
)
async def test_subentry_entity_and_selector_translations(
    hass, language, plant_label, paused
):
    subentries = await async_get_translations(
        hass, language, "config_subentries", {DOMAIN}
    )
    assert (
        subentries[f"component.{DOMAIN}.config_subentries.plant.initiate_flow.user"]
        == plant_label
    )
    entities = await async_get_translations(hass, language, "entity", {DOMAIN})
    assert (
        entities[f"component.{DOMAIN}.entity.sensor.care_status.state.paused"] == paused
    )
    selectors = await async_get_translations(hass, language, "selector", {DOMAIN})
    assert selectors[f"component.{DOMAIN}.selector.month.options.3"]
