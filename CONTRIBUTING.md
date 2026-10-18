# Contributing

PlantBased is developed in milestones. M5 adds bundled TypeScript/Lit cards,
visual editors, automatic module registration and original SVG illustrations.
Before using an HA API, check the current official developer documentation and
the supported minimum HA release. Record compatibility decisions in DECISIONS.md.

## Local checks

Use Python **3.14.2 or newer** for the current HA test target:

```sh
python3.14 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy
.venv/bin/pytest
.venv/bin/python -m script.check_storage
```

For the exact minimum Home Assistant **2025.10.0**, use Python 3.13 in a separate
environment (the fixture packages pin incompatible HA versions):

```sh
python3.13 -m venv .venv-min
.venv-min/bin/python -m pip install -r requirements-test-min.txt
.venv-min/bin/pytest
.venv-min/bin/python -m script.check_storage
```

When running both coverage jobs concurrently, set COVERAGE_FILE to distinct
files in separate directories; the default `.coverage*` cleanup can otherwise
collide with another run’s data.

The test plugin supplies HA fixtures and a pinned HA package. Integration runtime
requirements remain empty. Tests must exercise real HA flows and lifecycle APIs;
do not substitute hand-written Home Assistant stubs for backend integration tests.
Coverage must stay ≥90%. The frontend packages in the Python test requirements
match each HA release's frontend manifest exactly; update those pins together.

## Frontend checks

Use Node **24** (minimum 22.12) and the committed npm lockfile:

```sh
npm ci
npm run typecheck
npm run format:check
python3 script/build_illustrations.py
npm run check:bundle
npx playwright install --with-deps chromium
npm test
```

When a compatible Chromium is already installed, skip the browser download and
run `CHROMIUM_PATH=/usr/bin/chromium npm test`. In this cloud workspace use
`NPM_CONFIG_CACHE=/workspace/.cache/npm` if the default cache is not writable.
The Playwright suite starts and stops its local test server automatically.

Edit sources in `frontend/src/`, regenerate SVGs with the original vector script,
then run `npm run format` and `npm run build`. Commit both source and generated
`custom_components/plantbased/frontend/` output. The production bundle includes
Lit and its third-party license notices; it needs no CDN or npm on the HA host.
CI rebuilds and rejects any committed bundle/source mismatch.

Browser tests load the actual compiled module with a fixture implementing the
public HA frontend contract. Backend tests independently exercise HA's actual
static server, official frontend index and authenticated registry WebSocket API
on both releases. This is not a full HA browser end-to-end test. Playwright writes
mobile, desktop, dark and illustration-gallery screenshots under `/tmp`; CI
uploads these and failure traces as `plantbased-browser-evidence`.

CI runs official hassfest and HACS actions without ignored checks. HACS reads the
GitHub revision and repository metadata, so a local schema check cannot establish
a successful remote HACS run. The public repository must have a description,
topics, issues enabled, and the MIT license committed.

## Manual smoke test

Install in a disposable supported Home Assistant instance, restart, add PlantBased
through Devices & services, and confirm setup. Check that a second hub is refused.
Reload and remove the hub. Add two groups and a plant in each. Confirm
16 entities per plant, five per group and eight on the hub. Exercise
care buttons, date corrections, intervals, snooze, pause/vacation and group
actions. Reconfigure and remove a group; its plants must survive unassigned.
Reload/restart and verify histories and pause state persist. Both German and
English dialogs and entity names should be readable. Check calendar all-day
boundaries, overdue dates and due-only to-do items. Complete a task and verify
history, counts, dates and calendar change together. In Developer tools, exercise
all four PlantBased actions with plant/group/entity/area targets and listen for
`plantbased_care_due` and `plantbased_care_done`. Download integration diagnostics
and check no notes, image addresses or location text is exported. Enable
reminders in the hub options and select test targets. Confirm one
summary per recipient at the local scheduled time, both care headings, correct
language, repeat-off behavior and no reminder during pause/vacation. Test all
Companion actions, summary replacement/clearing, reload/restart deduplication,
persistent-copy restoration and disabled/removed target cleanup. Automated tests
use fake notifier receivers through real HA services;
no test contacts a real mobile device or external provider.

Refresh an open HA tab, add both cards through the dashboard picker without a
manual resource, and select a plant/group through the editor. Check custom title,
hidden actions, group reassignment, renamed devices/entities, due/overdue/paused
and unavailable states, independent snoozes, failed actions and a broken custom
image. Exercise keyboard navigation, narrow columns, mobile and both themes in
German/English. Confirm an ordinary YAML-mode dashboard also loads the module.
After upgrading frontend assets, restart HA and refresh the browser to load the
new cache version. After uninstalling, remove dashboard cards and restart HA.

## Pull requests

Include the milestone, behavior changed, exact validation results, and any
assumptions or API compatibility findings. Do not commit tokens, personal HA
configuration, storage files, environments, or generated test reports.
Code and original artwork are contributed under the MIT license.
