# kiran-core

Kiran Studio shared delivery kit (fictional agency, synthetic data). Enable it in every client repo.

- `/kiran-core:proposal <brief.md>` (1.1.0): unknowns list (`unknowns.json`, every item `open`) + draft `proposal.md`; never writes a price.
- `/kiran-core:client-report <client-slug>`: weekly client report from `data/<client>.json` (reads the data file in the client repo).
- `/kiran-core:pr-review`: pull request review against `checks.md` and `scripts/check-site.py` in the client repo.
- `kiran-core:critic` agent: strict read-only critic, ends with `VERDICT: APPROVED|REJECTED`. 1.1.0 adds "Claims a proposal may never make".
- `secret-firewall` hook (PreToolUse, `Write|Edit|Bash|PowerShell`): blocks known key formats and `.env` access. Text guard only, not a secret scanner.
- `commit-gate` hook (PreToolUse, `Bash|PowerShell`): blocks `git commit` until `scripts/run-review.sh` records an approval for the exact staged diff.

Needs Git Bash (Windows) and Python 3 on PATH. Read `hooks/hooks.json` and `scripts/` before you install: hooks run as you.

Install (in the client repo, replace `<your-org>`):

    claude plugin install kiran-core --marketplace <your-org>/kiran-marketplace --scope project
