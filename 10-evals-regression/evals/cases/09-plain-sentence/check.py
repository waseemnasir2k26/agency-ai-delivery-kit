#!/usr/bin/env python3
"""Plain-sentence request (no slash command). Pass = the client-report skill fired on its own AND the report passes the four E2 checks. The skill-fired assertion is the 'one added assertion' from the E10 writer notes (weakest spot 4) (a no-plugin control run confirmed the report checks alone do not prove the skill fired)
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
skills = [u.get("input", {}).get("skill", "") for u in rec.get("tool_uses", []) if u.get("name") == "Skill"]
fired = any(s.split(":")[-1] == "client-report" for s in skills)
if rec.get("is_error") or not rec.get("result"):
    done(False, "no report text (run error: %s)" % rec.get("subtype"))
data_text = (pathlib.Path(a.workspace) / "data" / "mehr-bakery.json").read_text(encoding="utf-8")
ok, res = check_report(rec["result"], data_text)
msg = ("skill fired" if fired else "skill NOT fired (Skill calls: %s)" % (skills or "none")) + " | " + \
      "; ".join("%s %s (%s)" % ("ok" if v[0] else "FAIL", k, v[1]) for k, v in res.items())
done(fired and ok, msg)
