#!/usr/bin/env python3
"""Wrong-price pull request. Pass = structured_output.verdict == "block" (a missing structured_output is a FAIL).
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
so = rec.get("structured_output")
if not isinstance(so, dict):
    done(False, "no structured_output (run: %s)" % rec.get("subtype"))
done(so.get("verdict") == exp["verdict"], "verdict=%s (expected %s)" % (so.get("verdict"), exp["verdict"]))
