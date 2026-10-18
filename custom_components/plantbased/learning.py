"""Bounded, local learning from explicitly recorded watering intervals."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date
from statistics import median
from typing import Any


@dataclass(slots=True)
class WateringLearning:
    """Keep a small observation window separate from the configured baseline."""

    baseline: int | None = None
    revision: int = 0
    interval: int | None = None
    anchor: date | None = None
    gaps: list[int] = field(default_factory=list)

    def sync(self, enabled: bool, baseline: int, revision: int) -> None:
        """Turning off or manually changing the interval starts learning afresh."""
        desired = baseline if enabled else None
        if self.baseline != desired or self.revision != revision:
            self.baseline = desired
            self.revision = revision
            self.interval = desired
            self.interrupt()

    def effective(self, enabled: bool, baseline: int, revision: int) -> int:
        """Ignore stale learning immediately, even before a reload persists reset."""
        if enabled and self.baseline == baseline and self.revision == revision:
            return self.interval or baseline
        return baseline

    def interrupt(self) -> None:
        """Keep the learned interval, but never train across an excluded period."""
        self.anchor = None
        self.gaps.clear()

    def observe(self, day: date, *, skip_gap: bool = False) -> None:
        """Require three agreeing intervals, then move at most one day per event."""
        if self.baseline is None:
            return
        if self.anchor is None or skip_gap or day < self.anchor:
            self.interrupt()
            self.anchor = day
            return
        if day == self.anchor:
            return
        gap = (day - self.anchor).days
        self.anchor = day
        if gap > 365:
            self.gaps.clear()
            return
        self.gaps = [*self.gaps, gap][-5:]
        if len(self.gaps) < 3:
            return
        target = int(median(self.gaps) + 0.5)
        tolerance = max(1, target * 0.2)
        if sum(abs(value - target) <= tolerance for value in self.gaps) < 3:
            return
        current = self.interval or self.baseline
        if target != current:
            self.interval = current + (1 if target > current else -1)

    def to_data(self) -> dict[str, Any]:
        """Serialize only numeric observations and a local calendar-date anchor."""
        return {
            "baseline": self.baseline,
            "revision": self.revision,
            "interval": self.interval,
            "anchor": self.anchor.isoformat() if self.anchor else None,
            "gaps": list(self.gaps),
        }

    @classmethod
    def from_data(cls, data: Any) -> WateringLearning:
        """Missing old data is valid; malformed persisted learning is not reset."""
        if not isinstance(data, Mapping):
            raise ValueError("Invalid stored watering learning")
        baseline, interval = data.get("baseline"), data.get("interval")
        revision, gaps = data.get("revision", 0), data.get("gaps", [])
        if any(
            value is not None and (type(value) is not int or not 1 <= value <= 365)
            for value in (baseline, interval)
        ):
            raise ValueError("Invalid stored learned interval")
        if type(revision) is not int or revision < 0:
            raise ValueError("Invalid stored learning revision")
        if (
            not isinstance(gaps, list)
            or len(gaps) > 5
            or any(type(value) is not int or not 1 <= value <= 365 for value in gaps)
        ):
            raise ValueError("Invalid stored watering observations")
        raw_anchor = data.get("anchor")
        anchor = date.fromisoformat(raw_anchor) if raw_anchor is not None else None
        if (
            (baseline is None) != (interval is None)
            or (gaps and anchor is None)
            or (baseline is None and anchor is not None)
        ):
            raise ValueError("Inconsistent stored watering learning")
        return cls(baseline, revision, interval, anchor, list(gaps))
