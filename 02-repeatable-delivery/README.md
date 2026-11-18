# 02 · Repeatable Delivery — Repeatable Delivery Pack

**For the owner:** a weekly client report that comes out the same way every time, is tested before it
ships, and cannot be committed unreviewed. It runs itself at 7 AM and leaves a receipt when it fails,
so a wrong number never reaches a client unnoticed and nobody spends Monday morning rebuilding it.

**Shown in:** Episode 2, "Turn the written procedure into a skill, with a test", "Guard one: keep the
AI away from the keys file", "A reviewer and a commit gate", "Five commits: blocked, rejected,
approved, stale, through", "What the gate does not do", "The report that runs itself at 7 AM" and
"Break it on purpose: the missing data file".

All data is synthetic. Kiran Studio and its clients (Mehr Bakery, Sufi Threads, Noor Dental Clinic)
are fictional. Every `.example` email address and every `FAKE` key is fake on purpose.

## What's inside

| Path                                                                     | What it is                                                                                           |
| ------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------- |
| `kiran-ops/`                                                             | The demo project. Run Claude Code from inside this folder                                            |
| `kiran-ops/.claude/skills/client-report/SKILL.md`                        | The report skill (final version: six hard rules)                                                     |
| `kiran-ops/.claude/skills/client-report/checks.md`                       | The four pass/fail checks the test grades                                                            |
| `kiran-ops/tests/case1..3/input.txt`                                     | The three test cases (one client slug each)                                                          |
| `kiran-ops/tests/run-checks.py`                                          | Offline grader: four checks on each of three reports, prints `RESULT: x/3 PASS`                      |
| `kiran-ops/tests/run-cases.py`                                           | Runs the skill on the three cases with real `claude -p` calls (needs your login)                     |
| `kiran-ops/tests/sample-outputs/v1/`, `v2/`                              | The reports recorded in the episode: first skill (0/3, plus `SKILL.v1.md`) and final skill (3/3)     |
| `kiran-ops/data/*.json`                                                  | The three clients' weekly data (the truth the report must copy)                                      |
| `kiran-ops/.claude/settings.json`                                        | Deny rules, both `PreToolUse` hooks with `"matcher": "Bash\|PowerShell"`, `"defaultMode": "default"` |
| `kiran-ops/.claude/hooks/secret-firewall.sh`                             | Blocks shell commands that touch `.env*`, Bash and PowerShell spellings                              |
| `kiran-ops/.claude/hooks/commit-gate.sh` + `commit-shape.py`             | Blocks `git commit` from either tool unless an approval matches the staged diff                      |
| `kiran-ops/.claude/agents/reviewer.md`                                   | Read-only reviewer agent (Read, Grep, Glob)                                                          |
| `kiran-ops/scripts/run-review.sh`, `record-review.sh`                    | Ask the reviewer about the staged diff; stamp its verdict with the diff's sha256 (the fingerprint)   |
| `kiran-ops/git-hooks/pre-commit`                                         | The same check for humans typing `git commit`                                                        |
| `kiran-ops/src/pricing.py`, `tests/test_pricing.py`                      | Tiny code sample for the review demo, with its test                                                  |
| `kiran-ops/run-report.cmd`                                               | The 7 AM robot for Windows Task Scheduler (header note on bare mode and prompts)                     |
| `kiran-ops/run-report.sh`                                                | The same robot for cron (macOS, Linux, WSL)                                                          |
| `kiran-ops/schema.json`                                                  | JSON shape the robot's report must have                                                              |
| `kiran-ops/scripts/validate-report.py`                                   | Checks the robot's output and writes a report or a `FAILED` receipt                                  |
| `kiran-ops/tests/validator-selftest.py`, `tests/robot-samples/`          | Offline test of the validator on four recorded results                                               |
| `kiran-ops/.robot.env.example`, `.env.example`, `.gitignore`, `reports/` | Robot settings template, FAKE keys for the demo, ignore rules, output folder                         |
| `WINDOWS-HOOKS.md`                                                       | Git for Windows, why a `Bash` matcher misses PowerShell, live block test per tool                    |
| `RETEST-LOG.md`                                                          | The PowerShell retest: both tools blocked; the Bash-only control fails both PowerShell cases         |
| `bypass-tests/`                                                          | The three gate cheats cut from the episode, the hardened gate, and a runnable battery                |
| `HEADLESS-NOTES.md`                                                      | Trust, bare mode, `--permission-prompts none`, receipts, cost estimates                              |
| `SKILL-HEALTH.md`                                                        | Optional monthly `/skill-doctor` check with a log table                                              |
| `SYSTEM-MAP.md`                                                          | The one-page map (the PDF is not included)                                                           |

