# OWNERSHIP-SHEET: one owner per shared file

**Rule:** a worker may change files that belong only to its own client. A file that more than one
client's work touches is a SHARED file. Each shared file has exactly one owner. During parallel work,
nobody but the owner edits it. Everyone else writes their change into their request notes, and the
owner makes one combined edit after the client branches merge.

Why: in the episode, Sufi Threads and Noor Dental both asked for a new footer credit. Two workers in
two separate worktrees each changed `shared/footer.html`, and the third merge stopped with a
conflict. Separate copies do not prevent that. An owner does.

Filled in below for the Kiran Studio fixture (`kiran-sites/`). Copy the table for your own repo: one
row per shared file. The "Person" column is yours to fill.

| File or folder                      | Shared by                                             | Owner (role)                   | Person | Who may edit during parallel work                                        | Notes                                                                                                                                       |
| ----------------------------------- | ----------------------------------------------------- | ------------------------------ | ------ | ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `shared/footer.html`                | all three sites (build.py injects it into every page) | Lead developer                 |        | **Owner only.** Client workers never edit it                             | Sufi and Noor both asked for a footer change: the owner merges both requests into ONE line after the client merges, then re-runs the checks |
| `data/mehr-bakery.json`             | Mehr page, checker, critic, PR review                 | Account manager, Mehr Bakery   |        | Nobody in a worker session. Changed only from a confirmed client request | The truth for hours and prices. A worker changes the page to match the data, never the data to match the page                               |
| `data/sufi-threads.json`            | Sufi page, checker, critic, PR review                 | Account manager, Sufi Threads  |        | Same as above                                                            | Sale prices arrive here first, then the page follows                                                                                        |
| `data/noor-dental.json`             | Noor page, checker, critic, PR review                 | Account manager, Noor Dental   |        | Same as above                                                            |                                                                                                                                             |
| `scripts/check-site.py`             | every client, the critic, the PR review               | Lead developer                 |        | **Owner only**                                                           | A worker that "fixes" the checker to pass is the worst failure. Changes go through their own PR                                             |
| `scripts/build.py`                  | every client                                          | Lead developer                 |        | **Owner only**                                                           | In the recorded workflow run, round-2 builders edited build.py to add per-client footers: scope creep the critic must flag                  |
| `scripts/preview.py`                | every client                                          | Lead developer                 |        | Owner only                                                               | Reads `config/local.json`                                                                                                                   |
| `checks.md`                         | every client, the critic, the PR review               | Agency owner                   |        | **Owner only**                                                           | The rules. Never edited to make a page pass                                                                                                 |
| `config/local.json` (gitignored)    | every worktree, via `.worktreeinclude`                | Lead developer                 |        | Owner only; copied, never edited in a worktree                           | Local preview settings. No real secrets in it                                                                                               |
| `.worktreeinclude`, `.gitignore`    | every worktree                                        | Lead developer                 |        | Owner only                                                               |                                                                                                                                             |
| `.claude/workflows/site-refresh.js` | the weekly job                                        | Lead developer                 |        | Owner only                                                               | Edit in its own PR, re-run once by hand before the next Monday                                                                              |
| `.claude/agents/critic.md`          | workflow critic phase                                 | Agency owner                   |        | Owner only                                                               | Changing the critic changes what "approved" means                                                                                           |
| `.claude/skills/pr-review/SKILL.md` | every pull request                                    | Agency owner                   |        | Owner only                                                               | Name stays `pr-review`                                                                                                                      |
| `.github/workflows/site-review.yml` | every pull request                                    | Agency owner                   |        | Owner only                                                               | A PR that edits this file is skipped by the action: review those by hand                                                                    |
| `README.md`                         | everyone                                              | Lead developer                 |        | Owner only                                                               |                                                                                                                                             |
| `sites/mehr-bakery/`                | Mehr only                                             | Mehr worker (`worktree-mehr`)  |        | Mehr worker only                                                         | Not shared                                                                                                                                  |
| `sites/sufi-threads/`               | Sufi only                                             | Sufi worker (`worktree-sufi`)  |        | Sufi worker only                                                         | Not shared                                                                                                                                  |
| `sites/noor-dental/`                | Noor only                                             | Noor worker (`worktree-noor`)  |        | Noor worker only                                                         | Not shared                                                                                                                                  |
| `requests/<client>.md`              | read by the worker, critic, reviewer                  | Account manager of that client |        | Read-only for workers                                                    |                                                                                                                                             |
| `reports/`                          | the weekly workflow                                   | Workflow report phase          |        | Only the report step writes here                                         | One file per run: `reports/<date>-refresh.md`                                                                                               |

## Put the rule in the prompt too

Workers follow what they are told. In the episode, the plain prompt made one worker write the footer
text into the client page instead of `shared/footer.html`. Add a line like this to every worker
prompt:

> Do not edit shared/footer.html, scripts/, data/ or checks.md. If the request needs a change there,
> say so in your summary and stop. The owner makes that change.

## Before parallel work starts (checklist)

- [ ] Every shared file in this repo has a row and an owner.
- [ ] Each worker's prompt names the files it must not touch.
- [ ] Requests that touch a shared file are listed for its owner (here: the Sufi and Noor footer credits).
- [ ] The owner knows the merge order: client branches first, shared-file change last, then checks.
