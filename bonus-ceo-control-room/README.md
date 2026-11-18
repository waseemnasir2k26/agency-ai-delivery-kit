# Bonus · Monday Control Room — CEO Monday Pack

**For the owner:** One command runs the week's client maintenance in parallel (reports, site checks, bookings, a hook canary, a kit check, a cost report), each job with its own money, time and turn cap. You get one page: what is done, what needs your decision, what is at risk, and what it cost. Nothing is sent, merged or published: every outward action is a draft that waits for a person.

**Shown in:** Bonus episode, "BUILD: the job list", "BUILD: caps and the startup check", "BUILD: one command, the live run", "BREAK: the thing the AI may not fix" and "FIX: one page, and the human gate".

Kiran Studio and its clients (Mehr Bakery, Sufi Threads, Noor Dental Clinic) are fictional. All data is synthetic. Dollar figures are local estimates at API list price, not a bill.

## What's inside

| Path                                                                      | What it is                                                                                                                                                                                                                                                                                                                                                           |
| ------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `monday.py`                                                               | The orchestrator. Prints the limits first, runs a startup self-check (the agency kit `kiran-core` must load with its skills, else `PREFLIGHT FAILED`, exit 3), then runs nine jobs in parallel with per-job caps, a whole-run money cap, a wall clock and a free-memory wait. Writes `runs/<run>/digest.md`, `digest.html`, `facts.json`, `result.json`, `streams/`. |
| `clients.json`                                                            | The three fictional clients: which jobs each gets, and the kit release each is pinned to.                                                                                                                                                                                                                                                                            |
| `data/`                                                                   | Synthetic weekly numbers per client (input to the report jobs and their checks).                                                                                                                                                                                                                                                                                     |
| `.claude/settings.json`                                                   | Project settings for the child runs: manual mode, a deny rule for the booking connector's cancel tool, the kit plugin. The marketplace `path` is a placeholder: replace it with the full path to your `deps/kiran-marketplace`.                                                                                                                                      |
| `tools/cc_env.py`                                                         | Isolated config for every child Claude Code run (`CLAUDE_CONFIG_DIR=./.cfg`), parent-session variables stripped; your own `~/.claude` is never written. Mock mode passes no login at all.                                                                                                                                                                            |
| `tools/mock_api.py`                                                       | The forced-test stand-in for the model API (from Episode 10). Claude Code runs for real; only the model is replaced by a scripted plan. $0. Used by the startup self-check and the regression canary.                                                                                                                                                                |
| `tools/e2_report.py`                                                      | The Episode 2 report rules as code (three wins, no email address, no invented numbers, 150 words or fewer). `monday.py` imports it.                                                                                                                                                                                                                                  |
| `tools/offline_check.py`                                                  | Added for the kit: a $0 self-test of `verify.py`, `e2_report.py` and `mock_api.py`. No model, no Claude Code.                                                                                                                                                                                                                                                        |
| `tools/term/term.html`                                                    | The terminal page the recording used (xterm.js page shown in OBS). The xterm.js library files and fonts are not included.                                                                                                                                                                                                                                            |
| `sitewatch/site_watch.py`, `sitewatch/verify.py`                          | Copies of the Episode 9 Site Watch agent (Agent SDK + real browser) and its code judge `verify.py` (with a client filter).                                                                                                                                                                                                                                           |
| `sitewatch/data/`, `sitewatch/finding.schema.json`                        | The source-of-truth data for the two websites, and the evidence schema every agent finding must fill.                                                                                                                                                                                                                                                                |
| `sitewatch/www/`                                                          | The two fictional websites. `mehr-bakery/order.html` carries the planted price (PKR 1350 on the page, 1200 in the data): the CONTROLLED TEST in the episode.                                                                                                                                                                                                         |
| `sitewatch/order.clean.html`                                              | The Mehr Bakery order page before the planted price, to reset it.                                                                                                                                                                                                                                                                                                    |
| `kshell.py`                                                               | The tiny on-camera shell (`kiran>` prompt) that runs `python monday.py` and prints a digest.                                                                                                                                                                                                                                                                         |
| `rec_live.py`, `obs_rec.py`                                               | How the take was recorded: a real pseudo-terminal streamed into an OBS browser source. Reference only; Windows + OBS. `obs_rec.py` is included because `rec_live.py` imports its helpers.                                                                                                                                                                            |
| `sample-run/digest.md`, `sample-run/digest.html`, `sample-run/facts.json` | The digest and the job facts from the recorded run (run id replaced by `sample-run`).                                                                                                                                                                                                                                                                                |
| `.gitignore`                                                              | Keeps `.cfg/`, `runs/`, `captures/` and `deps/` out of git.                                                                                                                                                                                                                                                                                                          |

