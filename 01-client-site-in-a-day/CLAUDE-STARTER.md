# CLAUDE-STARTER.md: a rule sheet template for your own project

Copy this file into your project folder as `CLAUDE.md`, replace every `[...]`, and delete the lines that are not always true for this project. Claude Code reads `CLAUDE.md` at the start of every session.

How to judge a line: if you would not say it to a new team member on day one, it does not belong here. Keep it short (the official guidance is under 200 lines; ten is plenty for one site). It is guidance Claude reads, not a lock: the proof is still a check you run yourself.

```
# [PROJECT NAME]: project rules
- Read BRIEF.md before any change. The brief is the source of truth.
- [Mobile first. Check every change at 375px wide. Nothing may scroll sideways.]
- [Content type, e.g. menu items, prices and reviews] are SAMPLE until the client sends real ones. Keep the SAMPLE label visible.
- The phone number stays [PLACEHOLDER, e.g. +92 300 0000000] until the client confirms the real one.
- The [enquiry form] is TEST MODE. Never send form data over the internet without my written OK.
- Change only what I ask about. Tell me which files you changed.
- Never deploy or publish. Putting this online needs my explicit yes.
- After any change, tell me which lines of QA-CHECKLIST.md to rerun.
- [One rule learned from a failed check, e.g. Every button and link must be at least 44px tall at 375px wide, including small text links.]
```

When a check fails: fix the page with a bug report (see `PROMPTS.md`), then add one line here so the same mistake does not come back next session.

See `CLAUDE.md` in this folder for the filled Mehr Bakery version, and `MEMORY-NOTES.md` for how this file differs from the notes Claude keeps on its own.
