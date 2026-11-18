#!/usr/bin/env python3
"""Claude Code status line: which worktree am I in, how full is the context, what has this session cost.
Claude Code pipes a JSON object to this script on stdin and shows the first line it prints.
Output example:  [mehr] ctx 7% | $0.09      ("main" when the session is not in a worktree)
Python only (no jq needed). The $ figure is Claude Code's own estimate, not a bill."""
import json, sys

try:
    d = json.load(sys.stdin)
except Exception:
    print("[?] status unavailable"); sys.exit(0)
wt = (d.get("worktree") or {}).get("name") or (d.get("workspace") or {}).get("git_worktree") or "main"
pct = int((d.get("context_window") or {}).get("used_percentage") or 0)
cost = (d.get("cost") or {}).get("total_cost_usd") or 0
print(f"[{wt}] ctx {pct}% | ${cost:.2f}")
