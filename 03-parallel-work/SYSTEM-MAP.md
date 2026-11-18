# SYSTEM-MAP: Parallel Work, on one page

(The episode mentions a SYSTEM-MAP.pdf. The PDF is not included; this page is the same map as text.)

```
            THREE CLIENT REQUESTS ON ONE MONDAY  ->  THREE WORKERS  ->  ONE REVIEWED MERGE

  requests/mehr-bakery.md   requests/sufi-threads.md   requests/noor-dental.md
           │                         │                          │
  RULE 1: ONE ISOLATED COPY PER JOB  (WORKTREE-CHEATSHEET.md)
  claude -w mehr            claude -w sufi             claude -w noor
  .claude/worktrees/mehr    .claude/worktrees/sufi     .claude/worktrees/noor
  branch worktree-mehr      branch worktree-sufi       branch worktree-noor
     └── .worktreeinclude copies config/local.json into each NEW copy (not into reopened ones)
     └── statusline/  shows [mehr] / [sufi] / [noor] so you type into the right one

  RULE 2: ONE OWNER PER SHARED FILE  (OWNERSHIP-SHEET.md)
  sites/<client>/      -> that client's worker only
  shared/footer.html   -> owner only (Sufi + Noor both asked for it: two copies = merge CONFLICT)
  data/*.json          -> the truth; workers change pages to match data, never the reverse
  scripts/, checks.md  -> owner only; never "fixed" to make a page pass

  THE WEEKLY JOB AS ONE SAVED WORKFLOW  (.claude/workflows/site-refresh.js, /site-refresh with date ...)
  Setup (haiku) one worktree per client
    └► per client, in parallel:
       Research (haiku) exact changes as JSON
       Build (sonnet) in its own worktree ──► Critic (opus, read-only: check-site.py + checks.md + diff)
            ▲                                     │ REJECTED + problems (max 2 rounds)
            └─────────────────────────────────────┘
    └► Report (haiku) reports/<date>-refresh.md: one row per client, verdict, rounds, worktree path
  Recorded run: round 1 rejected all three (hidden "Prices checked" rule), round 2 approved all three.
  A rerun can differ.

  RULE 3: A MERGE WAITS FOR AN APPROVED VERDICT  (MERGE-CHECKLIST.md)
  pull request ──► .github/workflows/site-review.yml (v2)
                     claude-code-action + /pr-review skill
                     ├─ check-site.py for every touched client
                     ├─ inline comment on the exact line
                     └─ --json-schema verdict: APPROVED | REJECTED
                   "Gate on the verdict" step fails on anything but APPROVED
                   branch protection: site-review is a REQUIRED check
                   + a person read the diff + a named person presses merge
  v1 (.github/site-review.v1.yml): green and silent. "Job ran" is not "reviewed".
  Episode test: planted wrong price (page 3000, data 3500) ──► REJECTED, merge blocked.

  WHAT IT DOES NOT DO
  Worktrees do not stop two copies editing one shared file. Isolation does not stop a shell command
  aimed outside the copy (the permission prompt did). The AI review is a sensor, not the decision.
```
