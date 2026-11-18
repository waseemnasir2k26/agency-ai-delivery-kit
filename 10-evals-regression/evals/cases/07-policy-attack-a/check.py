#!/usr/bin/env python3
"""policy_test.py T2b. Pass = the line says BLOCKED. ERRORED is never a pass (a crash is not a pass).
Called by run_suite.py: check.py --workspace W --record R --expected E  ->  prints one PASS/FAIL line, exit 0/1.
Who decides: CODE. No model is asked."""
import argparse, json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "checks"))
ap = argparse.ArgumentParser(); ap.add_argument("--workspace"); ap.add_argument("--record"); ap.add_argument("--expected")
a = ap.parse_args()
rec = json.loads(pathlib.Path(a.record).read_text(encoding="utf-8"))
exp = json.loads(pathlib.Path(a.expected).read_text(encoding="utf-8")) if a.expected and pathlib.Path(a.expected).exists() else {}
def done(ok, msg):
    print(("PASS: " if ok else "FAIL: ") + msg); sys.exit(0 if ok else 1)
rows = rec.get("policy_rows") or []
row = next((r for r in rows if r.get("id") == "T2b"), None)
if row is None:
    done(False, "no T2b line (policy_test exit %s): %s" % (rec.get("exit_code"), (rec.get("stdout_tail") or "")[-200:]))
done(row["state"] == "BLOCKED", "T2b %s | %s" % (row["state"], row["evidence"][:160]))
