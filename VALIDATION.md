# Validation

## v0.2.2 — compact automatic room dashboards

Prepared for user review; publication follows the reviewed PR merge.

| Check | Executed local result |
| --- | --- |
| HA 2026.10.2 / Python 3.14.2 | **234 passed**, no skips or expected failures |
| HA 2025.10.0 / Python 3.13.2 | **234 passed**, no skips or expected failures |
| Integration statement/branch coverage | **98.06% current / 98.07% minimum** |
| Strict mypy / Ruff lint and format | Passed; 26 integration modules |
| TypeScript / Prettier / committed bundle | Passed; unchanged compiled frontend |
| Playwright / Chromium | **33 passed** |
| Actual-filesystem persistence, both HA versions | Passed |
| Release ZIP | **129,622 bytes**; both Python outputs byte-identical |

Four new real-HA tests verify three visible primary entities per plant, ten hidden
but enabled auxiliary entities, working hidden care buttons, original entity IDs,
one-time migration of existing plants, preserved user-hidden/disabled choices,
manual re-show surviving reload and unchanged care history. New config flows
record minor version 2. Future major versions are not migrated.

The initial minimum-version run overlapped Vite's output-directory rebuild and
failed while reading the temporarily absent bundle. The full minimum suite was
rerun after the build completed; all 234 tests passed without test changes.

Candidate SHA-256:

```text
f78ddf020c6b8a2d7e6180d867e7f18be5a2ef3844f37c4b54a081408cc4a97d  plantbased.zip
```

HA owns automatic room rendering. Official frontend source confirms hidden-entity
and category filtering; a full HA browser capture of the reduced room layout
remains manual. The PR checks record official hassfest/HACS acceptance.

---

## v0.2.1 — creation from the sidebar overview

Prepared for user review; publication follows the reviewed PR merge.

| Check | Executed local result |
| --- | --- |
| HA 2026.10.2 / Python 3.14.2 | **230 passed**, no skips or expected failures |
| HA 2025.10.0 / Python 3.13.2 | **230 passed**, no skips or expected failures |
| Integration statement/branch coverage | **98.04% current / 98.05% minimum** |
| Strict mypy / Ruff lint and format | Passed; 26 integration modules |
| TypeScript / Prettier / Vite build | Passed; **78.29 kB / 21.43 kB gzip** |
| Playwright / Chromium 154.0.8037.57 | **33 passed**, including all existing card/panel tests |
| Actual-filesystem persistence, both HA versions | Passed |
| Official local hassfest | 1 integration, 0 invalid; all validators |
| Release ZIP | **129,065 bytes**; both Python outputs byte-identical |

Four new native HA HTTP tests exercise the exact authenticated subentry endpoints
used by the panel: plant/group creation from returned schema defaults, local initial
care dates, optional groups, area and interval values, unchanged existing history,
duplicate-submit rejection, validation, cancellation and non-admin denial. Backend
implementation modules are not mocked or changed.

Six new browser tests exercise the compiled module and actual integration language
resources: opening both dialogs, default values, native selector controls, typed
values/omitted blanks, server validation, visible request failures, duplicate-submit
protection, cancellation, detached late-flow cleanup, unloaded-hub retry, keyboard
focus, mobile width and always-visible dialog actions. Native browser dialogs trap
focus; field contents scroll independently from the action buttons.

No species database or external provider calls are added. Research references and
the distinction between display names, species and editable recommendations are
recorded in DECISIONS.md. The README now features the project owner's original
v0.2.0 Home Assistant screenshot, uploaded as `docs/images/Screenshot Overview.png`.
Its caption distinguishes it from the additional browser fixture previews.

Candidate SHA-256:

```text
6605452e89065270042e985f1763485470ad516bee6c801046844f544af6f830  plantbased.zip
```

Reproduce through CONTRIBUTING.md using both Python environments, filesystem
checks, `npm test`, and `python -m script.build_release --tag v0.2.1`. Official local
hassfest used Core source `1b740dcd4bc1e669827fc94c8b4bd7a4bbbae734` and its existing
isolated environment. Full interactive HA/Companion acceptance remains manual.
The PR body/checks record final GitHub acceptance. Historical records follow.

