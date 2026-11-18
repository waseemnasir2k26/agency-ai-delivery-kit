# Promises

Every item promised on screen or in an episode description, mapped to its file in this kit.
Sources are the course's build folders. Paths in the last column are relative to the kit root.

**Coverage: 124 of 126 items delivered ✅ · 2 need the owner ⚠️ (listed at the end).**

| Episode | Pack | Promised item | Kit path | Status |
| --- | --- | --- | --- | --- |
| Ep 1 | Business Website Starter | `BRIEF-TEMPLATE.md` (five blanks + Mehr Bakery worked example) | 01-client-site-in-a-day/BRIEF-TEMPLATE.md | ✅ |
| Ep 1 | Business Website Starter | `starter/` (index.html, styles.css, site.js, inbox.html, BRIEF.md, CLAUDE.md, .claude/settings.json; all content SAMPLE) | 01-client-site-in-a-day/starter/ | ✅ |
| Ep 1 | Business Website Starter | `starter/.claude/settings.json` (pins Manual; header note) | 01-client-site-in-a-day/starter/.claude/settings.json + 01-client-site-in-a-day/starter/.claude/SETTINGS-NOTE.md (note also in README, PERMISSION-MODES.md) | ✅ |
| Ep 1 | Business Website Starter | `CLAUDE.md` (S9 rule sheet + 44px rule, 10 lines) | 01-client-site-in-a-day/CLAUDE.md (+ generic 01-client-site-in-a-day/CLAUDE-STARTER.md) | ✅ |
| Ep 1 | Business Website Starter | `QA-CHECKLIST.md` (5 lines from S10 + line 6, Chrome device toolbar how-to) | 01-client-site-in-a-day/QA-CHECKLIST.md | ✅ |
| Ep 1 | Business Website Starter | `CLIENT-CONTENT-CHECKLIST.md` | 01-client-site-in-a-day/CLIENT-CONTENT-CHECKLIST.md | ✅ |
| Ep 1 | Business Website Starter | `PROMPTS.md` (every TYPE card, both bug reports as sent, 3 spare templates, settings prompt) | 01-client-site-in-a-day/PROMPTS.md | ✅ |
| Ep 1 | Business Website Starter | `PERMISSION-MODES.md` | 01-client-site-in-a-day/PERMISSION-MODES.md | ✅ |
| Ep 1 | Business Website Starter | `MEMORY-NOTES.md` | 01-client-site-in-a-day/MEMORY-NOTES.md | ✅ |
| Ep 1 | Business Website Starter | `WINDOWS-NOTES.md` | 01-client-site-in-a-day/WINDOWS-NOTES.md | ✅ |
| Ep 2 | Repeatable Delivery Pack | `.claude/skills/client-report/SKILL.md` + `checks.md`, three cases, `run-checks.py` | 02-repeatable-delivery/kiran-ops/.claude/skills/client-report/ + kiran-ops/tests/ (case1..3, run-checks.py, run-cases.py, sample-outputs/) + kiran-ops/data/ | ✅ |
| Ep 2 | Repeatable Delivery Pack | `.claude/settings.json` (CHANGED: deny rules; both PreToolUse hooks with `"matcher": "Bash\|PowerShell"`; `"defaultMode": "default"`) | 02-repeatable-delivery/kiran-ops/.claude/settings.json.READY: ships switched off on purpose. Hooks run commands on your machine, so you turn them on yourself: rename it to settings.json | ✅ |
| Ep 2 | Repeatable Delivery Pack | `.claude/hooks/secret-firewall.sh` (CHANGED: PowerShell spellings Get-Content, gc, type, cat alias, Select-String, Copy-Item on .env_; header "reads command text only; a script that builds the name at runtime gets past it") | 02-repeatable-delivery/kiran-ops/.claude/hooks/secret-firewall.sh | ✅ |
| Ep 2 | Repeatable Delivery Pack | `.claude/hooks/commit-gate.sh` + `commit-shape.py` (CHANGED: matches `git commit` from both tools) | 02-repeatable-delivery/kiran-ops/.claude/hooks/commit-gate.sh, commit-shape.py | ✅ |
| Ep 2 | Repeatable Delivery Pack | `.claude/agents/reviewer.md` + review scripts | 02-repeatable-delivery/kiran-ops/.claude/agents/reviewer.md, kiran-ops/scripts/run-review.sh, record-review.sh | ✅ |
| Ep 2 | Repeatable Delivery Pack | `git-hooks/pre-commit` | 02-repeatable-delivery/kiran-ops/git-hooks/pre-commit | ✅ |
| Ep 2 | Repeatable Delivery Pack | `run-report.cmd` + `schema.json` + `validate-report.py` (CHANGED: header note on bare mode and `--permission-prompts none`) | 02-repeatable-delivery/kiran-ops/run-report.cmd, run-report.sh (cron twin), schema.json, scripts/validate-report.py, tests/validator-selftest.py, tests/robot-samples/ | ✅ |
| Ep 2 | Repeatable Delivery Pack | `WINDOWS-HOOKS.md` (NEW) | 02-repeatable-delivery/WINDOWS-HOOKS.md | ✅ |
| Ep 2 | Repeatable Delivery Pack | `RETEST-LOG.md` (NEW: PowerShell retest result) | 02-repeatable-delivery/RETEST-LOG.md | ✅ |
| Ep 2 | Repeatable Delivery Pack | `bypass-tests/` (three extra gate cheats + hardened gate) | 02-repeatable-delivery/bypass-tests/README.md + run-bypass-tests.sh | ✅ |
| Ep 2 | Repeatable Delivery Pack | `HEADLESS-NOTES.md` (NEW) | 02-repeatable-delivery/HEADLESS-NOTES.md | ✅ |
| Ep 2 | Repeatable Delivery Pack | `SYSTEM-MAP.pdf` | 02-repeatable-delivery/SYSTEM-MAP.md (✅ as SYSTEM-MAP.md; PDF not included) | ✅ |
| Ep 2 | Repeatable Delivery Pack | `SKILL-HEALTH.md` (NEW, optional: `/skill-doctor` monthly) | 02-repeatable-delivery/SKILL-HEALTH.md | ✅ |
| Ep 3 | Parallel Work Pack | `kiran-sites/` (the three-client fixture repo) | 03-parallel-work/kiran-sites/ | ✅ |
| Ep 3 | Parallel Work Pack | `.worktreeinclude` + `WORKTREE-CHEATSHEET.md` | 03-parallel-work/kiran-sites/.worktreeinclude + 03-parallel-work/WORKTREE-CHEATSHEET.md | ✅ |
| Ep 3 | Parallel Work Pack | `OWNERSHIP-SHEET.md` (one row per shared file, its owner, who may edit it in parallel work) | 03-parallel-work/OWNERSHIP-SHEET.md | ✅ |
| Ep 3 | Parallel Work Pack | `MERGE-CHECKLIST.md` (required check green · verdict approved, not just "job ran" · a person read the diff · who pressed merge) | 03-parallel-work/MERGE-CHECKLIST.md | ✅ |
| Ep 3 | Parallel Work Pack | `.claude/workflows/site-refresh.js` (saved four-phase workflow + availability/size note) | 03-parallel-work/kiran-sites/.claude/workflows/site-refresh.js | ✅ |
| Ep 3 | Parallel Work Pack | `.claude/agents/critic.md` (standalone subagent: name, description, tools, model) | 03-parallel-work/kiran-sites/.claude/agents/critic.md | ✅ |
| Ep 3 | Parallel Work Pack | `.claude/skills/pr-review/SKILL.md` (name locked `pr-review`) | 03-parallel-work/kiran-sites/.claude/skills/pr-review/SKILL.md | ✅ |
| Ep 3 | Parallel Work Pack | `.github/workflows/site-review.yml` (v1 and v2; auth header note + `plugin_marketplaces`/`plugins` note) | 03-parallel-work/kiran-sites/.github/workflows/site-review.yml (v2) + kiran-sites/.github/site-review.v1.yml (outside workflows/ so it never runs) | ✅ |
| Ep 3 | Parallel Work Pack | `statusline/` (the status line script, cut from the episode) | 03-parallel-work/statusline/ (statusline.py, settings-snippet.json, sample-\*.json, README.md) | ✅ |
| Ep 3 | Parallel Work Pack | `SYSTEM-MAP.pdf` | 03-parallel-work/SYSTEM-MAP.md (✅ as SYSTEM-MAP.md; PDF not included) | ✅ |
| Ep 4 | Website QA Pack | `site_watch.py`: the agent (`query()` + `ClaudeAgentOptions`, `tools=[]`, four in-process tools via `@tool` + `create_sdk_mcp_server`, `allowed_tools`, `can_use_tool`, `PreToolUse` audit hook, `max_turns`, `max_budget_usd`, `setting_sources=[]`); header with `pip install claude-agent-sdk` and "re-test after SDK updates" | 04-website-qa-agent/site_watch.py (+ requirements.txt) | ✅ |
| Ep 4 | Website QA Pack | `verify.py` + `finding.schema.json`: the verifier (a plain script decides pass / fail / NOT CHECKED) and the finding schema | 04-website-qa-agent/verify.py, 04-website-qa-agent/finding.schema.json (+ samples/lie-test, samples/capped-run) | ✅ |
| Ep 4 | Website QA Pack | `data/<client>.json`: the three client truth files | 04-website-qa-agent/kiran-sites/data/ | ✅ |
| Ep 4 | Website QA Pack | `make_www.py` + `serve.py`: the four attack pages, localhost only | 04-website-qa-agent/make_www.py, 04-website-qa-agent/serve.py | ✅ |
| Ep 4 | Website QA Pack | `nightly.cmd` + scheduler line (Windows Task Scheduler / cron line for a server) | 04-website-qa-agent/nightly.cmd, 04-website-qa-agent/nightly.sh, 04-website-qa-agent/scheduler-lines.txt | ✅ |
| Ep 4 | Website QA Pack | `REPORT-TEMPLATE.md`: morning report with the approval line: who approves, what they approve, where it is recorded | 04-website-qa-agent/REPORT-TEMPLATE.md | ✅ |
| Ep 4 | Website QA Pack | `API-KEY-SETUP.md`: API-key sign-in for client work (Agent SDK docs), key in an environment variable, never in code or on screen; cost per client comes from `total_cost_usd` (an estimate at list price) | 04-website-qa-agent/API-KEY-SETUP.md | ✅ |
| Ep 4 | Website QA Pack | `SDK-NOTES.md`: query vs `ClaudeSDKClient`; `can_use_tool` never called for tools in `allowed_tools`; redirects; both caps are fuses; catch the result error; the result message lists denied calls; the comma gotcha | 04-website-qa-agent/SDK-NOTES.md | ✅ |
| Ep 4 | Website QA Pack | `kiran-sites/`: the three-site fixture | 04-website-qa-agent/kiran-sites/ | ✅ |
| Ep 4 | Website QA Pack | Pointer replacing the removed retainer one-pager / price-on-hours worksheet: "How to price this: Episode 6, full cost of delivery." | 04-website-qa-agent/README.md (also in REPORT-TEMPLATE.md, API-KEY-SETUP.md) | ✅ |
| Ep 5 | Business Connector Pack | `noor-booking-app/`: SQLite + small local API + browser dashboard, two key roles (front-desk, connector), `seed.py`, `reset.py`. Synthetic data only | 05-business-connector/noor-booking-app/ | ✅ |
| Ep 5 | Business Connector Pack | `noor-bookings/server.py`: the four tools (`list_tomorrow_bookings`, `find_available_slots`, `get_booking_summary`, `draft_reschedule`), field whitelist, stderr logging, a test per tool | 05-business-connector/noor-bookings/server.py, 05-business-connector/smoke_test.py | ✅ |
| Ep 5 | Business Connector Pack | `.mcp.json` with `${NOOR_API_TOKEN}` (no secret in it) and `.claude/settings.json` with the four named allow rules and the deny rules | 05-business-connector/noor-bookings/.mcp.json, 05-business-connector/noor-bookings/.claude/settings.json, 05-business-connector/variants/ | ✅ |
| Ep 5 | Business Connector Pack | `noor-bookings-test/`: the deliberately wrong copy (`cancel_appointment`, wildcard allow, every-column output) with a README headed "WRONG ON PURPOSE. Never point this at a real system." | 05-business-connector/noor-bookings-test/ | ✅ |
| Ep 5 | Business Connector Pack | `seed_note.py`: the planted patient note fixture | 05-business-connector/noor-booking-app/seed_note.py | ✅ |
| Ep 5 | Business Connector Pack | Site Watch patch: the `mcp_servers` entry, the single `allowed_tools` name, and the `verify.py` slot re-check | 05-business-connector/SITE-WATCH-PATCH.md, 05-business-connector/site_watch_noor.py, 05-business-connector/verify_noor.py | ✅ |
| Ep 5 | Business Connector Pack | Secret scanning: pre-commit config, CI workflow, the custom rule for the test token shape, and the leaked-key order of work (revoke and rotate, remove, history, scanner) | 05-business-connector/.pre-commit-config.yaml, 05-business-connector/ci-secrets.yml, 05-business-connector/.gitleaks.toml, 05-business-connector/SECRET-SCANNING.md | ✅ |
| Ep 5 | Business Connector Pack | `handover-template.md` + the filled Noor example: tool, reads, returns, who applies the change, tests run, approver | 05-business-connector/handover-template.md, 05-business-connector/handover-noor.md | ✅ |
| Ep 5 | Business Connector Pack | `tool-surface-checklist.md`: per tool, which box stops it (tool exists / permission rule / key role), most it can return, personal fields returned, worst case if a stranger controlled the prompt | 05-business-connector/tool-surface-checklist.md | ✅ |
| Ep 5 | Business Connector Pack | `pyproject.toml` / `requirements.txt` pinning `mcp>=2.3,<3`; the `claude mcp add` line with the name-before-`-e` rule and the Windows venv-interpreter path | 05-business-connector/requirements.txt, 05-business-connector/README.md (step 3) | ✅ |
| Ep 5 | Business Connector Pack | "Scripted runs" note: `claude -p` and SDK runs load project `.mcp.json` servers without the approval prompt; use `--strict-mcp-config`, `--setting-sources user` or `disabledMcpjsonServers` to keep a server out of a script | 05-business-connector/SCRIPTED-RUNS.md | ✅ |
| Ep 5 | Business Connector Pack | Advanced insert: the over-large result demo (`list_all_patients` on the test copy, 10,000 / 25,000 token figures, saved-file behaviour, `count` + paged `search` as the fix), tool search and the first line of a tool description, the stdout rule for stdio servers, the unset-variable warning in `claude mcp list`, the HTTP transport for teams | 05-business-connector/ADVANCED.md | ✅ |
| Ep 5 | Business Connector Pack | Prerequisites stated on the pack page: Python 3.11+ in a project venv (Windows: point the server at the venv's `python.exe`), Node (Inspector), Claude Code, Git; no paid API key for the app or Inspector tests; Site Watch billed as in Episode 4 | 05-business-connector/README.md (step 1), 05-business-connector/SITE-WATCH-PATCH.md | ✅ |
| Ep 6 | AI Cost Kit | `run_job.py`: capped job runner (`--client --job --setup --runs --cap`, `--timeout`, `--total-cap`, refuses without a cap, pre-flight, status done/failed/capped/timeout/preflight_failed) | 06-ai-cost-control/run_job.py | ✅ |
| Ep 6 | AI Cost Kit | `cost_report.py`: per-run table, min-max range per setup, cost per client per month, NOT MEASURED, source footer | 06-ai-cost-control/cost_report.py (+ sample-runs/, sample-report/) | ✅ |
| Ep 6 | AI Cost Kit | `model-table.md`: step → model → effort → why, "never downgrade the judge" fixed row, plus a blank copy | 06-ai-cost-control/model-table.md | ✅ |
| Ep 6 | AI Cost Kit | `pricing-worksheet.xlsx`: green measured, blue owner-entered, yellow assumption cells, "AI run cost floor" line, hours-saved value line, no prices | 06-ai-cost-control/pricing-worksheet.xlsx (+ pricing-worksheet.csv twin) | ✅ |
| Ep 6 | AI Cost Kit | `caps-checklist.md`: every unattended job, how it runs, where its cap is set, workspace spend limit behind it | 06-ai-cost-control/caps-checklist.md | ✅ |
| Ep 6 | AI Cost Kit | `CLAUDE.md` diet checklist: what stays, what becomes a skill, one named owner, under 200 lines | 06-ai-cost-control/CLAUDE-DIET-CHECKLIST.md | ✅ |
| Ep 6 | AI Cost Kit | Quality-versus-cost review sheet: one row per setup, cost range beside the planted-mistake result | 06-ai-cost-control/QUALITY-VS-COST-REVIEW.md | ✅ |
| Ep 6 | AI Cost Kit | Advanced notes: `Prompt cache (main)` in `/usage`, mid-session model switch, plan usage breakdown + version gates, OpenTelemetry per-client tags | 06-ai-cost-control/ADVANCED-NOTES.md | ✅ |
| Ep 6 | AI Cost Kit | Fixture: the long `CLAUDE.fat.md` | 06-ai-cost-control/kiran-sites/fixtures/CLAUDE.fat.md | ✅ |
| Ep 6 | AI Cost Kit | Fixture: `check-site.stuck.py` | 06-ai-cost-control/kiran-sites/fixtures/check-site.stuck.py | ✅ |
| Ep 6 | AI Cost Kit | Fixture: the Mehr Bakery request with the planted price | 06-ai-cost-control/kiran-sites/fixtures/request-mehr-bakery.md | ✅ |
| Ep 6 | AI Cost Kit | Fixture: `data/mehr-bakery.json` | 06-ai-cost-control/kiran-sites/data/mehr-bakery.json | ✅ |
| Ep 6 | AI Cost Kit | Fixture: the four setup configs | 06-ai-cost-control/setups/ (A, C, D, STUCK + A-trimmed) | ✅ |
| Ep 7 | Agency Kit Pack | Starter plugin (the `kiran-core` layout): `plugin.json` · `skills/client-report/` · `skills/pr-review/` · `agents/critic.md` · `hooks/hooks.json` → `secret-firewall.sh` (+ `secret_firewall.py`), `commit-gate.sh` (+ `commit-shape.py`) via `${CLAUDE_PLUGIN_ROOT}`; `run-review.sh` / `record-review.sh` call `--agent kiran-core:critic` | 07-agency-kit-plugins/kiran-marketplace/plugins/kiran-core/ | ✅ |
| Ep 7 | Agency Kit Pack | Example client plugin (`kiran-noor`): `.mcp.json` for `noor-bookings`, four read and draft tools, `NOOR_API_TOKEN` by name, `${NOOR_PYTHON:-python}` + `${CLAUDE_PLUGIN_ROOT}/server.py`, no key, no permission rules | 07-agency-kit-plugins/kiran-marketplace/plugins/kiran-noor/ | ✅ |
| Ep 7 | Agency Kit Pack | `marketplace.json` for `kiran-marketplace` (two entries, relative sources, one name everywhere) | 07-agency-kit-plugins/kiran-marketplace/.claude-plugin/marketplace.json | ✅ |
| Ep 7 | Agency Kit Pack | `ci/check_kit.py`: three rules (one name · files changed ⇒ version changed · newest CHANGELOG entry = version); docstring fixed (tag does not check names) | 07-agency-kit-plugins/kiran-marketplace/ci/check_kit.py | ✅ |
| Ep 7 | Agency Kit Pack | CI workflow `validate-kit.yml`: validate --strict + tag --dry-run --force + check_kit --base origin/<base>; private-marketplace read token note | 07-agency-kit-plugins/kiran-marketplace/.github/workflows/validate-kit.yml | ✅ |
| Ep 7 | Agency Kit Pack | Hook matchers (`Write\|Edit\|Bash\|PowerShell`, `Bash\|PowerShell`), shell form via `${CLAUDE_PLUGIN_ROOT}`, `.gitattributes` keeps hook scripts LF | 07-agency-kit-plugins/kiran-marketplace/plugins/kiran-core/hooks/hooks.json + kiran-marketplace/.gitattributes + README.md "Why these choices" + HOOK-REVIEW-CHECKLIST.md | ✅ |
| Ep 7 | Agency Kit Pack | Team settings snippet: committed `.claude/settings.json` block (`extraKnownMarketplaces` + `enabledPlugins`, CLI key order, `enabledPlugins` first), the two commands, pinned-tag form (`"ref": "kiran-core--v<version>"`) | 07-agency-kit-plugins/TEAM-SETTINGS-SNIPPET.md + team-settings.snippet.json + team-settings.pinned.snippet.json | ✅ |
| Ep 7 | Agency Kit Pack | `ONBOARDING.md`: shorter path first (4 commands · 1 prompt; long path 6 · 1), install-order warning, two-command update line, pin-move line, `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1`, trust prompt paragraph | 07-agency-kit-plugins/kiran-marketplace/ONBOARDING.md | ✅ |
| Ep 7 | Agency Kit Pack | `CHANGELOG.md` template + release rule (no new version, no release) | 07-agency-kit-plugins/CHANGELOG-TEMPLATE.md + kiran-marketplace/CHANGELOG.md | ✅ |
| Ep 7 | Agency Kit Pack | Hook review checklist: what to read in a plugin's `hooks.json` and scripts before you install it | 07-agency-kit-plugins/HOOK-REVIEW-CHECKLIST.md | ✅ |
| Ep 7 | Agency Kit Pack | Advanced checks, one page (all 12: source paths · trust · context trimming · namespaced commands · double-firing hooks · private repo access · auto-update · plugin evals · MCP approvals · cloud sessions · headless runs · session-only load) | 07-agency-kit-plugins/ADVANCED-CHECKS.md | ✅ |
| Ep 8 | Team Policy Pack | `TEAM-POLICY.md`: the one-page policy, both versions (before and after the fix), with the five questions and the owner line | 08-team-policy/TEAM-POLICY.md | ✅ |
| Ep 8 | Team Policy Pack | `policy-matrix.md`: role × action × data table (owner, freelancer; read, change, ask, never; test line per cell) | 08-team-policy/policy-matrix.md | ✅ |
| Ep 8 | Team Policy Pack | `managed-settings.template.json`: the full Windows file with placeholders `<org>` and `<collector>`, plus a Linux/macOS variant without the WSL line (EXAMPLE ONLY) | 08-team-policy/managed-settings.template.json + managed-settings.template.linux-macos.json | ✅ |
| Ep 8 | Team Policy Pack | `managed-settings.annotated.md`: one note per key (what it stops, what it does NOT stop, which test, docs link) | 08-team-policy/managed-settings.annotated.md | ✅ |
| Ep 8 | Team Policy Pack | `ENVIRONMENT-CHECKLIST.md`: three system paths, WSL folder + `wslInheritsWindowsSettings`, `/status` + `claude doctor`, WSL2 check, `bubblewrap` + `socat`, server-managed settings, native-Windows note, device-ownership upgrade path | 08-team-policy/ENVIRONMENT-CHECKLIST.md | ✅ |
| Ep 8 | Team Policy Pack | `HEADLESS-NOTE.md`: `--allowedTools` ignored, `--plugin-dir` / `--agents` / `--mcp-config` rejected; how the Episode 6, 9, 10 runners are set up | 08-team-policy/HEADLESS-NOTE.md | ✅ |
| Ep 8 | Team Policy Pack | `policy_test.py` + fixture repo (planted README, fake `.env`, planted `.claude/settings.json`, `leak.py`, throwaway plugin folder): one PASS/FAIL line per attack; BLOCKED and ERRORED differ | 08-team-policy/policy_test.py + fixture/ + lab/ + policy/ + scripts/ + results/ (recorded WSL2 samples) | ✅ |
| Ep 8 | Team Policy Pack | `otel-console-setup.md` + local collector config: recorded by default, left out, one-page detail logging decision form | 08-team-policy/otel-console-setup.md + otel/collector-config.yaml + lab/otel_sink.py | ✅ |
| Ep 8 | Team Policy Pack | `POLICY-OWNER.md`: new allow rule request, auto mode decision record, rerun `policy_test.py` after every update and policy edit | 08-team-policy/POLICY-OWNER.md | ✅ |
| Ep 8 | Team Policy Pack | Optional lines, off by default and marked untested: `allowManagedHooksOnly`, `availableModels` + `enforceAvailableModels`, `syncClaudeAiPlugins: false`, `permissions.denyInsteadOfPrompting` | 08-team-policy/OPTIONAL-LINES.md | ✅ |
| Ep 8 | Team Policy Pack | Native Windows run result ("goes in the pack with its own result file") | ⚠️ owner: not run yet; 08-team-policy/results/WINDOWS-RUN-PENDING.md says so and gives the exact steps + result file name | ⚠️ |
| Ep 9 | Client Delivery Pack | `pipeline.py` (stages proposal · answers · build · qa · go-live · report · summary · approve <gate>; behaviour pre-flight: fake-key canary + `kiran-core:*` commands; each stage checks `gates.md` and `unknowns.json`) | 09-client-delivery-pipeline/pipeline.py (+ tools/) | ✅ |
| Ep 9 | Client Delivery Pack | `gates.md` template (four rows: send, merge, go-live, approve report; columns: what is approved, name and role, version, recorded) | 09-client-delivery-pipeline/jobs/\_new-job-template/gates.md (filled example: jobs/sufi-winter/gates.md) | ✅ |
| Ep 9 | Client Delivery Pack | One-page gate sheet: what the approver reads at each gate and what they may not skip | 09-client-delivery-pipeline/GATE-SHEET.md | ✅ |
| Ep 9 | Client Delivery Pack | Unknowns checklist (prices, hours, offer terms, enquiry destination, photos, who approves, legal lines) | 09-client-delivery-pipeline/UNKNOWNS-CHECKLIST.md | ✅ |
| Ep 9 | Client Delivery Pack | `unknowns.json` example | 09-client-delivery-pipeline/jobs/sufi-winter/unknowns.json + jobs/\_new-job-template/unknowns.json | ✅ |
| Ep 9 | Client Delivery Pack | The blocking pre-flight | 09-client-delivery-pipeline/pipeline.py (recorded result: fixtures/test-setups/b1-skipped-unknowns/recorded/fixed-blocked.txt) | ✅ |
| Ep 9 | Client Delivery Pack | `build_report.py` (reads verify.json only; counts headline; NOT CHECKED is never PASS; evidence link per row; false-"passed" check) | 09-client-delivery-pipeline/build_report.py | ✅ |
| Ep 9 | Client Delivery Pack | Evidence report template with the approval row | 09-client-delivery-pipeline/REPORT-TEMPLATE.md | ✅ |
| Ep 9 | Client Delivery Pack | `critic` addition: "Claims a proposal may never make" list (ships in `kiran-core`) | 09-client-delivery-pipeline/critic-claims-list.md (excerpt; full agent in 07-agency-kit-plugins/kiran-marketplace/plugins/kiran-core/agents/critic.md) | ✅ |
| Ep 9 | Client Delivery Pack | `go-live.yml` (protected environment) | 09-client-delivery-pipeline/.github/workflows/go-live.yml (+ review.yml) | ✅ |
| Ep 9 | Client Delivery Pack | The deny rule (Bash + PowerShell twins), labelled "seatbelt, not the lock", with the four-spelling probe from Test 2 | 09-client-delivery-pipeline/DENY-RULE.md + deny-rule.snippet.json + .claude/settings.json | ✅ |
| Ep 9 | Client Delivery Pack | Service boundary sheet (six rows, example cells empty) | 09-client-delivery-pipeline/SERVICE-BOUNDARY.md | ✅ |
| Ep 9 | Client Delivery Pack | Pricing worksheet (full cost of delivery: one MEASURED row, one MEASURE-ON-A-REAL-JOB row (gate time), six OWNER-ENTERED rows, margin; no prices) | 09-client-delivery-pipeline/pricing-worksheet.md + pricing-worksheet.csv | ✅ |
| Ep 9 | Client Delivery Pack | Project-vs-retainer one-pager | 09-client-delivery-pipeline/PROJECT-VS-RETAINER.md | ✅ |
| Ep 9 | Client Delivery Pack | Fixture: `jobs/sufi-winter/` (brief, answered data file) | 09-client-delivery-pipeline/jobs/sufi-winter/ + data/sufi-threads.json | ✅ |
| Ep 9 | Client Delivery Pack | The three test set-ups (`b1` skipped unknowns · `b3` "ship" instruction · `b4` planted rejected finding) | 09-client-delivery-pipeline/fixtures/test-setups/ (b1-skipped-unknowns, b3-ship-instruction, b4-planted-rejected-finding) + break_tests.py | ✅ |
| Ep 10 | Regression Pack | `evals/run_suite.py`: plain Python runner (fresh temp workspace, `claude -p` or the episode's script, N runs, one code check per case, suite cost cap + timeout printed first, pass rate / cost / duration, model full name from `modelUsage`, Claude Code / plugin / fixture versions, free hook canary `00-hooks-alive` first, load assertion every run, `--bare` → exit 3, `--case-model CASE=MODEL`, eval machine) | 10-evals-regression/evals/run_suite.py (+ evals/tools/mock_api.py) | ✅ |
| Ep 10 | Regression Pack | `evals/cases/` template: nine case folders (`case.json`, `input/`, `check.py`) with the pass marks used on screen; expected results kept runner-side in `evals/expected/` | 10-evals-regression/evals/cases/ (+ CASE-TEMPLATE.md), 10-evals-regression/evals/expected/ | ✅ |
| Ep 10 | Regression Pack | Small card: expected answers stay in the runner's folder, never copied into the agent's workspace (not tested on camera) | 10-evals-regression/evals/cases/CASE-TEMPLATE.md, README.md | ✅ |
| Ep 10 | Regression Pack | `evals/baseline.json`: a sample baseline (fictional data) and the field list | 10-evals-regression/evals/baseline.json, 10-evals-regression/evals/BASELINE-FIELDS.md | ✅ |
| Ep 10 | Regression Pack | `evals/diff_report.py`: before/after report with the empty decision line, and the keep / investigate / roll back key | 10-evals-regression/evals/diff_report.py | ✅ |
| Ep 10 | Regression Pack | Judge test kit: the handcrafted report and verifier file (labelled handcrafted), the flag-only judge config | 10-evals-regression/evals/cases/judge-test/ | ✅ |
| Ep 10 | Regression Pack | A `claude plugin eval` starter case for one skill, with a note on what that command covers and what it does not | 10-evals-regression/kiran-core/evals/plain-sentence-report/, 10-evals-regression/PLUGIN-EVAL-NOTE.md | ✅ |
| Ep 10 | Regression Pack | Settings snippet: pinned `model`, alias env block, named-tool allow list for the booking case | 10-evals-regression/settings-snippet.json (+ .claude/settings.json) | ✅ |
| Ep 10 | Regression Pack | Upgrade-day runbook card (`UPGRADE-DAY-RUNBOOK.md`; the one-page PDF is not built yet) | 10-evals-regression/UPGRADE-DAY-RUNBOOK.md (markdown card; no PDF, as the pack states) | ✅ |
| Ep 10 | Regression Pack | The three tested candidates (`candidates/`: shorter skill label, tidier argument hint, report stage on another tier) with their five-run results | 10-evals-regression/candidates/ (+ README.md, C3 = command line), 10-evals-regression/results/ | ✅ |
| Ep 10 | Regression Pack | Prerequisites, stated in the pack README (Python 3.11+, Claude Code, earlier episode assets, eval machine with bubblewrap + socat, ideally an API key; running the suite spends real money: set the cap first) | 10-evals-regression/README.md (step 1) | ✅ |
| Bonus | CEO Monday Pack | `monday.py` | bonus-ceo-control-room/monday.py | ✅ |
| Bonus | CEO Monday Pack | `clients.json` | bonus-ceo-control-room/clients.json | ✅ |
| Bonus | CEO Monday Pack | `tools/cc_env.py` (isolated config) | bonus-ceo-control-room/tools/cc_env.py | ✅ |
| Bonus | CEO Monday Pack | `tools/mock_api.py` (forced-test stand-in, $0) | bonus-ceo-control-room/tools/mock_api.py | ✅ |
| Bonus | CEO Monday Pack | `sitewatch/` (Site Watch + `verify.py` copies) | bonus-ceo-control-room/sitewatch/ | ✅ |
| Bonus | CEO Monday Pack | `kshell.py` + `rec_live.py` (how the take was recorded) | bonus-ceo-control-room/kshell.py, bonus-ceo-control-room/rec_live.py (+ obs_rec.py, tools/term/term.html) | ✅ |
| Bonus | CEO Monday Pack | the run's `digest.md` / `digest.html` / `facts.json` | bonus-ceo-control-room/sample-run/ | ✅ |
| Bonus | CEO Monday Pack | Free tool: Lead Leak Audit (link) | linked from root README by the lead; not part of this module | ✅ |

## Opt-in step

- **Episode 2, `02-repeatable-delivery/kiran-ops/.claude/settings.json.READY`**: the hooks file ships switched off. Read it, then rename it to `settings.json` to activate the deny rules and both hooks.
- **Episode 8, native Windows policy run**: not run yet, as the episode says. `08-team-policy/results/WINDOWS-RUN-PENDING.md` has the exact steps and the result file name.
