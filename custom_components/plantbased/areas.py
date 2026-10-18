"""Keep group areas and member device areas consistent without losing fallbacks."""

from asyncio import Handle
from collections.abc import Callable, Mapping
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers import area_registry as ar
from homeassistant.helpers import device_registry as dr

from .registry import device_for_subentry


def valid_area(hass: HomeAssistant, value: Any) -> str | None:
    """Never assign an area which has been removed from HA."""
    return (
        value
        if isinstance(value, str) and ar.async_get(hass).async_get_area(value)
        else None
    )


def inherited_area(
    hass: HomeAssistant, entry: ConfigEntry, data: Mapping[str, Any]
) -> str | None:
    """A registered group device is authoritative, including an unset area."""
    group_id = data.get("group")
    if not group_id or not (group := entry.subentries.get(group_id)):
        return None
    if group.subentry_type != "group":
        return None
    if device := device_for_subentry(hass, entry.entry_id, group_id):
        return valid_area(hass, device.area_id)
    return valid_area(hass, group.data.get("area"))


def plant_area(
    hass: HomeAssistant, entry: ConfigEntry, data: Mapping[str, Any]
) -> str | None:
    """The plant's own saved area is a fallback for absent group areas."""
    return inherited_area(hass, entry, data) or valid_area(hass, data.get("area"))


@callback
def _set_area(
    hass: HomeAssistant, entry: ConfigEntry, key: str, area: str | None
) -> None:
    if (
        device := device_for_subentry(hass, entry.entry_id, key)
    ) and device.area_id != area:
        dr.async_get(hass).async_update_device(device.id, area_id=area)


@callback
def _save_area(
    hass: HomeAssistant, entry: ConfigEntry, key: str, area: str | None
) -> None:
    subentry = entry.subentries[key]
    if subentry.data.get("area") != area:
        hass.config_entries.async_update_subentry(
            entry, subentry, data={**subentry.data, "area": area}
        )


@callback
def async_sync_group_area(
    hass: HomeAssistant,
    entry: ConfigEntry,
    key: str,
    area: str | None,
    *,
    save_group: bool = True,
) -> None:
    area = valid_area(hass, area)
    group = entry.subentries[key]
    members = [
        plant_id
        for plant_id, plant in entry.subentries.items()
        if plant.subentry_type == "plant" and plant.data.get("group") == key
    ]
    # Before an area-less group gains an area, preserve each current own area.
    # This also respects native HA device-area edits made while unloaded.
    if not group.data.get("area"):
        for plant_id in members:
            if device := device_for_subentry(hass, entry.entry_id, plant_id):
                _save_area(hass, entry, plant_id, valid_area(hass, device.area_id))
    if save_group:
        _save_area(hass, entry, key, area)
    for plant_id in members:
        own = valid_area(hass, entry.subentries[plant_id].data.get("area"))
        _set_area(hass, entry, plant_id, area or own)


@callback
def async_change_group_area(
    hass: HomeAssistant, entry: ConfigEntry, key: str, area: str | None
) -> None:
    """Apply form changes before saving the group, even with an unloaded hub."""
    area = valid_area(hass, area)
    _set_area(hass, entry, key, area)
    async_sync_group_area(hass, entry, key, area, save_group=False)


class AreaCoordinator:
    """Synchronize public registry changes; all listeners belong to the entry."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self._active = False
        self._unsubscribe: Callable[[], None] | None = None
        self._pending: set[str] = set()
        self._scheduled: Handle | None = None
        self.devices = {
            device.id: key
            for key in entry.subentries
            if (device := device_for_subentry(hass, entry.entry_id, key))
        }

    @callback
    def async_start(self, orphaned_plants: set[str]) -> None:
        """Restore fallbacks and enforce inheritance after every setup/reload."""
        for key in orphaned_plants:
            _set_area(
                self.hass,
                self.entry,
                key,
                valid_area(self.hass, self.entry.subentries[key].data.get("area")),
            )
        for key, group in list(self.entry.subentries.items()):
            if group.subentry_type != "group":
                continue
            device = device_for_subentry(self.hass, self.entry.entry_id, key)
            if device:
                async_sync_group_area(
                    self.hass, self.entry, key, valid_area(self.hass, device.area_id)
                )
        self._active = True
        self._unsubscribe = self.hass.bus.async_listen(
            dr.EVENT_DEVICE_REGISTRY_UPDATED, self._async_registry_updated
        )
        self.entry.async_on_unload(self.async_stop)

    @callback
    def async_stop(self) -> None:
        """Ignore queued events belonging to an unloaded entry."""
        self._active = False
        if self._scheduled:
            self._scheduled.cancel()
            self._scheduled = None
        self._pending.clear()
        if self._unsubscribe:
            self._unsubscribe()
            self._unsubscribe = None

    @callback
    def _async_registry_updated(
        self, event: Event[dr.EventDeviceRegistryUpdatedData]
    ) -> None:
        if (
            not self._active
            or event.data["action"] != "update"
            or "area_id" not in event.data["changes"]
        ):
            return
        key = self.devices.get(event.data["device_id"])
        if not key:
            return
        self._pending.add(key)
        if self._scheduled is None:
            self._scheduled = self.hass.loop.call_soon(self._async_process_pending)

    @callback
    def _async_process_pending(self) -> None:
        """Process a registry transaction together, with parent changes first.

        HA may still clear member areas while deleting an area. Waiting until
        that synchronous transaction finishes prevents it undoing restoration.
        """
        self._scheduled = None
        if not self._active:
            return
        pending, self._pending = self._pending, set()
        for key in sorted(
            pending,
            key=lambda item: (
                self.entry.subentries[item].subentry_type != "group"
                if item in self.entry.subentries
                else True
            ),
        ):
            self._async_process_device_area(key)

    @callback
    def _async_process_device_area(self, key: str) -> None:
        if not (subentry := self.entry.subentries.get(key)):
            return
        device = device_for_subentry(self.hass, self.entry.entry_id, key)
        if not device:
            return
        if subentry.subentry_type == "group":
            async_sync_group_area(
                self.hass, self.entry, key, valid_area(self.hass, device.area_id)
            )
            return
        group_id = subentry.data.get("group")
        if group_id and (group := self.entry.subentries.get(group_id)):
            group_device = device_for_subentry(self.hass, self.entry.entry_id, group_id)
            # Area deletion may dispatch a member update before the group update.
            if group_device and group.data.get("area") != group_device.area_id:
                async_sync_group_area(
                    self.hass,
                    self.entry,
                    group_id,
                    valid_area(self.hass, group_device.area_id),
                )
        if area := inherited_area(self.hass, self.entry, subentry.data):
            _set_area(self.hass, self.entry, key, area)
        else:
            current = device_for_subentry(self.hass, self.entry.entry_id, key)
            if current:
                _save_area(
                    self.hass, self.entry, key, valid_area(self.hass, current.area_id)
                )
