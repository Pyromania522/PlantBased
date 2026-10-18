"""Read-only all-day calendar of outstanding care dates."""

from datetime import date, datetime, timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util import dt as dt_util

from .entity import PlantBasedEntity
from .manager import PlantBasedConfigEntry
from .models import CareType
from .schedule import calculate

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PlantBasedConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([CareCalendar(entry.runtime_data, None, "care_calendar")])


class CareCalendar(PlantBasedEntity, CalendarEntity):
    """One event per next outstanding care task; never project unperformed care."""

    _attr_supported_features = 0

    def _events(self) -> list[CalendarEvent]:
        manager = self.manager
        today = dt_util.now().date()
        events: list[CalendarEvent] = []
        for key, config in manager.configs.items():
            state = manager.plants[key]
            if state.paused or manager.vacation:
                continue
            schedule = calculate(config, state, today)
            fertilizing = schedule.next_fertilizing
            # Resolve a season-resume marker to the actual interval's next due day.
            if fertilizing is not None and fertilizing > today:
                fertilizing = calculate(config, state, fertilizing).next_fertilizing
            dates: list[tuple[CareType, date | None]] = [
                ("water", schedule.next_watering),
                ("fertilize", fertilizing),
            ]
            for care, day in dates:
                if day is None:
                    continue
                events.append(
                    CalendarEvent(
                        start=day,
                        end=day + timedelta(days=1),
                        summary=manager.care_summary(key, care),
                        uid=f"{key}:{care}:{day.isoformat()}",
                    )
                )
        return sorted(events, key=lambda event: (event.start, event.uid or ""))

    @property
    def event(self) -> CalendarEvent | None:
        return next(
            (
                event
                for event in self._events()
                if event.start_datetime_local >= dt_util.start_of_local_day()
            ),
            None,
        )

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        if end_date <= start_date:
            return []
        return [
            event
            for event in self._events()
            if event.end_datetime_local > start_date
            and event.start_datetime_local < end_date
        ]
