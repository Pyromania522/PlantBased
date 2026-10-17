# PlantBased

Local, calendar-based houseplant care for Home Assistant. No plant sensors, cloud
accounts, or external Python requirements.

**Development status: M1 — hub skeleton.** Only the hub can currently be added.
Plants, groups, care schedules, entities, reminders, and dashboard cards follow in
M2–M5. Do not use this milestone to manage plant care.

## Installation

Requires Home Assistant **2025.10.0 or later**.

1. In HACS, open **Custom repositories** and add
   `https://github.com/Pyromania522/PlantBased` with category **Integration**.
2. Download PlantBased and restart Home Assistant.
3. Open **Settings → Devices & services → Add integration → PlantBased**.
4. Confirm the dialog. One PlantBased hub is allowed per installation.

Alternatively, copy `custom_components/plantbased` into your Home Assistant
configuration's `custom_components` directory and restart Home Assistant.

M1 creates no devices or entities. Configuration is UI-only, without YAML or
credentials. Reload or remove the hub from Devices & services. To uninstall,
remove the hub, uninstall through HACS, and restart Home Assistant.

Local brand images work on HA 2026.3+. Earlier versions may show a generic icon.

## Roadmap

| Milestone | Scope | Status |
| --- | --- | --- |
| M1 | HACS structure, hub, translations, validation | Implemented; GitHub CI verified |
| M2 | Plant/group subentries, storage, scheduling, entities | Planned |
| M3 | Actions, events, calendar, to-do, diagnostics | Planned |
| M4 | Summary and actionable notifications | Planned |
| M5 | Lovelace cards, visual editors, illustrations | Planned |
| M6 | Complete documentation and v0.1.0 release | Planned |

The manifest's `0.1.0` is a development version. A public release is reserved for M6.

## Deutsch

PlantBased wird eine lokale, kalenderbasierte Pflanzenpflege für Home Assistant.
Feuchtigkeits-, Licht- und Bodensensoren sowie Cloud-Dienste sind nicht vorgesehen.

**Aktueller Stand: M1, das Grundgerüst.** Bisher lässt sich ausschließlich der Hub
hinzufügen. Pflanzen, Gruppen, Gieß- und Düngetermine, Erinnerungen und
Dashboard-Karten folgen in den nächsten Meilensteinen.

Installation: In HACS unter **Benutzerdefinierte Repositories** die oben genannte
Adresse als **Integration** hinzufügen, herunterladen und Home Assistant neu
starten. Unter **Einstellungen → Geräte & Dienste → Integration hinzufügen** nach
**PlantBased** suchen und bestätigen. Es ist genau ein Hub möglich; die
Einrichtung erfolgt ohne YAML, Konto oder Sensoren. Zum Entfernen den Hub unter
Geräte & Dienste löschen, in HACS deinstallieren und Home Assistant neu starten.

## Development and license

See [CONTRIBUTING.md](CONTRIBUTING.md), [DECISIONS.md](DECISIONS.md), and
[VALIDATION.md](VALIDATION.md). Code and original artwork use the [MIT License](LICENSE).
