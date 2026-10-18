"""Exercise the real Home Assistant flow manager and entry lifecycle."""

from homeassistant.config_entries import SOURCE_USER, ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.plantbased.const import DOMAIN, NAME


async def test_confirm_hub_and_lifecycle(hass: HomeAssistant) -> None:
    """Setup waits for confirmation, loads, reloads, unloads, and removes."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    assert not hass.config_entries.async_entries(DOMAIN)

    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == NAME
    assert result["data"] == {}
    await hass.async_block_till_done()

    entry = result["result"]
    assert entry.unique_id == DOMAIN
    assert entry.version == 1
    assert entry.minor_version == 2
    assert entry.state is ConfigEntryState.LOADED
    assert await hass.config_entries.async_reload(entry.entry_id)
    assert entry.state is ConfigEntryState.LOADED
    assert await hass.config_entries.async_unload(entry.entry_id)
    assert entry.state is ConfigEntryState.NOT_LOADED
    assert await hass.config_entries.async_remove(entry.entry_id)
    assert not hass.config_entries.async_entries(DOMAIN)


async def test_single_hub(hass: HomeAssistant) -> None:
    """The manifest rejects a second hub, including legacy entries without IDs."""
    entry = MockConfigEntry(domain=DOMAIN, title=NAME, data={})
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "single_instance_allowed"


async def test_parallel_flows(hass: HomeAssistant) -> None:
    """Two pending dialogs cannot create duplicate hubs."""
    first = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    second = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert first["type"] is FlowResultType.FORM
    assert second["type"] is FlowResultType.ABORT
    assert second["reason"] == "already_in_progress"


async def test_entry_added_during_confirmation(hass: HomeAssistant) -> None:
    """A hub appearing after the form opened is not overwritten or duplicated."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    entry = MockConfigEntry(domain=DOMAIN, title=NAME, data={}, unique_id=DOMAIN)
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
    assert len(hass.config_entries.async_entries(DOMAIN)) == 1
