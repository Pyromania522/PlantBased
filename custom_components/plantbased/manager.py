"""Event-driven runtime, atomic persistence and shared care operations."""

import asyncio
from collections.abc import Callable, Iterable
from copy import deepcopy
from datetime import date, datetime, timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_CORE_CONFIG_UPDATE
from homeassistant.core import CoreState, Event, HomeAssistant, callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.start import async_at_start
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .models import CareType, PlantConfig, PlantState
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

    async def async_load(self) -> None:
        """Restore runtime data, seed new plants and prune deleted plants."""
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

    @callback
    def _track_midnight(self) -> None:
        if self._midnight_unsubscribe is not None:
            self._midnight_unsubscribe()
        self._midnight_unsubscribe = async_track_time_change(
            self.hass, self._async_midnight, hour=0, minute=0, second=0
        )

    @callback
    def _async_config_updated(self, event: Event[dict[str, Any]]) -> None:
        if "time_zone" in event.data:
            self._track_midnight()
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
        for listener in tuple(self._listeners):
            listener()

    @callback
    def async_add_listener(self, listener: Callable[[], None]) -> Callable[[], None]:
        """Subscribe an entity; its removal hook owns the unsubscribe."""
        self._listeners.add(listener)
        return lambda: self._listeners.discard(listener)

    @callback
    def async_stop(self) -> None:
        """Cancel startup/midnight listeners, including failed-setup cleanup."""
        self._stopped = True
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
        self, ids: Iterable[str], care: CareType, value: date | None = None
    ) -> None:
        """Record each action in one serialized, durable transaction."""
        value = value or dt_util.now().date()
        if value > dt_util.now().date():
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="future_date"
            )
        async with self._lock:
            selected = self._validate(ids)
            plants = deepcopy(self.plants)
            for key in selected:
                plants[key].mark_done(care, value)
            await self._commit(plants, self.vacation)

    async def async_mark_group(self, group_id: str, care: CareType) -> None:
        """Group buttons act on every current member, including paused plants."""
        if group_id not in self.entry.subentries:
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="not_available"
            )
        await self.async_mark_done(self.members(group_id), care)

    async def async_snooze(self, plant_id: str, care: CareType, days: int = 1) -> None:
        """Snooze overdue care until at least tomorrow; accumulate repeated delays."""
        if type(days) is not int or not 1 <= days <= 365:
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="invalid_interval"
            )
        async with self._lock:
            self._validate([plant_id])
            plants = deepcopy(self.plants)
            state, config = plants[plant_id], self.configs[plant_id]
            today = dt_util.now().date()
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
        self._validate([plant_id])
        if not 1 <= days <= 365 or not float(days).is_integer():
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="invalid_interval"
            )
        subentry = self.entry.subentries[plant_id]
        key = "watering_interval" if care == "water" else "fertilizing_interval"
        self.hass.config_entries.async_update_subentry(
            self.entry, subentry, data={**subentry.data, key: int(days)}
        )
