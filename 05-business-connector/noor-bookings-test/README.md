# WRONG ON PURPOSE. Never point this at a real system.

`noor-bookings-test` is the deliberately broken copy of `noor-bookings` used for the Episode 5 break tests
(CONTROLLED TEST). Fictional clinic, synthetic data.

| Box | Mistake |
|---|---|
| 1 Tools that exist | fifth tool `cancel_appointment` (changes data) |
| 2 Claude Code permission rule | `.claude/settings.json` allows `mcp__noor-bookings-test__*` (wildcard = blank cheque) |
| 3 The booking system's own key | run with the front-desk key in `NOOR_API_TOKEN` |
| + | every tool returns every column (phone numbers, raw notes) |

The fix (Episode 5, S4a) deletes this folder. See `../README.md` for run commands.
