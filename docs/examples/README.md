# Automation examples / Automationsbeispiele

These optional examples extend PlantBased; the integration itself remains UI-only.
HA **2025.10.0+** supports the `triggers` / `actions` syntax used here. Automated
tests load these exact YAML files into HA's real automation engine on the minimum
and current targets, including real PlantBased due/done events and group actions.

## Install in the UI

1. In **Settings → Automations & scenes → Create automation**, create an empty
   automation and open **Edit in YAML**.
2. Paste one complete file below, save it and turn it on. Create a separate
   automation for each file. These files are single mappings for the UI editor;
   when using `automations.yaml`, add each mapping as a list item instead.
3. For the group example, replace `REPLACE_WITH_GROUP_DEVICE_ID` by selecting the
   intended PlantBased **group** in the action's visual target picker. Device IDs
   are registry IDs, not entity IDs or group names. Never use the overview hub as
   a care target. You can copy the chosen device ID from the resulting YAML.

| File | Result |
| --- | --- |
| [care_due_notification.yaml](care_due_notification.yaml) | Creates one persistent HA message per plant/care type at the transition to due |
| [care_done_clear_notification.yaml](care_done_clear_notification.yaml) | Clears only that plant/care message after successfully recorded care |
| [mark_group_watered.yaml](mark_group_watered.yaml) | A manually run automation records watering for the selected group's current members |

The first two examples form a pair. Their notification IDs share the
`plantbased_care_` prefix and include the actual device ID and care type. They are
separate from the integration's built-in summary, so enabling both can produce
both kinds of message. Prefer built-in reminders for a scheduled daily summary.
The example messages are English; adapt the text in the automation to your language.

Due events happen on transitions, including reload/startup for currently due work,
season entry and unpausing. Remaining overdue does not fire every day. An
automation enabled after the startup event waits until a later due transition or
integration reload. The examples do not send a phone notification. Done events
follow successful persistence. Paused plants are excluded from due events, but the
manual group action can record real care for paused members too.

### Event payload

Both `plantbased_care_due` and `plantbased_care_done` contain:

```yaml
device_id: EXAMPLE_DEVICE_REGISTRY_ID
name: Monstera
care_type: water  # water or fertilize
```

A task completing, date correction, native care button or dashboard action uses
the same done event. An integration reload can republish currently due tasks;
notification IDs replace the previous example message rather than creating copies.

### Other actions

Use **Developer tools → Actions** to try a target and let HA's editor generate YAML:

```yaml
action: plantbased.snooze
target:
  device_id: REPLACE_WITH_PLANT_OR_GROUP_DEVICE_ID
data:
  care_type: water
  days: 1
```

```yaml
action: plantbased.set_interval
target:
  device_id: REPLACE_WITH_PLANT_OR_GROUP_DEVICE_ID
data:
  care_type: fertilize
  days: 28
```

`plantbased.mark_watered` and `plantbased.mark_fertilized` accept an optional
`date: "2026-06-15"` for an actual past care date. Omit it to use today in HA's
time zone. Future dates and fractional days are rejected. Snooze changes the due
date without recording care. A missing target never selects every plant.

## Deutsch

Unter **Einstellungen → Automationen & Szenen → Automation erstellen** eine leere
Automation öffnen und über **In YAML bearbeiten** jeweils eine vollständige Datei
einfügen. Für jedes Beispiel eine eigene Automation speichern. Beim Gruppenbeispiel
`REPLACE_WITH_GROUP_DEVICE_ID` durch die Geräte-ID der gewünschten PlantBased-Gruppe
ersetzen; am einfachsten das Ziel im visuellen Aktionseditor auswählen.

Die ersten beiden Beispiele gehören zusammen: Fälligkeit erzeugt eine HA-Meldung
für genau eine Pflanze und Pflegeart. Erfolgreich gespeicherte Pflege entfernt die
passende Meldung. Die Ereignisse werden bei Zustandsübergängen ausgelöst, nicht
jeden Tag erneut. Die Meldungstexte lassen sich im YAML ins Deutsche ändern.
Für tägliche Sammelmeldungen die eingebaute Erinnerungsfunktion verwenden; beide
Wege gleichzeitig können mehrere Meldungen erzeugen.

Das Gruppenbeispiel wird nach tatsächlich erledigtem Gießen manuell ausgeführt.
Es erfasst Pflege nur für aktuelle Gruppenmitglieder, auch wenn diese pausiert
sind. **Verschieben** erfasst keine Pflege, sondern verschiebt den Termin.
