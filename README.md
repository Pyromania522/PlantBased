# PlantBased

Local, calendar-based houseplant care for Home Assistant. No plant sensors, cloud
accounts, or external Python requirements.

**Development status: M5 — dashboard cards, visual editors and illustrations.**
Plants and groups have care controls, automation actions/events, a care calendar
and a task list. Optional reminders now send one grouped summary through selected
HA notifiers, with mobile care/snooze actions and an optional persistent HA copy.
Single-plant, group and overview cards now include English/German controls and
twelve original illustrations. This remains a development milestone; the complete
v0.1.0 release follows in M6.

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

PlantBased provides 16 entities per plant, five per group and eight on the hub. Care-status
attributes include group, species, image metadata, overdue days and history.
Calculated sensor entities do not require any physical sensor or sensor selection.
Image presets resolve to bundled original SVGs. Custom image paths/URLs are
loaded by the browser and are not downloaded by the backend.

## Dashboard cards

After restarting HA and adding PlantBased, refresh an already-open browser tab.
The integration loads its card module automatically: **no manual dashboard
resource entry or separate frontend repository is needed**.

1. Open your dashboard, choose **Edit dashboard → Add card**, and search for
   **PlantBased**.
2. Choose **PlantBased** and select a PlantBased plant or group
   in the visual editor. A group displays its current members in a compact grid.
3. Add **PlantBased Overview / Übersicht** for hub counts and the list of due plants.
4. Optionally set a title or hide the action buttons in either editor.

Plant cards show watering/fertilizing countdowns, group names, and distinct
healthy, due, overdue, paused and unavailable states. **Watered**, **Fertilized**
and separate **Watering +1 day / Fertilizing +1 day** snooze choices use the existing care actions. Buttons wait
for HA confirmation; failures show a message without marking care done. Care can
still be recorded during a pause. Disabled fertilizing has no enabled action.
The overview uses the hub's actual counters; pause/vacation plants stay out of its
due list. Entity and device renames do not require editing the card configuration.

These are optional dashboard YAML equivalents; integration setup stays UI-only:

```yaml
type: custom:plantbased-card
device_id: YOUR_PLANT_OR_GROUP_DEVICE_ID
title: Living room
show_actions: true
```

```yaml
type: custom:plantbased-overview-card
show_actions: true
```

`device_id` is the registry ID selected by the editor, not an entity ID. An empty
selection never targets all plants. `title` is optional; `show_actions` defaults
to `true`. Overview needs no device selection. Device/group membership updates and
care states arrive through HA's normal push connection, without polling.

Choose an illustration in the plant's **Reconfigure** dialog: generic, monstera,
ficus, pothos, snake plant, succulent, cactus, fern, orchid, herb, palm or hanging
plant. Alternatively use `/local/plants/your-photo.png` (a file under HA's
`www/plants/`) or an HTTP(S) image URL. A failed image falls back to the preset.
External images require browser access to that host; bundled presets work locally.
The cards follow the browser's HA language and theme, including dark mode and
narrow mobile/dashboard columns. Other languages fall back to English.

## Calendar, tasks and automation actions

The hub's **Care calendar** shows one all-day event for each plant's next open
watering/fertilizing date. An overdue task remains on its original date until
care is recorded or snoozed; repeated future care is not assumed. Paused plants
and global vacation are excluded. Outside the fertilizing season, the calendar
resolves the season-start marker against the actual interval before showing an
event. Thus a far-future interval does not create a premature calendar task.

The hub's **Plant care** to-do list contains currently due tasks only. Check an
item to record that care for today; dates, histories, counts and the calendar
update together. Completed tasks leave the list and remain in the plant's
history. Rename, manual task creation/deletion and due-date edits are unavailable;
edit the plant's settings/date entities instead. Refresh a stale task list before
completing a task from an older care cycle.

Four actions are available under **Developer tools → Actions**:

| Action | Fields | Targets |
| --- | --- | --- |
| `plantbased.mark_watered` | Optional `date`, defaults to today | Plant/group devices or their entities |
| `plantbased.mark_fertilized` | Optional `date`, defaults to today | Plant/group devices or their entities |
| `plantbased.snooze` | `care_type`: `water`/`fertilize`; `days`: 1–365, default 1 | Plant/group devices or their entities |
| `plantbased.set_interval` | `care_type`: `water`/`fertilize`; `days`: 1–365 | Plant/group devices or their entities |

Group targets expand to their current members, including paused plants. Multiple
references to the same plant act only once. Area/label targeting is supported;
`entity_id: all` explicitly selects every PlantBased plant. A missing target does
not select all plants. Hub targets are not plant/group targets. Invalid direct
targets fail before any plant changes. Bulk marks/snoozes save as one transaction.
Future care dates and fractional day counts are rejected.