## Use it in 5 steps

1. **Check the prerequisites.** Python 3.11 or newer and Claude Code on the PATH:

   ```bash
   python --version
   claude --version
   ```

   On Windows, run the commands below in PowerShell from this folder; they are the same.

2. **Run the free checks first ($0, no model, no login used).**

   ```bash
   python tools/offline_check.py      # verify.py, report rules, mock API -> "OFFLINE CHECK: PASS (3/3)"
   python monday.py --help
   python monday.py --bare --plain    # CONTROLLED TEST: must stop with "PREFLIGHT FAILED ... Nothing ran.", exit 3
   ```

   `--bare` starts one Claude Code run against the local mock API (`tools/mock_api.py`) with the isolated config in `./.cfg`. No model is called and nothing runs after the failed self-check. The same `PREFLIGHT FAILED` appears without `--bare` until step 3 is done, because the kit is not installed yet.

3. **Bring in the parts from the other episodes.** The real run needs three folders from earlier modules, placed in `./deps/` (or point `KIRAN_DEPS` at a folder that holds them):
   - `deps/noor-booking-app/` (`app.py`, `reset.py`) and `deps/noor-bookings/server.py` from the Episode 5 module (the clinic's booking app and its read-only connector)
   - `deps/kiran-marketplace/` from the Episode 9 module (a git repo with the `kiran-core--v*` release tags)

   Optional variables: `NOOR_PYTHON` (a Python with the Episode 5 requirements) and `SDK_PYTHON` (a Python with `claude-agent-sdk` and `playwright` for Site Watch). Both default to the Python that runs `monday.py`. If a part is missing, `monday.py` prints which one and stops with exit 4 before any job starts.

4. **Install the kit into the isolated config and sign in.** Put the full path of `deps/kiran-marketplace` into `.claude/settings.json`, then, with `CLAUDE_CONFIG_DIR` pointing at `./.cfg`, add the marketplace and install `kiran-core@kiran-marketplace` with `--scope project`, as in Episode 9:

   ```bash
   # macOS / Linux / WSL
   export CLAUDE_CONFIG_DIR="$PWD/.cfg"
   # Windows PowerShell
   $env:CLAUDE_CONFIG_DIR = "$PWD\.cfg"
   ```

   Real runs use your Claude login (see `tools/cc_env.py` for how the login reaches the child runs). Re-check the plugin commands against https://code.claude.com/docs after each Claude Code update.

5. **Run Monday.** Read the caps first: whole run `--run-cap` (default 2.00 USD, estimate), wall clock `--wall-min` (default 12), `--workers` (default 5).
   ```bash
   python monday.py            # live control-room view in a terminal
   python monday.py --plain    # log lines instead
   ```
   Open `runs/<run>/digest.html` in a browser. Every decision on it is yours: approve a report, pick the right price, approve the reschedule drafts, upgrade a client's kit or wait. Compare with `sample-run/digest.html`.

## Limits — what it does NOT do

- It does not send, publish, merge or change anything in a client system. Reports are drafts, reschedules are drafts, and the Site Watch agent does not edit the website.
- It does not run on its own on a schedule. You start it. A scheduled version needs its own caps and circuit breaker first.
- The full run needs the Episode 5 and Episode 9 modules plus your Claude login. Only the free checks in step 2 run with this folder alone.
- Dollar figures are local estimates at API list price, not a bill. On a subscription login there is no per-run invoice to compare against.
- The digest is a summary written by a model. Code checks that every number in it appears in the job facts and that the four headings are there; it does not check the wording. Read the facts behind a decision before you act on it.
- Site Watch needs a real browser (Playwright Chromium) and the Agent SDK. `tools/cc_env.py` looks for a Windows Playwright Chromium build; on other systems set `SITEWATCH_CHROME` or let Playwright use its default.
- Tested with fictional clients and small jobs on one machine. It is not a load test, and nine parallel jobs need free memory (`--min-free-gb`).
- `rec_live.py` / `obs_rec.py` are a reference for how the episode was recorded (Windows, OBS Studio, pywinpty, websockets, websocket-client, the xterm.js files). They were not run for the kit.
- The authentication path reads your login from `~/.claude/.credentials.json` when that file exists. Where the login lives elsewhere (for example the macOS Keychain), sign in inside `./.cfg` instead.

## Tested

Offline for the kit: all Python files compile, all JSON parses, `python tools/offline_check.py` → PASS 3/3 (verify.py finds the planted PKR 1350 vs 1200 price), `python monday.py --bare --plain` → `PREFLIGHT FAILED`, exit 3, one request to the local mock only, isolated config in a scratch copy. The full nine-job run needs your Claude login and was not re-run for the kit; `sample-run/` is the recorded result.
