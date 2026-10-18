"""Validated reminder options and public service/entity discovery."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import time
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.selector import SelectOptionDict


@dataclass(frozen=True, slots=True)
class ReminderOptions:
    enabled: bool = False
    at: time = time(9)
    targets: tuple[str, ...] = ()
    repeat: bool = True
    persistent: bool = False
    snooze: bool = True

    @classmethod
    def from_data(cls, data: Mapping[str, Any]) -> ReminderOptions:
        return cls(
            enabled=data.get("reminder_enabled", False),
            at=time.fromisoformat(data.get("reminder_time", "09:00:00")).replace(
                microsecond=0
            ),
            targets=tuple(dict.fromkeys(data.get("notify_targets", []))),
            repeat=data.get("repeat_daily", True),
            persistent=data.get("persistent_notification", False),
            snooze=data.get("snooze_action", True),
        )


def available_targets(hass: HomeAssistant) -> list[SelectOptionDict]:
    """Never access a notifier's private credentials or integration runtime."""
    options: list[SelectOptionDict] = [
        {"value": f"service:{name}", "label": f"notify.{name}"}
        for name in sorted(hass.services.async_services().get("notify", {}))
        if name not in {"send_message", "persistent_notification", "reload"}
    ]
    registry = er.async_get(hass)
    if hass.services.has_service("notify", "send_message"):
        for state in sorted(
            hass.states.async_all("notify"), key=lambda state: state.entity_id
        ):
            registered = registry.async_get(state.entity_id)
            if state.state == "unavailable" or (
                registered is not None and registered.platform == "mobile_app"
            ):
                continue
            options.append({"value": f"entity:{state.entity_id}", "label": state.name})
    return options
