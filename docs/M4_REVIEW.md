# Add local care reminders and Companion notification actions (M4)

M3 exposed due care through controls, events, calendar and tasks but did not send
reminders. This adds opt-in hub options for local reminder time, notifier targets,
daily repeat, a persistent HA copy and an optional mobile Snooze 1 day button.
One summary per selected recipient groups currently due plants by care type.
English/German content follows HA's language; pause/vacation and season rules
reuse the care engine.

Private versioned receipt storage supports startup catch-up and ordinary
reload/restart/DST deduplication. Tagged mobile summaries replace/clear with care
changes; persistent copies are restored and dismissed as needed. Removed targets
and disabled/removed hubs clean up known messages. Notify entities support basic
message/title delivery; Companion action/tag payloads use notify.mobile_app_*
services because the entity API does not support that data.

Mobile action IDs scope changes to the still-due task identities in the original
message. Actions are checked again under the care lock, preventing stale/replayed
messages from completing healthy or later-cycle plants. Bulk snooze handles both
care types in one verified transaction. Recipient failures cannot modify care or
block other targets. Diagnostics exclude target IDs and action tokens.

Validation: **181 tests pass on each of HA 2025.10.0/Python 3.13.2 and
HA 2026.10.2/Python 3.14.2**, no skips/xfails, **98.51% statement/branch coverage**.
Ruff, strict mypy on 24 modules, official local hassfest and independent real-file
care/reminder storage checks pass. Tests use native options flows, public HA
notify services/entities, persistent-notification callbacks and mobile event
payloads, including both DST changes, concurrency, failures and cleanup.
Exact-head remote CI acceptance is recorded on this PR.

Assumptions in DECISIONS.md: reminders default off at 09:00 HA-local time;
repeat off means newly due tasks trigger another scheduled summary. Startup
catches up today's unsent reminder. Skipped clock times shift forward by the DST
gap. Mobile actions affect only listed, still-due tasks; other channels receive
basic summaries without universal recall. Runtime notification wording has a
small bilingual catalog because HA's integration translation schema has no
arbitrary notification-text category; hub options use standard EN/DE resources.

Provider service acceptance cannot prove phone delivery/clearing. Delivery and
durable receipt writes cannot be one external transaction; a crash between them
can repeat a message (mobile tags replace it). No real device/provider send,
browser manual test, full process restart, Silver tier or release is claimed.
Runtime requirements remain empty. Frontend/cards/artwork remain M5, release M6.
