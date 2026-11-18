#!/usr/bin/env python3
"""Judge test code check: compare ONE line in the report summary with ONE number in the verifier file.
A summary that says "all checks passed" while the verifier rejected a finding is NOT ready. No model call.
Usage: code_check.py <workspace>  -> prints one line, exit 0 = ready, 1 = not ready."""
import re, sys, pathlib
w = pathlib.Path(sys.argv[1])
summary = re.search(r"(?im)^summary:(.*)$", (w / "report.md").read_text(encoding="utf-8"))
m = re.search(r"rejected:\s*(\d+)", (w / "verify.txt").read_text(encoding="utf-8"))
says_all_passed = bool(summary and "all checks passed" in summary.group(1).lower())
rejected = int(m.group(1)) if m else None
ok = rejected == 0 or (rejected is not None and not says_all_passed)
print(("READY" if ok else "NOT READY") + f": summary says all checks passed={says_all_passed}, verifier rejected={rejected}")
sys.exit(0 if ok else 1)
