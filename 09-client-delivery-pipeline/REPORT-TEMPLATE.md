# Evidence report template

`build_report.py` fills this layout from `runs/<run>/verify.json` and nothing else (no model, no run summary).
Use it as the shape for any client QA report, by script or by hand.

Rules:

1. **Headline counts first:** ACCEPTED n · REJECTED n · NOT CHECKED n.
2. **NOT CHECKED is never PASS.** A check that could not be machine-checked is listed under "Needs a human look".
3. **Every row has evidence:** check · result · page URL · quoted text · screenshot.
4. **No false "passed":** pass wording ("passed", "all checks passed", "no issues found") may not appear unless
   REJECTED = 0, NOT CHECKED = 0 and verifier issues = 0. `python build_report.py runs/<run> --check <file>` exits 1 otherwise,
   and `pipeline.py approve report` refuses.
5. **Approval row** at the end, filled by the owner, not the builder, and recorded in `jobs/<job>/gates.md` row 4.

---

# Client report: <job>

**ACCEPTED __ · REJECTED __ · NOT CHECKED __**
Checker verdict: **__** · verifier issues: __ · findings filed: __
Source: `verify.json` from verify.py (plain Python, no model). NOT CHECKED never counts as a pass.

## Built

- <page URL> · screenshot `<path>`
- <page URL> · screenshot `<path>` · form <METHOD> → <action>

## Checked

| Check | Result | Page | Quoted text | Screenshot |
| --- | --- | --- | --- | --- |
| <check> (model: <model status>) | ACCEPTED / REJECTED / NOT CHECKED | <URL> | "<exact text seen on the page>" | <path> |

## Needs a human look

- NOT CHECKED: <check>: <why> · quoted "<text>" · page <URL>
- REJECTED: <check>: <why> · quoted "<text>" · page <URL>
- (or) Nothing. Every finding was accepted by the checker.

## Approval

Approved by (owner, not the builder): ____ · role: ____ · report version (commit): ____ · recorded: ____
The approver opened the page themselves, every line above has evidence, and every human-look item is fixed or told to the client.
A recorded approval in `jobs/<job>/gates.md` row 4. Not a legal signature.

---

Filled examples: `jobs/sufi-winter/report.md` (careful run: ACCEPTED 5 · REJECTED 0 · NOT CHECKED 1) and
`fixtures/test-setups/b4-planted-rejected-finding/recorded/report.v2.md` (planted rejected finding:
ACCEPTED 5 · REJECTED 1 · NOT CHECKED 1).
