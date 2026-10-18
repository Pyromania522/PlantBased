"""Private, versioned reminder receipts, separate from the plant-care store."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
import re
from typing import Any

from homeassistant.core import HomeAssistant

from .storage import VerifiedStore, storage_key


def is_task_uid(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parts = value.split(":")
    if len(parts) != 3 or not parts[0] or parts[1] not in ("water", "fertilize"):
        return False
    try:
        date.fromisoformat(parts[2])
    except ValueError:
        return False
    return True


@dataclass(slots=True)
class Receipt:
    day: date | None = None
    seen: set[str] = field(default_factory=set)
    active: set[str] = field(default_factory=set)
    token: str = ""
    text: str = ""

    def to_data(self) -> dict[str, Any]:
        return {
            "day": self.day.isoformat() if self.day else None,
            "seen": sorted(self.seen),
            "active": sorted(self.active),
            "token": self.token,
            "text": self.text,
        }

    @classmethod
    def from_data(cls, data: Any) -> Receipt:
        if not isinstance(data, dict):
            raise ValueError("Invalid reminder receipt")
        for key in ("seen", "active"):
            if not isinstance(data.get(key), list) or not all(
                is_task_uid(uid) for uid in data[key]
            ):
                raise ValueError("Invalid reminder tasks")
        token = data.get("token")
        if not isinstance(token, str) or (
            token and re.fullmatch(r"[0-9a-f]{32}", token) is None
        ):
            raise ValueError("Invalid reminder action ID")
        if not isinstance(data.get("text"), str):
            raise ValueError("Invalid reminder text")
        return cls(
            date.fromisoformat(data["day"]) if data.get("day") is not None else None,
            set(data["seen"]),
            set(data["active"]),
            token,
            data["text"],
        )


class ReminderStore(VerifiedStore):
    def __init__(self, hass: HomeAssistant, entry_id: str) -> None:
        super().__init__(
            hass,
            1,
            f"{storage_key(entry_id)}.reminders",
            atomic_writes=True,
            private=True,
        )

    async def _async_migrate_func(
        self, old_major_version: int, old_minor_version: int, old_data: dict[str, Any]
    ) -> dict[str, Any]:
        # No earlier reminder format exists. Never interpret a care store as one.
        raise NotImplementedError


def decode_receipts(data: dict[str, Any] | None) -> dict[str, Receipt]:
    if data is None:
        return {}
    records = data.get("recipients")
    if not isinstance(records, dict) or any(
        not isinstance(key, str)
        or not (key == "persistent" or key.startswith(("service:", "entity:notify.")))
        for key in records
    ):
        raise ValueError("Invalid reminder recipients")
    return {key: Receipt.from_data(value) for key, value in records.items()}