---

## v0.2.0 — sidebar and visual plant overview

The new version is prepared for user review; publication follows the PR merge.
The PR checks/body record remote acceptance for the final commit.

| Check | Executed local result |
| --- | --- |
| HA 2026.10.2 / Python 3.14.2 | **226 passed**, no skips or expected failures |
| HA 2025.10.0 / Python 3.13.2 | **226 passed**, no skips or expected failures |
| Combined integration statement/branch coverage | **98.04% current / 98.05% minimum** |
| Strict mypy | Passed on all 26 integration modules |
| Ruff lint / format | Passed |
| TypeScript / Prettier / Vite production build | Passed; **67.13 kB / 18.80 kB gzip** |
| Playwright / Chromium 154.0.8037.57 | **27 passed**, including all existing card tests |
| Actual-filesystem care/reminder persistence, both versions | Passed |
| Official local hassfest | 1 integration, 0 invalid; all validators |
| Release ZIP | **126,458 bytes**, valid/extractable; byte-identical on both Python versions |

HA-native tests verify panel registration in actual `get_panels` responses,
authenticated entity/device/area registry reads for admins and read-only users,
direct page HTTP bootstrap, reload/removal lifecycle, failed unload preserving the
page, stable care history and process-wide asset registration. Existing care,
reminder and package-rejection tests remain included. No HA modules are replaced.

Ten added browser tests exercise the compiled panel: all-plant cards, group
collages/empty groups, expandable members, area moves/renames, unassigned plants,
search, due-only filtering, admin links, escaped names, safe care targets,
disconnects, retries, subscription cleanup, touch controls and light/dark layouts.
Keyed rendering preserves an expanded group when preceding cards are filtered out.
Existing card fixtures moved into a shared helper; their 17 assertions/tests remain.

Committed screenshots in `docs/images/panel-*.png` are actual Chromium fixture
captures with demonstration data. They are not a full Home Assistant installation
or a claim of manual Companion/process-restart acceptance. The sidebar menu event
and custom-panel contract were checked in official frontend source; API references
and lifecycle choices are recorded in DECISIONS.md.

The local candidate SHA-256 is:

```text
5dba46ec5c859ec0e6f786f3e24e8aae1adba040a22f0cb73ed94a5be07a85f2  plantbased.zip
```

Reproduce with CONTRIBUTING.md's checks, `pytest` and filesystem checks in both
Python environments, `npm test`, and `python -m script.build_release --tag v0.2.0`.
Official local hassfest used Core source
`1b740dcd4bc1e669827fc94c8b4bd7a4bbbae734` with its isolated validator environment.
The unchanged CI workflow runs official HACS/hassfest, both HA targets, browser
checks, strict quality checks and the actual release-package preflight.

Earlier version and milestone evidence follows as historical records.

---

## v0.1.1 — optional groups and inherited areas

The patch is prepared for review; v0.1.1 publication follows the user's PR merge.
GitHub checks and the PR body record remote acceptance for the final commit.

| Check | Executed local result |
| --- | --- |
| HA 2026.10.2 / Python 3.14.2 | **223 passed**, no skips or expected failures |
| HA 2025.10.0 / Python 3.13.2 | **223 passed**, no skips or expected failures |
| Combined integration statement/branch coverage | **98.03% current / 98.04% minimum** |
| Strict mypy | Passed on all 26 integration modules |
| Ruff lint / format | Passed |
| Prettier / Vite committed bundle check | Passed; shipped frontend unchanged |
| Actual-filesystem care/reminder persistence, both versions | Passed |
| Official local hassfest | 1 integration, 0 invalid; all validators |
| Release package | **121,681 bytes**; both Python outputs byte-identical |

Twenty-one additional tests exercise HA-native schema serialization and subentry
flows, omitted/explicit **No group** creation and unassignment, area precedence,
own-area fallback, moving/removing groups, native registry edits, deleted HA areas,
unload/reload and listener cleanup. Existing device identity, care history and
standalone areas survive these operations. Both language resources are loaded
through HA's translation helper. All existing package rejection gates now derive
the release version from the actual manifest and still execute unchanged checks.

