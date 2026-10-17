# Suggested PR: Add the PlantBased single-hub skeleton (M1)

PlantBased previously contained only a project title. This change adds an
installable custom-integration layout and a confirmed UI flow for one local hub.
It supplies HACS metadata, English/German dialogs, MIT licensing, original local
brand artwork, contributor documentation, and GitHub validation workflows.

The flow rejects duplicate and parallel setup. The real HA entry lifecycle
supports loading, reloading, unloading, and removal. M1 deliberately creates no
plants, devices, entities, care actions, or frontend resources. The original
requirements are retained in PROJECT_BRIEF.md for later milestones.

Assumptions and compatibility decisions are detailed in ../DECISIONS.md:
`0.1.0` is the requested development manifest version, while the release waits for
M6; the hub's singleton ID is `plantbased`; local brand images use HA ≥2026.3's
supported directory, with a generic fallback permitted on the minimum HA version.
No authentication or YAML is introduced. No quality-scale tier is claimed yet.

Validation: 7 tests pass on each of HA 2025.10.0/Python 3.13.2 and HA
2026.10.2/Python 3.14.2, with 100% statement/branch coverage of the small skeleton.
Ruff, strict mypy, all official hassfest integration validators, official HACS
manifest schemas, and the local HACS brand validator pass. Full GitHub CI/HACS
metadata validation is tracked in ../VALIDATION.md. The complete current HACS
index (3,225 integrations) and Core API have now been checked: no domain collision.
The user supplied the repository description/topics and merged the separate
MIT-license PR #2. GitHub now detects MIT on the default branch. Both the push
and PR workflows passed on implementation commit `cd28af4`: hassfest, HACS,
quality, and both HA test jobs. All HACS checks remained enabled. The earlier
metadata failures were resolved without changing integration logic. See
../VALIDATION.md for exact runs, scope, and limitations.
