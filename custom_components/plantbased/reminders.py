"""Local scheduled summaries, durable receipts and scoped Companion actions."""

import asyncio
from collections.abc import Callable
from copy import deepcopy
from datetime import UTC, date, datetime
import logging
from secrets import token_hex
from typing import TYPE_CHECKING, Any

from homeassistant.components import persistent_notification

if TYPE_CHECKING:
    from homeassistant.components.notify.const import NotifyEntityFeature
else:
    from homeassistant.components.notify import NotifyEntityFeature
from homeassistant.const import EVENT_CORE_CONFIG_UPDATE, EVENT_SERVICE_REGISTERED
from homeassistant.core import CoreState, Event, HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.event import (
    async_track_point_in_time,
    async_track_time_change,
)
from homeassistant.helpers.start import async_at_started
from homeassistant.util import dt as dt_util

from .manager import PlantManager
from .models import CareType
from .notification_texts import notification_texts
from .reminder_options import ReminderOptions
from .reminder_storage import Receipt, ReminderStore, decode_receipts
from .schedule import calculate

_LOGGER = logging.getLogger(__name__)


class ReminderCoordinator:
    """Own subscriptions and notification state for one loaded hub."""

    def __init__(self, manager: PlantManager) -> None:
        self.manager = manager
        self.hass = manager.hass
        self.entry = manager.entry
        self.options = ReminderOptions.from_data(self.entry.options)
        self.store = ReminderStore(self.hass, self.entry.entry_id)
        self.receipts: dict[str, Receipt] = {}
        self.tag = f"plantbased_{self.entry.entry_id}"
        self._lock = asyncio.Lock()
        self._unsubs: list[Callable[[], None]] = []
        self._timer: Callable[[], None] | None = None
        self._gap_timer: Callable[[], None] | None = None
        self._gap_day: date | None = None
        self._worker: asyncio.Task[None] | None = None
        self._dirty = False
        self._send = False
        self._stopped = False
        self._restore_persistent = True

    async def async_load(self) -> None:
        self.receipts = decode_receipts(await self.store.async_load())

    @callback
    def async_start(self) -> None:
        self._track_time()
        self._unsubs = [
            self.manager.async_add_listener(self._async_changed),
            self.hass.bus.async_listen(
                EVENT_CORE_CONFIG_UPDATE, self._async_config_changed
            ),
            self.hass.bus.async_listen(
                EVENT_SERVICE_REGISTERED, self._async_service_registered
            ),
            self.hass.bus.async_listen(
                "mobile_app_notification_action", self._async_action
            ),
            async_at_started(self.hass, self._async_started),
        ]
        self._async_schedule()

    @callback
    def _track_time(self) -> None:
        if self._timer is not None:
            self._timer()
        at = self.options.at
        self._timer = async_track_time_change(
            self.hass,
            self._async_time,
            hour=at.hour,
            minute=at.minute,
            second=at.second,
        )
        self._track_gap()

    @callback
    def _track_gap(self) -> None:
        """Schedule a single forward-normalized occurrence for a skipped DST time."""
        if self._gap_timer is not None:
            self._gap_timer()
            self._gap_timer = None
        now = dt_util.now()
        self._gap_day = now.date()
        desired = datetime.combine(now.date(), self.options.at, tzinfo=now.tzinfo)
        normalized = desired.astimezone(UTC).astimezone(now.tzinfo)
        if (
            normalized.replace(tzinfo=None) != desired.replace(tzinfo=None)
            and normalized > now
        ):
            self._gap_timer = async_track_point_in_time(
                self.hass, self._async_time, normalized
            )

    @callback
    def _async_time(self, now: datetime) -> None:
        self._async_schedule(send=True)

    @callback
    def _async_started(self, hass: HomeAssistant) -> None:
        self._async_schedule(send=True)

    @callback
    def _async_changed(self) -> None:
        if self._gap_day != dt_util.now().date():
            self._track_gap()
        self._async_schedule()

    @callback
    def _async_config_changed(self, event: Event[dict[str, Any]]) -> None:
        if "time_zone" in event.data:
            self._track_time()
        if "time_zone" in event.data or "language" in event.data:
            self._async_schedule(send=True)

    @callback
    def _async_service_registered(self, event: Event[dict[str, Any]]) -> None:
        if event.data.get("domain") == "notify":
            self._async_schedule(send=True)

    @callback
    def _async_schedule(self, *, send: bool = False) -> None:
        if self._stopped:
            return
        self._dirty = True
        self._send |= send
        if self._worker is None:
            self._worker = self.entry.async_create_task(
                self.hass, self._async_work(), "PlantBased reminders", eager_start=False
            )

    async def _async_work(self) -> None:
        try:
            while self._dirty and not self._stopped:
                send, self._send = self._send, False
                self._dirty = False
                try:
                    async with self._lock:
                        await self._async_process(send)
                except (HomeAssistantError, ValueError, TimeoutError):
                    _LOGGER.warning(
                        "Unable to update PlantBased reminders; "
                        "check notification targets and local storage"
                    )
        finally:
            self._worker = None

    def due_tasks(self) -> dict[str, tuple[str, CareType]]:
        tasks: dict[str, tuple[str, CareType]] = {}
        today = dt_util.now().date()
        for key, config in self.manager.configs.items():
            schedule = calculate(
                config, self.manager.plants[key], today, self.manager.vacation
            )
            care_dates: list[tuple[CareType, date | None, bool]] = [
                ("water", schedule.next_watering, schedule.needs_water),
                ("fertilize", schedule.next_fertilizing, schedule.needs_fertilizer),
            ]
            for care, day, active in care_dates:
                if active and day is not None:
                    tasks[f"{key}:{care}:{day.isoformat()}"] = (key, care)
        return tasks

    def _summary(self, tasks: dict[str, tuple[str, CareType]]) -> tuple[str, str]:
        texts = notification_texts(self.hass.config.language)
        lines = []
        for care in ("water", "fertilize"):
            names = sorted(
                self.manager.configs[key].name
                for key, kind in tasks.values()
                if kind == care
            )
            if names:
                lines.append(f"{texts[care]}: " + ", ".join(names))
        return texts["title"], "\n".join(lines)

    @staticmethod
    def _is_mobile(target: str) -> bool:
        return target.startswith("service:mobile_app_")

    async def _async_deliver(self, target: str, data: dict[str, Any]) -> bool:
        try:
            if target == "persistent":
                if data["message"] == "clear_notification":
                    persistent_notification.async_dismiss(self.hass, self.tag)
                else:
                    persistent_notification.async_create(
                        self.hass,
                        data["message"],
                        title=data["title"],
                        notification_id=self.tag,
                    )
            else:
                payload = dict(data)
                if target.startswith("service:"):
                    service = target.removeprefix("service:")
                else:
                    service = "send_message"
                    entity_id = target.removeprefix("entity:")
                    state = self.hass.states.get(entity_id)
                    if state is None or state.state == "unavailable":
                        return False
                    payload["entity_id"] = entity_id
                    if (
                        not state.attributes.get("supported_features", 0)
                        & NotifyEntityFeature.TITLE
                    ):
                        payload.pop("title", None)
                async with asyncio.timeout(15):
                    await self.hass.services.async_call(
                        "notify", service, payload, blocking=True
                    )
        except (HomeAssistantError, TimeoutError):
            _LOGGER.warning(
                "Unable to deliver a PlantBased reminder; "
                "check the selected notification target"
            )
            return False
        return True

    def _mobile_data(
        self, receipt: Receipt, tasks: dict[str, tuple[str, CareType]], *, refresh: bool
    ) -> dict[str, Any]:
        texts = notification_texts(self.hass.config.language)
        actions = []
        for operation, care, label in [
            ("water", "water", "all_watered"),
            ("fertilize", "fertilize", "all_fertilized"),
        ]:
            if any(kind == care for _, kind in tasks.values()):
                actions.append(
                    {
                        "action": f"{self.tag}:{receipt.token}:{operation}",
                        "title": texts[label],
                    }
                )
        if self.options.snooze:
            actions.append(
                {
                    "action": f"{self.tag}:{receipt.token}:snooze",
                    "title": texts["snooze"],
                }
            )
        return {"tag": self.tag, "actions": actions, "alert_once": refresh}

    async def _async_process(self, send: bool) -> None:
        if self._stopped or self.hass.state in (
            CoreState.stopping,
            CoreState.final_write,
            CoreState.stopped,
        ):
            return
        tasks = self.due_tasks()
        options = self.options
        enabled = options.enabled and self.entry.disabled_by is None
        selected = set(options.targets) if enabled else set()
        if enabled and options.persistent:
            selected.add("persistent")
        updated = deepcopy(self.receipts)
        now = dt_util.now()
        title, message = self._summary(tasks)
        content = title + "\n" + message
        for target in sorted(set(updated) | selected):
            receipt = updated.setdefault(target, Receipt())
            receipt.seen.intersection_update(tasks)
            active = bool(receipt.active)
            if target not in selected or not tasks:
                if active and (self._is_mobile(target) or target == "persistent"):
                    if not await self._async_deliver(
                        target,
                        {"message": "clear_notification", "data": {"tag": self.tag}},
                    ):
                        continue
                receipt.active.clear()
                receipt.token = ""
                receipt.text = ""
                if target not in selected:
                    del updated[target]
                continue
            scheduled = (
                send
                and now.time().replace(tzinfo=None) >= options.at
                and receipt.day != now.date()
                and (options.repeat or bool(set(tasks) - receipt.seen))
            )
            refresh = (
                active
                and (self._is_mobile(target) or target == "persistent")
                and (
                    receipt.active != set(tasks)
                    or receipt.text != content
                    or (target == "persistent" and self._restore_persistent)
                )
            )
            if not (scheduled or refresh):
                continue
            candidate = deepcopy(receipt)
            candidate.active = set(tasks)
            candidate.text = content
            if scheduled:
                candidate.seen.update(tasks)
                candidate.day = now.date()
            data: dict[str, Any] = {"title": title, "message": message}
            if self._is_mobile(target):
                candidate.token = token_hex(16)
                data["data"] = self._mobile_data(
                    candidate, tasks, refresh=not scheduled
                )
            if await self._async_deliver(target, data):
                updated[target] = candidate
                if target == "persistent":
                    self._restore_persistent = False
        if updated != self.receipts:
            await self.store.async_save(
                {
                    "recipients": {
                        key: receipt.to_data() for key, receipt in updated.items()
                    }
                }
            )
            self.receipts = updated

    async def _async_action(self, event: Event[dict[str, Any]]) -> None:
        action = event.data.get("action")
        if not isinstance(action, str) or not action.startswith(self.tag + ":"):
            return
        async with self._lock:
            if self._stopped or not self.options.enabled:
                return
            parts = action.split(":")
            if len(parts) != 3 or parts[2] not in ("water", "fertilize", "snooze"):
                return
            operation = parts[2]
            if operation == "snooze" and not self.options.snooze:
                return
            receipt = next(
                (
                    receipt
                    for target, receipt in self.receipts.items()
                    if self._is_mobile(target)
                    and target in self.options.targets
                    and receipt.token
                    and receipt.token == parts[1]
                ),
                None,
            )
            if receipt is None:
                return
            tasks = self.due_tasks()
            selected = [
                tasks[uid]
                for uid in receipt.active & tasks.keys()
                if operation == "snooze" or tasks[uid][1] == operation
            ]
            if not selected:
                return
            try:
                if operation == "snooze":
                    await self.manager.async_snooze_tasks(
                        selected, expected_tasks=receipt.active
                    )
                else:
                    await self.manager.async_mark_done(
                        [key for key, _ in selected],
                        "water" if operation == "water" else "fertilize",
                        expected_tasks=receipt.active,
                    )
            except (HomeAssistantError, TimeoutError):
                _LOGGER.warning(
                    "Unable to apply a PlantBased notification action; "
                    "care was not confirmed"
                )
            self._async_schedule()

    @callback
    def async_stop(self) -> None:
        self._stopped = True
        if self._timer is not None:
            self._timer()
            self._timer = None
        if self._gap_timer is not None:
            self._gap_timer()
            self._gap_timer = None
        for unsubscribe in self._unsubs:
            unsubscribe()
        self._unsubs.clear()

    async def async_shutdown(self) -> None:
        if self.entry.disabled_by is not None:
            async with self._lock:
                await self._async_process(False)
        self.async_stop()
        if self._worker is not None:
            await self._worker
        async with self._lock:
            pass


async def async_remove_reminders(hass: HomeAssistant, entry_id: str) -> None:
    """Best-effort clear on hub deletion, after Core has removed runtime_data."""
    tag = f"plantbased_{entry_id}"
    persistent_notification.async_dismiss(hass, tag)
    store = ReminderStore(hass, entry_id)
    try:
        receipts = decode_receipts(await store.async_load())
    except (HomeAssistantError, ValueError, TypeError, NotImplementedError):
        return
    for target, receipt in receipts.items():
        if not receipt.active or not ReminderCoordinator._is_mobile(target):
            continue
        try:
            async with asyncio.timeout(15):
                await hass.services.async_call(
                    "notify",
                    target.removeprefix("service:"),
                    {"message": "clear_notification", "data": {"tag": tag}},
                    blocking=True,
                )
        except (HomeAssistantError, TimeoutError):
            _LOGGER.warning("Unable to clear a removed PlantBased notification")
