# 06 · AI Cost Control — AI Cost Kit

**For the owner:** know what one client job costs to deliver with AI, from measured runs instead of a plan screen.
Every unattended job gets a dollar cap that cuts it off, and a one-page model table stops quality from being traded
away for a few cents. The worksheet turns the measured cost into a full cost-of-delivery floor, with no prices filled in.

**Shown in:** Episode 6, "BUILD: the first honest number", "Leak 1: the note that got too long", "Leak 3: the job
with no cap", "The diet, the loop rule, the fuse", "Live run: the budget stops the job", "One table, and the judge",
"Handover: the report, the floor, the next problem".

**Prerequisites:** Claude Code installed, Python 3.11+ (standard library only), and for real cost-per-job figures a
Console API key in its **own workspace with a small spend limit**. A subscription login alone will run the scripts,
but the dollar figures are then a local estimate at API list price, not cost-per-job figures and not a bill.

All clients, requests and prices in this module are fictional test data (Kiran Studio, Mehr Bakery).

## What's inside

| Path                        | What it is                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `run_job.py`                | Capped job runner. `--client --job --setup --runs --cap`, plus `--timeout` (wall clock, kills the process tree), `--max-turns` and `--total-cap` (spend ledger over `runs/`). Refuses to start without `--cap`; only `--uncapped-test` overrides, and it still needs `--backstop` and prints a warning. Pre-flight on the session's init event (workflow, four agents, three skills, plugins, SessionStart hook marker, credential) before the first reply. Writes one JSON record per run to `runs/` with `status: done / failed / capped / timeout / preflight_failed`. |
| `cost_report.py`            | Reads `runs/*.json` + `runs/*.meta.json` and writes the per-run table, the min-max range per setup, cost per client per month (`NOT MEASURED` for a client with no runs), a source footer, plus `pricing-floor.md/.csv` and `pricing-worksheet.xlsx` filled with measured cells only.                                                                                                                                                                                                                                                                                     |
| `model-table.md`            | Step → model → effort → why, with the fixed row "never downgrade the judge", plus a blank copy.                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| `pricing-worksheet.xlsx`    | Blank full-cost-of-delivery worksheet: green measured, blue owner-entered, yellow assumption cells, a separate "AI run cost floor (not the job floor)" line, the floor formula and the hours-saved value line. No figures.                                                                                                                                                                                                                                                                                                                                                |
| `pricing-worksheet.csv`     | The same worksheet as plain CSV.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `caps-checklist.md`         | Every unattended job, how it runs, where its cap is set, and the workspace spend limit behind it. Example + blank copy.                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| `CLAUDE-DIET-CHECKLIST.md`  | What stays in `CLAUDE.md`, what becomes a skill, one named owner, the docs target of under 200 lines. Example + blank copy.                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `QUALITY-VS-COST-REVIEW.md` | One row per setup: cost range beside the planted-mistake result. Recorded example + blank copy.                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| `ADVANCED-NOTES.md`         | `Prompt cache (main)` in `/usage`, mid-session model switch, plan usage breakdown, OpenTelemetry per-client tags.                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `setups/`                   | Setup configs: `A.json` (all Opus, long CLAUDE.md), `C.json` (routed, judge on Opus), `D.json` (all Haiku), `STUCK.json` (checker always fails, controlled test), plus `A-trimmed.json`.                                                                                                                                                                                                                                                                                                                                                                                  |
| `kiran-sites/`              | The Claude Code project the job runs in: `CLAUDE.md`, `.claude/settings.json`, `.claude/workflows/site-refresh.js`, `.claude/agents/` (reader, builder, critic, reporter), `.claude/skills/` (pr-review, deploy-steps, brand-voice), `.claude/hooks/session_marker.py`, `check-site.py`, `data/`, `requests/`, `sites/`, `scripts/`, `shared/`.                                                                                                                                                                                                                           |
| `kiran-sites/fixtures/`     | `CLAUDE.fat.md` (134 lines), `CLAUDE.trimmed.md` (15 lines), `check-site.stuck.py`, `check-site.good.py`, `request-mehr-bakery.md` (the planted price), `pristine/` page. The truth file is `kiran-sites/data/mehr-bakery.json`.                                                                                                                                                                                                                                                                                                                                          |
| `sample-runs/`              | Three scrubbed run records from the recording (`C1` routed, `D3` all-Haiku, `STUCK2` capped), each a `.json` + `.meta.json` pair, so `cost_report.py` can be tried offline.                                                                                                                                                                                                                                                                                                                                                                                               |
| `.gitignore` | Keeps your own `runs/`, `out/` and `report/` outputs out of git. |
| `sample-report/`            | The episode's recorded report over all nine runs: `cost_report.md/.csv`, `pricing-floor.md/.csv`, `pricing-worksheet.xlsx` (only the measured AI run cost cell is filled).                                                                                                                                                                                                                                                                                                                                                                                                |

