## M5: dashboard cards and original illustrations

PlantBased now ships `custom:plantbased-card` for one plant or a group, and
`custom:plantbased-overview-card` for actual hub counts and due-care actions.
Both appear in HA's card picker, have visual editors, English/German labels,
HA theme colors, dark/mobile layouts and keyboard-accessible care controls.
Twelve original MIT SVG illustrations are included; custom photos fall back to
the selected preset if loading fails.

The integration serves one locally bundled TypeScript/Lit module and registers
it automatically through public frontend/static-path APIs. No manual dashboard
resource entry or separate frontend installation is required. Registry IDs keep
cards working after device/entity renames; group membership and care states
update through HA pushes. Existing actions receive explicit device targets;
duplicate pending presses are disabled and failures do not mark care done.

### Verified APIs and assumptions

Official developer-doc, current Core/frontend, HACS and both released HA sources
were inspected before implementation; exact references are in DECISIONS.md.
`frontend.add_extra_js_url` loads an extra frontend module in both storage and
YAML dashboard modes, rather than modifying private Lovelace collections.
Registration lasts for the HA process and is intentionally retained across entry
reload/removal. An already-open browser must refresh after integration loading.
Bundle/illustration hashes version browser URLs. The older supported `hass`
property and an accessible native device select preserve minimum-version support.
The optional image entity is omitted; no integration runtime dependency is added.

### Validation

- HA **2026.10.2 / Python 3.14.2: 185 passed**, **98.54%** statement/branch coverage.
- HA **2025.10.0 / Python 3.13.2: 185 passed**, **98.55%** statement/branch coverage.
- Strict mypy on 25 modules; Ruff lint/format; TypeScript and Prettier passed.
- Production JS: **47.47 kB / 14.23 kB gzip**, bundled Lit and license notices.
- **17 Chromium browser tests passed**; mobile, desktop, dark and 12-illustration
  screenshots were visually inspected. CI rebuilds committed assets and SVGs.
- HA-native actual HTTP/static/module injection and authenticated registry WS
  tests passed on both versions. Official local hassfest: 1 integration, 0 invalid.
- Independent actual-filesystem care/reminder persistence checks passed on both.

Browser tests use the real compiled module with the public HA API contract fixture;
backend tests separately verify real HA APIs. A complete HA browser/Companion
manual smoke test and actual phone delivery are not claimed. See VALIDATION.md.

This completes **M5 only**. Documentation/release automation and the v0.1.0 public
release remain M6. No release/tag or HACS default-repository submission is created.