The new area coordinator uses public registry events; coalesced parent/member
updates prevent HA area deletion from overwriting restored fallback areas. Pure
area edits refresh metadata without reloading the live care manager, avoiding
reentrant reloads midway through registry synchronization. Tests
run against actual supported HA implementations, without replacing HA modules.
The browser workflow still runs the existing 17 frontend tests. No full interactive
HA installation or process restart is claimed for this patch.

The final local candidate's SHA-256 is:

```text
b0ec2c5ff3a03c1292761b2f9f716781a46d4cda90e6cca5f4645cff2f6cc709  plantbased.zip
```

Reproduce using CONTRIBUTING.md, then run both `pytest` environments,
`python -m script.check_storage` in each, and `python -m script.build_release
--tag v0.1.1`. Official local hassfest used Core source
`1b740dcd4bc1e669827fc94c8b4bd7a4bbbae734` with the existing isolated validator
environment. No checks are ignored. Earlier milestone records follow.

---

## M6 — documentation, automation examples and release preflight

M6 prepares the complete v0.1.0 documentation and release machinery. A passing PR
build is not a published release: the version tag and public release follow the
reviewed M6 merge. Exact-head remote validation is recorded in the PR checks/body.

| Check | Executed result |
| --- | --- |
| HA 2026.10.2 / Python 3.14.2 | **202 passed**, no skips or expected failures |
| HA 2025.10.0 / Python 3.13.2 | **202 passed**, no skips or expected failures |
| Combined integration statement/branch coverage | **98.60% current / 98.61% minimum** |
| Strict mypy | Passed on all 25 integration modules |
| Ruff lint / format | Passed |
| TypeScript / Prettier / Vite committed bundle check | Passed |
| Playwright / local Chromium 154.0.8037.57 | **17 passed** |
| Actual-filesystem care/reminder persistence, both versions | Passed |
| Official actionlint 1.7.12 | Both workflows passed |
| Release package and checksum | **118,141 bytes**, valid/extractable ZIP |
| Cross-Python repeatable package | Python 3.13.2 and 3.14.2 outputs byte-identical |

The full M1–M5 integration suite remains included. Fifteen new packaging tests
exercise actual ZIP creation and extraction, complete byte-for-byte runtime file
inclusion, compileable extracted Python files, twelve SVGs, both licenses,
checksums, fixed metadata and repeatability. They reject mismatched/unstable tags,
frontend/lockfile version differences, missing notes/assets, modified illustrations,
tracked symlinks/caches and omit untracked local files. The publisher will repeat
version/hash/content verification before making any release public.

Two new HA-native tests load the exact example YAML files into HA's actual
automation engine. Integration reload emits real due events and creates separate
water/fertilizer notifications. A successful real care action emits done and
removes only the matching message. The manually triggered group example changes
only current members. Both supported releases execute these tests without mocks
of the automation engine or PlantBased actions.

The local candidate's SHA-256 is:

```text
a6f946c1689ea17c287a3161437aa4efc7b1b17807560608ae7b085a5e65c7cc  plantbased.zip
```

Reproduce the environments and frontend commands in CONTRIBUTING.md, then:

```sh
COVERAGE_FILE=/tmp/plantbased-m6-cov-current/data .venv/bin/pytest
COVERAGE_FILE=/tmp/plantbased-m6-cov-min/data .venv-min/bin/pytest
.venv/bin/python -m script.check_storage
.venv-min/bin/python -m script.check_storage
.venv/bin/python -m script.build_release --tag v0.1.0 --output /tmp/plantbased-m6-current-package
.venv-min/bin/python -m script.build_release --tag v0.1.0 --output /tmp/plantbased-m6-min-package
cmp /tmp/plantbased-m6-current-package/plantbased.zip /tmp/plantbased-m6-min-package/plantbased.zip
```

The official actionlint binary was downloaded from its GitHub release and verified
against that release's SHA-256 checksum list before use. Its schema/shell checks
cover the reusable validation workflow and tag-gated publisher. Branch/PR CI now
has seven jobs, including an actual release-package preflight/candidate artifact.
Hassfest and HACS remain official unmodified validators without ignores; their
exact-head remote outcome is recorded in the PR.

