"""Calendar boundaries, complete seasons, pause and independent schedules."""

from dataclasses import replace
from datetime import date

import pytest

from custom_components.plantbased.models import PlantConfig, PlantState
from custom_components.plantbased.schedule import calculate, in_season, season_start


@pytest.mark.parametrize(
    ("last", "interval", "today", "due", "days"),
    [
        ("2024-02-28", 1, "2024-02-29", True, 0),
        ("2024-02-28", 1, "2024-03-01", True, -1),
        ("2025-02-28", 1, "2025-03-01", True, 0),
        ("2026-12-31", 1, "2027-01-01", True, 0),
        ("2026-06-01", 7, "2026-06-07", False, 1),
        ("2026-06-01", 7, "2026-06-08", True, 0),
        ("2026-06-01", 7, "2026-06-15", True, -7),
        ("2025-06-15", 365, "2026-06-15", True, 0),
    ],
)
def test_local_day_due(last, interval, today, due, days):
    value = date.fromisoformat(last)
    result = calculate(
        PlantConfig("Plant", watering_interval=interval, fertilizing_enabled=False),
        PlantState(value, value),
        date.fromisoformat(today),
    )
    assert result.needs_water is due
    assert result.watering_days == days
    assert result.next_fertilizing is None
    assert result.fertilizing_days is None
    assert result.overdue is (due and days < 0)


@pytest.mark.parametrize(
    ("today", "expected"),
    [
        ("2026-02-28", "2026-03-01"),
        ("2026-03-01", "2026-03-01"),
        ("2026-09-30", "2026-03-01"),
        ("2026-10-01", "2027-03-01"),
        ("2026-12-31", "2027-03-01"),
    ],
)
def test_northern_season_boundaries(today, expected):
    day = date.fromisoformat(today)
    result = calculate(
        PlantConfig("Plant"), PlantState(date(2026, 1, 1), date(2026, 1, 1)), day
    )
    assert result.next_fertilizing == date.fromisoformat(expected)
    assert result.needs_fertilizer is (3 <= day.month <= 9)


@pytest.mark.parametrize(
    ("today", "expected", "active"),
    [
        ("2026-10-31", "2026-11-01", False),
        ("2026-11-01", "2026-11-01", True),
        ("2027-01-01", "2026-11-01", True),
        ("2027-02-28", "2026-11-01", True),
        ("2027-03-01", "2027-11-01", False),
    ],
)
def test_wrapping_season(today, expected, active):
    config = PlantConfig("Plant", season_start=11, season_end=2)
    result = calculate(
        config,
        PlantState(date(2026, 1, 1), date(2026, 1, 1)),
        date.fromisoformat(today),
    )
    assert result.next_fertilizing == date.fromisoformat(expected)
    assert result.needs_fertilizer is active


@pytest.mark.parametrize(
    ("last_watered", "last_fertilized", "status"),
    [
        ("2026-06-14", "2026-06-14", "ok"),
        ("2026-06-01", "2026-06-14", "water"),
        ("2026-06-14", "2026-05-01", "fertilize"),
        ("2026-06-01", "2026-05-01", "water_and_fertilize"),
    ],
)
def test_independent_care_status(last_watered, last_fertilized, status):
    result = calculate(
        PlantConfig("Plant", all_year=True),
        PlantState(
            date.fromisoformat(last_watered), date.fromisoformat(last_fertilized)
        ),
        date(2026, 6, 15),
    )
    assert result.status == status


@pytest.mark.parametrize("vacation", [False, True])
def test_pause_keeps_original_dates(vacation):
    config = PlantConfig("Plant", all_year=True)
    original = PlantState(date(2026, 1, 1), date(2026, 1, 1), paused=not vacation)
    result = calculate(config, original, date(2026, 6, 15), vacation)
    assert result.status == "paused"
    assert not result.needs_water and not result.needs_fertilizer and not result.overdue
    resumed = calculate(config, replace(original, paused=False), date(2026, 6, 15))
    assert resumed.status == "water_and_fertilize"
    assert resumed.next_watering == date(2026, 1, 8)


@pytest.mark.parametrize(
    "all_year,start,end", [(True, 3, 9), (False, 1, 12), (False, 3, 2)]
)
def test_continuous_year_has_no_artificial_reset(all_year, start, end):
    result = calculate(
        PlantConfig("Plant", all_year=all_year, season_start=start, season_end=end),
        PlantState(date(2025, 11, 1), date(2025, 11, 1)),
        date(2026, 1, 1),
    )
    assert result.next_fertilizing == date(2025, 11, 29)
    assert result.needs_fertilizer


def test_future_fertilizer_date_moves_into_next_window():
    result = calculate(
        PlantConfig("Plant", fertilizing_interval=90),
        PlantState(date(2026, 6, 1), date(2026, 9, 1)),
        date(2026, 9, 15),
    )
    assert result.next_fertilizing == date(2027, 3, 1)
    assert not result.needs_fertilizer
    assert in_season(date(2026, 3, 1), 3, 3)
    assert not in_season(date(2026, 4, 1), 3, 3)
    assert season_start(date(2026, 4, 1), 3, 3) == date(2027, 3, 1)


def test_snoozes_are_independent():
    state = PlantState(
        date(2026, 6, 1), date(2026, 5, 1), watering_snooze=8, fertilizing_snooze=18
    )
    config = PlantConfig("Plant", all_year=True)
    result = calculate(config, state, date(2026, 6, 15))
    assert result.watering_days == 1 and result.fertilizing_days == 1
    assert result.status == "ok"
    state.mark_done("water", date(2026, 6, 15))
    assert state.watering_snooze == 0 and state.fertilizing_snooze == 18
