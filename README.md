# PlantBased

Local, calendar-based houseplant care for Home Assistant. No plant sensors, cloud
accounts, or external Python requirements.

**Development status: M2 — plants, groups and local care schedules.** Each plant
has independent watering/fertilizing dates, editable intervals, care buttons,
status and pause controls. Group actions and hub counts are available.
Calendar/to-do entities, integration actions/events, notifications and dashboard
cards follow in M3–M5. This is a development milestone, not the complete v0.1.0.

## Installation

Requires Home Assistant **2025.10.0 or later**.

1. In HACS, open **Custom repositories** and add
   `https://github.com/Pyromania522/PlantBased` with category **Integration**.
2. Download PlantBased and restart Home Assistant.
3. Open **Settings → Devices & services → Add integration → PlantBased**.
4. Confirm the dialog. One PlantBased hub is allowed per installation.
5. On the integration card, choose **Add group** (optional) or **Add plant**.
   Give the plant a name, review the default care intervals and initial dates,
   and select its group and area if desired.

Alternatively, copy `custom_components/plantbased` into your Home Assistant
configuration's `custom_components` directory and restart Home Assistant.

Configuration is UI-only, without YAML or credentials. Plants and groups appear
as devices owned by native config subentries. Use **Reconfigure** on a subentry
to edit its settings; use the date entities to correct its last-care dates.
Reload or remove the hub from Devices & services. To uninstall, remove the hub
(which deletes its runtime history), uninstall through HACS, and restart HA.

Local brand images work on HA 2026.3+. Earlier versions may show a generic icon.

## Care workflow

- **Mark watered / Mark fertilized** records today's local date and clears only
  that care timer's snooze. Editable date entities allow a past-date correction;
  last-care dates cannot be in the future.
- **Snooze** moves overdue care to tomorrow. Repeated presses add another day
  to the already postponed due date. Watering and fertilizing remain independent.
- **Pause plant / Vacation mode** suppress due flags and overview counts. The
  original dates keep running; overdue care reappears when unpaused. You can
  still record actual care while paused.
- Group buttons apply to **all members of that group**, including paused plants.
  Deleting a group unassigns its plants; deleting a plant removes its device,
  entities and runtime history.
- Intervals use local calendar days, not elapsed hours. State recalculates on
  changes, at local midnight, at HA start and on time-zone changes. No polling.
- Fertilizing defaults to March–September, inclusive. Seasons crossing New Year
  are supported. Outside the season, the next-fertilizing date shows the next
  season's first day; the interval is rechecked on that day. Disabled fertilizing
  has no due date. **All year** keeps the ordinary interval throughout the year.

Runtime dates, snoozes, pause/vacation state and the last 10 dates per care type
are stored in Home Assistant's private `.storage/plantbased.<entry_id>` file.
They survive hub reloads and HA restarts. Include HA's storage in your backups.
An unreadable store stops setup with a translated error instead of resetting
care dates. Restore it from a known-good backup before reloading.

M2 provides 16 entities per plant, five per group and six on the hub. Care-status
attributes include group, species, image metadata, overdue days and history.
Calculated sensor entities do not require any physical sensor or sensor selection.
Image presets are stored now; their illustrations/cards arrive in M5. Custom
image paths/URLs are metadata and are not downloaded by the backend.

## Roadmap

| Milestone | Scope | Status |
| --- | --- | --- |
| M1 | HACS structure, hub, translations, validation | Implemented; GitHub CI verified |
| M2 | Plant/group subentries, storage, scheduling, entities | Implemented; see VALIDATION.md |
| M3 | Actions, events, calendar, to-do, diagnostics | Planned |
| M4 | Summary and actionable notifications | Planned |
| M5 | Lovelace cards, visual editors, illustrations | Planned |
| M6 | Complete documentation and v0.1.0 release | Planned |

The manifest's `0.1.0` is a development version. A public release is reserved for M6.

## Deutsch

PlantBased bietet lokale, kalenderbasierte Pflanzenpflege für Home Assistant.
Feuchtigkeits-, Licht- und Bodensensoren sowie Cloud-Dienste sind nicht vorgesehen.

**Aktueller Stand: M2.** Pflanzen und Gruppen lassen sich über die Integrationskarte
hinzufügen. Jede Pflanze erhält eigene Gieß- und Düngetermine, Datums- und
Intervallfelder, Pflegeknöpfe und einen Pausenschalter. Kalender, Aufgabenliste,
Automationsereignisse, Erinnerungen und Dashboard-Karten folgen später.

Installation: In HACS unter **Benutzerdefinierte Repositories** die oben genannte
Adresse als **Integration** hinzufügen, herunterladen und Home Assistant neu
starten. Unter **Einstellungen → Geräte & Dienste → Integration hinzufügen** nach
**PlantBased** suchen und bestätigen. Es ist genau ein Hub möglich; die
Einrichtung erfolgt ohne YAML, Konto oder Sensoren. Zum Entfernen den Hub unter
Geräte & Dienste löschen, in HACS deinstallieren und Home Assistant neu starten.

Über **Pflanze hinzufügen** genügt zunächst ein Name; die Intervalle sind mit
sieben Tagen fürs Gießen und 28 Tagen fürs Düngen vorbelegt. Gruppen und Bereiche
sind optional. **Wässern** und **Düngen** tragen das heutige Datum ein. Mit den
Datumsentitäten lässt sich eine zurückliegende Pflege nachtragen. Ein Datum in
der Zukunft wird abgelehnt.

Die Düngesaison läuft standardmäßig von März bis einschließlich September.
Zeiträume über den Jahreswechsel und ganzjähriges Düngen sind ebenfalls möglich.
Außerhalb der Saison zeigt das nächste Düngetermin-Feld den Beginn der nächsten
Saison an; das Intervall wird an diesem Tag erneut geprüft.

**Pflanzenpflege pausieren** und der globale **Urlaubsmodus** unterdrücken fällige
Pflege in den Statusanzeigen und Zählern. Die ursprünglichen Termine bleiben
erhalten und können nach dem Ausschalten sofort wieder überfällig sein.
Verschieben setzt bereits überfällige Pflege mindestens auf morgen; erneutes
Drücken verschiebt um einen weiteren Tag. Gruppenaktionen gelten nur für die
Mitglieder der gewählten Gruppe, auch für pausierte Pflanzen.

Beim Löschen einer Gruppe bleiben die Pflanzen erhalten und werden keiner Gruppe
mehr zugeordnet. Datumswerte, Verschiebungen, Pausen und die letzten zehn Einträge
je Pflegeart bleiben nach einem Neustart erhalten. Ein defekter Speicher wird nicht stillschweigend
zurückgesetzt; vor dem erneuten Laden muss eine Sicherung wiederhergestellt werden.

## Development and license

See [CONTRIBUTING.md](CONTRIBUTING.md), [DECISIONS.md](DECISIONS.md), and
[VALIDATION.md](VALIDATION.md). Code and original artwork use the [MIT License](LICENSE).