The events `plantbased_care_due` and `plantbased_care_done` contain `device_id`,
`name` and `care_type` (`water` or `fertilize`). Due events fire on transitions to
due, including season entry, unpause and startup/reload for already-due care.
They do not repeat every overdue day. Done events fire after a successful save,
including care recorded through buttons, date entities, actions and to-do items.
Use these events as automation triggers independently of the optional reminders.

Download **Diagnostics** from the integration entry menu to inspect care state.
The integration's payload includes plant names, dates, histories and care settings;
it excludes notes, species, group names, areas, location notes and image paths/URLs.
Calendar/task text follows HA's configured language; entity and action names are
translated by Home Assistant.

## Optional reminders

Open **Configure** on the PlantBased hub under **Settings → Devices & services**.
Reminders are **off by default**. Enable them and choose available notification
targets, or enable the persistent HA notification. The default reminder time is
**09:00 in Home Assistant's configured time zone**, with daily repeat enabled.
Select the `notify.mobile_app_*` service for Companion app action buttons.
New-style notify entities are also selectable for ordinary message/title delivery.

At the chosen time, one summary per selected target lists due plants under
watering and fertilizing headings. Paused/vacation work and out-of-season or
disabled fertilizing are excluded. English/German text follows HA's configured
language, with English fallback for other languages. You can choose:

- **Repeat daily while care is due**: otherwise only a newly due care task causes
  another scheduled summary. The summary still lists all currently due tasks.
- **Also show a persistent notification**: keeps a matching summary in HA and
  dismisses it when nothing is due.
- **Include mobile Snooze 1 day action**: adds a third Companion button alongside
  **All watered** and **All fertilized**, when those care types are due.

Mobile actions affect the still-due tasks listed by that message. Healthy plants,
newer care cycles and paused plants are never marked by an old message. Snooze
postpones both listed care types in one saved operation. Mobile summaries use one
entry-specific tag, so changes replace the current message and finishing care
clears it. Persistent copies update/dismiss too. Turning off reminders, removing
a target or disabling/removing the hub attempts to clear known mobile/persistent
messages. Ordinary notifier messages cannot be recalled through their generic API.

If HA starts after the chosen time, today's unsent reminder is caught up. Private
versioned receipts in `.storage/plantbased.<entry_id>.reminders` avoid duplicate
scheduled sends on ordinary reload/restart and during the repeated DST hour.
A skipped DST clock time is shifted forward by the gap. Persistent copies are
restored after HA startup. Include the care and reminder stores in backups.

A provider accepting a service call does not guarantee phone delivery or clearing;
Companion permissions, connectivity and platform limits still apply. A crash
between delivery and receipt persistence can repeat a message; mobile tags replace
it. Target failures are isolated and never mark care done. PlantBased delegates
to configured HA notifiers and makes no notification network request itself.

## Roadmap

| Milestone | Scope | Status |
| --- | --- | --- |
| M1 | HACS structure, hub, translations, validation | Implemented; GitHub CI verified |
| M2 | Plant/group subentries, storage, scheduling, entities | Implemented; see VALIDATION.md |
| M3 | Actions, events, calendar, to-do, diagnostics | Implemented; see VALIDATION.md |
| M4 | Summary and actionable notifications | Implemented; see VALIDATION.md |
| M5 | Lovelace cards, visual editors, illustrations | Implemented; see VALIDATION.md |
| M6 | Complete documentation and v0.1.0 release | Planned |

The manifest's `0.1.0` is a development version. A public release is reserved for M6.

## Deutsch

PlantBased bietet lokale, kalenderbasierte Pflanzenpflege für Home Assistant.
Feuchtigkeits-, Licht- und Bodensensoren sowie Cloud-Dienste sind nicht vorgesehen.

**Aktueller Stand: M5.** Pflanzen und Gruppen lassen sich über die Integrationskarte
hinzufügen. Jede Pflanze erhält eigene Gieß- und Düngetermine, Datums- und
Intervallfelder, Pflegeknöpfe und einen Pausenschalter. Pflegekalender,
Aufgabenliste, Automationsaktionen und Ereignisse sind verfügbar. Optionale
Sammelerinnerungen, mobile Pflegeaktionen und Dashboard-Karten mit zwölf eigenen
Pflanzenillustrationen sind enthalten. Die Veröffentlichung von v0.1.0 folgt in M6.

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

Der **Pflegekalender** am Hub zeigt den jeweils nächsten offenen Gieß- und
Düngetermin ganztägig. Überfällige Termine bleiben am ursprünglichen Datum;
weitere Wiederholungen werden erst nach erfasster Pflege berechnet. Pausierte
Pflanzen erscheinen weder im Kalender noch in der Aufgabenliste.

In der Aufgabenliste **Pflanzenpflege** genügt ein Häkchen: Die jeweilige Pflege
wird für heute gespeichert und die Aufgabe verschwindet. Der Verlauf bleibt
erhalten. Namen und Termine werden an der Pflanze bearbeitet. Ist eine Aufgabe
nicht mehr aktuell, die Liste vor dem Abhaken aktualisieren.

