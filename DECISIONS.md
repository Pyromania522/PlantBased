# Decisions and verified references

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