No version tag or public release is created during PR work. The final tag workflow,
GitHub asset publication and HACS installation from that public release remain
unexecuted until after the user merges M6. No full interactive HA/browser test,
process-level restart or real phone delivery is claimed. Actual Chromium fixture
previews are labeled as such; full HA/Companion capture placeholders are explicit.
See docs/RELEASING.md and docs/QUALITY.md for the release and acceptance boundaries.

Earlier milestone evidence follows as historical records.

---

## M5 — dashboard cards, editors and original illustrations

M5 is implemented. Results below executed locally on the final implementation;
remote acceptance is recorded against the PR head in its checks and description.

| Check | Result |
| --- | --- |
| HA 2026.10.2 / Python 3.14.2 | **185 passed**, no skips or expected failures |
| HA 2025.10.0 / Python 3.13.2 | **185 passed**, no skips or expected failures |
| Combined statement/branch coverage | **98.54% current / 98.55% minimum** |
| Strict mypy | Passed on all 25 integration modules |
| Ruff lint and formatting | Passed |
| TypeScript strict check and Prettier | Passed |
| Vite production build | One JS module, **47.47 kB / 14.23 kB gzip**, bundled Lit |
| Chromium 154.0.8037.57 / Playwright | **17 passed**, no skips |
| Original SVGs | 12 distinct, safe, rendered originals; source/shipped parity |
| Official local hassfest | 1 integration, 0 invalid; all integration validators |
| Independent actual-filesystem checks, both HA versions | Care and reminder stores passed |

The full M1–M4 suite remains included. New HA-native tests check idempotent static
registration across entry reload/removal, actual HTTP serving of the committed
bundle and all SVGs, module injection into the official HA frontend index, and
authenticated device/entity registry responses including translation keys,
unique IDs and config-subentry ownership. Preset URLs and fertilizing metadata
are checked on real care-status entities. No requirement auto-installation is
needed: test-only frontend wheels match each supported HA manifest.

Seventeen browser tests load the actual compiled production module. They cover
plant/group/overview cards, real hub count consumption, care status pushes,
renames/group changes, scoped actions and independent snooze, pending/error
feedback, paused/unavailable/disabled-fertilizer states, registry recovery,
reconnect/unsubscribe, safe image fallback and escaped user text. They also check
stub configuration, duplicate module loads, empty/missing/deleted selection,
visual-editor filtering and bubbling config changes, title/action options,
German labels, keyboard operation, minimum touch size, narrow desktop columns,
mobile/dark layouts and all twelve rendered SVG illustrations.

The browser fixture supplies the public HA connection/state contract; it does not
run the complete HA application. Native backend HTTP/WS tests independently
exercise the APIs that fixture represents on both supported releases. Screenshots
were visually inspected in the local Chromium run. CI uploads mobile, desktop,
dark and gallery images plus any failure traces. No full HA browser/Companion
manual test, real phone delivery or full HA process restart is claimed.

Reproduce using CONTRIBUTING.md's two Python environments and Node 24:

```sh
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy
COVERAGE_FILE=/tmp/plantbased-m5-cov-current/data .venv/bin/pytest
COVERAGE_FILE=/tmp/plantbased-m5-cov-min/data .venv-min/bin/pytest
.venv/bin/python -m script.check_storage
.venv-min/bin/python -m script.check_storage
npm ci
npm run typecheck
npm run format:check
python3 script/build_illustrations.py
npm run check:bundle
CHROMIUM_PATH=/usr/bin/chromium npm test
```

Official local hassfest used Core dev
`1b740dcd4bc1e669827fc94c8b4bd7a4bbbae734` with the same command/environment
recorded below for M4. See DECISIONS.md for current frontend references and public
module-registration assumptions. Public release and release automation remain M6.

Earlier milestone evidence follows as historical records.

---

## M4 — reminder options, scheduled summaries and mobile actions

M4 is implemented. The following executed locally on the milestone's final
implementation. Its PR checks/description record exact-head remote CI acceptance;
local success alone does not establish a successful GitHub run.

