#!/usr/bin/env python3
"""SessionStart hook: proves to run_job.py that project hooks loaded in this session.

Writes .claude/run-state/<session_id>.hook.json. run_job.py's pre-flight fails loudly
if the marker for its session does not appear (e.g. a future --bare default skips hooks).
"""
import json, sys, time
from pathlib import Path

try:
    payload = json.load(sys.stdin)
except Exception:
    payload = {}
sid = str(payload.get("session_id") or "unknown")
out = Path(__file__).resolve().parent.parent / "run-state"
out.mkdir(exist_ok=True)
(out / (sid + ".hook.json")).write_text(json.dumps({
    "hook": "session-marker", "event": payload.get("hook_event_name", "SessionStart"),
    "session_id": sid, "source": payload.get("source"), "t": time.time()}), encoding="utf-8")
