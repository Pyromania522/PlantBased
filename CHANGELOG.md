# Changelog

## Unreleased — 0.1.0 development

### Added in M3

- Four translated care actions with plant/group/entity/area/label targets,
  deduplication, whole-day validation and durable bulk marks/snoozes.
- Due-transition and successfully saved care-done automation events, including
  native button/date controls and task completion.
- Read-only all-day care calendar and due-only to-do list; completing a task
  records care, with stale/concurrent task protection.
- Allowlisted downloadable diagnostics without free text other than plant names.
- Eight hub entities total; calendar/task text follows HA's configured language.
- Native service, automation-event, season, DST overlap, diagnostics-download,
  translation and failure-path tests on minimum/current HA.

### Added in M2

- Plant and group config subentries with translated create/reconfigure flows,
  native device/entity ownership, areas and stable IDs.
- Independent calendar-day care schedules, seasonal fertilizing, pause/vacation,
  snooze, editable dates/intervals and group-only bulk buttons.
- 16 calculated/control entities per plant, five per group, and six on the hub.
- Atomic, private, versioned storage with migration and bounded histories;
  write verification and corruption preservation before successful care feedback.
- English/German entity names/states, selectors, subentry labels and errors.
- Frozen-time integration, calendar-boundary, DST, storage and lifecycle tests on
  minimum/current HA. See VALIDATION.md for exact results and milestone limits.

### Added in M1

- HACS repository layout, metadata, and original brand assets.
- UI confirmation to create exactly one local PlantBased hub.
- English and German configuration text.
- Unload/reload support, minimum/current HA tests, and validation CI.
- Verified M1 on HA 2025.10.0 and 2026.10.2, with hassfest, HACS, Ruff, mypy,
  and both test jobs passing on GitHub.

The complete v0.1.0 release is planned for M6. No release has been published.
