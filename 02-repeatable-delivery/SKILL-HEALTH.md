# SKILL-HEALTH: a monthly check on the team's skills (optional)

Every skill Claude Code loads puts its name and description into the context of every session. A
skill nobody uses still costs context, and two skills with similar descriptions make Claude pick the
wrong one. Once a month, look at the whole set.

## 1. Run `/skill-doctor`

Inside Claude Code, in the project (and once in your home folder for personal skills):

```
/skill-doctor
```

It reports which loaded skills go unused and what they cost in context. If your Claude Code release
does not have it yet, `/skills` lists what is loaded; check usage by hand.

## 2. Decide per skill

| Finding                                      | Action                                                      |
| -------------------------------------------- | ----------------------------------------------------------- |
| Not used in a month, no client depends on it | Remove it, or move it out of `.claude/skills/`              |
| Used, but the description is long            | Shorten the description; keep the detail in the body        |
| Two skills with overlapping descriptions     | Merge them, or make each description say when NOT to use it |
| Used, and its test fails                     | Fix the skill, never the test (see step 3)                  |

## 3. Re-run the skill tests

A skill is only "healthy" if its test still passes. For the report skill in this pack:

```bash
cd kiran-ops
python tests/run-cases.py runs/this-month    # real model calls, needs your Claude login
python tests/run-checks.py runs/this-month   # free, offline grader: expect RESULT: 3/3 PASS
```

Also re-run after every Claude Code update and after any edit to `SKILL.md`.

## 4. Monthly log (fill in)

| Month | Skills loaded | Unused | Removed / merged | Report skill test (x/3) | Checked by |
| ----- | ------------- | ------ | ---------------- | ----------------------- | ---------- |
|       |               |        |                  |                         |            |
|       |               |        |                  |                         |            |
|       |               |        |                  |                         |            |
