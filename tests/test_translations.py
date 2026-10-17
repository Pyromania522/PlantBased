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
