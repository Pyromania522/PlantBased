"""Event-driven runtime, atomic persistence and shared care operations."""

import asyncio
from collections.abc import Callable, Iterable
from copy import deepcopy
from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .reminders import ReminderCoordinator

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_CORE_CONFIG_UPDATE
from homeassistant.core import CoreState, Event, HomeAssistant, callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.start import async_at_start
from homeassistant.helpers.translation import async_get_translations
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .models import CareType, PlantConfig, PlantState
from .registry import device_for_subentry
from .schedule import CareSchedule, calculate
from .storage import PlantStore

type PlantBasedConfigEntry = ConfigEntry[PlantManager]


class PlantManager:
    """One per-entry state owner; entities are memory-only views of this state."""

    def __init__(self, hass: HomeAssistant, entry: PlantBasedConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self.store = PlantStore(hass, entry.entry_id)
        self.today = dt_util.now().date()
        self.configs = {
            key: PlantConfig.from_data(sub.data)
            for key, sub in entry.subentries.items()
            if sub.subentry_type == "plant"
        }
        self.plants: dict[str, PlantState] = {}
        self.schedules: dict[str, CareSchedule] = {}
        self.vacation = False
        self._lock = asyncio.Lock()
        self._listeners: set[Callable[[], None]] = set()
        self._unsubscribers: list[Callable[[], None]] = []
        self._midnight_unsubscribe: Callable[[], None] | None = None
        self._stopped = False
        self._events_active = False
        self._due: set[tuple[str, CareType]] = set()
        self.care_labels: dict[CareType, str] = {}
        self.reminders: ReminderCoordinator | None = None

    async def async_load(self) -> None:
        """Restore runtime data, seed new plants and prune deleted plants."""
        await self._async_load_labels()
        saved = await self.store.async_load()
        if saved is not None:
            self.vacation = saved.get("vacation", False)
            if not isinstance(self.vacation, bool) or not isinstance(
                saved.get("plants"), dict
            ):
                raise ValueError("Invalid stored hub state")
        stored_plants = saved["plants"] if saved is not None else {}
        self.plants = {
            key: PlantState.from_data(stored_plants[key])
            if key in stored_plants
            else PlantState.initial(self.entry.subentries[key].data, self.today)
            for key in self.configs
        }
        await self.store.async_save(self._serialize(self.plants, self.vacation))
        self._recalculate()

    async def _async_load_labels(self) -> None:
        translations = await async_get_translations(
            self.hass, self.hass.config.language, "selector", {DOMAIN}
        )
        self.care_labels = {
            care: translations[f"component.{DOMAIN}.selector.care_type.options.{care}"]
            for care in ("water", "fertilize")
        }

    def care_summary(self, plant_id: str, care: CareType) -> str:
        """Build text using HA's configured language and the current plant name."""
        return f"{self.care_labels[care]}: {self.configs[plant_id].name}"

    @staticmethod
    def _serialize(plants: dict[str, PlantState], vacation: bool) -> dict[str, Any]:
        return {
            "vacation": vacation,
            "plants": {key: state.to_data() for key, state in plants.items()},
        }

    @callback
    def async_start(self) -> None:
        """Subscribe to local midnight and HA start; never poll."""
        self._track_midnight()
        self._unsubscribers = [
            async_at_start(self.hass, self._async_started),
            self.hass.bus.async_listen(
                EVENT_CORE_CONFIG_UPDATE, self._async_config_updated
            ),
        ]
        self._events_active = True
        self._recalculate()

    @callback
    def _track_midnight(self) -> None:
        if self._midnight_unsubscribe is not None:
            self._midnight_unsubscribe()
        self._midnight_unsubscribe = async_track_time_change(
            self.hass, self._async_midnight, hour=0, minute=0, second=0
        )

    async def _async_config_updated(self, event: Event[dict[str, Any]]) -> None:
        if "language" in event.data:
            await self._async_load_labels()
        if "time_zone" in event.data:
            self._track_midnight()
        if "time_zone" in event.data or "language" in event.data:
            self._recalculate()

    @callback
    def _async_started(self, hass: HomeAssistant) -> None:
        self._recalculate()

    @callback
    def _async_midnight(self, now: datetime) -> None:
        self._recalculate()

    @callback
    def _recalculate(self) -> None:
        self.today = dt_util.now().date()
        self.schedules = {
            key: calculate(self.configs[key], state, self.today, self.vacation)
            for key, state in self.plants.items()
        }
        if self._events_active:
            due: set[tuple[str, CareType]] = set()
            for key, schedule in self.schedules.items():
                if schedule.needs_water:
                    due.add((key, "water"))
                if schedule.needs_fertilizer:
                    due.add((key, "fertilize"))
            for key, care in sorted(due - self._due):
                self._fire_care_event("due", key, care)
            self._due = due
        for listener in tuple(self._listeners):
            listener()

    @callback
    def _fire_care_event(self, action: str, plant_id: str, care: CareType) -> None:
        device = device_for_subentry(self.hass, self.entry.entry_id, plant_id)
        if device is not None:
            self.hass.bus.async_fire(
                f"{DOMAIN}_care_{action}",
                {
                    "device_id": device.id,
                    "name": self.configs[plant_id].name,
                    "care_type": care,
                },
            )

    @callback
    def async_add_listener(self, listener: Callable[[], None]) -> Callable[[], None]:
        """Subscribe an entity; its removal hook owns the unsubscribe."""
        self._listeners.add(listener)
        return lambda: self._listeners.discard(listener)

    @callback
    def async_stop(self) -> None:
        """Cancel startup/midnight listeners, including failed-setup cleanup."""
        self._stopped = True
        self._events_active = False
        if self.reminders is not None:
            self.reminders.async_stop()
        if self._midnight_unsubscribe is not None:
            self._midnight_unsubscribe()
            self._midnight_unsubscribe = None
        for unsubscribe in self._unsubscribers:
            unsubscribe()
        self._unsubscribers.clear()

    async def async_shutdown(self) -> None:
        """Finish in-flight storage writes before the next manager can load."""
        async with self._lock:
            self.async_stop()

    def members(self, group_id: str | None = None) -> list[str]:
        """Resolve group membership from configuration, not entity names."""
        return [
            key
            for key, config in self.configs.items()
            if group_id is None or config.group == group_id
        ]

    def _validate(self, ids: Iterable[str]) -> list[str]:
        selected = list(dict.fromkeys(ids))
        if (
            self._stopped
            or self.hass.state
            in (CoreState.stopping, CoreState.final_write, CoreState.stopped)
            or any(
                key not in self.entry.subentries or key not in self.plants
                for key in selected
            )
        ):
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="not_available"
            )
        return selected

    async def _commit(self, plants: dict[str, PlantState], vacation: bool) -> None:
        # Save the candidate first: a failed write must not report an action done.
        await self.store.async_save(self._serialize(plants, vacation))
        self.plants = plants
        self.vacation = vacation
        self._recalculate()

    async def async_mark_done(
        self,
        ids: Iterable[str],
        care: CareType,
        value: date | None = None,
        *,
        expected_due: date | None = None,
        expected_tasks: set[str] | None = None,
    ) -> None:
        """Record each action in one serialized, durable transaction."""
        value = value or dt_util.now().date()
        if value > dt_util.now().date():
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="future_date"
            )
        async with self._lock:
            selected = self._validate(ids)
            if expected_tasks is not None:
                self._validate_expected(
                    [(key, care) for key in selected], expected_tasks
                )
            if expected_due is not None:
                for key in selected:
                    schedule = calculate(
                        self.configs[key],
                        self.plants[key],
                        dt_util.now().date(),
                        self.vacation,
                    )
                    due = (
                        schedule.next_watering
                        if care == "water"
                        else schedule.next_fertilizing
                    )
                    active = (
                        schedule.needs_water
                        if care == "water"
                        else schedule.needs_fertilizer
                    )
                    if not active or due != expected_due:
                        raise ServiceValidationError(
                            translation_domain=DOMAIN, translation_key="stale_task"
                        )
            plants = deepcopy(self.plants)
            for key in selected:
                plants[key].mark_done(care, value)
            await self._commit(plants, self.vacation)
            for key in selected:
                self._fire_care_event("done", key, care)

    async def async_mark_group(self, group_id: str, care: CareType) -> None:
        """Group buttons act on every current member, including paused plants."""
        if group_id not in self.entry.subentries:
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="not_available"
            )
        await self.async_mark_done(self.members(group_id), care)

    async def async_snooze(self, plant_id: str, care: CareType, days: int = 1) -> None:
        """Snooze overdue care until at least tomorrow; accumulate repeated delays."""
        await self.async_snooze_many([plant_id], care, days)

    async def async_snooze_many(
        self, ids: Iterable[str], care: CareType, days: int = 1
    ) -> None:
        """Apply a bulk snooze as one checked storage transaction."""
        await self.async_snooze_tasks([(key, care) for key in ids], days)

    def _validate_expected(
        self, tasks: Iterable[tuple[str, CareType]], expected: set[str]
    ) -> None:
        for key, care in tasks:
            schedule = calculate(
                self.configs[key], self.plants[key], dt_util.now().date(), self.vacation
            )
            day = (
                schedule.next_watering if care == "water" else schedule.next_fertilizing
            )
            active = (
                schedule.needs_water if care == "water" else schedule.needs_fertilizer
            )
            if (
                not active
                or day is None
                or f"{key}:{care}:{day.isoformat()}" not in expected
            ):
                raise ServiceValidationError(
                    translation_domain=DOMAIN, translation_key="stale_task"
                )

    async def async_snooze_tasks(
        self,
        tasks: Iterable[tuple[str, CareType]],
        days: int = 1,
        *,
        expected_tasks: set[str] | None = None,
    ) -> None:
        """Snooze multiple care types with one save, including mobile bulk snooze."""
        if type(days) is not int or not 1 <= days <= 365:
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="invalid_interval"
            )
        async with self._lock:
            selected = list(dict.fromkeys(tasks))
            self._validate([key for key, _ in selected])
            if expected_tasks is not None:
                self._validate_expected(selected, expected_tasks)
            plants = deepcopy(self.plants)
            today = dt_util.now().date()
            for plant_id, care in selected:
                state, config = plants[plant_id], self.configs[plant_id]
                if care == "water":
                    base = state.last_watered + timedelta(days=config.watering_interval)
                    state.watering_snooze = (
                        max(base + timedelta(days=state.watering_snooze), today)
                        + timedelta(days=days)
                        - base
                    ).days
                else:
                    base = state.last_fertilized + timedelta(
                        days=config.fertilizing_interval
                    )
                    state.fertilizing_snooze = (
                        max(base + timedelta(days=state.fertilizing_snooze), today)
                        + timedelta(days=days)
                        - base
                    ).days
            await self._commit(plants, self.vacation)

    async def async_pause(self, plant_id: str | None, paused: bool) -> None:
        """Persist vacation/plant pause without shifting either original date."""
        async with self._lock:
            self._validate([plant_id] if plant_id is not None else [])
            plants = deepcopy(self.plants)
            if plant_id is not None:
                plants[plant_id].paused = paused
            await self._commit(plants, paused if plant_id is None else self.vacation)

    @callback
    def async_set_interval(self, plant_id: str, care: CareType, days: float) -> None:
        """Numbers edit the real subentry; the shared update listener reloads it."""
        self.async_set_intervals([plant_id], care, days)

    @callback
    def async_set_intervals(
        self, ids: Iterable[str], care: CareType, days: float
    ) -> None:
        """Validate every member before updating any subentry configuration."""
        selected = self._validate(ids)
        if not 1 <= days <= 365 or not float(days).is_integer():
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="invalid_interval"
            )
        key = "watering_interval" if care == "water" else "fertilizing_interval"
        for plant_id in selected:
            subentry = self.entry.subentries[plant_id]
            self.hass.config_entries.async_update_subentry(
                self.entry, subentry, data={**subentry.data, key: int(days)}
            )
