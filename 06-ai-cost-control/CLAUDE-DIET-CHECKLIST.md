# CLAUDE.md diet checklist

`CLAUDE.md` is loaded into context at the start of every session, for every task. Skills load only when a task
needs them. A long `CLAUDE.md` is a cost you pay on every job, whether the job needs those lines or not.

## The rule

**CLAUDE.md keeps only what is true for EVERY task. One named owner. Everything else becomes a skill.**
The Claude Code docs set a target: keep `CLAUDE.md` under 200 lines.

## Checklist

- [ ] **One named owner** at the top of the file ("Owner of this file: the studio lead. Change it only by pull
      request."). A role, not a shared inbox.
- [ ] For every section, ask: is this true for every task? If not, it moves.
- [ ] **Stays:** where things live, where the truth lives (the data files), hard rules that apply to every edit
      (placeholder phone only, no emails on pages, run the checker after every edit, never commit local config,
      never push without a human review), the client list.
- [ ] **Becomes a skill** (`.claude/skills/<name>/SKILL.md`): checklists for one kind of task (PR review), deploy
      steps, brand voice guides per client, anything long that only some tasks need.
- [ ] The trimmed file names each skill in one line so people can find it.
- [ ] Under 200 lines (docs target). Shorter is better.
- [ ] Measure the load before and after with `/context` (the Memory files row for the project `CLAUDE.md`).
- [ ] Do not claim a dollar saving until you have re-run the job with the short file. The load is the measured fact.

## Kiran Studio example (recorded result)

|                                                 | Before                                                                                                                                          | After                                    |
| ----------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- |
| File                                            | `kiran-sites/fixtures/CLAUDE.fat.md`                                                                                                            | `kiran-sites/fixtures/CLAUDE.trimmed.md` |
| Lines                                           | 134                                                                                                                                             | 15                                       |
| `/context` Memory files row (project CLAUDE.md) | about 2.9k tokens                                                                                                                               | 337 tokens                               |
| Moved to skills                                 | PR checklist → `.claude/skills/pr-review/` · deploy steps → `.claude/skills/deploy-steps/` · three voice guides → `.claude/skills/brand-voice/` |                                          |
| Dollar saving                                   | not claimed: the expensive setup was not re-run with the short file                                                                             |                                          |

## Blank copy

| Section in your CLAUDE.md | True for every task? (y/n) | Stays / moves to skill | Skill name | Done |
| ------------------------- | -------------------------- | ---------------------- | ---------- | ---- |
|                           |                            |                        |            |      |
|                           |                            |                        |            |      |
|                           |                            |                        |            |      |

Owner of this file: **********\_\_********** · Lines before: \_**\_ · Lines after: \_\_**
