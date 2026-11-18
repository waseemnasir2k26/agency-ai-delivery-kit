# Upgrade day (one card) · Kiran Studio · fictional agency

1. **FREEZE.** Model pinned by its full name (`evals/pin.json`, `.claude/settings.json`). Plugin pinned by version and release tag (`claude plugin tag ./kiran-core` -> `kiran-core--v<version>`). Write down the Claude Code version (`claude --version`).
2. **CHANGE ONE THING.** Only one. If three things change and a case drops, the report cannot tell you which one did it.
3. **RUN THE SUITE, limits on.** `python3 evals/run_suite.py --runs 5 --max-suite-usd <cap> --timeout-min <t> --out evals/runs/after-change.json` on the eval machine (`eval-machine/`). The runner stops if the plugin or its hooks did not load.
4. **READ THE REPORT.** `python3 evals/diff_report.py evals/baseline.json evals/runs/after-change.json`
5. **A PERSON DECIDES** and writes it on the decision line: KEEP (every case at or above its mark) · INVESTIGATE (a case moved but stayed at or above its mark, or cost or duration moved) · ROLL BACK (a must-pass case fell below its mark).
6. **SHADOW -> ONE CLIENT -> ALL.** Shadow = new version does Mehr Bakery's weekly job beside the old one; only the old output is sent; a person compares the two.

**ROLLBACK = put the two pins back:** `git checkout kiran-core--v<pinned> -- kiran-core` + the pinned full model name, then the same two commands (steps 3-4). Each collaborator still updates their own install (Episode 7).

Costs are client-side estimates at list price, not an invoice. Models available on record day. Rerun the test when the model changes.
