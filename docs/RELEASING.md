# Releasing PlantBased

Versions v0.1.0 and v0.1.1 are published. Follow this process for subsequent releases.
Merging a release-preparation PR does not publish a release.
The tag-triggered workflow publishes after all checks pass. Do not create a tag
from a feature branch: the publisher requires the tagged commit to be on `main`.

## Prepare a version

1. Update the version in `custom_components/plantbased/manifest.json`,
   `package.json`, and both root version fields in `package-lock.json` together.
2. Add `docs/releases/vX.Y.Z.md`, update CHANGELOG.md and the user documentation.
   Stable `MAJOR.MINOR.PATCH` tags are supported; prereleases need an explicit
   future extension to this workflow.
3. Rebuild illustrations/cards, run the checks in CONTRIBUTING.md, and build
   the candidate with `python3 -m script.build_release --tag vX.Y.Z`.
4. Open a PR, inspect the `plantbased-release-candidate` CI artifact, and merge
   after validation. The artifact contains `plantbased.zip` and `SHA256SUMS`.

## Publish v0.2.0 after its reviewed merge

From a clean checkout that includes the merged fix/version commit:

```sh
git switch main
git pull --ff-only origin main
git tag -a v0.2.0 -m "PlantBased v0.2.0"
git push origin v0.2.0
```

The **Release** workflow calls the same seven-job validation workflow used by PRs:
hassfest, HACS, Ruff/mypy, both HA versions with filesystem checks, browser/build
checks, and package preflight. Branch validation does not run a duplicate tag
workflow. Publication waits for every validation job, downloads its verified
candidate, checks tag/manifest/frontend versions, verifies the checksum and
compares a fresh package byte-for-byte before publishing.

Only the final publication job has `contents: write`; it uses GitHub's built-in
`github.token`. No personal access token or new repository secret is required.
The publisher creates a draft, uploads both files, then publishes the complete
release and marks it Latest. A failed upload leaves a draft for a retry; a
completed published release is never overwritten by a rerun. For a failed check,
fix the problem before retrying. Do not move a published tag to different code;
ship a new patch version instead. A tag alone is not a GitHub Release or a HACS
release: verify the final workflow and published assets.

## Package contract

`plantbased.zip` contains a single `plantbased/` directory. Extract it into HA's
`custom_components/` directory. It contains the full tracked integration tree,
compiled JS, all twelve SVGs, translations, brand images, the repository MIT
license and bundled third-party notices. Local caches, untracked files, tests,
source build tooling, HA configuration and storage are excluded. Tracked links,
caches and unexpected extensions are rejected. ZIP timestamps and permissions
are fixed and entries sorted, making repeated builds reproducible with the same
Python/zlib toolchain. The package builder itself uses only the Python standard
library and does not import Home Assistant.

HACS keeps its normal repository/tag installation path (`zip_release` is not
set). The attached ZIP is for manual installation; HACS users select the published
version normally. This avoids changing repository download behavior while the
first release is being introduced.

Verify a downloaded asset in a directory containing both files:

```sh
sha256sum --check SHA256SUMS
```

This checks transport/file integrity; it is not a signature or independent
provenance attestation. Inspect the matching tag and CI when reviewing a release.

## Verification limits and review

The branch CI exercises package creation and uploads reviewable assets. A public
GitHub Release is not created during PR validation. The final tag/publication
path must be observed after merging and pushing the version tag; do not mark it
executed before then. Full interactive HA installation, a physical phone and
provider delivery remain manual checks documented in CONTRIBUTING.md.

Before any future HACS default-list submission, recheck current HACS requirements,
ensure the public release and all validators are green without ignores, then
submit the repository alphabetically in `hacs/default` as its owner or major
contributor. Default-list submission is outside v0.1.0.

## Deutsch

Nach dem Merge der Korrektur den geprüften Stand von `main` mit **v0.2.0** markieren
und den Tag pushen. Der Workflow prüft alles erneut, baut das ZIP und veröffentlicht erst
danach das vollständige GitHub Release. Ein Merge allein veröffentlicht nichts.
Zusätzliche Zugangsdaten sind nicht nötig. Bis zum Tag-Lauf bleiben der
Release-Kandidat im CI-Artefakt und die Versionsnotizen prüfbar.
