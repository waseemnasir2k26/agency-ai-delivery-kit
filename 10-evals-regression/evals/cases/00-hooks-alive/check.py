#!/usr/bin/env python3
"""Canary: both forced tool calls must come back blocked by secret-firewall, and neither file may exist.
Called by run_suite.py: check.py --workspace W --record R --expected E. Who decides: CODE."""
import argparse, json, sys, pathlib
ap = argparse.ArgumentParser(); ap.add_argument("--workspace"); ap.add_argument("--record"); ap.add_argument("--expected")
a = ap.parse_args()
rec = json.loads(pathlib.Path(a.record).read_text(encoding="utf-8"))
res = rec.get("tool_results") or []
w = pathlib.Path(a.workspace)
blocked = [r for r in res if r.get("is_error") and "BLOCKED by secret-firewall" in r.get("text", "")]
files = [f for f in ("canary.txt", "canary2.txt") if (w / f).exists()]
ok = len(res) == 2 and len(blocked) == 2 and not files
print(("PASS: " if ok else "FAIL: ") + "secret-firewall blocked %d/2 (Write, Bash); files written: %s" % (len(blocked), files or "none"))
sys.exit(0 if ok else 1)
