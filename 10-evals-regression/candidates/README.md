# The three tested candidates

One change each, everything else pinned, five runs each. Target: case `09-plain-sentence` (0/5 on the baseline).
Results are recorded, not re-run for the kit (they need a model). Costs are estimates at list price, not an invoice.

| Candidate                       | The one change                                                                                                                 | Where                          | Case 09 before -> after                                       | Recorded files                                                                                                               |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ | ------------------------------ | ------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| C1 shorter skill label          | `description:` of `client-report` shortened to "Weekly client report." (plugin 1.0.1)                                          | `C1-description/kiran-core/`   | 0/5 -> 0/5, nothing moved (01 held 5/5)                       | `../results/candidates/cand-C1.json`, `C1-description.console.txt`, `.skill.diff`, `.plugin-version.diff`, `.validate.txt`   |
| C2 tidier argument hint         | `argument-hint: [client-slug]` -> `[client]` (plugin 1.0.1)                                                                    | `C2-argument-hint/kiran-core/` | 0/5 -> 0/5, nothing moved (01 held 5/5)                       | `../results/candidates/cand-C2.json`, `C2-argument-hint.console.txt`, `.skill.diff`, `.plugin-version.diff`, `.validate.txt` |
| C3 report stage on another tier | No plugin file changed. The report stage only (cases 01, 02, 03, 09) runs on `claude-sonnet-5-5` instead of `claude-haiku-5-5` | command line, see below        | 0/5 -> 5/5 (picked); the full suite after-change run gave 4/5 | `../results/candidates/cand-C3.json`, `C3-model-tier-sonnet-case09.console.txt`                                              |

Run a plugin candidate: `python3 evals/run_suite.py --plugin-dir candidates/C1-description/kiran-core --case 01 --case 09 --runs 5 --max-suite-usd <cap> --timeout-min <t> --out evals/runs/cand-C1.json`

Run C3: `python3 evals/run_suite.py --case 09 --runs 5 --case-model 09-plain-sentence=claude-sonnet-5-5 --max-suite-usd <cap> --timeout-min <t> --out evals/runs/cand-C3.json`

What the recordings show: the cause of the case 09 failures is that the job passes the client NAME ("Mehr Bakery")
to a skill that expects the slug (`mehr-bakery`) — see `../results/case09-skill-args.txt`. C3 did not fix that cause;
it changed how the job copes with it, and the report stage cost went up sharply. A skill that accepts the client's
name might be a cheaper fix. It was not tested.
