You are a senior Home Assistant integration developer. Build a production-quality, public custom integration for Home Assistant that is distributed via HACS from a GitHub repository. Work in milestones, verify every Home Assistant API you use against the CURRENT official developer docs (https://developers.home-assistant.io) and the current HACS docs (https://hacs.xyz/docs/publish/) before coding — your training data may be outdated, especially regarding config subentries, entity naming, and frontend registration. Do not invent APIs. If something is ambiguous, state your assumption explicitly in the PR/commit description and in DECISIONS.md.

# 1. Product summary
Name: "PlantBased" (domain: plantbased). Repository: https://github.com/Pyromania522/PlantBased (owner: Pyromania522). Before you start, check that the domain does not collide with a Home Assistant core integration or an existing HACS default integration; if it does, propose an alternative and stop for confirmation.

Purpose: Track houseplant care purely by timers (NO sensors in this version). Every plant is a real Home Assistant device with its own watering timer and its own fertilizing timer. Plants can be assigned to groups. A built-in Lovelace card shows a small illustration of each plant plus whether it needs water and/or fertilizer, and an overview card shows how many of all plants need water / fertilizer. Everything must be fully available in English and German.

Hard constraints:
- Timer/calendar based only. No moisture/light/soil sensors, no sensor selection fields, no cloud services, no external Python requirements (manifest "requirements": []).
- UI-only configuration (config flow + config subentries + options). No YAML configuration.
- Local only, iot_class "calculated", integration_type "hub".
- Minimum Home Assistant version: 2025.10.0 (target user runs 2026.10.x in Docker with HACS). Python version per current HA requirement.
- No secrets, personal data or tokens anywhere in the repository.

# 2. Data model and configuration UX
- One config entry = the "PlantBased" hub (only one allowed; single_config_entry).
- Plants and groups are CONFIG SUBENTRIES of the hub (subentry types "plant" and "group"), so the user can click "Add plant" / "Add group" directly on the integration card. Each subentry has a reconfigure flow.
- Plant subentry fields: name (required), group (optional, select from existing groups), area (optional, area selector, suggested_area for the device), species/notes (optional free text), location note (optional), image (preset illustration select OR custom image path/URL such as /local/plants/monstera.png), watering interval in days (1–365, default 7), fertilizing enabled (bool, default true), fertilizing interval in days (1–365, default 28), fertilizing season (start month / end month, default March–September, option "all year"), initial last-watered date and last-fertilized date (default today).
- Group subentry fields: name, optional image preset, optional area.
- Hub options flow: reminder enabled (bool), reminder time (default 09:00), notify targets (multi-select of available notify.* / mobile_app services), repeat daily while due (bool, default true), also create persistent notification (bool), include "Snooze 1 day" action button (bool).
- Removing a subentry removes its device and entities cleanly. Removing a group unassigns its plants (do not delete plants).

# 3. Scheduling logic
- Due logic is based on LOCAL calendar days (HA time zone), not on hours: needs_water = today >= last_watered + watering_interval (+ active snooze). Same for fertilizer.
- Fertilizer is never due outside the fertilizing season; next_fertilizing then shows the first day of the next season window.
- Pause / vacation mode per plant (switch) and globally (hub switch): while paused nothing becomes due and no reminders are sent; on unpause, schedules continue from the original dates (document the behavior).
- Snooze: postpones the current due date by N days (default 1) for watering or fertilizing; reset automatically when the action is marked done.
- No polling. Recalculate on state changes, on date edits, at local midnight (async_track_time_change) and at HA start.
- Persist runtime state (last dates, snooze, history) with homeassistant.helpers.storage.Store per config entry, versioned with a migration function. Keep the last 10 watering and fertilizing dates per plant as history.

# 4. Entities (use has_entity_name = True, translation_key for every entity, stable unique_ids based on subentry_id, proper device_info, entity_category where appropriate)
Per plant device:
- button: mark watered, mark fertilized, snooze watering, snooze fertilizing
- date (editable): last watered, last fertilized
- number (config category, box mode, unit days): watering interval, fertilizing interval
- sensor (device_class date): next watering, next fertilizing
- sensor (unit days, may be negative when overdue): days until watering, days until fertilizing
- binary_sensor: needs water, needs fertilizer (translated states, not "problem")
- sensor (device_class enum, translated): care status = ok | water | fertilize | water_and_fertilize | paused; attributes: group, image url, species, overdue days, history
- switch: pause plant
- image entity (optional, only if technically clean): the plant illustration
Per group device:
- sensors: number of plants, plants needing water, plants needing fertilizer
- buttons: mark all watered, mark all fertilized (only acts on member plants)
Hub device ("Plant overview"):
- sensors: total plants, plants needing water, plants needing fertilizer, plants overdue (attributes: lists of plant names)
- binary_sensor: any plant needs care
- switch: global vacation mode
- calendar entity: all upcoming watering/fertilizing dates (all-day events)
- todo entity: "Plant care" list containing currently due tasks; completing an item marks that plant as watered/fertilized

# 5. Actions (services), events, notifications
- Actions with translated names/descriptions in services.yaml + translations, targeting plant or group devices/entities: plantbased.mark_watered (optional date), mark_fertilized (optional date), snooze (care_type, days), set_interval (care_type, days).
- Fire events plantbased_care_due and plantbased_care_done (data: plant device_id, name, care_type) for user automations.
- Built-in reminder (if enabled in hub options): at reminder time send ONE summary notification to the selected notify targets listing due plants grouped by water/fertilizer, translated to the HA language. For mobile_app targets add actionable buttons "All watered", "All fertilized", "Snooze 1 day" and handle mobile_app_notification_action events. Use a notification tag so the push is cleared/replaced when nothing is due anymore. Optional persistent notification, dismissed automatically when everything is done.

# 6. Dashboard cards (shipped inside the integration)
- Bundle a compiled, dependency-light Lovelace card (TypeScript + Lit, built with Rollup/Vite into one JS file committed to custom_components/plantbased/frontend/). Serve it via the HTTP static path API and register it automatically as a frontend module resource so the user does not have to add resources manually. Verify the current recommended way to do this.
- custom:plantbased-card: shows plant illustration, name, group, water and fertilizer status chips with days left / overdue, color states (ok / due / overdue / paused), quick action buttons (watered, fertilized, snooze). Supports a single plant (device) or a group (shows all members in a compact grid). Visual card editor with device picker.
- custom:plantbased-overview-card: counts of plants needing water / fertilizer / overdue / total, list of due plants with one-tap actions.
- Card texts in English and German based on hass.locale/language; respect HA themes, dark mode and mobile layout.
- Ship 8–12 original, simple SVG plant illustrations (e.g. monstera, ficus, pothos, snake plant, succulent, cactus, fern, orchid, herb, palm, hanging plant, generic) created by you under the repo license. No copyrighted or AI-scraped artwork.

# 7. Translations
- strings.json plus translations/en.json and translations/de.json covering config flow, subentry flows, options, entity names and states, actions, issues/repairs, and selector options. German must be natural German ("Wässern", "Düngen", "Gießen fällig", "Düngesaison", "Urlaubsmodus"), not literal translations.
- README in English with a German section (or README.de.md).

# 8. Quality, tests, CI
- Follow the Home Assistant integration quality scale; target at least Silver rules that apply to a calculated hub integration (config flow tests, unique ids, entity translations, diagnostics, reauth not needed, unload/reload support, repair issues where useful). Add diagnostics with no personal data except plant names.
- Async only, typed (mypy-clean), ruff-clean, no blocking I/O in the event loop.
- Tests with pytest-homeassistant-custom-component: config flow, subentry flows, scheduling edge cases (month/season boundaries, DST change, leap year, snooze, pause, group bulk actions, deleting groups), storage migration, actions, notifications/action events, todo and calendar. Aim for >= 90 % coverage of non-frontend code. Freeze time in tests.
- GitHub Actions: hassfest, HACS validation action, ruff, mypy, pytest, frontend build check. A release workflow that builds the card and attaches a zip to GitHub Releases on tag vX.Y.Z.
- Repo files: hacs.json (name, homeassistant min version, render_readme), manifest.json (domain, name, version, documentation, issue_tracker, codeowners [@Pyromania522], documentation and issue_tracker URLs pointing to https://github.com/Pyromania522/PlantBased, config_flow true, integration_type, iot_class, dependencies/after_dependencies as needed e.g. http, frontend, mobile_app), LICENSE (MIT), CHANGELOG.md, DECISIONS.md, CONTRIBUTING.md, issue templates, brand icon/logo prepared according to the current Home Assistant brands process.
- Semantic versioning, start at 0.1.0.

# 9. Milestones (stop after each, summarize, show test results)
M1 Skeleton: repo structure, manifest, hacs.json, hub config flow, CI green (hassfest + HACS validation).
M2 Plants and groups as subentries/devices, storage, scheduling engine, all plant/group/hub entities, translations DE/EN, tests.
M3 Actions, events, snooze, pause/vacation, fertilizing season, calendar, todo, diagnostics, tests.
M4 Reminder notifications incl. actionable mobile_app buttons, tests.
M5 Lovelace cards + illustrations + auto-registration, visual editor, DE/EN.
M6 Docs (README with screenshots placeholders, installation via HACS custom repository, examples of automations using events/actions, uninstall), release v0.1.0.

# 10. Acceptance criteria
- Installable via HACS "Custom repositories" (category Integration) on HA 2025.10+; after restart "PlantBased" can be added from Settings > Devices & services.
- A new plant can be added in under a minute from the integration card and immediately appears as a device with all entities, in the selected area and group.
- Watering and fertilizing timers work independently per plant; marking done updates dates, statuses, counts, calendar, todo and clears reminders.
- Group buttons affect only member plants; overview counts are correct.
- Cards work without manual resource configuration, show illustration and status, and are fully translated in German and English.
- Restarting HA keeps all dates, snoozes, pauses and history.
- All CI checks green; no warnings in the HA log during normal operation.

# 11. Out of scope for v0.1.0 (prepare extension points only)
Sensors (moisture etc.), OpenPlantbook/species databases, weather-based adjustments, cloud sync, HACS default-repository submission (document the remaining steps in DECISIONS.md).

Start with M1. Before writing code, give me a short implementation plan including the verified HA APIs you will use (with doc links) and any open questions.