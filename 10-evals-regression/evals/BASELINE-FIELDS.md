# Baseline format: the field list

`evals/baseline.json` is a real five-run baseline from the recorded suite (fictional agency, synthetic data).
Every suite run (`run_suite.py --out <file>.json`) writes the same shape, so any two files can go into
`diff_report.py`. Dates and the Claude Code version were removed from the kit copy (`recorded run`,
`recorded release`); your own runs fill them in.

## `header` — what was under test

| Field                                           | Meaning                                                                                     |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------- |
| `label`                                         | Run name (defaults to the `--out` file name)                                                |
| `started_utc`                                   | Start time of the suite                                                                     |
| `model_pinned`                                  | The job model, full name (asserted from `modelUsage` on every run)                          |
| `case_models`                                   | One-stage overrides from `--case-model CASE=MODEL` (empty = none)                           |
| `claude_code_version`                           | Output of `claude --version`                                                                |
| `plugin`, `plugin_version`                      | Plugin under test, from its `plugin.json`                                                   |
| `plugin_dir`                                    | Folder the plugin was loaded from (redacted to `<project>`)                                 |
| `plugin_description_client_report`              | The `description:` line of the client-report skill (shows a label edit in the report)       |
| `fixture_version`                               | Hash of every file in `evals/cases/` and `evals/expected/`. Edit a fixture and this changes |
| `runs_override`, `max_suite_usd`, `timeout_min` | The run count and the two limits printed before the first run                               |
| `bare`                                          | `true` only for the controlled `--bare` test (pre-flight must stop it)                      |
| `eval_machine_policy`                           | `eval variant` when the eval-machine managed policy is installed                            |
| `preflight`                                     | Result of the `00-hooks-alive` canary (`ok` + its one line)                                 |

## `summary` — the whole suite

`cases` · `at_or_above_mark` · `must_pass_failed` (list) · `suite_cost_usd` (estimate at list price, not an invoice) ·
`suite_wall_s` · `errors` · `total_runs`

## `cases.<id>` — one row per case

| Field                             | Meaning                                                                                                                                                    |
| --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `title`, `origin`, `kind`         | What the case is, which episode it came from, how it runs (`claude`, `script`, `judge`)                                                                    |
| `runs`, `runs_planned`            | Runs done / runs asked for (fewer = a limit stopped the suite)                                                                                             |
| `passes`, `pass_rate`             | Passing runs, e.g. `4/5`                                                                                                                                   |
| `pass_mark`, `must_pass`          | The mark written in `case.json` before any baseline                                                                                                        |
| `at_or_above_mark`                | `true` when pass rate >= mark and every planned run finished                                                                                               |
| `mean_cost_usd`, `total_cost_usd` | Cost per run and per case (estimates)                                                                                                                      |
| `mean_wall_s`                     | Mean duration per run                                                                                                                                      |
| `errors`                          | Runs that ended in an error or a non-`success` subtype                                                                                                     |
| `run_detail[]`                    | Per run: `pass`, the check's one `check` line, `cost_usd`, `wall_s`, `subtype`, `errored`, `model_usage_keys`, `num_turns`, `extra_plugins`, `judge_ready` |
| `judge`                           | Judge cases only: role, model, how many times the judge said ready                                                                                         |

`stopped` (top level) is `null` unless the cost cap or the time limit ended the suite early.