## Use it in 5 steps

1. **Check prerequisites.** `python --version` (3.11+) and `claude --version`. For cost-per-job numbers, create an
   API key in its own Console workspace with a small spend limit and set it for this shell only:
   bash `export ANTHROPIC_API_KEY=<your key>` · PowerShell `$env:ANTHROPIC_API_KEY = "<your key>"`.
   Never paste the key into a file in this folder.
2. **Try the report offline (no model call):**
   `python cost_report.py sample-runs/ --out out/cost_report.md --floor-setup C`
   Read `out/cost_report.md`: the per-run table, the range per setup, and `NOT MEASURED` for Sufi Threads and
   Noor Dental Clinic.
3. **Measure your job with a cap** (this calls Claude and spends money, capped):
   `python run_job.py --client mehr-bakery --job site-refresh --setup C --runs 3 --cap 1.00`
   On a subscription login it refuses unless you add `--allow-subscription-estimate`. Without `--cap` it refuses
   to start. Repeat for the setups you want to compare (`--setup A`, `--setup D`).
   Controlled test of the fuse: `python run_job.py --client mehr-bakery --setup STUCK --runs 1 --cap 0.05`.
4. **Report and review:** `python cost_report.py runs/ --out report/cost_report.md --floor-setup C`, then fill
   `QUALITY-VS-COST-REVIEW.md` and `model-table.md` from it. Never downgrade the judge.
5. **Price floor and caps:** open `pricing-worksheet.xlsx` (or the `.csv`), paste the top of your cost range into
   the green cell, time one human review with a stopwatch, enter your blue and yellow cells, and list every
   unattended job in `caps-checklist.md`. The price comes from the hours the job saves, checked against the floor.

Note: `run_job.py` resets `kiran-sites/` before every run (pristine page, the setup's `CLAUDE.md`, the `model:` and
`effort:` lines in each agent file, the checker). Point it at a copy, not at a live client project.

## Limits — what it does NOT do

- It does not produce a bill. Every dollar figure is Claude Code's client-side estimate at API list price; the
  Console invoice is the bill. On a subscription login the figure is a local estimate, not what you paid.
- It does not set prices. The worksheet has no figures; margin, rates and assumptions are your decisions.
- The recorded numbers come from one small job, one fictional client, and one to three runs per setup. Your jobs
  will move them: run it on your own job before you quote anyone.
- `--max-turns` is not a cost limit: it counts main-session turns only. The dollar cap is the real limit, and spend
  can pass it slightly, so leave headroom and keep a workspace spend limit behind it.
- One job type is wired in (`site-refresh`). Other jobs need their own entry in `JOBS` in `run_job.py`.
- The pre-flight checks what the init event reports; on a failure the runner exits with code 1 and
  `PRE-FLIGHT FAILED`. It cannot prove a skill or agent behaved well, only that it loaded.
- The OpenTelemetry notes were not exercised in the recorded runs.

## Tested

Offline for the kit: `run_job.py --help`; `run_job.py` with no `--cap`, with `--cap 0`, and `--uncapped-test`
without `--backstop` all print `REFUSED` and exit 1 before any Claude process starts; `cost_report.py` over
`sample-runs/` prints the report with `NOT MEASURED` rows; both `.xlsx` files have no values in owner or assumption
cells; all Python files parse, all JSON loads, `site-refresh.js` passes `node --check`. The capped live runs need
your Claude login / API key.
