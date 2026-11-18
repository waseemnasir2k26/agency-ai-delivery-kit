# Quality-versus-cost review sheet

One row per setup. The cost range sits beside the planted-mistake result, so nobody picks a cheaper setup by
looking at the cost column alone.

How to fill it:

1. Plant one known mistake in the job's input (here: the client request asks for a price the data file does not
   have). The judge must reject it.
2. Run each setup at least three times with `run_job.py` (with a cap).
3. Run `cost_report.py`. Copy the "Range per setup" row: cost range, wall time range, planted mistake caught.
4. Read the runs where the judge approved: did the mistake reach the output at all?
5. Never average without the range. Fewer than three runs = a single reading, not a number.

## Kiran Studio example (recorded result)

Job: monthly site refresh, Mehr Bakery (fictional). Planted mistake: Fruit cake requested at PKR 1500, data file
says PKR 1200. Cost figures are Claude Code's own estimates at API list price on a subscription login:
**LOCAL ESTIMATE, NOT A BILL**. Full table: `sample-report/cost_report.md`.

| Setup | What                                                                         | Runs | Cost range per run (est.) | Planted mistake result                                                                              | Decision                                |
| ----- | ---------------------------------------------------------------------------- | ---- | ------------------------- | --------------------------------------------------------------------------------------------------- | --------------------------------------- |
| A     | every step on Opus, long CLAUDE.md                                           | 1    | $0.4939                   | rejected in 1 of 1                                                                                  | too few runs to rank; most expensive    |
| C     | routed: Haiku reads/reports, Sonnet builds, judge on Opus, trimmed CLAUDE.md | 3    | $0.0651 - $0.1013         | rejected in 3 of 3                                                                                  | **chosen**                              |
| D     | all Haiku, judge on Haiku too (controlled test)                              | 3    | $0.0066 - $0.0108         | rejected 2 of 2 times the wrong price reached the page; run 3 kept the data price, nothing to catch | rejected: the judge is never downgraded |
| STUCK | checker always fails (controlled test, wrong on purpose)                     | 2    | $0.0071 - $0.0079         | run 2 stopped by the dollar cap: status CAPPED                                                      | proves the fuse, not a setup to use     |

Judge step alone on Opus in Setup C (only the critic runs on Opus there): $0.0218 - $0.0521 per run (est.).
That is the most a downgrade of the judge could save per job.

---

## Blank copy

Job: **********\_\_********** · Planted mistake: **********\_\_********** · Cost basis: API key / subscription estimate

| Setup | What | Runs | Cost range per run (est.) | Wall time range | Planted mistake result | Decision |
| ----- | ---- | ---- | ------------------------- | --------------- | ---------------------- | -------- |
|       |      |      |                           |                 |                        |          |
|       |      |      |                           |                 |                        |          |
|       |      |      |                           |                 |                        |          |
|       |      |      |                           |                 |                        |          |
