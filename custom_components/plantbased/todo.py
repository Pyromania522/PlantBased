"""Computed due-care tasks; completion uses the shared durable care operation."""

from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.components.todo.const import (
        TodoItemStatus,
        TodoListEntityFeature,
    )
    from homeassistant.components.todo.entity import TodoItem, TodoListEntity
else:
    from homeassistant.components.todo import (
        TodoItem,
        TodoItemStatus,
        TodoListEntity,
        TodoListEntityFeature,
    )
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import DOMAIN
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
    async_add_entities([CareTodo(entry.runtime_data, None, "plant_care")])


class CareTodo(PlantBasedEntity, TodoListEntity):
    """Only currently due tasks; history is kept in PlantState."""

    _attr_supported_features = TodoListEntityFeature.UPDATE_TODO_ITEM

    @property
    def todo_items(self) -> list[TodoItem]:
        manager = self.manager
        items: list[TodoItem] = []
        for key, config in manager.configs.items():
            schedule = calculate(
                config, manager.plants[key], dt_util.now().date(), manager.vacation
            )
            due: list[tuple[CareType, date | None, bool]] = [
                ("water", schedule.next_watering, schedule.needs_water),
                ("fertilize", schedule.next_fertilizing, schedule.needs_fertilizer),
            ]
            for care, day, active in due:
                if active and day is not None:
                    items.append(
                        TodoItem(
                            uid=f"{key}:{care}:{day.isoformat()}",
                            summary=manager.care_summary(key, care),
                            due=day,
                            status=TodoItemStatus.NEEDS_ACTION,
                        )
                    )
        return sorted(items, key=lambda item: (str(item.due), item.uid or ""))

    async def async_update_todo_item(self, item: TodoItem) -> None:
        current = next((task for task in self.todo_items if task.uid == item.uid), None)
        if current is None:
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="stale_task"
            )
        if (
            item.status != TodoItemStatus.COMPLETED
            or item.summary != current.summary
            or item.due != current.due
            or item.description != current.description
        ):
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="task_read_only"
            )
        assert item.uid is not None
        plant_id, care, due = item.uid.split(":")
        await self.manager.async_mark_done(
            [plant_id],
            "water" if care == "water" else "fertilize",
            expected_due=date.fromisoformat(due),
        )
