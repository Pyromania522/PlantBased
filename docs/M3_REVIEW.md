# Add care actions, automation events, calendar, tasks and diagnostics (M3)

M2 exposed plant care through entity controls only. This adds four translated
PlantBased actions targeting plants/groups by device or entity, plus area/label
selection and explicit all-plant targeting. Targets are deduplicated and direct
invalid targets fail before mutation; bulk marks/snoozes use one verified save.
Actions stay registered when the hub is unloaded and return translated errors.

The hub gains a read-only all-day care calendar and a due-only to-do list.
Completing a task records care through the same persisted operation as buttons,
date entities and domain actions. Stale/concurrent task completion is validated
under the storage lock. Care-due events fire on due transitions, and care-done
events fire only after confirmed persistence, with registry device IDs.

Diagnostics export an allowlisted care snapshot; only plant names are included
as free text. Notes, species, group names, locations and image addresses are
excluded. Calendar/task text follows HA's configured language; entity/action
names, fields, care labels and errors are translated in German and English.

Validation: **129 passed on each of HA 2025.10.0/Python 3.13.2 and
2026.10.2/Python 3.14.2**, no skips/xfails, **99.37% statement/branch coverage**
(100% statements). Ruff, strict mypy on 20 modules and official local hassfest
pass. Real-filesystem storage checks pass on both versions. Tests include native
calendar/to-do services, authenticated HA diagnostics download, target resolution,
season/DST boundaries, events, concurrency and write failures. Exact-head remote
CI acceptance is recorded on this PR.

Assumptions documented in DECISIONS.md: the calendar shows the next outstanding
care date per plant/care, with overdue dates retained, rather than projecting
unperformed future care; season-resume markers are resolved against the actual
interval for calendar events. Paused/vacation work is excluded. Completed tasks
leave the computed list and remain in history; task edits other than completion
are rejected. Due events publish already-due care once on setup/reload and do not
repeat every overdue day. Dates default to the current local day. No target never
means all plants; empty valid groups are no-ops. Basic pause/snooze/season behavior
from M2 is reused and covered by M3 automation/platform tests.

No new runtime dependency, browser manual test, full HA process restart, Silver
tier or public release is claimed. Notifications remain M4; cards/illustrations
remain M5; release remains M6. The manifest stays the development version 0.1.0.
