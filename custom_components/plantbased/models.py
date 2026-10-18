"""Configuration and persisted runtime state, independent of entity platforms."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Literal

from .const import HISTORY_LIMIT
from .learning import WateringLearning

type CareType = Literal["water", "fertilize"]


@dataclass(frozen=True, slots=True)
class PlantConfig:
    """A plant's configuration belongs to its config subentry."""

    name: str
    group: str | None = None
    area: str | None = None
    species: str = ""
    notes: str = ""
    location_note: str = ""
    image_preset: str = "generic"
    image_url: str = ""
    watering_interval: int = 7
    adaptive_watering: bool = False
    learning_revision: int = 0
    fertilizing_enabled: bool = True
    fertilizing_interval: int = 28
    all_year: bool = False
    season_start: int = 3
    season_end: int = 9

    @classmethod
    def from_data(cls, data: Mapping[str, Any]) -> PlantConfig:
        """Read the validated fields, excluding creation-only seed dates."""
        return cls(
            **{
                key: value
                for key, value in data.items()
                if key in cls.__dataclass_fields__
            }
        )


@dataclass(slots=True)
class PlantState:
    """Runtime dates, snoozes, pause and bounded care histories."""

    last_watered: date
    last_fertilized: date
    watering_snooze: int = 0
    fertilizing_snooze: int = 0
    paused: bool = False
    watering_history: list[date] = field(default_factory=list)
    fertilizing_history: list[date] = field(default_factory=list)
    watering_learning: WateringLearning = field(default_factory=WateringLearning)

    @classmethod
    def initial(cls, data: Mapping[str, Any], today: date) -> PlantState:
        """Seed a new plant once; reconfiguration never resets runtime dates."""
        watered = date.fromisoformat(
            data.get("initial_last_watered", today.isoformat())
        )
        fertilized = date.fromisoformat(
            data.get("initial_last_fertilized", today.isoformat())
        )
        return cls(
            watered,
            fertilized,
            watering_history=[watered],
            fertilizing_history=[fertilized],
        )

    @classmethod
    def from_data(cls, data: Mapping[str, Any]) -> PlantState:
        """Load versioned storage and reject malformed data without resetting it."""
        watered = date.fromisoformat(data["last_watered"])
        fertilized = date.fromisoformat(data["last_fertilized"])
        snoozes = [data.get("watering_snooze", 0), data.get("fertilizing_snooze", 0)]
        if any(type(value) is not int or value < 0 for value in snoozes):
            raise ValueError("Invalid stored snooze")
        paused = data.get("paused", False)
        if not isinstance(paused, bool):
            raise ValueError("Invalid stored pause")
        return cls(
            watered,
            fertilized,
            watering_snooze=snoozes[0],
            fertilizing_snooze=snoozes[1],
            paused=paused,
            watering_history=[
                date.fromisoformat(value)
                for value in data.get("watering_history", [watered.isoformat()])
            ][-HISTORY_LIMIT:],
            fertilizing_history=[
                date.fromisoformat(value)
                for value in data.get("fertilizing_history", [fertilized.isoformat()])
            ][-HISTORY_LIMIT:],
            watering_learning=WateringLearning.from_data(
                data.get("watering_learning", {})
            ),
        )

    def to_data(self) -> dict[str, Any]:
        """Serialize dates as ISO calendar dates, without timezone offsets."""
        return {
            "last_watered": self.last_watered.isoformat(),
            "last_fertilized": self.last_fertilized.isoformat(),
            "watering_snooze": self.watering_snooze,
            "fertilizing_snooze": self.fertilizing_snooze,
            "paused": self.paused,
            "watering_history": [value.isoformat() for value in self.watering_history],
            "fertilizing_history": [
                value.isoformat() for value in self.fertilizing_history
            ],
            "watering_learning": self.watering_learning.to_data(),
        }

    def watering_interval(self, config: PlantConfig) -> int:
        """Return the active learned interval or the configured manual baseline."""
        return self.watering_learning.effective(
            config.adaptive_watering, config.watering_interval, config.learning_revision
        )

    def mark_done(self, care: CareType, value: date) -> None:
        """Update the independent timer, reset its snooze and record the action."""
        if care == "water":
            self.last_watered = value
            self.watering_snooze = 0
            self.watering_history = [*self.watering_history, value][-HISTORY_LIMIT:]
        else:
            self.last_fertilized = value
            self.fertilizing_snooze = 0
            self.fertilizing_history = [*self.fertilizing_history, value][
                -HISTORY_LIMIT:
            ]