> **Before you start (packaging note):** the settings file ships as
> `kiran-ops/.claude/settings.json.READY` if `settings.json` is missing in your copy. Rename it to
> `settings.json`. Without it, no deny rule and no hook is active.

## Use it in 5 steps

1. **Check prerequisites.**

   ```bash
   claude --version && git --version && bash --version && python --version
   python -m pip install jsonschema        # for the 7 AM validator
   ```

   Windows: install Git for Windows first (it provides `bash`); read `WINDOWS-HOOKS.md`. Use
   `python3` instead of `python` on macOS/Linux if that is your command name.

2. **Make it a git repo** (the commit gate needs one). Copy `kiran-ops` somewhere you own, then:

   ```bash
   cd kiran-ops
   git init -b main
   git config core.hooksPath git-hooks       # turns on the human pre-commit hook
   git add . && git commit -m "Kiran ops starter" --no-verify   # setup commit only
   ```

   `--no-verify` is for this setup commit only: the human hook blocks any commit without an approval.

3. **Test the skill.** Offline first, then for real:

   ```bash
   python tests/run-checks.py tests/sample-outputs/v1    # recorded first skill: RESULT: 0/3 PASS
   python tests/run-checks.py tests/sample-outputs/v2    # recorded final skill: RESULT: 3/3 PASS
   python tests/run-cases.py runs/mine                    # real run, needs your Claude login
   python tests/run-checks.py runs/mine
   ```

   If a case fails, change `SKILL.md`, never `checks.md` or the grader. The test defines the spec.

4. **Try the guard rails.**

   ```bash
   bash ../bypass-tests/run-bypass-tests.sh        # offline: 58 cases, expect 0 unexpected
   ```

   Then live (needs your login): follow `WINDOWS-HOOKS.md` step 4 to see each block once. For the
   review loop, plant the episode's bug in `src/pricing.py` (`return price - price * pct`), `git add`
   it, run `bash scripts/run-review.sh` (expect REJECTED), ask Claude to commit (expect BLOCKED), fix
   it back to `price * pct / 100`, `git add`, re-run the review (APPROVED), commit.

5. **Schedule the 7 AM report.**
   ```bash
   python tests/validator-selftest.py              # offline: RESULT: 4/4 as expected
   cp .robot.env.example .robot.env                # PowerShell: Copy-Item .robot.env.example .robot.env
   ```
   Windows: run `.\run-report.cmd` once by hand, look in `reports\`, then create the task with the
   `schtasks /create ...` line in its header. macOS/Linux/WSL: `bash run-report.sh`, then the cron line
   in its header. Read `HEADLESS-NOTES.md` before leaving it unattended.

## Limits — what it does NOT do

- The hooks read command **text**. A command that builds the file name at runtime
  (`open('.'+'env')`), or a script file that opens `.env` inside its own code, gets past the firewall.
  `bypass-tests/` lists these gaps. Keep real secrets out of the project folder.
- Deny rules do not cover a script that opens files itself; we saw a `python -c` write get past the
  `Edit(...)` deny rule until the commit gate's text guard was added.
- The commit gate is a workflow gate, not a security boundary. A person can still `git commit
--no-verify`, and anyone with shell access can change the hooks.
- The reviewer is a model. It found the seeded pricing bug in our runs; it will not find every bug.
  The gate proves a review happened on this exact diff, not that the code is right.
- The skill's `allowed-tools: Read` pre-approves Read for that turn. It does not restrict other tools.
- The robot needs the machine on, awake and logged in at 7 AM (Task Scheduler "Interactive only"), and
  `claude` logged in. It reports on one client per run (`ROBOT_CLIENT`).
- The PowerShell spellings added to the hooks after the live retest were tested offline only.
- No cost guarantees: cost figures in Claude's output are estimates, not a bill.

## Tested

Offline for the kit: `run-checks.py` on the recorded outputs (v1 0/3, v2 3/3, as in the episode),
`run-bypass-tests.sh` 58/58 as expected (Bash and PowerShell tool JSON), `validator-selftest.py` 4/4,
`test_pricing.py` 2/2, JSON parse of settings and schema. Live model runs need your Claude login.
