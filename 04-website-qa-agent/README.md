# 04 · Website QA Agent — Website QA Pack

**For the owner:** a site can pass a page checker and still show the customer the wrong price at checkout.
Site Watch opens each client site like a customer every night and compares what it sees with the client's own
data file; a plain script decides pass or fail, and a named person approves the report before a client sees it.

**Shown in:** Episode 4, "Four tools and nothing else", "Test 1: a pass with no proof", "Test 2: the hidden line
on the page", "Test 3: the link that leaves the site", "Test 4: the catalogue that never ends", "The nightly job
and the morning report", "What the client sees, limits, free pack".

## What's inside

| Path                             | What it is                                                                                                                                                                                                                                                                                                                           |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `site_watch.py`                  | The agent: `query()` + `ClaudeAgentOptions` with `tools=[]`, four in-process tools (`visit`, `click`, `read_truth`, `report`) via `@tool` + `create_sdk_mcp_server`, `allowed_tools`, `can_use_tool` guard, `PreToolUse` audit hook, `max_turns`, `max_budget_usd`, `setting_sources=[]`. Writes `runs/<run>/run.json` + screenshots |
| `verify.py`                      | The verifier. Plain Python, no model: rejects findings without evidence, re-checks every quote against `data/<client>.json`, sweeps every opened page, writes `runs/<run>/report.md` with PASS / FAIL / NOT CHECKED per site                                                                                                         |
| `finding.schema.json`            | The finding schema the agent must fill: client, check, status, expected, seen_text, evidence_url, screenshot                                                                                                                                                                                                                         |
| `kiran-sites/`                   | The three-site fixture (Mehr Bakery, Noor Dental, Sufi Threads; fictional, synthetic): pages, `data/<client>.json` truth files, shared footer, `checks.md`, client requests, the deterministic page checker `scripts/check-site.py`                                                                                                  |
| `kiran-sites/data/<client>.json` | The three client truth files (hours, prices, phone) that both the agent and `verify.py` read                                                                                                                                                                                                                                         |
| `make_www.py`                    | Builds the fixture into `www/<scenario>/` for five scenarios: `clean`, `down` (Noor site missing), `inject` (hidden line), `offsite` (link to example.com), `runaway` (endless catalogue)                                                                                                                                            |
| `serve.py`                       | Serves `www/` on `127.0.0.1` only (default port 8090) and generates the endless catalogue pages                                                                                                                                                                                                                                      |
| `nightly.cmd`                    | Windows nightly job: Site Watch on all sites, then `verify.py`                                                                                                                                                                                                                                                                       |
| `nightly.sh`                     | The same job for a Linux / macOS server                                                                                                                                                                                                                                                                                              |
| `scheduler-lines.txt`            | The Windows Task Scheduler line (and its delete line) and a cron line for a server                                                                                                                                                                                                                                                   |
| `requirements.txt`               | `claude-agent-sdk` and `playwright`, unpinned on purpose: re-test after updates                                                                                                                                                                                                                                                      |
| `REPORT-TEMPLATE.md`             | Morning report with the approval block: who approves, what they approve, where it is recorded; plus a filled example                                                                                                                                                                                                                 |
| `API-KEY-SETUP.md`               | API-key sign-in for client work, key in an environment variable only, `total_cost_usd` = an estimate at list price                                                                                                                                                                                                                   |
| `SDK-NOTES.md`                   | The developer asides cut from the video: `query()` vs `ClaudeSDKClient`, `allowed_tools` skips `can_use_tool`, redirects, caps are fuses, catching `ResultError`, denied calls, the comma gotcha                                                                                                                                     |
| `samples/lie-test/`              | A recorded run plus 3 handcrafted lying findings, so you can watch `verify.py` REJECT and OVERRIDE without a model. `shots/*.txt` are text stand-ins for screenshots                                                                                                                                                                 |
| `samples/capped-run/`            | A recorded run that hit the turn cap: two sites come out NOT CHECKED                                                                                                                                                                                                                                                                 |
| `.gitignore`                     | Keeps `www/`, `runs/`, logs, venvs and `.env` out of git                                                                                                                                                                                                                                                                             |

How to price this: Episode 6, full cost of delivery (module `06-ai-cost-control`).

## Use it in 5 steps

1. **Prerequisites.** Python 3.11+ and a project venv:
   ```
   python -m venv .venv
   .venv\Scripts\activate            (Windows)   |   source .venv/bin/activate   (macOS / Linux)
   pip install -r requirements.txt
   python -m playwright install chromium
   python -c "import claude_agent_sdk, playwright; print('ok')"
   ```
2. **Build and serve the fixture sites** (leave the server running in its own terminal):
   ```
   python make_www.py
   python serve.py                   # http://localhost:8090/clean/sufi-threads/
   ```
3. **Watch the judge work with no model and no cost:**
   ```
   python verify.py samples/lie-test      # 3 lies: REJECTED, REJECTED, OVERRIDDEN; Sufi Threads FAIL
   python verify.py samples/capped-run    # turn cap hit: Mehr Bakery and Noor Dental NOT CHECKED
   ```
   Each writes `report.md` into that sample folder.
4. **Run Site Watch for real** (needs your Claude login or `ANTHROPIC_API_KEY`, see `API-KEY-SETUP.md`; every run is billed):
   ```
   python site_watch.py --run first --scenario clean
   python verify.py runs/first
   ```
   The four attacks from the episode: `--scenario inject`, `--scenario offsite`, `--scenario runaway --clients sufi-threads --max-turns 12 --task "Open the full catalogue and confirm the lawn suit price shown there."`,
   `--scenario down`. Add `--mode naive` to see the version without evidence rules. Lower `--budget` to test the budget fuse.
5. **Schedule it and approve the report.** Windows: `scheduler-lines.txt` (replace `<project>`; `nightly.cmd` runs both steps).
   Server: the cron line in the same file with `nightly.sh`. Each morning a named person fills the approval block in
   `REPORT-TEMPLATE.md` before anything goes to a client.

## Limits — what it does NOT do

- It only tests localhost. `guard()` and `click` refuse any host that is not `localhost` / `127.0.0.1`. To watch real
  client sites, replace `is_local()` with an allowlist of each client's own domains, and add a final-URL check
  for redirects inside the tools (`SDK-NOTES.md` §3). That change is yours to make and test.
- It checks only what is in `data/<client>.json`: hours, prices, phone, and the main button. It is not an SEO,
  accessibility, speed or security audit.
- The hidden-line attack did not fool the agent in the recorded runs. That is not a promise for other wording or
  other models. The defences lower the risk; they do not remove it. `verify.py` has the last word.
- "Needs a human look" items are not decided by the script. A person decides them.
- `total_cost_usd` is an estimate at list price, not a bill. Caps can overshoot slightly (`SDK-NOTES.md` §4).
- Fixture only: fictional clients, synthetic data. No retainer pricing is included.
- The real Site Watch run was not re-run for the kit (it needs a Claude login or API key).

## Tested

Offline, on a scratch copy: all 7 `.py` files compile; `make_www.py` built 5 scenarios; `serve.py` served the
clean, runaway, inject and offsite pages on localhost (and 404 for the `down` site), then was stopped;
`verify.py` on `samples/lie-test` gave REJECTED / REJECTED / OVERRIDDEN and PASS / PASS / FAIL, and on
`samples/capped-run` gave NOT CHECKED / NOT CHECKED / FAIL; `site_watch.py --help` printed its options.
A live Site Watch run was SKIPPED (needs your Claude login / API key).