| Check | Result |
| --- | --- |
| HA 2026.10.2 / Python 3.14.2 | **181 passed**, no skips or expected failures |
| HA 2025.10.0 / Python 3.13.2 | **181 passed**, no skips or expected failures |
| Combined statement/branch coverage | **98.51%** on each target |
| Strict mypy | Passed on all 24 integration modules |
| Ruff lint and formatting | Passed |
| Official local hassfest | 1 integration, 0 invalid; all integration validators |
| Independent actual-filesystem checks, both HA versions | Care and reminder stores passed |

The M1–M3 suite remains included. M4 adds real options-flow tests, live service and
notify-entity discovery, unknown initial notify timestamps, supported title
features, stale target removal and no-target validation. Public notify service
receivers capture payloads without contacting an external provider. Modern notify
entity tests use HA's actual notify entity component and send_message service.
Persistent notifications use HA's real public create/dismiss/callback API.

Frozen-time tests cover grouped summaries, daily and new-task-only reminders,
startup catch-up, durable reload deduplication, both Europe/Berlin DST changes,
a skipped 02:30 clock time and a repeated hour. They cover language changes,
English/German/fallback content, optional snooze buttons, one-transaction bulk
snooze, care completion, tag replacement/clearing, pause/vacation, disabled
fertilizer, target removal/recovery, hub disabling/deletion and persistent-copy
restoration. Mobile events exercise wrong/malformed action IDs, replays, later
care cycles and revalidation after waiting for the care lock.

Failure tests cover independent recipients, care write failure with no done
event, reminder receipt write failure without changing care, malformed receipt
schemas and setup failure without overwriting the reminder store. Diagnostics do
not export notification target IDs or action tokens. Existing native calendar,
to-do, events, storage and diagnostics tests continue to pass.

Reproduce with the environments in CONTRIBUTING.md. Separate coverage directories
avoid interference when running both jobs concurrently:

```sh
mkdir -p /tmp/plantbased-m4-cov-current /tmp/plantbased-m4-cov-min
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy
COVERAGE_FILE=/tmp/plantbased-m4-cov-current/data .venv/bin/pytest --cov-report=xml:/tmp/plantbased-m4-current-coverage.xml
COVERAGE_FILE=/tmp/plantbased-m4-cov-min/data .venv-min/bin/pytest --cov-report=xml:/tmp/plantbased-m4-min-coverage.xml
.venv/bin/python -m script.check_storage
.venv-min/bin/python -m script.check_storage
```

The real-file check independently verifies private care and reminder files,
actual JSON save/fresh read, receipt restoration, corruption preservation and
removal. Official local hassfest uses Core source
`506d5c077399457a9557bbe4a887f5b3229d2520` in the cached checkout:

```sh
PATH=/workspace/.venvs/plantbased-hassfest/bin:$PATH \
PYTHONPATH=/tmp/plantbased-m3-core \
/workspace/.venvs/plantbased-hassfest/bin/python -m script.hassfest \
  --action validate \
  --integration-path /workspace/PlantBased/custom_components/plantbased
```

No real phone/provider delivery, browser manual test or full HA process restart
is claimed. The API payloads, real HA services, native lifecycle and durable
filesystem restoration are tested separately. HA's standard custom-integration
warning is not suppressed; injected failures deliberately log generic warnings.
Provider acceptance/clearing limits and the delivery/receipt crash window are
explicit in DECISIONS.md. Frontend/cards remain M5; public release remains M6.

Earlier milestone evidence follows as historical records.

---

## M3 — actions, events, calendar, to-do and diagnostics

The M3 backend is implemented. These results executed locally on the milestone's
final implementation. Exact-head GitHub validation is recorded in its PR checks
and PR description; local success alone does not establish remote acceptance.

| Check | Result |
| --- | --- |
| HA 2026.10.2 / Python 3.14.2 | **131 passed**, no skips or expected failures |
| HA 2025.10.0 / Python 3.13.2 | **131 passed**, no skips or expected failures |
| Combined statement/branch coverage | **99.37%** on each target; 100% statements |
| Strict mypy | Passed on all 20 integration modules |
| Ruff lint and formatting | Passed |
| Official local hassfest | 1 integration, 0 invalid; all integration validators |
| Independent actual-filesystem checks, both HA versions | Passed |

