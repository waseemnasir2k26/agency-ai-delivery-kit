# Caps checklist: every unattended job has a fuse and a breaker

A cap set in a prompt ("please keep it cheap") is a wish. A cap set in config is a fuse: it cuts.
Behind every job cap sits the main breaker: the **spend limit on the Console workspace** that holds the API key.

Rules for every row:

- [ ] The job runs through a runner or scheduler, not a chat window left open.
- [ ] Its dollar cap is set **in config or on the command line** (`--max-budget-usd`, `max_budget_usd`), not in a prompt.
- [ ] A turn limit alone does not count as a cap: `--max-turns` counts main-session turns only, and workflow
      steps running underneath are not counted.
- [ ] There is a wall-clock timeout that kills the whole process tree.
- [ ] The cap has headroom: per the docs, spend can pass the cap a little. It is a fuse, not an exact meter.
- [ ] The API key lives in its own Console workspace with its own spend limit (the auto-created Claude Code
      workspace cannot hold API keys).
- [ ] A capped run is recorded as `capped`, not `done`, and the cost report counts it.
- [ ] On the machine that runs jobs unattended, session loops are off: `CLAUDE_CODE_DISABLE_CRON=1`.

## Kiran Studio example

Rows 1-3 are the jobs from earlier episodes. Their cap mechanism depends on how you built them: check your own
build and fill the cells. Only row 4 was measured in Episode 6.

| #   | Unattended job              | How it runs                        | Where the cap is set                                                       | Cap present?                                  | Workspace spend limit behind it |
| --- | --------------------------- | ---------------------------------- | -------------------------------------------------------------------------- | --------------------------------------------- | ------------------------------- |
| 1   | Client report on a schedule | your scheduler                     | **\_\_**                                                                   | yes / no                                      | **\_\_** (you set this)         |
| 2   | Review on pull requests     | GitHub Actions                     | **\_\_**                                                                   | yes / no                                      | **\_\_** (you set this)         |
| 3   | Site Watch nightly checks   | OS scheduler                       | `max_budget_usd` in its config                                             | yes / no                                      | **\_\_** (you set this)         |
| 4   | Monthly site refresh        | `run_job.py` from the OS scheduler | `--cap` (passed to `--max-budget-usd`), plus `--timeout` and `--total-cap` | yes: `run_job.py` refuses to start without it | **\_\_** (you set this)         |

Scheduler options for repeating work: cloud scheduled tasks (`/schedule`), Desktop scheduled tasks, GitHub Actions
`schedule:`, or the OS scheduler (Task Scheduler / cron) calling `run_job.py`.

---

## Blank copy

| #   | Unattended job | How it runs | Where the cap is set | Cap present? | Timeout | Workspace spend limit behind it | Owner |
| --- | -------------- | ----------- | -------------------- | ------------ | ------- | ------------------------------- | ----- |
| 1   |                |             |                      |              |         |                                 |       |
| 2   |                |             |                      |              |         |                                 |       |
| 3   |                |             |                      |              |         |                                 |       |
| 4   |                |             |                      |              |         |                                 |       |
| 5   |                |             |                      |              |         |                                 |       |

Any row with "Cap present? = no" is the first thing to fix.
