#!/usr/bin/env python3
"""Offline self-test for scripts/validate-report.py. No model call, no login needed.

Feeds four recorded Claude results (tests/robot-samples/*.json) to the validator inside a
temporary copy of the project and checks that only the green one produces a report:
  green.json             -> OK, reports/<date>.json, exit 0
  missing-data-file.json -> FAILED receipt (the skill's data file was missing), exit 1
  budget-exhausted.json  -> FAILED receipt (--max-budget-usd hit), exit 1
  wrong-number.json      -> FAILED receipt (leads do not match the data file), exit 1
usage: python tests/validator-selftest.py      (needs: pip install jsonschema)
"""
import pathlib, shutil, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
CASES = [("green.json", 0, None), ("missing-data-file.json", 1, "no structured_output"),
         ("budget-exhausted.json", 1, "error_max_budget_usd"), ("wrong-number.json", 1, "numbers do not match")]
fails = 0
for name, want_exit, want_reason in CASES:
    with tempfile.TemporaryDirectory() as tmp:
        t = pathlib.Path(tmp)
        shutil.copytree(ROOT / "scripts", t / "scripts")
        shutil.copytree(ROOT / "data", t / "data")
        shutil.copy(ROOT / "schema.json", t / "schema.json")
        (t / "reports").mkdir()
        shutil.copy(ROOT / "tests" / "robot-samples" / name, t / "reports" / "_last.json")
        claude_exit = "1" if name == "budget-exhausted.json" else "0"
        p = subprocess.run([sys.executable, str(t / "scripts" / "validate-report.py"), claude_exit, "mehr-bakery"],
                           capture_output=True, text=True)
        receipts = list((t / "reports").glob("FAILED-*.txt"))
        reports = [f for f in (t / "reports").glob("*.json") if f.name != "_last.json"]
        text = receipts[0].read_text(encoding="utf-8") if receipts else ""
        ok = p.returncode == want_exit and (
            (want_reason is None and reports and not receipts) or
            (want_reason is not None and receipts and want_reason in text and not reports))
        fails += 0 if ok else 1
        print(f"{'PASS' if ok else 'FAIL'}  {name:24} exit={p.returncode}  {p.stdout.strip()}")
print(f"RESULT: {len(CASES) - fails}/{len(CASES)} as expected")
sys.exit(1 if fails else 0)