The full M2 suite remains included. M3 additionally exercises real HA domain
services with native device/entity/UUID/area/label targets, group membership,
deduplication, explicit all-plant selection, invalid-target rejection without
partial mutations, empty groups, unloaded/stopping hubs and integer day schemas.
Bulk configuration edits survive reload; concurrent care actions preserve history.

Event tests subscribe to HA's bus and check registry device IDs, independent care
types, exactly-on-transition due events, startup/reload, unpause, season entry,
snooze expiry, button/date operations and no done event after a failed write.
Native calendar/get_events and todo/get_items/update_item services verify actual
platform registration, all-day dates, completion, shared state updates, language
changes, snooze, pause/vacation, reload and removal. Exact range boundaries,
midday overlap and both Europe/Berlin DST changes are tested. Seasonal markers
cannot create a premature calendar fertilizing event. Stale and concurrent task
completion is checked again under the storage lock; failed saves retain tasks.

Diagnostics are tested both directly and through HA's authenticated diagnostics
download endpoint, including disabled entries and setup failures without loaded
runtime data. The allowlist excludes notes, species, area/location text,
group names and image addresses; returned histories cannot mutate runtime data.
Action/field, entity and care-label translations load through HA in English and
German. No new integration runtime dependency, polling or network call is added.

Reproduce using the environments in CONTRIBUTING.md:

```sh
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy
.venv/bin/pytest
.venv/bin/python -m script.check_storage
COVERAGE_FILE=.coverage.min .venv-min/bin/pytest --cov-report=xml:/tmp/plantbased-m3-min-coverage.xml
.venv-min/bin/python -m script.check_storage
```

Official local hassfest used Core source
`5aeba2ef167655fe737cda9c2f3628f7f87f9847`:

```sh
PATH=/workspace/.venvs/plantbased-hassfest/bin:$PATH \
PYTHONPATH=/tmp/plantbased-m3-core \
/workspace/.venvs/plantbased-hassfest/bin/python -m script.hassfest \
  --action validate \
  --integration-path /workspace/PlantBased/custom_components/plantbased
```

No browser-based manual test or complete HA process restart is claimed. Actual
storage serialization and fresh reads are separately exercised on real files;
HA-native reloads are covered in the integration suite. HA's standard custom
integration warning is not suppressed. Notifications/actionable mobile buttons
remain M4; frontend cards/illustrations remain M5; release remains M6.

The earlier milestone records follow for historical reference.

---

## M2 — plants, groups, scheduling and persistence

The M2 backend is implemented. The following checks executed locally on the
exact source in this milestone. The associated GitHub PR checks establish remote
acceptance for its final revision; local success alone does not establish that.

| Check | Result |
| --- | --- |
| HA 2026.10.2 / Python 3.14.2 | **90 passed**, no skips or expected failures |
| HA 2025.10.0 / Python 3.13.2 | **90 passed**, no skips or expected failures |
| Combined statement/branch coverage | **99.50%** on each target; 100% statements |
| Strict mypy | Passed on all 16 integration modules |
| Ruff lint and formatting | Passed |
| Official local hassfest | 1 integration, 0 invalid; all integration validators |
| Independent actual-filesystem checks, both HA versions | Private permissions, save/fresh read, corrupt-file preservation, removal passed |

Tests use HA's real subentry flow manager, device/entity registries, native entity
services and time trackers. They verify 16 entities per plant, five per group and
six on the hub, including member-only bulk care, independent timers, date and
interval edits, stable identity through reconfigure, area changes, group/plant
removal, reload persistence and bounded concurrent histories. Calendar edge
cases include leap years, inclusive and wrapping seasons, continuous year-round
seasons, disabled fertilizing, snooze, pause/vacation, local midnight after both
DST changes and runtime time-zone changes.

Failure tests exercise actual HA Store write-error handling, unsupported storage
versions, malformed runtime values, repeated reload of corrupt JSON without a
reset, unavailable targets, future-date rejection and failed platform unload.
Both English and German resources are loaded through HA's translation helper;
all entity translation keys are registered and both language files match.

