# 03 · Parallel Work — Parallel Work Pack

**For the owner:** three client jobs in the same week without one worker erasing another's work,
without two people fighting over one shared file, and without a wrong price merging because a check
"went green". Fewer redo hours, fewer client-facing mistakes, one named person accountable per merge.

**Shown in:** Episode 3, "Three clients, three workers, three copies", "A worker reaches outside its
copy", "Two workers clash over one shared file", "The weekly job as one saved workflow", "Save it and
rerun it", "A reviewer on every pull request", "Green did not mean reviewed" and "The planted wrong
price".

All data is synthetic. Kiran Studio and its clients (Mehr Bakery, Sufi Threads, Noor Dental) are
fictional; the only phone number is the placeholder `+92 300 0000000`.

## What's inside

| Path                                            | What it is                                                                                                                                                                                                |
| ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `kiran-sites/`                                  | The three-client fixture repo: `sites/`, `data/` (the truth), `requests/` (this week's three asks), `shared/footer.html`, `scripts/` (check-site, build, preview), `checks.md`, `README.md`, `.gitignore` |
| `kiran-sites/config/local.json`                 | The gitignored local preview file (fake values) that new worktrees are missing                                                                                                                            |
| `kiran-sites/.worktreeinclude`                  | Copies `config/local.json` into each new worktree                                                                                                                                                         |
| `kiran-sites/.claude/workflows/site-refresh.js` | The saved workflow: setup, research, build, critic (max 2 rounds), report. Availability note inside                                                                                                       |
| `kiran-sites/.claude/agents/critic.md`          | The critic as a standalone subagent (name, description, tools, model)                                                                                                                                     |
| `kiran-sites/.claude/skills/pr-review/SKILL.md` | The pull request review skill. Name locked: `pr-review`                                                                                                                                                   |
| `kiran-sites/.github/workflows/site-review.yml` | v2: inline comments allowed, JSON verdict, fails on anything but APPROVED. Auth and plugin notes in the header                                                                                            |
| `kiran-sites/.github/site-review.v1.yml`        | v1: green and silent, kept outside `workflows/` so it never runs                                                                                                                                          |
| `WORKTREE-CHEATSHEET.md`                        | `claude --worktree <name>`, `.worktreeinclude` (new worktrees only), trust prompt, keep vs remove, `.claude/worktrees/` in `.gitignore`, Windows notes                                                    |
| `OWNERSHIP-SHEET.md`                            | Filled sheet: every shared file in the fixture, its owner, who may edit it during parallel work                                                                                                           |
| `MERGE-CHECKLIST.md`                            | Required check green, verdict approved (not "job ran"), a person read the diff, who pressed merge                                                                                                         |
| `statusline/`                                   | Status line script (cut from the episode), settings snippet, two sample inputs, README                                                                                                                    |
| `SYSTEM-MAP.md`                                 | The one-page map (the PDF is not included)                                                                                                                                                                |

## Use it in 5 steps

1. **Check prerequisites.**

   ```bash
   claude --version && git --version && python --version
   ```

   Windows needs Git for Windows for worktrees. Use `python3` if that is your command name (the PR
   review on GitHub's Linux runner uses `python3`).

2. **Make the fixture a git repo.** Copy `kiran-sites` somewhere you own, then:

   ```bash
   cd kiran-sites
   git init -b main
   git config core.autocrlf false
   git add . && git commit -m "fixture: three client sites"
   python scripts/check-site.py sufi-threads     # FAIL (4/6) on purpose: the requests are not done yet
   ```

   `config/local.json` stays untracked (it is gitignored); that is the point of `.worktreeinclude`.

3. **Run three workers in three copies.** Read `OWNERSHIP-SHEET.md` first. Three terminals:

   ```bash
   claude --worktree mehr     # then: "Do requests/mehr-bakery.md. Do not edit shared/footer.html,
   claude --worktree sufi     #  scripts/, data/ or checks.md. Run python scripts/check-site.py <client>.
   claude --worktree noor     #  Commit on this branch."
   ```

   Optional: install `statusline/` so each terminal shows its worktree name. In the noor copy, try
   `python scripts/preview.py noor-dental`; it works only because `.worktreeinclude` copied the local
   file when the copy was created.

4. **Merge with an owner, then save the weekly job.** Merge on a scratch branch
   (`WORKTREE-CHEATSHEET.md`). The footer owner makes one combined footer edit last. Then add
   `{"workflowSizeGuideline": "large"}` to `kiran-sites/.claude/settings.json` and run the saved
   workflow from a fresh session in `kiran-sites`:

   ```
   /site-refresh with date YYYY-MM-DD
   ```

   It makes one worktree per client, has the critic check each build, and writes
   `reports/<date>-refresh.md`. Dynamic workflows depend on your plan: check `/config` and the
   workflows docs page first.

5. **Put a reviewer on every pull request.** Push the repo to a private GitHub repo of your own, add
   the secret named in the header of `.github/workflows/site-review.yml` (a team should use
   `ANTHROPIC_API_KEY` from a Claude Console account), install the Claude GitHub app, and make
   `site-review` a required check (`MERGE-CHECKLIST.md`). Test it the way the episode did: open a PR
   that changes Noor's cleaning price on the page to 3000 while `data/noor-dental.json` says 3500.
   Expect a REJECTED verdict, an inline comment on that line, and a blocked merge.

The critic file was written by hand. You can also ask Claude to create a subagent file; the old
`/agents` setup screen is gone.

## Limits — what it does NOT do

- Worktrees isolate files, not decisions: two copies can still change one shared file. Only the
  ownership rule prevents that.
- Worktree isolation stops Claude's edit tools from touching the main checkout. A shell command aimed
  outside the copy was stopped in our test only by the normal permission prompt.
- `.worktreeinclude` applies when a worktree is created, not when an existing one is reopened.
- The workflow's critic is a model. In the recorded runs it approved after two rounds; one rerun left
  a client REJECTED after two rounds. Round-2 builders also edited `scripts/build.py` unasked. A person
  still reads the diff.
- The `critic` subagent has Bash (to run `check-site.py`); it is told to read only, but Bash itself
  is not read-only. Remove Bash from its tools if you want a strictly read-only critic and run the
  checker yourself.
- The PR review needs a GitHub repo, the Claude GitHub app and a paid credential; it was not run for
  the kit. A PR that edits the workflow file skips its own review. Infrastructure errors (an HTTP 504
  during setup) can turn the check red without a verdict.
- `check-site.py` checks hours, prices, phone, email, viewport and the "Prices checked" line. It does
  not check design, spelling or anything else.

## Tested

Offline for the kit: `check-site.py` on the fixture (4/6, 4/6, 5/6 FAIL as recorded; 6/6 PASS on all
three after applying the data in a scratch copy), `build.py`, `preview.py` with and without
`config/local.json`, `node --check` on `site-refresh.js`, YAML parse of both workflow files, the
status line script on sample JSON. Workers, the saved workflow and the PR review need your Claude login.
