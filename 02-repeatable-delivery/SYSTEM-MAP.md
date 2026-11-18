# SYSTEM-MAP: Repeatable Delivery, on one page

(The episode mentions a SYSTEM-MAP.pdf. The PDF is not included; this page is the same map as text.)

```
                      KIRAN STUDIO: ONE WEEKLY CLIENT REPORT, DONE THE SAME WAY EVERY TIME

  data/<client>.json  ──►  /client-report <client>  ──►  report text          tests/run-checks.py
  (the truth)              .claude/skills/              Wins (exactly 3)  ──► 4 pass/fail checks
                           client-report/SKILL.md       Numbers (copied)      x 3 test reports
                           6 hard rules                 Next                  v1: 0/3   v2: 3/3
                                                        <=150 words, no email

  ────────────────────────────────── GUARD RAILS (every session) ──────────────────────────────────

  Claude wants to...            What stops it                                Where
  read .env with the Read tool  deny rule  Read(./.env), Read(./.env.*)      .claude/settings.json
  read .env from a shell        secret-firewall.sh (exit 2)                  .claude/hooks/
     Bash: cat .e*  type .env     matcher "Bash|PowerShell"
     PowerShell: Get-Content .env, Select-String, Copy-Item
  edit hooks / settings /       deny rules  Edit(./.claude/hooks/**) ...     .claude/settings.json
     the approval file          + write guard in commit-gate.sh
  git commit                    commit-gate.sh (exit 2) unless:              .claude/hooks/
                                  .claude/review.json says approved
                                  AND its diff_sha == sha256(staged diff)
                                  AND nothing unstaged, no -a / paths / alias
  a human: git commit           git-hooks/pre-commit (same hash check)       git config core.hooksPath git-hooks

  ────────────────────────────────── REVIEW LOOP ──────────────────────────────────

  git add  ──►  bash scripts/run-review.sh  ──►  reviewer agent (Read, Grep, Glob only)
                                                    │  ends with VERDICT: APPROVED | REJECTED
                                                    ▼
                scripts/record-review.sh  ──►  .claude/review.json {verdict, diff_sha}
                (the script stamps the hash; the model never writes it)
                                                    ▼
                git commit  ──►  commit-gate: blocked / rejected / stale / through

  ────────────────────────────────── 7 AM, NOBODY WATCHING ──────────────────────────────────

  Task Scheduler 07:00 (or cron)
     └► run-report.cmd / run-report.sh
          └► claude -p "/client-report <client>" --json-schema schema.json --max-budget-usd <cap>
               --setting-sources project --strict-mcp-config        (NOT --bare: needs hooks + skill)
          └► scripts/validate-report.py
               JSON ok? completed? structured_output? schema ok? numbers == data file?
                 yes ─► reports/<date>.json        (Last Result 0)
                 no  ─► reports/FAILED-<time>.txt  (Last Result 1: reason, exit code, cost estimate)

  ────────────────────────────────── WHAT IT DOES NOT DO ──────────────────────────────────
  Hooks read command TEXT. A script that builds ".env" at runtime gets past the firewall.
  The commit gate is a workflow gate, not a security boundary. Real secrets live outside the repo.
```
