# API key setup for client work

Site Watch runs on the Claude Agent SDK. On your own laptop, for learning, it can use your Claude login.
For anything you run for a client, or sell, use an API key.

## Why an API key

The Agent SDK overview says, in a note under "Get started": unless previously approved, Anthropic does not allow
third-party developers to offer claude.ai login or rate limits for their products, including agents built on the
Claude Agent SDK. Use the API key authentication described in the Quickstart instead.
Source: https://code.claude.com/docs/en/agent-sdk/overview. Re-read it before you sign a client; terms change.

## Set the key (environment variable only)

Create the key in the Claude Console (one key per client or per job makes revoking and cost tracking easier).
Then put it in the environment of the machine or service that runs the job:

```powershell
# Windows PowerShell, this session only
$env:ANTHROPIC_API_KEY = "<paste the key>"
# Windows, persistent for your user (opens a new shell to take effect)
setx ANTHROPIC_API_KEY "<paste the key>"
```

```sh
# Linux / macOS, this shell only
export ANTHROPIC_API_KEY="<paste the key>"
# cron / systemd: put it in a file only the service user can read (see scheduler-lines.txt), never in the crontab
```

Rules:

- Never in code. `site_watch.py` has no key in it and reads none itself; the SDK picks up `ANTHROPIC_API_KEY`.
- Never in a committed file. `.env` is in `.gitignore`. A secret scanner before every commit is in Module 5.
- Never on screen. Do not print the environment, do not screen-share a terminal that shows it, and show only
  the variable NAME in docs and recordings.
- If a key leaks: revoke and issue a new one in the Console first, then clean up files and history
  (full order of work: Module 5, `SECRET-SCANNING.md`).

## Cost per client

Every run writes `total_cost_usd` into `runs/<run>/run.json`, and `verify.py` puts it on the first line of the
report. That number is the SDK's **estimate at list price**. It is not an invoice: your actual bill can differ
(discounts, caching, plan). Use it to compare runs and spot a runaway, and read the real spend in the Console.

Two caps limit spend per run: `--budget` (maps to `max_budget_usd`) and `--max-turns` (maps to `max_turns`).
Both are fuses, not exact limits. See `SDK-NOTES.md`.

How to price this: Episode 6, full cost of delivery.