The test suite's standard HA storage fixture isolates test state. Separate
unmocked Python processes additionally exercised PlantStore with temporary real
files on both HA versions, checking on-disk JSON, restrictive file modes, fresh
reads, repeated corruption rejection and file removal. These are distinct from
coverage measurements and a full HA process restart/browser test.

Reproduce from the repository root using CONTRIBUTING.md's installed environments:

```sh
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy
.venv/bin/pytest
.venv/bin/python -m script.check_storage
COVERAGE_FILE=.coverage.min .venv-min/bin/pytest --cov-report=xml:/tmp/plantbased-m2-min-coverage.xml
.venv-min/bin/python -m script.check_storage
```

Local hassfest used official Core source
`4dbd9dca6febcc36a348d2a9fff69833e68fb36a` and its isolated validator environment:

```sh
PATH=/workspace/.venvs/plantbased-hassfest/bin:$PATH \
PYTHONPATH=/tmp/plantbased-m2-core \
/workspace/.venvs/plantbased-hassfest/bin/python -m script.hassfest \
  --action validate \
  --integration-path /workspace/PlantBased/custom_components/plantbased
```

No normal-operation PlantBased error or API deprecation warning was observed.
HA's standard warning about loading a custom integration is generated by Core;
it is not suppressed. Fault-injection tests deliberately produce error logs.
No browser-based manual test is claimed. Calendar/to-do, integration actions and
events, diagnostics, reminders and frontend cards remain later milestones.
See DECISIONS.md for verified APIs, compatibility and scheduling assumptions.

The original M1 evidence is retained below as a historical milestone record.

---

## M1 validation — 2026-10-17

**M1 is implemented and validated locally and by GitHub CI.**
GitHub delivery and remote checks are tracked below. No release or HACS
default-catalog submission has been performed.

## Executed results

| Check | Result |
| --- | --- |
| HA 2026.10.2, Python 3.14.2, test plugin 0.13.373 | **7 passed**, no skips or expected failures |
| HA 2025.10.0, Python 3.13.2, test plugin 0.13.285 | **7 passed**, no skips or expected failures |
| Python coverage, each HA target | **100% statements and branches** of M1: 19 statements, 2 branch exits |
| Ruff 0.17.1 lint and format check | Passed |
| mypy 2.4.0, strict, 3 integration source files | Passed |
| Official hassfest, all integration validators | **1 integration, 0 invalid** |
| Official HACS manifest schemas | `hacs.json` and integration manifest passed |
| Official HACS local brand validator | Passed with the actual checkout's PNG file paths |
| GitHub hassfest and HACS actions | Passed on implementation commit `cd28af4` |
| GitHub quality and both HA test jobs | Passed on implementation commit `cd28af4` |
| PNG specification | 4 RGBA PNGs; normal 256×256, hDPI 512×512 |
| Brand regeneration | `script/build_brand.py` executed successfully |
| GitHub workflow, issue templates, Dependabot YAML | Parsed successfully |
| Whitespace errors | `git diff --check` passed |
| Complete current HACS integration-domain index | 3,225 entries checked; no `plantbased` collision |
| Current Core domain check | GitHub API confirms no `plantbased` component on `dev` |
| Reusable cloud install script | Executed twice successfully, preserving usable environments |

The coverage percentage describes only the small hub skeleton. It does not
measure or establish readiness of the planned plant-care features.

The seven tests cover explicit confirmation, creation and entry data, stable
unique ID, real setup/reload/unload/removal, singleton enforcement for existing
entries, parallel flows, an entry appearing during confirmation, both languages
through HA's translation loader, and translation-key parity. There are no mocked
Home Assistant implementation modules. No browser-based manual UI test was run.

## Reproduce the integration checks

From `/workspace/PlantBased`, after the setup in CONTRIBUTING.md:

```sh
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy
.venv/bin/pytest
COVERAGE_FILE=.coverage.min .venv-min/bin/pytest --cov-report=xml:/tmp/plantbased-min-coverage.xml
```

The separate coverage file prevents the minimum/current runs from competing for
the same report. All generated environments and reports are excluded from Git.

### Official validators used locally

hassfest was run from the official HA Core source at
`b7a099a1f282cdcbbfefe8332d6de39de73aacee`, with that checkout's requirements and
its own isolated environment. No validators were skipped. The command from that
Core checkout was:

