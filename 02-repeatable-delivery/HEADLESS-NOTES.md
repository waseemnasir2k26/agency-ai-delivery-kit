# HEADLESS-NOTES: running Claude Code with nobody watching

The 7 AM robot (`kiran-ops/run-report.cmd`, or `run-report.sh` for cron) runs `claude -p` with no
person at the keyboard. Read this before you schedule it.

## 1. `claude -p` trusts the folder it runs in

An interactive session asks "do you trust this folder?" the first time. `claude -p` does not ask. It
loads that project's `.claude/settings.json` hooks (which run shell commands on your machine) and the
MCP servers in its `.mcp.json`. So:

- Only run `claude -p` in folders you own and have read. Never point the robot at a freshly cloned
  repo from someone else.
- The robot passes `--strict-mcp-config` with no `--mcp-config`, so it starts no MCP servers from
  `.mcp.json`. Keep that flag unless the report really needs a server.
- `--setting-sources project` loads only the project's settings, not your personal ones. The run is
  the same on every machine, and your own global hooks do not leak into it.

## 2. Bare mode: faster, but it switches off what this run needs

`--bare` is a minimal mode. In the release used for the recording, `claude --help` says it skips
hooks from settings and plugins, plugin sync, auto-memory and `CLAUDE.md` auto-discovery, and that it
signs in only with an API key (`ANTHROPIC_API_KEY`), never with your subscription login. Good for a
fast, predictable one-off call; wrong for this robot, which needs the project hooks, the
`client-report` skill, and (on most small teams) a subscription login.

Claude Code docs say bare mode is planned to become the default for `claude -p`. If an update flips
it, expect the hooks to stop running and the login to fail or change. The run then returns an error
or no `structured_output`, and the validator writes a `FAILED` receipt instead of a report. That is
the right failure: nothing fake goes out. When you see it after an update, check the flags first
(`claude --help`, look for how to turn bare mode off), then the skill. Re-read `claude --help` after
every Claude Code update.

## 3. Nobody is there to answer a prompt

The project uses `"defaultMode": "default"`, so a tool that is not pre-approved asks first. In a
headless run there is no one to ask. Two options:

- Pre-approve exactly what the run needs (`--allowedTools ...`, or the skill's `allowed-tools`). Note:
  a skill's `allowed-tools` pre-approves those tools for that turn. It does not remove other tools.
- For unattended runs, consider `--permission-prompts none` so any prompt is denied at once instead
  of waited on. A denied step then shows up as a `FAILED` receipt, not as a run that hangs.

Never use `--dangerously-skip-permissions` for a scheduled run.

## 4. Caps and receipts

- `--max-budget-usd` stops the run when its estimated spend passes the cap (`ROBOT_BUDGET` in
  `.robot.env`). In the episode a cap far below one run's need produced
  `reason: claude failed (error_max_budget_usd)` and no report.
- `--json-schema schema.json` makes Claude return a fixed JSON shape (`structured_output`).
  `scripts/validate-report.py` then checks, in order: valid JSON, no error, run completed,
  `structured_output` present, schema valid, and the three numbers equal the data file.
- Any failure writes `reports/FAILED-<time>.txt` with the exit code, the reason and a filtered
  stderr tail, and the wrapper exits 1 (Task Scheduler "Last Result" 1). Success writes
  `reports/<date>.json` and exits 0.

| Receipt reason                          | Usual cause                                                      | First thing to check                |
| --------------------------------------- | ---------------------------------------------------------------- | ----------------------------------- |
| `no structured_output in claude result` | the skill's `!` command failed (data file missing), or bare mode | `claude said:` line in the receipt  |
| `claude failed (error_max_budget_usd)`  | budget cap reached                                               | `ROBOT_BUDGET`                      |
| `run did not complete: ...`             | turn limit, interruption                                         | the `terminal_reason` line          |
| `schema validation failed`              | the report shape changed                                         | `schema.json` vs the skill          |
| `numbers do not match the data file`    | the model changed a figure                                       | the data file, then the skill rules |
| `claude produced no valid JSON output`  | not logged in, `claude` not on PATH                              | run the wrapper by hand once        |

## 5. Cost figures are estimates, not a bill

`total_cost_usd` in Claude's JSON output (and the cost line the validator prints) is an estimate
calculated by the client. Your real charge is what your plan or the Claude Console billing page shows.
Use the estimate to set the budget cap, not for invoicing.

## 6. The scheduler itself

- Windows Task Scheduler, as created by the `schtasks` line in `run-report.cmd`, runs "Interactive
  only": you must be logged on. By default it will not start on battery, and it is not set to wake a
  sleeping laptop. The machine must be awake at seven.
- cron (macOS / Linux / WSL) runs with a tiny `PATH`; put the full path to `claude` in
  `run-report.sh`. The cron user must be logged in to Claude Code.
- Check the result the next morning: `schtasks /query /tn KiranDailyReport /v /fo list` shows
  "Last Run Time" and "Last Result" (0 = report written, 1 = receipt written).
- Turn it off when you stop using it: `schtasks /change /tn KiranDailyReport /disable`.
