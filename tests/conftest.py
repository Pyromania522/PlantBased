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


@pytest.fixture
async def reminder_hub(hass, freezer):
    from copy import deepcopy

    from homeassistant.components import persistent_notification as pn
    from homeassistant.core import CoreState

    from .common import make_hub
    from .test_reminders import DEFAULTS, register_notifier

    freezer.move_to("2026-06-15T08:59:50Z")
    await hass.config.async_set_time_zone("UTC")
    received = register_notifier(hass)
    persistent = []
    pn.async_register_callback(
        hass, lambda kind, items: persistent.append((kind, deepcopy(items)))
    )
    entry = make_hub(hass)
    hass.config_entries.async_update_entry(entry, options=DEFAULTS)
    hass.set_state(CoreState.running)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry, received, persistent
