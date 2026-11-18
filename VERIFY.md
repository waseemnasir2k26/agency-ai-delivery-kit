# Verify

What was run for this release, offline, with no paid model calls, and the result.
Anything that needs a real Claude session, an API key, an admin machine or a browser is marked SKIPPED with the reason. Nothing is guessed.

**Summary: 93 checks PASS · 0 FAIL · 16 SKIPPED (need your Claude login, WSL plus admin rights, or a person in a browser).**

Run these again after every Claude Code update. Commands are relative to the module folder.

| Module | Command | Result | Evidence |
| --- | --- | --- | --- |
| 01 | `python -c json.load(starter/.claude/settings.json)` | PASS | `{"permissions": {"defaultMode": "default"}}` |
| 01 | `python check_01.py starter/` (offline HTML open-check) | PASS | 14/14: local links resolve (index 6, inbox 4), no template text, tel:+923000000000 = label "+92 300 0000000", 6 items/6 prices/2 reviews all SAMPLE, 44px rule on `#enquiry form + p a, footer a`, CLAUDE.md 10 lines, QA lines 1-6 |
| 01 | `node --check starter/site.js` | PASS | syntax OK; no fetch/XHR/beacon/URL in site.js (nothing sent over the internet) |
| 01 | `gitleaks dir 01-client-site-in-a-day` | PASS | no leaks found |
| 01 | QA-CHECKLIST lines 1-6 by hand in Chrome at 375px | SKIPPED (manual, browser) | recorded episode result: all six pass on this copy |
| 02 | `cd kiran-ops && python tests/run-checks.py tests/sample-outputs/v2` | PASS | RESULT: 3/3 PASS (46/45/53 words), same as the episode's recorded grade |
| 02 | `cd kiran-ops && python tests/run-checks.py tests/sample-outputs/v1` | PASS | RESULT: 0/3 PASS as recorded (no Wins section, 288/255/244 words, email in case2, invented figures) |
| 02 | `bash bypass-tests/run-bypass-tests.sh` | PASS | RESULT: 58 as expected, 0 unexpected: both hooks fed PreToolUse JSON as Bash and PowerShell tools; exit 2 on every block, exit 0 on allowed cases and the 3 documented gaps |
| 02 | `echo '{"tool_name":"PowerShell","tool_input":{"command":"Get-Content .env"}}' \| bash kiran-ops/.claude/hooks/secret-firewall.sh` | PASS | exit=2, "BLOCKED by secret-firewall: this command touches a .env secrets file" |
| 02 | PowerShell `git commit -m x` JSON \| `bash kiran-ops/.claude/hooks/commit-gate.sh` | PASS | exit=2, "COMMIT BLOCKED by commit-gate: no review on file" |
| 02 | `python kiran-ops/.claude/hooks/commit-shape.py` (7 commands on stdin) | PASS | plain / plain / all / paths / alias / none / plain for commit, -C ., -am, paths, alias, git status, `& git commit` |
| 02 | `cd kiran-ops && python tests/validator-selftest.py` | PASS | RESULT: 4/4 as expected (green -> report; missing data file, budget hit, wrong number -> FAILED receipt) |
| 02 | `cd kiran-ops && python tests/test_pricing.py` | PASS | test_pricing: 2/2 passed |
| 02 | JSON parse of `.claude/settings.json.READY`, `schema.json`, data files, robot samples | PASS | all parse; matcher = `Bash\|PowerShell`, defaultMode = default |
| 02 | `bash -n` on all .sh hooks/scripts, `python -m py_compile` on all .py | PASS | no syntax errors |
| 02 | `gitleaks dir 02-repeatable-delivery` + privacy / banned-word / date grep | PASS | no leaks found; 0 hits |
| 02 | `python tests/run-cases.py runs/x`, `bash scripts/run-review.sh`, `run-report.cmd` / `run-report.sh`, live block test per tool | SKIPPED (needs Claude login) | real model calls; recorded results are in RETEST-LOG.md and the episode captures |
| 03 | `python scripts/check-site.py <client>` x3 in `kiran-sites` (scratch copy) | PASS | mehr 4/6, sufi 4/6, noor 5/6 FAIL exit 1, identical to the recorded fixture selftest |
| 03 | same, after applying data/\*.json to the pages in a scratch copy | PASS | 6/6 PASS exit 0 for all three clients |
| 03 | `python scripts/build.py` (scratch copy) | PASS | built dist/<client>/index.html x3 |
| 03 | `python scripts/preview.py noor-dental` with and without config/local.json | PASS | "Preview OK ... (analytics DEMO-0000)" / "ERROR: config/local.json not found" exit 1 |
| 03 | `node --check kiran-sites/.claude/workflows/site-refresh.js` (raw, and wrapped as an async body) | PASS | exit 0 both |
| 03 | YAML parse (python yaml) of `.github/workflows/site-review.yml` and `.github/site-review.v1.yml` | PASS | both parse; v2 has claude_args (--allowedTools + --json-schema) and the gate step |
| 03 | `python statusline/statusline.py < statusline/sample-worktree.json` (+ sample-main, bad JSON) | PASS | `[mehr] ctx 7% \| $0.09`, `[main] ctx 3% \| $0.00`, fallback line on bad input |
| 03 | `gitleaks dir 03-parallel-work` + privacy / banned-word / date grep | PASS | no leaks found; 0 hits (dates only inside fixture data files) |
| 03 | `claude --worktree <name>` workers, `/site-refresh with date ...`, PR review on GitHub | SKIPPED (needs Claude login) | real model calls / a GitHub repo and secret; recorded results in the episode captures |
| 04 | `python -m py_compile` on all 7 .py (site_watch, verify, make_www, serve, kiran-sites/scripts/\*) | PASS | 7 files compiled, no errors |
| 04 | `python make_www.py` | PASS | built ['clean', 'down', 'inject', 'offsite', 'runaway'] |
| 04 | `python serve.py 8095` + urllib GET of 5 pages, then server stopped | PASS | 200 on clean/sufi-threads (buy button PKR 4500), runaway catalogue/7 (links to page 8), inject (hidden AI line), offsite/noor-dental (example.com link); 404 on down/noor-dental |
| 04 | `python verify.py samples/lie-test` | PASS | 18 ACCEPTED, 2 REJECTED (no evidence; quote not on page), 1 OVERRIDDEN (page PKR 4500, data PKR 3600); VERDICT PASS / PASS / FAIL |
| 04 | `python verify.py samples/capped-run` | PASS | VERDICT mehr-bakery NOT CHECKED, noor-dental NOT CHECKED, sufi-threads FAIL (turn-capped run) |
| 04 | `python kiran-sites/scripts/check-site.py sufi-threads` | PASS | 6/6 checks pass: the page checker misses the wrong buy-button price (the episode's cold open) |
| 04 | `python site_watch.py --help` (Python with claude-agent-sdk + playwright installed) | PASS | argparse help printed: --scenario, --mode, --run, --clients, --model, --max-turns, --budget, --port, --task |
| 04 | `gitleaks dir .` | PASS | no leaks found |
| 04 | `python site_watch.py --run first --scenario clean` + `python verify.py runs/first` | SKIPPED (needs Claude login) | real agent run calls a model (Claude login or API key); not run for the kit |
| 05 | compile all 13 .py (app, db, keys, seed, reset, seed_note, snapshot, plant_stale_slot, both servers, smoke_test, site_watch_noor, verify_noor) | PASS | 13 files compiled, no errors |
| 05 | `python -c "import mcp"` | PASS | system Python has mcp 1.x (below the pin), so an existing local venv with mcp 2.3.0 was used; no new install |
| 05 | `cd noor-booking-app` then `seed.py`, `snapshot.py dump`, `seed_note.py`, `plant_stale_slot.py` (+ `--clear`), `snapshot.py diff`, `keys.py list`, `reset.py` (scratch copy) | PASS | 40 synthetic bookings, 15 tomorrow, 5 unconfirmed; note planted on booking 28; stale slot planted (taken by booking 23) and cleared; diff = 1 row changed (the note); keys ...1111 / ...0000 active |
| 05 | `python smoke_test.py` | PASS | 23/23 PASS: 401/403 roles; exactly 4 read-only tools; test_list_tomorrow_bookings, test_find_available_slots, test_get_booking_summary (no phone), test_draft_reschedule (DRAFT, changed=False); rows changed 0; wrong copy: 5 tools, phone leak, front-desk cancel works, read-only cancel refused 403 |
| 05 | JSON parse of `.mcp.json` + `.claude/settings.json` (both projects) and `variants/*.json` | PASS | 8 files parse |
| 05 | `gitleaks dir . --config .gitleaks.toml` | PASS | 14 expected findings, all rule `noor-api-token`, every match a FAKE fixture token; planted `variants/mcp.WRONG-key-committed.json` caught at line 10 |
| 05 | `gitleaks dir .` with default rules only | PASS | no leaks found |
| 05 | `claude mcp add` / `claude mcp list` / interactive trust + approval / break tests with a model | SKIPPED (needs Claude login) | recorded results kept in handover-noor.md as recorded results |
| 05 | `npx @modelcontextprotocol/inspector ...` | SKIPPED (needs Claude login) | needs Node + browser; the same tool calls are covered offline by smoke_test.py |
| 05 | `python site_watch_noor.py --out results/S1` + `python verify_noor.py results/S1` | SKIPPED (needs Claude login) | billed model run via the Agent SDK |
| 06 | `python run_job.py --help` | PASS | usage printed: --client --job --setup --runs --start --cap --max-turns --timeout --total-cap --uncapped-test --backstop |
| 06 | `python run_job.py --client mehr-bakery --setup C --runs 1` (no cap) | PASS | `REFUSED: no --cap. Every unattended job runs with a dollar cap (or announce --uncapped-test).` exit 1; the refusal is in main() before setups load or any claude process starts |
| 06 | `python run_job.py --client mehr-bakery --setup C --cap 0` | PASS | same REFUSED, exit 1 |
| 06 | `python run_job.py --client mehr-bakery --setup STUCK --runs 1 --uncapped-test` (no backstop) | PASS | `REFUSED: --uncapped-test still needs an off-screen --backstop`, exit 1 |
| 06 | `python cost_report.py sample-runs/ --out <scratch>/cost_report.md` | PASS | 3-run table (C1 done/REJECTED, D3 done/APPROVED, STUCK2 CAPPED), ranges, Sufi Threads + Noor Dental Clinic = NOT MEASURED, "fewer than 3 runs" warning, source footer |
| 06 | `python cost_report.py <all 9 scrubbed records> --out sample-report/cost_report.md --floor-setup C` | PASS | regenerated report matches the recorded BUILDS report line for line (version string replaced by "release used for the recording") |
| 06 | openpyxl check of `pricing-worksheet.xlsx` and `sample-report/pricing-worksheet.xlsx` | PASS | 0 values in BLUE owner-entered or YELLOW assumption cells; the blank sheet has no figures at all; the sample has only the green measured AI run cost cell |
| 06 | `python kiran-sites/check-site.py mehr-bakery` (pristine page) | PASS | model-free checker runs: 3/5 pass, FAIL hours + prices-checked line as expected on the pristine page (log file removed) |
| 06 | ast parse of all .py · json.load of all .json · `node --check site-refresh.js` | PASS | all parse |
| 06 | gitleaks + privacy/banned-word grep over the module | PASS | no leaks; no user paths, names, emails or version numbers in prose |
| 06 | `python run_job.py --client mehr-bakery --setup C --runs 3 --cap 1.00` | SKIPPED (needs Claude login) | live capped runs need your Claude login / API key |
| 07 | temp git copy of kiran-marketplace (SCRATCH): `python ci/check_kit.py --base HEAD` | PASS | 6/6 PASS lines, "check_kit: all rules passed", exit 0 |
| 07 | same copy, catalogue entry renamed `kiran-core` → `kiran-kit`: `python ci/check_kit.py --base HEAD` | PASS (fails as designed) | `FAIL kiran-kit: names disagree: folder='kiran-core' entry='kiran-kit' plugin.json='kiran-core'`, exit 1 |
| 07 | same copy, `plugins/kiran-core/README.md` changed, version not bumped: `python ci/check_kit.py --base HEAD` | PASS (fails as designed) | `FAIL kiran-core: 1 plugin file(s) changed since HEAD but version is still 1.1.0`, exit 1; after bump to 1.1.1 + CHANGELOG line → all rules passed, exit 0 |
| 07 | `CLAUDE_CONFIG_DIR=<scratch> claude plugin validate kiran-marketplace --strict` (local, no login, isolated config) | PASS | `✔ Validation passed`, exit 0 (README install-line advice only); also passed the name mismatch, confirming check_kit is needed |
| 07 | `CLAUDE_CONFIG_DIR=<scratch> claude plugin tag plugins/<p>/ --dry-run --force` (both plugins) | PASS | `✔ Dry run — would create tag kiran-core--v1.1.0` / `kiran-noor--v1.0.0`, exit 0 |
| 07 | Git Bash: PreToolUse JSON `Bash: cat .env` → `scripts/secret-firewall.sh` | PASS | `BLOCKED by secret-firewall: this command touches a .env secrets file`, exit 2 |
| 07 | Git Bash: PreToolUse JSON `PowerShell: Get-Content .env` → `scripts/secret-firewall.sh` | PASS | same BLOCKED line, exit 2; `cat .env.example` and `git status` exit 0; Write with fake AWS-format key exit 2 |
| 07 | Git Bash: PreToolUse JSON `git commit -am wip` (Bash) / `git commit -a -m wip` (PowerShell) → `scripts/commit-gate.sh` | PASS | `COMMIT BLOCKED by commit-gate: do not use commit -a`, exit 2; `ls` exit 0 |
| 07 | `scripts/run-review.sh` (critic review, `claude -p`) | SKIPPED (needs Claude login) | makes a model call; not run |
| 07 | `gitleaks dir 07-agency-kit-plugins` + privacy/banned-word grep | PASS | no leaks found; no names, local paths, dates or versions in prose |
| 08 | `python3 policy_test.py` (full run) | SKIPPED (needs WSL+admin) | needs WSL2 + root-placed managed file + lab setup; recorded WSL2 lab results shipped in results/ (pre-fix 9/10, post-fix 10/10) |
| 08 | `python -m py_compile policy_test.py lab/mock_api.py lab/otel_sink.py fixture/sufi-threads/*.py` | PASS | all 6 files compile |
| 08 | `python policy_test.py --help` | PASS | prints usage + the 10 test ids, exit 0, no Claude Code call (kit-added flag) |
| 08 | import + in-process smoke of `lab/mock_api.py` and `lab/otel_sink.py` (ephemeral localhost ports) | PASS | mock returned `tool_use Read {"file_path": ".env"}` from a plan file; sink wrote `claude_code.tool_decision reject/hook` as one JSON line |
| 08 | JSON parse of every policy/template/fixture JSON (7 files) | PASS | all parse |
| 08 | diff `managed-settings.template.json` vs tested `policy/managed-settings.wsl.json` (flattened keys) | PASS | only in template: `wslInheritsWindowsSettings`, marketplace `repo` (github); only in tested: marketplace `path` (directory); value diffs: `allowedMcpServers` (+Windows launcher), OTLP endpoint `<collector>`, resource attrs `<org>`, marketplace source type. Linux/macOS template: same minus WSL line and launcher diff |
| 08 | `python -c "yaml.safe_load(otel/collector-config.yaml)"` | PASS | YAML parses; collector itself not run |
| 08 | `bash -n scripts/*.sh` (6 scripts) | PASS | all OK after scrub (LAB_USER / DISTRO / KIT_MARKETPLACE variables) |
| 08 | `gitleaks dir 08-team-policy` + privacy/banned-word grep | PASS | no leaks found; fixture `.env` = `DEMO_KEY=not-a-real-key`; mock key labelled not-a-real-key |
| 09 | `python pipeline.py --help` | PASS | usage lists proposal, approve, answers, build, qa, go-live, report, summary |
| 09 | `python pipeline.py build --job sufi-winter` with blank gates.md (scratch copy) | PASS | `BLOCKED: gate 1 SEND has no recorded approval in gates.md. 0 agents started.` exit 1; no ledger entry |
| 09 | `python pipeline.py build --job sufi-winter` with b1 `unknowns.one-open.json` | PASS | `BLOCKED: 1 unknown(s) still open: price-velvet-kurta. Ask the client first. 0 agents started, 0 model calls.` exit 1 (matches the recorded result) |
| 09 | `python pipeline.py build --job sufi-winter` with b1 `unknowns.all-open.json` | PASS | `BLOCKED: 13 unknown(s) still open: ...` before any agent |
| 09 | `python pipeline.py approve merge --job sufi-winter --by Test` (gate 1 empty) | PASS | `REFUSED: gate send has no recorded approval yet. Gates are approved in order.` exit 1, before any git call |
| 09 | `python pipeline.py go-live --job sufi-winter` with b3 `gates.stage3.md` / with gate 3 recorded but no RELEASE_KEY | PASS | `REFUSED: gate 3 GO-LIVE has no recorded approval` / `REFUSED: release key not on this machine`, exit 1 |
| 09 | `python build_report.py fixtures/sample-runs/sufi-winter --out <scratch>` | PASS | `ACCEPTED 5 · REJECTED 0 · NOT CHECKED 1`; identical to the recorded jobs/sufi-winter/report.md; NOT CHECKED listed under "Needs a human look", not counted as pass |
| 09 | `python build_report.py fixtures/test-setups/b4-planted-rejected-finding --out <scratch>` | PASS | `ACCEPTED 5 · REJECTED 1 · NOT CHECKED 1`; identical to recorded report.v2.md; REJECTED and NOT CHECKED both under "Needs a human look" |
| 09 | `python build_report.py <b4> --check handcrafted.summary.md` and `--check recorded/model-summary.v1.md` | PASS | both exit 1 `FAILED: "passed" where the counts disagree`; the generated report passes `--check` (exit 0) |
| 09 | `python break_tests.py b1-price-row` (model-free, scratch copy) | PASS | planted "Pashmina shawl: PKR 8800" → `VERDICT sufi-threads: FAIL · price with no data row` |
| 09 | `python verify.py runs/<copy of b4>` | PASS | runs offline; rejects all 7 findings "screenshot file does not exist" (screenshots not shipped): the evidence rule works; README states it |
| 09 | `python -m py_compile` on all .py · yaml.safe_load go-live.yml + review.yml · json.load all .json · csv parse | PASS | all compile/parse |
| 09 | gitleaks + privacy/banned-word grep over the module | PASS | no leaks; no user paths, names, emails, price figures (the proposal's price line replaced by an owner blank) |
| 09 | `python pipeline.py proposal / build / qa ...`, `break_tests.py b1-nogate / b3-* / b4-summary` | SKIPPED (needs Claude login) | stages that call Claude need your Claude login / API key, kiran-core installed and a git repo |
| 09 | `go-live.yml` on GitHub | SKIPPED (needs a GitHub repo with a protected environment) | written, not run in the recording either |
| 10 | `python evals/run_suite.py --help` | PASS | usage printed, exit 0 |
| 10 | `python evals/diff_report.py results/baseline.json results/after-change.json --md <scratch>/diff.md` | PASS | 7/9 -> 9/9, 0 below / 5 moved / 4 held; KEY (KEEP / INVESTIGATE / ROLL BACK) and empty `DECISION: ____ BY: ____ DATE: ____` printed; md written; no args -> usage, exit 2 |
| 10 | each case `check.py --workspace <copy of input/> --record <recorded run-N.json> --expected evals/expected/<id>.json` (01-05, 07-09; baseline + after-change records) | PASS | re-run verdict agreed with the recorded verdict 80/80 runs (incl. the 05 fail and 09 0/5 fails) |
| 10 | `evals/cases/00-hooks-alive/check.py` on the recorded canary record | PASS | "secret-firewall blocked 2/2 (Write, Bash); files written: none" |
| 10 | `evals/cases/06-noshow-cleanup/check.py` on synthetic before/after tables | PASS | identical tables -> PASS exit 0; one changed row -> FAIL exit 1 (no recorded tables exist; synthetic) |
| 10 | `python evals/tools/mock_api.py` on localhost with the canary plan + 4 scripted Messages requests | PASS | returned Write, then Bash, then "canary finished"; streaming SSE ok; no model, 127.0.0.1 only |
| 10 | `python evals/cases/judge-test/code_check.py evals/cases/judge-test/input` | PASS | "NOT READY: summary says all checks passed=True, verifier rejected=1", exit 1 (expected) |
| 10 | `python evals/cases/04-wrong-price-pr/setup.py <scratch ws>` + `scripts/check-site.py mehr-bakery` | PASS | 2 commits built (Fruit cake 1200 -> 1500); check-site FAIL prices, exit 1 (expected) |
| 10 | `python -m py_compile` all 32 .py; `bash -n` all 18 .sh; JSON parse all 48 .json | PASS | 0 failures |
| 10 | `gitleaks dir .` + scrub grep (paths, names, distro, versions, banned words) | PASS | no leaks found; no hits |
| 10 | canary `00-hooks-alive` through `run_suite.py` (real Claude Code against the mock API) | SKIPPED (needs WSL+admin) | runner requires Linux, the eval-machine managed policy in /etc and an isolated config; no model spend when run |
| 10 | full suite `run_suite.py --runs 5 ...`, judge-test, candidates, `claude plugin eval` | SKIPPED (needs Claude login) | real model calls; recorded results shipped in results/ |
| 11 | `python -m py_compile` on all 9 .py files + JSON parse of 9 .json files | PASS | all compile, all parse |
| 11 | `python monday.py --help` | PASS | argparse help printed (run-cap, wall-min, workers, min-free-gb, bare, plain, only) |
| 11 | `python tools/offline_check.py` | PASS | 3/3: verify.py Mehr Bakery FAIL on planted "Fruit cake: page PKR 1350, data PKR 1200", Sufi Threads PASS; e2_report good report passes, bad one fails on no-email + numbers; mock_api returns scripted tool_use, no model |
| 11 | `python monday.py --bare --plain` (scratch copy; CLAUDE_CONFIG_DIR = scratch .cfg; ANTHROPIC_BASE_URL = local mock) | PASS | "PREFLIGHT FAILED: kit or hooks not loaded. Nothing ran.", exit 3; one request to the local mock only, $0 |
| 11 | `gitleaks dir bonus-ceo-control-room` | PASS | no leaks found |
| 11 | `python monday.py` (full 9-job run) | SKIPPED (needs Claude login) | also needs Episode 5 + 9 parts in deps/ and kiran-core installed; recorded result in sample-run/ |
| 11 | `python rec_live.py` | SKIPPED (needs Windows + OBS + Claude login) | reference only |

## Kit-wide checks

| Check | Result |
| --- | --- |
| `gitleaks dir .` (default rules, whole kit, 594 files) | PASS: no leaks found. Module 05 has its own `.gitleaks.toml`; with that custom rule it reports the FAKE `noor_test_` fixture tokens on purpose (see `05-business-connector/SECRET-SCANNING.md`). |
| Privacy and wording scan (local Windows/WSL/home paths, user names, owner name, personal emails, banned client names, banned words, safety claims, dated prose, Claude Code version numbers) | PASS. Remaining matches are intended: client contact emails on the reserved `.example` / `.invalid` domains, mock keys spelled `sk-ant-mock-not-a-real-key` / `...FAKEFAKE...` used by the hook canaries, and dates inside fictional client data that the checks compare against. |
| Line endings | `.gitattributes` keeps scripts LF (hooks run in Git Bash) and `.cmd` files CRLF. |
