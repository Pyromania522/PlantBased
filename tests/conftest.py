"""Home Assistant test fixtures."""

from collections.abc import Generator

import pytest

pytest_plugins = ["pytest_homeassistant_custom_component"]


@pytest.fixture(autouse=True)
def custom_integrations(enable_custom_integrations: None) -> Generator[None]:
    """Allow Home Assistant to discover this repository's integration."""
    yield


@pytest.fixture
async def plant_hub(hass, freezer):
    """A due and a current plant in separate groups on a frozen summer day."""
    from .common import make_hub

    freezer.move_to("2026-06-15T10:00:00+00:00")
    entry = make_hub(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry
