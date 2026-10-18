# Decisions and verified references

## M6 documentation, packages and publication

Verified the current official developer-doc and HACS publishing sources again
(`50b518898989b67bb76b69827f227aa6f0acd32a` and
`4f06a5bd11088a21a453fdcb3eda1603353e6c8a`), HA user-doc source at
`8e2059e13f61f1c0650c11ac94c9e86c393fd8af`, and official GitHub Actions docs
at `dae83f7d28f3b8e10015bd6b6d8b72267cedceca`. No new integration runtime API
is added. Current and minimum released automation engines execute the actual
documented `triggers`/`actions`, event data templates and service targets.

| Contract | Reference |
| --- | --- |
| Automation event triggers and templated action data/targets | [HA triggers](https://www.home-assistant.io/docs/automation/trigger/), [script actions](https://www.home-assistant.io/docs/scripts/perform-actions/), installed released implementations |
| HACS release discovery and integration directory layout | [Integration publishing](https://hacs.xyz/docs/publish/integration/), [general publishing](https://hacs.xyz/docs/publish/start/), [default-list requirements](https://hacs.xyz/docs/publish/include/) |
| Reusable validation and permission limits | [Reusable workflows](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows) |
| Draft/create/upload/publish and refusing absent tags | Official installed [gh release](https://cli.github.com/manual/gh_release) command help (`--verify-tag`, `--draft`, `--clobber`, `--latest`) |

Keep normal HACS repository/tag downloads; `zip_release` is deliberately unset.
The additional `plantbased.zip` is a manual-install artifact containing a single
`plantbased/` folder for extraction into `custom_components/`. All runtime files
remain inside the integration as HACS requires. A tracked-file allowlist excludes
untracked local configuration/caches; tracked symlinks and unexpected extensions
are rejected. Include the repository MIT license and the bundle's third-party
notices. Fixed timestamps/permissions, sorted entries and matching Python/zlib
produce deterministic ZIPs; SHA256SUMS checks file integrity, not signatures.

The package script requires stable semantic versions matching the tag, integration,
npm package and both lockfile roots, plus per-version release notes and all twelve
matching SVGs. Branch/PR CI builds the actual ZIP and uploads a reviewable candidate.
On `v*` tag pushes, the Release workflow calls all seven validation jobs and the
publisher requires the tagged commit on `main`. It verifies the candidate hash
and compares a fresh archive before using only the built-in GitHub token. Write
permission is limited to the publisher. Upload to a draft before making a complete
release public; retrying may replace draft assets but never a published release.

Continue the established user-reviewed PR workflow: no automatic M6 PR merge.
The version tag and public release follow that merge, rather than tagging a feature
branch. A passing preflight or a saved draft is not a published release. Actual tag
publication is reported only after observed success. Screenshot previews are
identified as real Chromium fixture captures; full-HA and phone captures remain
explicit placeholders. Full HA browser/process restart and physical phone delivery
remain manual acceptance checks, not inferred from automated API tests.

HACS default-list submission is outside v0.1.0. A later owner/contributor submission
must recheck name collisions, green no-ignore validators, metadata/license/brand
requirements and an actual published release, then add the repository alphabetically
to `hacs/default`. No official quality-scale tier is claimed.

## M5 scope and verified frontend APIs

Before coding, official developer-doc source
`50b518898989b67bb76b69827f227aa6f0acd32a`, Core dev
`1b740dcd4bc1e669827fc94c8b4bd7a4bbbae734`, frontend source
`b399dac7881d03df938fb4cad5200b68811c24f2`, HACS documentation
`4f06a5bd11088a21a453fdcb3eda1603353e6c8a`, and both installed supported
releases were checked. The websites remain denied by this cloud policy; their
official Git repositories are used.

| Contract | Official reference |
| --- | --- |
| `async_register_static_paths([StaticPathConfig(...)])` | [Async static paths](https://developers.home-assistant.io/blog/2024/06/18/async_register_static_paths/) |
| `frontend.add_extra_js_url(hass, url)` | Public custom-integration API documented in [Core frontend source](https://github.com/home-assistant/core/blob/dev/homeassistant/components/frontend/__init__.py), verified on both releases |
| Custom elements, `setConfig`, `hass`, `getCardSize`, `getGridOptions`, visual editors, `config-changed`, `window.customCards` | [Custom cards](https://developers.home-assistant.io/docs/frontend/custom-ui/custom-card/) |
| `hass.states`, `hass.locale.language`/`language`, `callWS`, `callService` with target | [Frontend data](https://developers.home-assistant.io/docs/frontend/data/), released frontend types |
| Entity/device registry list and update subscriptions | [WebSocket API](https://developers.home-assistant.io/docs/api/websocket/), official frontend registry clients and both released Core handlers |

The integration registers its bundle once as an extra **frontend module**, using
the supported public API, rather than editing private Lovelace resource
collections. It therefore works for both storage and YAML dashboard modes, without
manual resource entries. Static registration and module loading live for the HA
process; entry reloads/removal cannot register duplicate routes/modules. A fresh
browser reload is needed if the UI was already open when the integration loaded.
The JavaScript and illustration URLs include a content-derived cache version
covering the compiled bundle and all twelve SVGs.
There is one locally bundled TypeScript/Lit module, without CDN imports, external
fonts, frontend telemetry or runtime Python requirements.

The single/group card selects a plant/group device ID. The overview covers all
PlantBased plants. Device/entity IDs and known translation keys/unique IDs are
resolved through the registries, never guessed from entity names. Registry update
subscriptions refresh metadata; normal hass state pushes update care displays.
Connections/subscriptions are released when a card/editor is removed. The older
supported `hass` property is used because the newly recommended context APIs are
not available on the minimum release.

The visual editor uses an accessible native device select populated only with
PlantBased plant/group devices, avoiding undocumented lazy-loading of HA's picker
components. Standard `getConfigElement`, stub configs and bubbling/composed
`config-changed` events provide HA's graphical card editing contract. User titles,
plant names and backend errors render as escaped text. Custom images allow only
/local/ paths or HTTP(S) URLs without credentials and fall back to a local preset
on failure. All twelve SVGs are authored from original vector primitives under
MIT; no downloaded artwork or generated raster images are used.

Care buttons call the existing integration actions with a device target; pending
operations disable duplicate presses and failures are visible without optimistic
state changes. Snooze offers independent watering/fertilizing choices. Paused and
unavailable status remain distinct; overdue uses due flags and negative days, so
seasonally inactive care is not colored overdue. Cards use HA theme variables,
German/English labels, keyboard-accessible controls and responsive layouts.
Image entities remain optional and are not added. Public release remains M6.

HA's pytest plugin disables requirement installation, so dev/test requirements
explicitly pin the official `home-assistant-frontend` package to each release's
frontend manifest (20260930.4/current and 20251001.0/minimum). These are test-only
dependencies. Native HTTP tests verify module injection into the actual frontend
index and static assets, and authenticated WebSocket tests verify registry fields
used by the cards. Browser tests use the real compiled module and a public-API
fixture rather than a complete HA app; a full interactive HA/Companion smoke test
is still a separate check. No claim of automatic HACS default-list submission or
published release is made.

## M4 scope, verified APIs and behavior

Before implementation, the official developer documentation at
`50b518898989b67bb76b69827f227aa6f0acd32a`, Core dev at
`506d5c077399457a9557bbe4a887f5b3229d2520` and both supported released implementations were inspected. Official
Companion documentation at `a2034d40d8e8b19ef7c75c08014e75795c45d9c5`
verifies actionable payloads, unique action identifiers, event payloads, tag
replacement/clearing and Android alert-once behavior. HACS docs remain at
`4f06a5bd11088a21a453fdcb3eda1603353e6c8a`.

| API / contract | Official reference |
| --- | --- |
| `async_get_options_flow`, `OptionsFlow.config_entry`, `async_step_init`, `async_create_entry` | [Options flow](https://developers.home-assistant.io/docs/core/integration/options_flow/) |
| Local `async_track_time_change`, startup hooks, config/time-zone changes, entry-owned tasks and unload | [Events](https://developers.home-assistant.io/docs/integration_listen_events/), public released helpers and config entries |
| Legacy notify services versus notify entity message/title limits | [Notify entity](https://developers.home-assistant.io/docs/core/entity/notify/), both released notify/mobile_app implementations |
| `data.actions`, unique action IDs, `mobile_app_notification_action` | [Companion actions](https://companion.home-assistant.io/docs/notifications/actionable-notifications/) |
| `data.tag`, `clear_notification`, `alert_once` | [Companion basic notifications](https://companion.home-assistant.io/docs/notifications/notifications-basic/) |
| Persistent create/dismiss callbacks | [Official persistent notification source](https://github.com/home-assistant/core/blob/dev/homeassistant/components/persistent_notification/__init__.py) |

Reminders default off, at 09:00 HA-local time, repeat daily on, persistent copy
off and snooze action on. Enabling requires at least one target or the persistent
copy. Target selection discovers available notify services and notify entities;
mobile_app entities are represented by their legacy mobile_app service because
the current entity API cannot carry action/tag data. Generic `send_message` and
persistent-notification bridge services are not selectable. No optional notifier
or Companion app is forced to install. A persistent-notification dependency is
required for the native persistent API.

One summary per selected recipient groups all currently due plants by care type.
Pause, vacation, disabled fertilizer and season rules are shared with the care
engine. The scheduled callback uses local wall-clock time. Startup after the
scheduled time catches up today's unsent reminder; durable per-recipient dates
prevent duplicate sends on ordinary reload, restart and a repeated DST hour.
A nonexistent DST wall time is forward-normalized with a single point-in-time
callback prepared at setup and local day changes; no recurring poll is added.
Persistent copies are restored on reload/start because HA stores them in memory.
With daily repeat off, only newly due task identities cause a scheduled summary;
completing/snoozing/pausing a task ends its due episode. No polling is introduced.

Existing mobile summaries are replaced under one entry-scoped tag when their
pending tasks change; when no work remains, the tag is cleared. Persistent copies
are updated/dismissed likewise. Other notify services/entities receive a basic
summary at the scheduled time: their APIs do not promise recall or action data.
Delivery errors are isolated by recipient and cannot change care history. HA
service acceptance cannot prove device delivery. Sending and writing a durable
receipt are not an atomic external transaction; a crash or receipt-write failure
in between can repeat a message (mobile tags replace it).

Mobile actions affect only tasks listed by that message that are still due in
the same care cycle. Opaque per-message action IDs are retained in private local
state; unrelated, stale and replayed events cannot reset healthy/later-cycle
plants. All-watered/all-fertilized affect the corresponding due list; Snooze 1 day
postpones both listed care types as one care-state transaction. No action can
bypass pause/vacation. Removing targets/disabling reminders clears known mobile
and persistent messages; temporary unavailable clear targets are retained for a
later attempt. Disabling/removing the hub also attempts message cleanup and removes reminder
receipts on deletion. Mobile clearing is best effort; Companion platform/device
limitations still apply. A fresh notify entity has unknown timestamp state but
is usable before its first send; only unavailable entities are excluded.

Runtime notification wording uses a small English/German catalog in
`notification_texts.py`, with English fallback, because HA's standard integration
translation schema has no arbitrary notification-text category. Hub options and
errors remain in strings.json and translations/en.json/de.json. Notification
text follows HA's configured language, with no user text in logging or diagnostics
other than the already allowed plant names. Notifications delegate to the user's
existing HA notifiers; PlantBased makes no network requests itself. Frontend
cards/artwork remain M5, public release M6.

## M3 scope, verified APIs and assumptions

Before M3 coding, the official developer-doc source at
`50b518898989b67bb76b69827f227aa6f0acd32a`, current Core dev at
`5aeba2ef167655fe737cda9c2f3628f7f87f9847` and both installed supported
releases were inspected. To-do runtime imports use the documented public
platform exports on both releases; static checking uses the current entity/const
modules because current Core does not mark those public re-exports in `__all__`.
The documentation websites return HTTP 403 in this
cloud session; their official Git repositories are accessible. HACS documentation
HEAD remains `4f06a5bd11088a21a453fdcb3eda1603353e6c8a`.

| M3 API | Official reference |
| --- | --- |
| Domain actions in `async_setup`, `async_register`, target schemas, `async_extract_entity_ids` | [Actions](https://developers.home-assistant.io/docs/dev_101_services/), released `helpers/service.py` and `config_validation.py` |
| Event bus `async_fire` with registry `device_id` | [Events](https://developers.home-assistant.io/docs/integration_events/) |
| `CalendarEntity.event`, `async_get_events`, all-day `CalendarEvent` with exclusive end | [Calendar](https://developers.home-assistant.io/docs/core/entity/calendar/) |
| `TodoListEntity.todo_items`, `TodoItem`, status-only `async_update_todo_item` | [To-do](https://developers.home-assistant.io/docs/core/entity/todo/) |
| `async_get_config_entry_diagnostics` | [Diagnostics](https://developers.home-assistant.io/docs/core/integration/diagnostics/) |
| Action/field and selector translations | [Internationalization](https://developers.home-assistant.io/docs/internationalization/core/#service-actions) |

Actions register once in integration setup and remain registered when the hub is
unloaded. They require explicit targets, expand group membership, deduplicate
plants and validate all direct targets before mutation. Standard device/entity,
area and label targeting uses HA's public target resolver; indirect foreign
entities in an area are ignored. Direct foreign, missing or hub targets fail.
`entity_id: all` explicitly selects all loaded PlantBased plants. No target never
means all plants. An empty valid group is a successful no-op. Intervals remain
subentry configuration; bulk snooze and marks are single storage transactions.

The calendar shows each plant's next outstanding watering/fertilizing date,
including its original overdue date when that date is in the requested range.
It does not invent repeated future actions before actual care has happened.
All-day ends are exclusive; queries use true time overlap in HA's local zone.
Paused plants/global vacation are absent. Outside the fertilizer season the
sensor's season-resume marker is resolved against the actual interval before
creating a calendar event. Disabled fertilizer is absent. Read-only calendar
mutation features are not advertised.

The to-do list contains only currently due tasks. Completing one records care
for the current local date and removes it. Other task edits are rejected. Task
UIDs include plant ID, care type and due date, preventing a stale UI completion
from marking a later care cycle done. Validation and completion share the storage
lock. Completed items are represented in care history, not retained in this
computed task list. Calendar/task text uses HA's configured language and translated
care labels; language changes refresh those labels.

`plantbased_care_due` fires once per false-to-true due transition, including
unpause, season entry and startup/reload for already-due plants; it does not fire
every overdue day. `plantbased_care_done` fires after a verified successful save,
for each selected plant/care, from buttons, date edits, actions and task completion.
The requested two event names take precedence over the docs' general naming
recommendation. Event logic belongs to the manager, never individual entities.

Diagnostics use an allowlist. Plant names are the only included user free text;
notes, species, group names, areas, location, image URLs/paths, config entry
contents and credentials are excluded. Care dates, histories, intervals, season,
pause, computed status and counts remain useful for debugging. If an entry is
disabled, unloaded or failed setup, diagnostics report entry state and counts
without accessing unavailable runtime data. Notifications are
M4; frontend cards/artwork are M5. No public release or Silver tier is claimed.

## M2 scope and current API verification

M2 adds plant/group subentries, native devices, persisted care state and the six
entity platforms: binary sensor, button, date, number, sensor and switch. Each
plant has 16 entities, each group five, and the overview six. Calendar/to-do,
integration-wide actions/events and diagnostics remain M3. Reminder options and
notifications remain M4; illustration resources, image entities and cards remain
M5. Basic snooze, pause/vacation and season calculations are implemented now
because the M2 entity controls and care statuses must already work consistently.

Before implementation, the current official developer-doc source at
`50b518898989b67bb76b69827f227aa6f0acd32a` was read alongside Core `dev` at
`4dbd9dca6febcc36a348d2a9fff69833e68fb36a`, and both installed released HA
versions. No private HA write/lifecycle API is used in the integration.

| M2 API / contract | Verified official reference |
| --- | --- |
| `async_get_supported_subentry_types`, `ConfigSubentryFlow`, `async_create_entry`, `async_update_and_abort`, reconfigure context | [Subentry flows](https://developers.home-assistant.io/docs/core/integration/config_flow/#subentry-flows) |
| `async_update_subentry`, `async_remove_subentry`, update listeners, unload hooks, platform setup/unload | [Config entries](https://developers.home-assistant.io/docs/config_entries_index/), released Core `config_entries.py` |
| `ConfigEntry.runtime_data` with a typed manager | [Runtime data](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/runtime-data/) |
| `config_subentry_id` in `async_add_entities`, device registration and registry ownership | [Device registry](https://developers.home-assistant.io/docs/device_registry_index/), released `entity_platform.py` |
| `has_entity_name`, `translation_key`, `async_added_to_hass`, `async_on_remove`, push updates | [Entity](https://developers.home-assistant.io/docs/core/entity/) |
| Native values and methods for each of the six platforms | [Sensor](https://developers.home-assistant.io/docs/core/entity/sensor/), [binary sensor](https://developers.home-assistant.io/docs/core/entity/binary-sensor/), [button](https://developers.home-assistant.io/docs/core/entity/button/), [date](https://developers.home-assistant.io/docs/core/entity/date/), [number](https://developers.home-assistant.io/docs/core/entity/number/), [switch](https://developers.home-assistant.io/docs/core/entity/switch/) |
| `async_track_time_change`, `async_at_start`, core time-zone updates | [Listening for events](https://developers.home-assistant.io/docs/integration_listen_events/), released `helpers/event.py` and `helpers/start.py` |
| Versioned `Store`, migration, atomic/private writes, public load/save/remove | [Official storage source](https://github.com/home-assistant/core/blob/dev/homeassistant/helpers/storage.py) plus both released implementations |
| Executor-based filesystem preflight | [Working with async](https://developers.home-assistant.io/docs/asyncio_working_with_async/) |
| Entity, selector, device and subentry translations | [Internationalization](https://developers.home-assistant.io/docs/internationalization/core/) |

The internationalization schema requires subentry `entry_type` and
`initiate_flow.user` (plus a reconfigure label). The small config-flow example's
`title` alone is insufficient; the integration follows the current translation
reference and all hassfest integration validators pass.

### Supported-version compatibility

- HA has used Probatio since 2026.9 and officially aliases the public
  `voluptuous` import at startup. The isolated schema module uses that supported
  alias and current Probatio types for static checking, so no extra dependency
  or guessed transition-version branch is required. See the official
  [validation-engine announcement](https://developers.home-assistant.io/blog/2026/09/30/probatio-validation-engine/).
- Current HA deprecates cross-entry `device_registry.async_get_device` lookups.
  The integration uses `async_entries_for_config_entry` and identifiers scoped
  to the owning hub, which is supported by both versions and avoids deprecation
  warnings. `suggested_area` is only passed when registering the device; explicit
  subentry area edits use `async_update_device(area_id=...)`.
- Subentry edits use `async_update_and_abort` with the shared entry update
  listener. `async_update_reload_and_abort` must not be combined with that
  listener on current HA. Creates, reconfigure, interval edits and removal use
  the same reload lifecycle and preserve stable entity/device identities.
- Existing hub entries remain version 1. M1 had no subentries or runtime store,
  so there is no existing M1 care data to migrate. New Store version 1 includes
  an explicitly defined internal pre-release v0 migration fixture; v0 was never
  a published PlantBased storage format. Unsupported versions are not reset.

### Scheduling and UX assumptions

- All dates use HA's configured time zone and calendar-day arithmetic. Midnight
  uses `async_track_time_change`; a time-zone setting change resubscribes it and
  recalculates the local day. There is no periodic polling.
- A due task starts on `today >= last_date + interval + snooze`. Negative day
  counts remain visible while paused, but due flags and overdue overview counts
  exclude paused plants. Unpausing resumes the original dates without shifting.
- Fertilizing seasons include complete boundary months and may cross New Year.
  A season covering all 12 months behaves like all-year mode. Disabled
  fertilizing has no next date. Outside a season the next-fertilizing sensor is
  the requested **season-resume marker**; the original interval is checked again
  when the season opens. A far-future interval is therefore not prematurely due
  merely because that marker is displayed.
- Snoozing overdue care moves it to at least tomorrow; repeating snooze extends
  the current postponed date. Each care type has its own offset, reset by marking
  that care done or correcting its date.
- Creation-only seed dates default to today. Reconfigure changes settings;
  date entities edit runtime last-care dates, so ordinary reconfiguration cannot
  reset history. Last-care dates entered by users cannot be in the future.
- Every button/date correction is retained in operation order, allowing repeated
  dates, with only the last 10 dates per care type kept. Groups act on all current
  members, including paused plants; they never act on other groups.
- HA generates each subentry ID. There is no external plant identifier, so a
  name is not used as `unique_id`; duplicate names are allowed. Device and entity
  identities use the immutable subentry ID.
- Optional image presets and custom URLs are metadata in M2. No guessed frontend
  URL is emitted for not-yet-shipped illustrations, and the backend never fetches
  user image URLs. No image entity or resource registration is claimed yet.

### Persistence and failure behavior

Configuration (including intervals) belongs to HA subentries. Dates, snoozes,
histories, individual pause and global vacation belong to one private, atomic
Store per hub. State mutations are serialized by a lock; unload waits for an
in-flight write. New actions are rejected during HA shutdown.

HA Store logs and swallows some write errors. PlantBased therefore confirms
the candidate snapshot with a fresh public Store read before acknowledging a
care action or updating entities. This deliberately trades one small async read
per write for a checked save, without overriding HA's private write methods.
JSON/envelope preflight also runs in the executor before Store loading: malformed
existing files remain unchanged and cause a translated setup failure instead of
being mistaken for a new hub. Tests cover the real swallowed-write-error path,
repeated loading of corrupt files, migration, pruning and concurrent care.

Silver is still a target rather than a claimed tier; the later diagnostics,
actions, calendar/to-do and applicable remaining quality rules are outstanding.

## M1 scope and assumptions

- M1 creates only the hub. No fake devices, placeholder entities, actions, storage
  files, or frontend registration are introduced before their milestone.
- `0.1.0` is the requested manifest version. The public release is deferred to M6;
  the README and confirmation dialog identify the unfinished scope.
- The single hub's stable config-entry unique ID is `plantbased`. The manifest's
  `single_config_entry` and unique-ID checks prevent duplicate setup, including
  overlapping confirmation dialogs. No user-controlled names identify the hub.
- The empty confirmation form needs no schema library. This avoids binding M1 to
  schema-library changes between minimum and current HA releases.
- No YAML, authentication, network, or Python dependencies are needed at runtime.
  Frontend/mobile-app dependencies will be added only when actually used.
- HA 2026.10.2 requires Python ≥3.14.2. The minimum HA 2025.10.0 is tested with
  Python 3.13. Each test target uses its compatible custom-component test plugin.
- No quality-scale tier is claimed. Silver needs the later implementation,
  diagnostics, and applicable tests; a skeleton is insufficient.

## Documentation review (2026-10-17)

The websites were denied by cloud egress policy. Their current official source
repositories were read using the supported HTTPS Git route:

- `home-assistant/developers.home-assistant` at
  `50b518898989b67bb76b69827f227aa6f0acd32a`.
- `hacs/documentation` at `4f06a5bd11088a21a453fdcb3eda1603353e6c8a`.
- HA Core `dev` at `b7a099a1f282cdcbbfefe8332d6de39de73aacee` was inspected
  alongside the docs for actual signatures. Tests use published HA versions.

Verified M1 APIs and contracts:

| Contract | Official documentation |
| --- | --- |
| `ConfigFlow`, `async_step_user`, `async_set_unique_id`, `_abort_if_unique_id_configured` | [Config flow](https://developers.home-assistant.io/docs/core/integration/config_flow/) |
| `async_show_form`, `async_create_entry` | [Data entry flow](https://developers.home-assistant.io/docs/data_entry_flow_index/) |
| `async_setup_entry`, `async_unload_entry`, setup/removal lifecycle | [Config entries](https://developers.home-assistant.io/docs/config_entries_index/) |
| `single_config_entry`, custom version, `hub`, `calculated`, `requirements` | [Manifest](https://developers.home-assistant.io/docs/creating_integration_manifest/) |
| `strings.json`, expanded EN/DE translations | [Translations](https://developers.home-assistant.io/docs/internationalization/core/) |
| Directory structure, metadata, and local brand assets | [HACS integration publishing](https://hacs.xyz/docs/publish/integration/) |
| Official validation and default-catalog requirements | [HACS action](https://hacs.xyz/docs/publish/action/), [catalog](https://hacs.xyz/docs/publish/include/) |
| Local brand images since HA 2026.3 | [Brand images](https://developers.home-assistant.io/docs/core/integration/brand_images/) |

`render_readme` remains accepted by HACS's current `HACS_MANIFEST_JSON_SCHEMA`,
although the general publishing page no longer lists it. It is retained as
explicitly requested. Test support additionally uses HA's entry manager and
`async_get_translations`; these were checked against current Core signatures.

## Domain collision check

Before implementation, the full tracked tree of current HA Core was checked:
`homeassistant/components/plantbased` does not exist. The current `hacs/default`
integration catalog contains no repository named PlantBased (case-insensitive).
Relevant plant-care entries are also checked for their actual integration domain.
This is a point-in-time check, not a domain reservation; repeat before release.

Checked catalog domains: `plant_care`, `planta`, `simple_plant`, `plantlab`,
`smartyplants`, `openplantbook`, and `plant_diary`. This is the catalog-name and
relevant-manifest check. After the network settings were saved, the complete
generated HACS index at `https://data-v2.hacs.xyz/integration/data.json` was read:
all 3,225 entries had a domain field, and none matched `plantbased`
case-insensitively. The GitHub API also confirmed that Core's
`homeassistant/components/plantbased` path does not exist on `dev`.

## Branding and HACS publication

Original MIT-licensed source artwork lives under `assets/brand/`. The integration
ships local `brand/` images supported by HA ≥2026.3 and current HACS. On HA
2025.10, a generic fallback is acceptable; this does not increase the minimum.
The same square sprout is the icon and logo: the official brands specification
supports the icon-as-logo fallback. Both normal/hDPI and light/dark PNGs ship.

HACS default-catalog submission is outside v0.1.0 scope. Before a later submission:
publish the complete implementation, pass hassfest and HACS without ignores,
confirm the domain again, set description/topics, enable issues, and create a
GitHub release. A future HA Core contribution requires moving assets to
`home-assistant/brands/core_integrations/plantbased` through its review process.
No external brands PR has been opened.

GitHub API access returned a proxy tunnel denial (`403`) at `api.github.com`.
An existing GitHub variable was detected and used for that read-only check;
no credential values were displayed or requested. This establishes a network
blocker, not missing authentication. Git access works through the platform proxy.
After the user saved the environment settings, current runtime observations
reported the additional destinations as enforced. GitHub API and HACS-index
requests returned HTTP 200 with the existing authentication. HACS publishing
documentation also returned HTTP 200. The HA documentation website still
returned HTTP 403, so the verified official source references above remain the
documentation basis. The full HACS action requires a GitHub revision containing
this milestone. Its license check reads GitHub's repository-level license
metadata, which is based on the default branch; adding LICENSE on a feature
branch alone does not satisfy that bootstrap requirement.
Repository settings updates for description and topics were attempted through
the existing authenticated GitHub API route and rejected with HTTP 403,
`Resource not accessible by integration`. Native Git's branch-push dry run
succeeded. These are distinct operation scopes; no replacement secret is needed
for the working Git route. The owner can supply description/topics in GitHub's
About editor. No HACS checks are bypassed to hide these prerequisites.

The user subsequently set description/topics and merged the MIT-only PR #2.
GitHub now detects MIT on `main`. Both previously failed HACS jobs passed on
retry, making the push and pull-request workflows fully green on implementation
commit `cd28af4a46853b953e20786bc6074d9947653d0f`. The earlier 403s and HACS
metadata failures are resolved prerequisites, not outstanding environment or
application defects. The integration code was unchanged during that resolution.

## Future milestones

Reverify subentry APIs, entity translations/naming, storage migration, scheduling,
and frontend registration before implementation. M1 does not claim verification
of unused APIs. Do not assume current subentry or frontend APIs are identical on
HA 2025.10 and HA 2026.10. Document compatibility paths with actual tests.
