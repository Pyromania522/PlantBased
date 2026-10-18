# Configuration reference / Einstellungen

All integration settings are edited in **Settings → Devices & services →
PlantBased**. There is exactly one hub. Add plant/group creates native subentries;
**Reconfigure** edits one subentry. **Configure** on the hub edits reminders.
Areas are HA registry areas. A group area takes precedence for its member plants;
otherwise each plant can use its own area. The own area stays saved as a fallback.
No physical sensor, account, credential or integration YAML is used.

The **PlantBased** sidebar page links administrators directly to this management
page through **Settings**. Its Plants/Groups/Areas views, search and due-only filter
change only the displayed view; they do not change memberships, schedules or HA
areas. Area grouping reads the actual device/area registries, including inherited
group areas. Group cards show counts for the whole group even while a search or
care filter narrows the expanded members. No additional setup is required.

## Plant

| Field | Default / effect |
| --- | --- |
| Name | Required; device name, freely editable |
| Group | Optional; choose **No group** for an independent plant. Removing the group leaves the plant unassigned |
| Own area | Optional fallback HA area, used when the plant has no group area |
| Species, notes, location note | Optional free text for your own care records; no species database lookup |
| Image preset | Generic; one of twelve bundled original illustrations |
| Custom image path/URL | Optional `/local/...` or browser-accessible HTTP(S); overrides the preset, falls back on load failure |
| Watering interval | Base of 7 whole calendar days; allowed 1–365; editing restarts learning |
| Learn watering rhythm | Off; opt in per plant to adapt the active interval from newly confirmed watering |
| Fertilizing enabled | On; turning it off removes fertilizer due dates/flags |
| Fertilizing interval | 28 whole calendar days; allowed 1–365 |
| Season start/end | March–September inclusive; ranges crossing New Year work |
| All year | Off; when on, ignores seasonal limits |
| Initial last-watered/fertilized | Today in HA's configured time zone; future dates are rejected |

Use the last-care **date entities** to correct runtime dates after creation.
Changing initial dates in a later configuration edit does not replace an existing
care history. The interval **number entities** edit the corresponding stored
configuration. With learning enabled, the watering number shows the active
interval; setting it manually also restarts learning, including when returning
to the original baseline. Native care buttons and card buttons record actual care
for today.

Learning keeps the last five eligible gaps and requires at least three within
one day or 20% of their median. It changes by at most one day per new watering
date, bounded to 1–365. The first confirmation establishes an anchor, so three
gaps require four confirmations on different dates. Duplicate same-day presses
add no samples. Explicitly dated actions/corrections interrupt observation.
Snoozed watering starts a new anchor without learning its delayed gap. Pauses and
vacation clear observations; the learned interval remains. Restarts retain both.
Disabling learning restores the configured baseline. Existing histories are not
reused. No fertilizer learning, account or external data is involved.

Per-plant pause and the hub's vacation switch are runtime controls. They suppress
due flags, reminders, calendar/tasks and due counts while dates continue to run.
Unpausing can therefore make old care overdue immediately. Group actions include
paused members because the action records work actually performed.

## Group

Name is required. Area and image preset are optional. A group stores no independent
care schedule: its counts and two care buttons use current members. The dashboard
group card displays each member's plant illustration. Removing a group never
removes its plants. A group's area is inherited by current members. Clearing
the group area or removing a plant from its group restores valid own areas.
Changes through the group device's HA area selector also synchronize members.
A conflicting area on a member device is corrected to the group area; edit the
group instead. Groups without an area allow members in different rooms.

## Hub reminders

| Setting | Default / effect |
| --- | --- |
| Reminders enabled | Off |
| Reminder time | 09:00, HA-local wall time |
| Notification targets | Empty; choose available legacy notify services or notify entities |
| Repeat daily while due | On; off sends scheduled summaries only for new due task identities |
| Persistent HA copy | Off; when enabled, matching HA summary is restored/updated/dismissed |
| Mobile Snooze 1 day action | On; applies to Companion service recipients |

Enabling reminders requires at least one target or the persistent HA copy.
Choose `notify.mobile_app_*` for actionable mobile messages. Ordinary notify
entities support message/title only. Unavailable/removed targets are not usable;
failures never mark care done. Other target choices, provider delivery limits,
restart receipts and DST behavior are explained in the README.

## Dashboard-only settings

`custom:plantbased-card` takes a plant/group `device_id`; the visual editor selects
it. `custom:plantbased-overview-card` needs no target. Both accept optional `title`
and `show_actions` (default true). These settings affect the card, not integration
configuration. Custom cards follow the current browser's HA locale/theme; native
HA labels and calendar/reminder text use HA's configured language.

## Deutsch

**Pflanze hinzufügen / Gruppe hinzufügen** erzeugt einen eigenen Eintrag unter
PlantBased. Über **Neu konfigurieren** lassen sich Name, Zuordnung und weitere
Felder ändern. **Keine Gruppe** hält die Pflanze unabhängig. Ein Gruppenbereich
hat Vorrang; der eigene Bereich bleibt als Rückfallwert gespeichert. Ohne
Gruppenbereich oder nach dem Entfernen aus der Gruppe wird er wieder verwendet.
Für Änderungen am aktiven Bereich einer gruppierten Pflanze den Bereich an der
Gruppe ändern. **Konfigurieren** am Hub öffnet die Erinnerungen. Die Gerätebereiche
werden über die HA-Geräteverwaltung geführt.

Bei einer Pflanze sind Gruppe, Bereich, Art, Notizen, Standortnotiz und Bild
optional. Standard: sieben Tage fürs Gießen, 28 fürs Düngen, Düngen eingeschaltet,
Saison März bis September und letzte Pflege jeweils heute. Ganze Intervalle von
1 bis 365 Tagen sowie Saisons über den Jahreswechsel sind möglich. **Ganzjährig**
hebt die Saisonbegrenzung auf. Ein eigenes `/local/`- oder HTTP(S)-Bild hat Vorrang
vor dem gewählten lokalen Motiv.

Nach dem Anlegen letzte Pflegedaten über die Datumsentitäten korrigieren. Die
ursprünglichen Startdaten einer späteren Konfigurationsänderung überschreiben
keinen vorhandenen Verlauf. Intervallfelder ändern die gespeicherte Einstellung.
Pausen und Urlaubsmodus lassen Termine weiterlaufen, unterdrücken aber fällige
Pflege; beim Beenden kann sie sofort wieder überfällig sein.

Erinnerungen sind zunächst aus. Standardzeit ist **09:00 Uhr in der HA-Zeitzone**,
tägliche Wiederholung und mobile Verschiebeaktion sind an, die zusätzliche
HA-Meldung ist aus. Zum Einschalten ein Ziel oder die HA-Meldung wählen. Für
mobile Aktionsknöpfe `notify.mobile_app_*` verwenden. Die Karteneinstellungen
betreffen nur die Darstellung; im visuellen Editor Pflanze/Gruppe, Titel und
Aktionsknöpfe wählen.