```sh
PATH=/workspace/.venvs/plantbased-hassfest/bin:$PATH \
PYTHONPATH=/tmp/plantbased-research/core \
/workspace/.venvs/plantbased-hassfest/bin/python -m script.hassfest \
  --action validate \
  --integration-path /workspace/PlantBased/custom_components/plantbased
```

The HACS source at `04fac58f2b04e263370c6ba9a7a3df0136268a80` was imported with
its official frontend package installed in the external research checkout.
`HACS_MANIFEST_JSON_SCHEMA` and `INTEGRATION_MANIFEST_JSON_SCHEMA` were called
directly on this repository's JSON files. `validate.brands.Validator.async_validate`
was called with local file paths and content-directory metadata. It found
`custom_components/plantbased/brand/icon.png`, so no remote brand fallback was
needed. These checks are deliberately **not described as a full HACS action run**.

The temporary source checkouts are research material, not application dependencies.
The committed workflow uses the official actions to repeat validation on GitHub.

## Diagnosed setup corrections

- The project root is explicitly in pytest's `pythonpath`; plain `pytest` and
  `python -m pytest` can both import the custom-components namespace.
- HA 2025.10's `aiodns==3.5.0` accepts unbounded newer `pycares` releases even
  though their API is incompatible. The minimum test environment pins
  `pycares==4.11.0`. This is a **test compatibility constraint**, not an integration
  runtime dependency or change to HA's production environment.
- hassfest's development dependencies are isolated from the released HA test
  environment, and its executable directory is on PATH for its Ruff subprocess.
- Python, uv caches, and executable links live in writable `/workspace` paths.

## Completed GitHub acceptance

M1 is delivered in [PR #1](https://github.com/Pyromania522/PlantBased/pull/1).
On the implementation commit `cd28af4a46853b953e20786bc6074d9947653d0f`, both
workflows completed successfully after the repository prerequisites were fixed:

- [Push validation, attempt 2](https://github.com/Pyromania522/PlantBased/actions/runs/39066667086/attempts/2)
- [Pull-request validation, attempt 2](https://github.com/Pyromania522/PlantBased/actions/runs/39066671366/attempts/2)

hassfest, HACS, quality (Ruff, formatting, strict mypy), and both HA test jobs
are green. Only the initially failed HACS jobs were retried; the already passing
jobs retained their successful results. The workflow has **no ignored HACS checks**.

The initial HACS failures were repository-level prerequisites: missing
description, topics, and detected license. The user added the description and
topics and merged the separate MIT-license [PR #2](https://github.com/Pyromania522/PlantBased/pull/2).
The GitHub API now confirms the description, topics, enabled issues, and detected
MIT license on `main`. No application-code correction or assertion bypass was
needed for HACS to pass.

The saved network changes are active. The full HACS index audit and Core API
check found no collision. GitHub API, HACS-index, and HACS publishing-doc requests
returned HTTP 200. The HA documentation website still returned HTTP 403; its
verified official source references remain documented in DECISIONS.md.

M1 is the hub skeleton only. Browser-based manual UI testing, M2–M6 features,
HACS default-catalog submission, and the public v0.1.0 release are not claimed by
these results. The current PR checks are authoritative for later documentation
or implementation commits.

## Saved cloud configuration draft

The following fields were saved and the user subsequently saved/published the
environment settings. Current runtime observations confirm the network rules are
enforced, and the saved configuration contains the installation/start instructions:

- `install_script`: reproducible Python/venv/dependency installation for both
  test targets, using the existing checkout.
- `start_skill`: working directory, milestone boundaries, test commands,
  interpreter selection, and the instruction not to create a Git worktree unless
  explicitly requested. M1 needs no persistent service process.
- `network.allowed_domains`: adds `developers.home-assistant.io`, `hacs.xyz`,
  `api.github.com`, and `data-v2.hacs.xyz`; existing package-manager presets are
  preserved. No new credentials or secret requirements were added.

Fresh requests verified GitHub and HACS access after the runtime update. The
configuration now has a published base version containing these settings. This
does not establish that a separate new cloud task has restored the snapshot.
