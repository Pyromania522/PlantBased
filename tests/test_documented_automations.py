"""Execute the documented YAML through HA's real automation engine."""

from datetime import date
from pathlib import Path

from homeassistant.components import persistent_notification as pn
from homeassistant.core import CoreState
from homeassistant.setup import async_setup_component
import yaml

from .common import device

EXAMPLES = Path(__file__).parents[1] / "docs/examples"


def example(name):
    return yaml.safe_load((EXAMPLES / name).read_text())


async def test_documented_due_and_done_automations_use_real_events(hass, plant_hub):
    notifications = {}

    def update(kind, items):
        if kind == pn.UpdateType.REMOVED:
            for key in items:
                notifications.pop(key, None)
        else:
            notifications.update(items)

    pn.async_register_callback(hass, update)
    hass.set_state(CoreState.running)
    assert await async_setup_component(
        hass,
        "automation",
        {
            "automation": [
                example("care_due_notification.yaml"),
                example("care_done_clear_notification.yaml"),
            ]
        },
    )
    await hass.async_block_till_done()
    assert await hass.config_entries.async_reload(plant_hub.entry_id)
    await hass.async_block_till_done()
    plant = device(hass, plant_hub, "monstera")
    water_id = f"plantbased_care_{plant.id}_water"
    fertilizer_id = f"plantbased_care_{plant.id}_fertilize"
    assert water_id in notifications
    assert fertilizer_id in notifications
    assert "Monstera" in notifications[water_id]["message"]
    assert "Watering" in notifications[water_id]["message"]
    assert "Fertilizing" in notifications[fertilizer_id]["message"]
    await hass.services.async_call(
        "plantbased", "mark_watered", {"device_id": plant.id}, blocking=True
    )
    await hass.async_block_till_done()
    assert water_id not in notifications
    assert fertilizer_id in notifications


async def test_documented_manual_group_action_changes_only_members(hass, plant_hub):
    config = example("mark_group_watered.yaml")
    config["actions"][0]["target"]["device_id"] = device(hass, plant_hub, "living").id
    assert await async_setup_component(hass, "automation", {"automation": [config]})
    await hass.async_block_till_done()
    entities = hass.states.async_entity_ids("automation")
    assert len(entities) == 1
    await hass.services.async_call(
        "automation", "trigger", {"entity_id": entities[0]}, blocking=True
    )
    await hass.async_block_till_done()
    assert plant_hub.runtime_data.plants["monstera"].last_watered == date(2026, 6, 15)
    assert plant_hub.runtime_data.plants["ficus"].last_watered == date(2026, 6, 14)
