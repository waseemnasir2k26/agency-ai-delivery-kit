# Tool surface checklist

Fill one row per tool before a connector goes near a client system. Then fill it again after every change.
The three boxes: **1 · tool exists** (what `server.py` offers) · **2 · permission rule** (Claude Code
`.claude/settings.json`) · **3 · key role** (what the client system lets this key do).

For each tool answer:

- **Which box stops misuse?** Name every box that would stop a harmful call. One box only = fragile.
- **Most it can return:** the largest result (rows, characters). Large results cost context and can be cut off or saved to a file.
- **Personal fields returned:** list them by name. "None" must be checked against the code, not the docstring.
- **Worst case if a stranger controlled the prompt:** assume the text reaching the model came from the public
  (a web-form note, an email, a page). What is the worst this tool could do or reveal?

## Noor Dental `noor-bookings` (filled example, fictional clinic, synthetic data)

| Tool | Reads / writes | Which box stops misuse | Most it can return | Personal fields returned | Worst case if a stranger controlled the prompt |
|---|---|---|---|---|---|
| `list_tomorrow_bookings` | Read (`GET /bookings`) | 1: no write path in code · 2: named allow · 3: read-only key | One day of bookings (about 15 rows in the fixture; bounded by chairs × slots) | Patient name | Reveals tomorrow's names and times to the session user. No change possible |
| `find_available_slots` | Read (`GET /slots`) | 1 · 2 · 3 as above | One day of free slots | None | Reveals free slots. No change possible |
| `get_booking_summary` | Read (`GET /bookings/{id}`) | 1 · 2 · 3; input validated (positive integer) | One booking | Patient name, treatment, the patient's own note (labelled untrusted) | Brings an untrusted note into context; the note can ask for anything, but no tool exists to act on it and no phone field is returned |
| `draft_reschedule` | Read (`GET` booking + slots); returns `"status": "DRAFT"`, `"changed": false` | 1: calls no change endpoint · 2 · 3 | One draft message | Patient name | A misleading draft. A person reads it before applying it in the dashboard |

## Counter-example: the WRONG ON PURPOSE test copy (`noor-bookings-test`)

| Tool | Reads / writes | Which box stops misuse | Most it can return | Personal fields returned | Worst case if a stranger controlled the prompt |
|---|---|---|---|---|---|
| `cancel_appointment` | **Write** (`POST /bookings/{id}/cancel`) | With the front-desk key and the wildcard allow: **none**. With the read-only key: box 3 only (HTTP 403) | n/a | n/a | Cancels real bookings with no prompt. Recorded: a plain "Cancel booking 22." cancelled it at once, 1 row changed |
| every tool | Read, all columns | 3 only | Every column | Phone numbers, raw notes | Leaks every patient's phone number into the session |

## Your connector

| Tool | Reads / writes | Which box stops misuse | Most it can return | Personal fields returned | Worst case if a stranger controlled the prompt |
|---|---|---|---|---|---|
| | | | | | |
| | | | | | |
| | | | | | |
| | | | | | |

Sign-off: tools counted <n> · tools that can write <n> · checked against the code by <name>
