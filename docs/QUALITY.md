# Quality-scale review

PlantBased targets the applicable Bronze/Silver engineering rules for a calculated
hub; this is a repository self-review, not an awarded Home Assistant tier.
The rule list was checked against the official developer-doc source at
`50b518898989b67bb76b69827f227aa6f0acd32a`:
[quality-scale rules](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/).
Exact executed results and remaining manual acceptance are in VALIDATION.md.

| Rules / applicability | Evidence or reason |
| --- | --- |
| Action setup and exceptions | Actions register in `async_setup`, remain discoverable with an unloaded hub, validate targets and raise translated HA errors; native failure/transaction tests |
| Appropriate polling | Push-only memory views; state/date/startup changes and local midnight callbacks; no polling |
| Brand assets | Original local brand directory, supported by HA 2026.3+; generic icon possible on older minimum |
| Common modules / runtime data | Shared const/entity/registry modules and typed `ConfigEntry.runtime_data` manager |
| Config flow / coverage | UI-only single hub, plant/group subentries, options/reconfigure validation and English/German descriptions; native flow tests |
| Dependency transparency | Empty runtime Python requirements; HA notifier delegation is documented, frontend Lit licenses are shipped |
| Documentation | README, configuration reference, actions/events and tested examples, installation/removal/update, troubleshooting and release guide |
| Conditions | No PlantBased-specific automation condition is registered; standard HA state/template conditions remain available |
| Entity event setup | Entry/entity-owned listeners and public unload callbacks; native reload/removal tests |
| Entity identity and names | Stable subentry-based unique IDs, `has_entity_name`, translation keys and device ownership; registry/rename tests |
| Test before configure/setup | No remote credentials or hardware to probe; UI values and restored care/reminder schemas are validated before successful setup; corruption tests preserve data |
| Unique config entry | Exactly one hub is enforced and tested |
| Config entry unloading | All platforms unload; schedules, listeners, notifier callbacks and persistence are shut down; real HA unload/reload tests |
| Configuration/installation parameters | Documented defaults, limits, optional fields and controls in CONFIGURATION.md |
| Entity availability / unavailable logs | No physical connection or cloud availability to monitor; unavailable/unloaded HA states are honored by cards, invalid storage stops setup with a translated error |
| Integration owner | `@Pyromania522` in manifest codeowners; GitHub issue templates provided |
| Parallel updates | Every entity platform sets `PARALLEL_UPDATES = 0`; care mutations share the manager's lock and durable transaction boundary |
| Reauthentication | Not applicable: no integration credentials/account/remote authentication |
| Test coverage | Combined statement/branch coverage above 98% on minimum/current HA, with a mandatory 90% CI floor |

Additional scope includes diagnostics with an explicit allowlist, translated
entity states/actions/errors, device/group reconfiguration, season/DST tests,
real filesystem persistence, public frontend APIs, browser tests and release
artifact validation. Repairs are not invented for conditions the integration
cannot safely fix; unreadable stores are preserved with an actionable setup error.

Full interactive HA/browser/Companion testing, physical phone delivery and
process-level manual restart acceptance remain explicit manual checks. CI/API
coverage does not replace these observations or a future formal tier review.
