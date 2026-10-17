# Contributing

PlantBased is developed in milestones. M1 contains only the configurable hub.
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
```

For the exact minimum Home Assistant **2025.10.0**, use Python 3.13 in a separate
environment (the fixture packages pin incompatible HA versions):

```sh
python3.13 -m venv .venv-min
.venv-min/bin/python -m pip install -r requirements-test-min.txt
.venv-min/bin/pytest
```

The test plugin supplies HA fixtures and a pinned HA package. Integration runtime
requirements remain empty. Tests must exercise real HA flows and lifecycle APIs;
do not substitute hand-written Home Assistant stubs. Coverage must stay ≥90%.

CI runs official hassfest and HACS actions without ignored checks. HACS reads the
GitHub revision and repository metadata, so a local schema check cannot establish
a successful remote HACS run. The public repository must have a description,
topics, issues enabled, and the MIT license committed.

## Manual smoke test

Install in a disposable supported Home Assistant instance, restart, add PlantBased
through Devices & services, and confirm setup. Check that a second hub is refused.
Reload and remove the hub. At M1, no devices, entities, services, or cards should
be created. Both German and English dialogs should be readable.

## Pull requests

Include the milestone, behavior changed, exact validation results, and any
assumptions or API compatibility findings. Do not commit tokens, personal HA
configuration, storage files, environments, or generated test reports.
Code and original artwork are contributed under the MIT license.
