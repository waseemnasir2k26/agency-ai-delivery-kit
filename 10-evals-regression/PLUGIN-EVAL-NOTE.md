# `claude plugin eval` starter case: what it covers and what it does not

**The case:** `kiran-core/evals/plain-sentence-report/` (one skill, `client-report`). Same request as suite case
`09-plain-sentence`: "Write this week's update for Mehr Bakery." Fictional client, synthetic data.

| File                            | What it is                                                                         |
| ------------------------------- | ---------------------------------------------------------------------------------- |
| `case.yaml`                     | Case name, description, scaffold script                                            |
| `prompt.md`                     | The request + `max_turns`, `timeout_seconds`, `allowed_tools`, `expected_outcome`  |
| `fixture.sh`                    | Scaffold: writes the three fictional client data files into `data/`                |
| `graders/skill-fired.md`        | `tool_used` grader: did the `client-report` skill fire                             |
| `graders/wins-three-bullets.md` | Regex: a Wins heading with exactly 3 bullets                                       |
| `graders/no-email.md`           | Regex: no email address in the reply                                               |
| `graders/client-ready.md`       | LLM grader: the three figures copied exactly, nothing invented, 150 words or fewer |

**Run it** (eval machine; spends real money, set the cap): `bash eval-machine/plugin-eval.sh` (no shell grant) or
`bash eval-machine/plugin-eval.sh shell`. The script calls
`claude plugin eval ./kiran-core --trust-plugin --scaffold --model claude-haiku-5-5 --judge-model claude-sonnet-5-5 --max-cost-usd <cap> --runs 3 ...`.
`--scaffold` runs `fixture.sh` as you: read it first.

## What it covers

- Did the skill fire? With a plugin path it runs two arms (with the plugin and without it) and reports the
  difference. The `tool_used: Skill` grader becomes a "plugin fired" indicator, not part of the score.
- Recorded result (no shell grant): score with plugin 0.11, without 0.11, difference 0.00; skill fired 3/3.

## What it does not cover

- Whether the client's report is right in the way the client cares about. That is the runner's job
  (`evals/run_suite.py` + each case's `check.py`): fixed pass marks, five runs, cost per run, a before/after report.
- Shell grants on a machine that cannot confine the shell. On the eval machine the managed sandbox block
  (`autoAllowBashIfSandboxed`) made it refuse the `Bash(cat data/*)` grant
  (`results/plugin-eval/v6-plugin-eval-shell-refused.txt`). Without the grant the skill's `!cat` data line cannot run
  in either arm, so the recorded difference of 0 says nothing about the plugin's value.
- It does not pin, compare against a baseline file, or print a keep / investigate / roll back key.

Recorded console line: `results/plugin-eval/plugin-eval.txt` (the full results.json and HTML report are not shipped).
