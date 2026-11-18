# Memory notes: CLAUDE.md vs auto memory

Every new Claude Code session starts a fresh conversation. Two kinds of file carry knowledge from one session to the next. They are not the same, and only one of them is yours.

|                            | `CLAUDE.md`                                                 | Auto memory                                         |
| -------------------------- | ----------------------------------------------------------- | --------------------------------------------------- |
| Who writes it              | You (or Claude drafts it and you read every line)           | Claude, on its own                                  |
| Who controls what is in it | You                                                         | Claude chooses what to keep                         |
| When it is loaded          | Every session                                               | Every session                                       |
| Where it lives             | In the project folder, next to your files                   | In Claude Code's own data folder                    |
| Use it for                 | Rules that must hold on every piece of work for this client | Nothing you rely on. Treat it as Claude's own notes |

Both are context Claude reads, not enforced configuration. Neither is a lock. The proof is still a check you run yourself (`QA-CHECKLIST.md`).

## CLAUDE.md

- Lives in the project folder. Claude reads it at the start of every session.
- Keep it short and specific. The official guidance is under 200 lines per file; the shorter and more specific it is, the more consistently Claude follows it. The Mehr Bakery file is 10 lines.
- Each line should be always true for this project. If you would not say it to a new team member on day one, it does not belong here.
- `/init` drafts a starter `CLAUDE.md` from the project. Read every line before you keep it.
- A project's `AGENTS.md` can also be read.
- When a check fails, fix the page with a bug report, then add one line to `CLAUDE.md` so the mistake does not come back next session.

Templates in this folder: `CLAUDE.md` (the filled Mehr Bakery version) and `CLAUDE-STARTER.md` (blank template for your own project).

## Auto memory

- On by default in local sessions. Claude keeps a few notes of its own between sessions.
- See what it has kept, or switch it off, with `/memory`.
- Switch it off for one project in that project's `.claude/settings.json`:

```json
{
  "autoMemoryEnabled": false
}
```

(Merge it with what is already there, for example next to `"permissions"`.)

## Keep sessions clean

- `/clear` starts a new conversation. Use it when you switch tasks, so old instructions do not leak into new work. `CLAUDE.md` is loaded again; the chat is not.

Re-check these commands and settings against https://code.claude.com/docs (page "Memory") after each Claude Code update.
