#!/usr/bin/env python3
"""E2 report checks on the client-report output (same four rules as the Episode 2 grader).
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
from e2_report import check_report
if rec.get("is_error") or not rec.get("result"):
    done(False, "no report text (run error: %s)" % rec.get("subtype"))
data_text = (pathlib.Path(a.workspace) / "data" / (exp["slug"] + ".json")).read_text(encoding="utf-8")
ok, res = check_report(rec["result"], data_text)
done(ok, "; ".join("%s %s (%s)" % ("ok" if v[0] else "FAIL", k, v[1]) for k, v in res.items()))
