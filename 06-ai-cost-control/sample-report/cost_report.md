# Kiran Studio · job cost report

Job: **monthly site refresh** · fictional agency and clients, synthetic data.

> **LOCAL ESTIMATE AT API LIST PRICE - NOT A BILL.** These runs used a subscription login: Claude Code computes the dollar figure on this machine from token counts at list price. It is not what you were charged. For cost-per-job numbers you can show a client, re-run with an API key in its own workspace.

## Runs

| run | setup | cost (est.) | per model (est.) | wall time | turns | critic verdict | checker calls | status |
|---|---|---|---|---|---|---|---|---|
| A1-mehr-bakery | A | $0.4939 | opus-5-5 $0.4939 | 55.3s | 1 | REJECTED | 1 | done |
| C1-mehr-bakery | C | $0.1013 | haiku-5-5 $0.0048 · opus-5-5 $0.0521 · sonnet-5-5 $0.0444 | 34.6s | 1 | REJECTED | 1 | done |
| C2-mehr-bakery | C | $0.1009 | haiku-5-5 $0.0049 · opus-5-5 $0.0512 · sonnet-5-5 $0.0449 | 37.1s | 1 | REJECTED | 1 | done |
| C3-mehr-bakery | C | $0.0651 | haiku-5-5 $0.0040 · opus-5-5 $0.0218 · sonnet-5-5 $0.0392 | 38.9s | 1 | REJECTED | 2 | done |
| D1-mehr-bakery | D | $0.0106 | haiku-5-5 $0.0106 | 27.9s | 1 | REJECTED | 1 | done |
| D2-mehr-bakery | D | $0.0108 | haiku-5-5 $0.0108 | 34.8s | 1 | REJECTED | 1 | done |
| D3-mehr-bakery | D | $0.0066 | haiku-5-5 $0.0066 | 33.2s | 1 | APPROVED | 2 | done |
| STUCK1-mehr-bakery | STUCK | $0.0079 | haiku-5-5 $0.0079 | 31.6s | 1 | REJECTED | 1 | done |
| STUCK2-mehr-bakery | STUCK | $0.0071 | haiku-5-5 $0.0071 | 31.1s | 1 | REJECTED | 1 | CAPPED (Reached maximum budget ($0.007)) |

`turns` = main-loop turns only. The workflow's four stage agents run in the background and do not
add turns, so a turn cap does not limit them; the dollar cap does (their spend is in the cost column).

## Range per setup (no average without its range)

| setup | what | runs | cost range (est.) | wall time range | planted wrong price caught |
|---|---|---|---|---|---|
| A | TODAY: every step = Opus, long CLAUDE.md | 1 | $0.4939 | 55s | rejected in 1 of 1 |
| C | ROUTED: Haiku reads/reports, Sonnet builds, judge on Opus, trimmed CLAUDE.md | 3 | $0.0651 - $0.1013 | 35s - 39s | rejected in 3 of 3 |
| D | ALL HAIKU: judge on Haiku too, trimmed CLAUDE.md (CONTROLLED TEST) | 3 | $0.0066 - $0.0108 | 28s - 35s | rejected in 2 of 3 |
| STUCK | CONTROLLED TEST, WRONG ON PURPOSE: checker always FAILS (check-site.stuck.py), all Haiku | 2 | $0.0071 - $0.0079 | 31s - 32s | rejected in 2 of 2 |

Setups with fewer than 3 runs (A, STUCK): one run is a story, not a number. Treat as a single reading.

## Cost per client per month (setup C)

| client | job runs / month | AI run cost / month (est.) |
|---|---|---|
| Mehr Bakery | 1 | $0.0651 - $0.1013 |
| Sufi Threads | 1 | NOT MEASURED |
| Noor Dental Clinic | 1 | NOT MEASURED |

---
Source: Claude Code release used for the recording · `claude -p --output-format stream-json` result records (`total_cost_usd`, `modelUsage[*].costUSD`, `num_turns`) · wall time measured by run_job.py · 9 runs · cost basis: list · subscription login: LOCAL ESTIMATE, NOT A BILL
