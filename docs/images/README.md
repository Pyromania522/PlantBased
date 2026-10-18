# Screenshots and capture placeholders

`panel-desktop.png`, `panel-mobile.png`, `panel-groups.png` and `panel-areas.png`
preview the v0.2.0 sidebar page. They are actual Chromium captures of the compiled
panel with demonstration data in the browser fixture, not captures from a full HA
installation. Browser tests also capture the dark theme in the CI evidence artifact.

The committed `overview-mobile.png` and `overview-dark.png` are actual Chromium
screenshots of PlantBased's compiled cards using the browser test fixture. The
names and care state are demonstration data. They preview the card appearance;
they are not screenshots of a complete Home Assistant installation.

Replace the following placeholders after a manual supported-HA smoke test. No
broken image links are used while these captures remain unavailable.

| Planned capture | Status | What it should show |
| --- | --- | --- |
| Integration setup and Add plant / Add group | Placeholder | Actual Devices & services UI in English/German |
| Single plant, group and visual editor | Placeholder | Selection, care status and group membership in HA |
| Care calendar and to-do list | Placeholder | Upcoming dates and completion updating the same plant |
| Companion reminder actions | Placeholder | A real summary with scoped care/snooze actions |

Use demonstration plant names and omit personal device details. Keep captions
explicit about the HA version, language, theme and whether a capture uses a fixture.
The source screenshots can be regenerated with the documented Playwright command;
see CONTRIBUTING.md. Code and original artwork, including these card previews,
are covered by the repository's MIT license.
