# Add native plant/group subentries and persisted care schedules (M2)

The M1 hub could not represent or care for individual plants. This change adds
one-step plant/group configuration, native subentry-owned devices and entities,
independent local-day care schedules, and persisted care history.

Plants expose date/interval controls, care and snooze buttons, translated status
and due flags, and a pause switch. Groups have member-only counts and bulk care
buttons. The hub has overview counts, an aggregate care flag and vacation mode.
Deleting a group keeps its plants unassigned; editing names/settings preserves
device/entity IDs and runtime dates.

Persistence uses a private versioned HA Store with atomic writes, migration,
bounded histories and verified saves. Corrupt/unsupported state is not silently
reset. Entity updates are event-driven, including local midnight and time-zone
changes. No external requirements or sensor inputs are introduced.

Validation: 90 tests pass on each of HA 2025.10.0/Python 3.13.2 and
2026.10.2/Python 3.14.2, with 99.50% combined statement/branch coverage and no
skips. Strict mypy, Ruff and official local hassfest pass. Independent real-file
checks pass on both versions for private permissions, save/read, corruption
preservation and deletion. Remote CI status is recorded on the PR's exact head.

Assumptions in DECISIONS.md: creation-only seed dates are edited later through
date entities; future last-care dates are rejected; outside-season fertilizing
dates show a season-resume marker; paused schedules retain original dates;
overdue snooze starts no earlier than tomorrow; image presets are metadata until
M5. Basic pause/snooze/season behavior supports M2's entities, while integration
actions/events, calendar/to-do and diagnostics remain M3. Notifications remain
M4 and cards/illustrations M5. No Silver tier, browser UI test or public release
is claimed. The manifest remains the requested development version 0.1.0.
