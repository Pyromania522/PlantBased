"""Pure calendar-day calculations; no HA clock, I/O, polling or services."""

from dataclasses import dataclass
from datetime import date, timedelta

from .models import PlantConfig, PlantState


def in_season(day: date, start: int, end: int) -> bool:
    """Include whole boundary months and support southern-hemisphere windows."""
    if start <= end:
        return start <= day.month <= end
    return day.month >= start or day.month <= end


def season_start(day: date, start: int, end: int) -> date:
    """Find the current window's start, or the next start when outside it."""
    year = day.year
    if in_season(day, start, end):
        if day.month < start:
            year -= 1
    elif day.month > start:
        year += 1
    return date(year, start, 1)


@dataclass(frozen=True, slots=True)
class CareSchedule:
    """Calculated state for one local day."""

    next_watering: date
    next_fertilizing: date | None
    watering_days: int
    fertilizing_days: int | None
    needs_water: bool
    needs_fertilizer: bool
    status: str

    @property
    def overdue(self) -> bool:
        """Count a plant once, excluding paused or seasonally inactive care."""
        return (self.needs_water and self.watering_days < 0) or (
            self.needs_fertilizer
            and self.fertilizing_days is not None
            and self.fertilizing_days < 0
        )


def calculate(
    config: PlantConfig, state: PlantState, today: date, vacation: bool = False
) -> CareSchedule:
    """Calculate independent timers using dates, so DST cannot shift a due day."""
    watering = state.last_watered + timedelta(
        days=config.watering_interval + state.watering_snooze
    )
    fertilizer: date | None = None
    year_round = config.all_year or (config.season_end - config.season_start) % 12 == 11
    active_season = year_round or in_season(
        today, config.season_start, config.season_end
    )
    if config.fertilizing_enabled:
        fertilizer = state.last_fertilized + timedelta(
            days=config.fertilizing_interval + state.fertilizing_snooze
        )
        if not year_round:
            if not active_season:
                # Outside the season, display the requested season-resume marker.
                fertilizer = season_start(today, config.season_start, config.season_end)
            else:
                fertilizer = max(
                    fertilizer,
                    season_start(today, config.season_start, config.season_end),
                )
                if not in_season(fertilizer, config.season_start, config.season_end):
                    fertilizer = season_start(
                        fertilizer, config.season_start, config.season_end
                    )

    paused = state.paused or vacation
    water_due = not paused and today >= watering
    fertilizer_due = (
        not paused and active_season and fertilizer is not None and today >= fertilizer
    )
    status = "ok"
    if paused:
        status = "paused"
    elif water_due and fertilizer_due:
        status = "water_and_fertilize"
    elif water_due:
        status = "water"
    elif fertilizer_due:
        status = "fertilize"
    return CareSchedule(
        watering,
        fertilizer,
        (watering - today).days,
        (fertilizer - today).days if fertilizer is not None else None,
        water_due,
        fertilizer_due,
        status,
    )