Unter **Entwicklerwerkzeuge → Aktionen** stehen `plantbased.mark_watered`,
`plantbased.mark_fertilized`, `plantbased.snooze` und `plantbased.set_interval`
zur Verfügung. Als Ziel Pflanzen- oder Gruppengeräte beziehungsweise deren
Entitäten wählen. Die Pflegeart lautet `water` oder `fertilize`, die Tageszahl
ist ganzzahlig zwischen 1 und 365. Gruppenaktionen ändern nur aktuelle Mitglieder;
mehrfach ausgewählte Pflanzen werden einmal bearbeitet.

Die Automationsereignisse `plantbased_care_due` und `plantbased_care_done` liefern
`device_id`, `name` und `care_type`. Fälligkeit wird beim Übergang gemeldet,
auch beim Start/Neuladen bereits fälliger Pflege; die Meldung wiederholt sich
nicht täglich. Erledigt-Ereignisse folgen erst nach erfolgreichem Speichern.
**Diagnosedaten herunterladen** im Menü des Integrationseintrags liefert
Pflegedaten mit Pflanzennamen, ohne Notizen, Standorte oder Bildadressen.

Erinnerungen sind zunächst **ausgeschaltet**. Unter **Einstellungen → Geräte &
Dienste → PlantBased → Konfigurieren** lassen sich Uhrzeit, Benachrichtigungsziele,
tägliche Wiederholung, eine zusätzliche HA-Meldung und die mobile Verschiebeaktion
festlegen. Standard ist **09:00 Uhr in der Home-Assistant-Zeitzone**. Mindestens
ein Ziel oder die zusätzliche HA-Meldung muss gewählt sein.

Für mobile Aktionsschaltflächen das Ziel `notify.mobile_app_*` wählen. **Alle
gewässert**, **Alle gedüngt** und optional **1 Tag verschieben** gelten nur für
noch fällige Aufgaben aus dieser Meldung. Alte Meldungen ändern keine späteren
Pflegezyklen. Neue Notify-Entitäten unterstützen einfache Nachrichten und Titel;
ihre derzeitige API bietet keine Aktions- oder Tag-Daten.

Mobile Sammelmeldungen werden unter demselben Tag aktualisiert und nach erledigter
Pflege zurückgezogen; die zusätzliche HA-Meldung wird ebenfalls aktualisiert oder
entfernt. Andere Benachrichtigungsanbieter können bereits versendete Nachrichten
nicht allgemein zurückrufen. Ist HA zur Erinnerungszeit ausgeschaltet, wird eine
heute noch nicht versendete Meldung nach dem Start nachgeholt. Versandnachweise
bleiben bei Neustarts erhalten; eine doppelte Uhrzeit bei der Zeitumstellung führt
nicht zu einer zweiten Tagesmeldung. Geräteverbindung, App-Berechtigungen und
Anbietergrenzen bestimmen die tatsächliche Zustellung.

### Dashboard-Karten

Nach dem HA-Neustart einen bereits geöffneten Browser-Tab neu laden. Die Karten
werden automatisch geladen; ein manueller Ressourceneintrag ist nicht nötig.
Unter **Dashboard bearbeiten → Karte hinzufügen** nach **PlantBased** suchen.
**PlantBased** bietet im visuellen Editor die Auswahl einer
Pflanze oder Gruppe. **PlantBased Overview / Übersicht** zeigt die Gesamtzahlen und alle
aktuell fälligen Pflanzen. Titel und Aktionsknöpfe lassen sich im Editor anpassen.

**Gewässert** und **Gedüngt** speichern die jeweilige Pflege. Unter
**Verschieben** lässt sich **Gießen +1 Tag** oder **Düngen +1 Tag** getrennt wählen. Während des
Speicherns sind doppelte Klicks gesperrt. Bei einem Fehler erscheint eine Meldung.
Pausen, überfällige Pflege und nicht verfügbare Pflanzen sind unterscheidbar.
Gruppenkarten folgen der aktuellen Zuordnung ihrer Pflanzen.

Unter **Neu konfigurieren** an der Pflanze eines von zwölf lokalen SVG-Motiven
wählen oder ein eigenes Bild wie `/local/plants/monstera.png` angeben. Die Datei
liegt dann unter `www/plants/` in der HA-Konfiguration. HTTP(S)-Bildadressen sind
ebenfalls möglich und werden vom Browser geladen. Ist das Bild nicht erreichbar,
erscheint das gewählte Motiv. Die Karten unterstützen Deutsch, Englisch,
HA-Themes, dunkle Darstellung und schmale Ansichten.

## Development and license

See [CONTRIBUTING.md](CONTRIBUTING.md), [DECISIONS.md](DECISIONS.md), and
[VALIDATION.md](VALIDATION.md). Code and original artwork use the [MIT License](LICENSE).
