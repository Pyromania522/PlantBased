# Changelog

## 0.1.0 — first complete version

Publication status and assets are listed in
[GitHub Releases](https://github.com/Pyromania522/PlantBased/releases).

### Added in M6

- Complete installation/update/backup/uninstall and troubleshooting guidance,
  including HA Container paths and English/German user instructions.
- Executable due/done notification and manual group-action automation examples,
  verified through the real HA automation engine on both supported targets.
- Real browser-fixture card previews and explicit full-HA/Companion screenshot
  placeholders, release notes and maintainer release instructions.
- Deterministic ZIP/checksum packaging with version/asset checks, original and
  third-party licenses, extraction tests and local-file exclusion.
- PR release-candidate artifacts and a version-tag workflow gated by all seven
  validation jobs; complete draft upload before publishing, without extra secrets.

### Added in M5

- Bundled plant/group and overview dashboard cards with graphical editors,
  registry-based device selection, live care state and existing care actions.
- English/German labels, theme colors, dark/mobile layouts, keyboard controls,
  independent snooze choices and visible action failures.
- Automatic public frontend-module/static-path registration, content-versioned
  URLs and reload-safe process-wide registration without manual resource entries.
- Twelve original MIT-licensed local SVG illustrations and custom-image fallback.
- Reproducible locked TypeScript/Lit/Vite build, license notices and CI browser
  checks with screenshots; actual HA HTTP/frontend/registry API compatibility tests.

### Added in M4

- Hub options for opt-in local-time reminders, available notification targets,
  daily repeat, persistent HA copy and optional mobile snooze action.
- One English/German due-care summary per recipient, private durable receipts,
  startup catch-up, DST handling and reload/restart deduplication.
- Scoped Companion all-watered/all-fertilized/snooze actions, stale-cycle checks,
  atomic bulk snooze and shared care-state updates.
- Tagged mobile replacement/clearing, persistent-copy restoration and cleanup
  for removed targets, disabled reminders and disabled/removed hubs.
- Ordinary notify entity support, recipient-isolated delivery failures and no
  notifier identifiers/action tokens in diagnostics.
- Real-filesystem reminder-receipt validation and minimum/current HA tests.

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

Public releases are created by the version-tag workflow after the reviewed merge;
a version in this changelog does not by itself publish a GitHub Release.
