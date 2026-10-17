"""Helpers that use HA registries and flow managers, without entity-name guesses."""

from types import MappingProxyType

from homeassistant.config_entries import ConfigSubentry
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.plantbased.const import DOMAIN


def subentry(kind, key, name, **data):
    return ConfigSubentry(
        data=MappingProxyType({"name": name, **data}),
        title=name,
        unique_id=None,
        subentry_id=key,
        subentry_type=kind,
    )


def make_hub(hass, *, with_plants=True):
    entry = MockConfigEntry(
        domain=DOMAIN, title="PlantBased", data={}, unique_id=DOMAIN
    )
    entry.add_to_hass(hass)
    if with_plants:
        for sub in [
            subentry("group", "living", "Living room"),
            subentry("group", "office", "Office"),
            subentry(
                "plant",
                "monstera",
                "Monstera",
                group="living",
                all_year=True,
                species="Monstera deliciosa",
                notes="Rotate weekly",
                image_url="/local/plants/monstera.png",
                image_preset="monstera",
                initial_last_watered="2026-06-01",
                initial_last_fertilized="2026-05-01",
            ),
            subentry(
                "plant",
                "ficus",
                "Ficus",
                group="office",
                all_year=True,
                initial_last_watered="2026-06-14",
                initial_last_fertilized="2026-06-14",
            ),
        ]:
            hass.config_entries.async_add_subentry(entry, sub)
    return entry


def entity_id(hass, target, key, platform="sensor"):
    result = er.async_get(hass).async_get_entity_id(platform, DOMAIN, f"{target}_{key}")
    assert result is not None, (platform, target, key)
    return result


def state(hass, target, key, platform="sensor"):
    result = hass.states.get(entity_id(hass, target, key, platform))
    assert result is not None
    return result


async def call(hass, target, key, platform="button", service="press", **data):
    await hass.services.async_call(
        platform,
        service,
        {"entity_id": entity_id(hass, target, key, platform), **data},
        blocking=True,
    )
    await hass.async_block_till_done()


def device(hass, entry, target):
    return next(
        (
            value
            for value in dr.async_entries_for_config_entry(
                dr.async_get(hass), entry.entry_id
            )
            if (DOMAIN, target) in value.identifiers
        ),
        None,
    )
