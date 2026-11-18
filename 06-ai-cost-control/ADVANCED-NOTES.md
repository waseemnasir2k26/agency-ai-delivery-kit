# Advanced notes (shown on screen only in Episode 6)

For the person who runs the jobs, not for the owner's first read. Screen labels and field names change between
Claude Code releases: re-check each item against the Claude Code docs (costs, prompt caching, monitoring usage)
after every Claude Code update.

## 1. Reading the `Prompt cache (main)` line in `/usage`

- `/usage` (`/cost` is an alias) shows a session block and, on recent releases, a `Prompt cache (main)` line for the
  main session.
- Claude Code re-sends the full context with every request: system prompt, project context including `CLAUDE.md`,
  and the conversation so far. Most of that is a re-read, and re-reads are billed at the cached token rate, which
  is far below the fresh input rate.
- Read the line as: how much of the main session's input came from cache versus was written fresh. A high cached
  share is normal and healthy in a long session. A sudden drop means something invalidated the cache (see note 2).
- On a Pro or Max subscription, the session dollar figure is computed locally from token counts at list price.
  It is not your bill.

## 2. Why a mid-session model switch re-reads the conversation uncached

Each model has its own prompt cache. If you switch model in the middle of a session (`/model`), the new model has
nothing cached, so the next request sends the whole conversation as fresh input for that model, once. On a long
session that single request can cost more than many cached ones. Pick the model per step up front (agent
frontmatter, see `model-table.md`) instead of switching mid-session.

## 3. The plan usage breakdown: Attribution, Recommendations, Loops

On subscription plans, recent releases of `/usage` add a plan usage breakdown:

- **Attribution:** which parts of your work used the plan.
- **Recommendations:** suggestions shown for items with a share of at least 10%. Per the docs, the figure is the
  share, "not how much the change saves". Do not quote it as a saving.
- **Loops:** usage by session loops (`/loop`). A session loop fires on its interval even while the session is
  idle, sending your full context each time.

**Version gate:** these rows only exist on recent Claude Code releases, and their labels can change. If you do not
see them, update Claude Code and look again; do not build a process that depends on the exact row names.

## 4. Tagging runs per client with OpenTelemetry

Claude Code can export usage metrics, including `claude_code.cost.usage` with a `model` attribute. Add your own
resource attributes to split cost per client and job.

```bash
# bash / zsh
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_METRICS_EXPORTER=console          # prints metrics to the console; use otlp for a real collector
export OTEL_RESOURCE_ATTRIBUTES="client=mehr-bakery,job=site-refresh"
python run_job.py --client mehr-bakery --setup C --runs 1 --cap 0.50
```

```powershell
# PowerShell
$env:CLAUDE_CODE_ENABLE_TELEMETRY = "1"
$env:OTEL_METRICS_EXPORTER = "console"
$env:OTEL_RESOURCE_ATTRIBUTES = "client=mehr-bakery,job=site-refresh"
python run_job.py --client mehr-bakery --setup C --runs 1 --cap 0.50
```

Rules:

- **No spaces** in `OTEL_RESOURCE_ATTRIBUTES` values. Use `mehr-bakery`, not `Mehr Bakery`.
- A repository's settings file cannot turn telemetry on. Set the variables in the environment of the machine that
  runs the job (or in your organisation's managed settings).
- The telemetry cost figure is the same client-side estimate as `total_cost_usd`. The Console invoice is the bill.
- Not exercised for the episode's recorded runs: treat this as a starting point and test it on your own setup.

## 5. Other switches worth knowing

- `CLAUDE_CODE_DISABLE_CRON=1` on an unattended machine: `/loop` and the cron tools are unavailable, so nothing can
  be scheduled from a chat window. In the episode's test, `/loop` replied that the command is not installed in that
  session, and nothing was scheduled.
- `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0`: a `-p` run otherwise waits a limited time for background workflow
  steps, then stops them and drops the partial result. `run_job.py` sets `0`, so only the caps stop a run.
- `--bare`: the docs say it will become the default for `-p` in a future release. Bare mode skips `CLAUDE.md`,
  skills, plugins, subagents and `.mcp.json`. The pre-flight in `run_job.py` turns that change into a loud failure
  instead of a silently wrong measurement.
- In `-p` mode, `ANTHROPIC_API_KEY` is always used when present. `/status` shows which credential is active.
