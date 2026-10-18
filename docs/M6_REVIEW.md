## M6: complete documentation and v0.1.0 release preparation

PlantBased now has complete English/German installation, HA Container paths,
configuration defaults, update/backup/uninstall and troubleshooting guidance.
The release notes, configuration reference, quality-scale self-review, maintainer
release guide, actual card-fixture previews and full-HA/Companion capture
placeholders make the final v0.1.0 behavior and remaining manual checks explicit.

Three copyable automation files cover due messages, matching done cleanup and
manually recording one group's watering. Two native integration tests load the
actual examples into HA's real automation engine and execute actual care events
and actions on both supported HA releases.

The new standard-library packager produces a complete manual-install
`plantbased.zip` plus SHA256SUMS from tracked runtime files. Versions, release
notes, required files and twelve original SVGs are checked. PR CI builds and
uploads a verified candidate. On a version tag, the publisher reuses all seven
validation jobs, requires the tagged commit on main, verifies the candidate
against a fresh build, uploads complete assets to a draft, then publishes.
Only the publisher has write permission; no new secret is required. Published
releases are never overwritten by a rerun.

### Decisions and scope

Official current HA, HACS and GitHub documentation/source references are recorded
in DECISIONS.md. No integration runtime API/behavior or frontend bundle changes.
HACS retains its normal repository/tag download behavior; the additional ZIP is
for manual installation and contains one `plantbased/` folder. The archive ships
both the MIT license and frontend dependency notices, excluding local data/caches.

This follows the established review process: the user merges M6 before the
v0.1.0 tag is pushed. This PR does not auto-merge or publish from a feature branch.
After merge, the tag workflow can publish the prepared release. The preflight is
executed; actual tag publication is not claimed before that workflow succeeds.

### Local validation

- **202 tests passed on each** HA 2026.10.2/Python 3.14.2 and HA 2025.10.0/Python 3.13.2.
- Integration statement/branch coverage: **98.60% current / 98.61% minimum**.
- **17 Chromium browser tests passed**; TypeScript/Prettier/production build passed.
- Ruff lint/format and strict mypy on all 25 integration modules passed.
- Fifteen ZIP/version/failure tests and two real automation-example tests included.
- Actual-filesystem care/reminder storage passed on both versions.
- Official **actionlint 1.7.12** passed on both workflows.
- **118,141-byte ZIP**; byte-identical Python 3.13/3.14 builds, valid extraction,
  checksum, complete runtime/SVG/translation/license contents.

No complete HA interactive/process-restart smoke test or real phone delivery is
claimed. README images are actual Chromium fixture captures with sample data.
HACS default-list submission and an official quality-scale tier remain outside
this release. See VALIDATION.md for exact commands, coverage and acceptance limits.
