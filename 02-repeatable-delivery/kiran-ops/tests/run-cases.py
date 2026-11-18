#!/usr/bin/env python3
"""Run the client-report skill on each case with the real claude CLI. usage: run-cases.py <outdir>"""
import json, subprocess, sys, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
total = 0.0
for case in sorted((root / "tests").glob("case*")):
    slug = (case / "input.txt").read_text().strip()
    p = subprocess.run(["claude", "-p", f"/client-report {slug}", "--model", "sonnet",
        "--setting-sources", "project", "--strict-mcp-config", "--output-format", "json",
        "--max-budget-usd", "0.5", "--no-session-persistence"],
        cwd=root, capture_output=True, text=True, encoding="utf-8")
    try:
        j = json.loads(p.stdout)
    except Exception:
        print(case.name, "no JSON, exit", p.returncode); continue
    (out / f"{case.name}.json").write_text(p.stdout, encoding="utf-8")
    (out / f"{case.name}.txt").write_text(j.get("result", ""), encoding="utf-8")
    total += j.get("total_cost_usd", 0)
    print(f"{case.name}: exit={p.returncode} cost=${j.get('total_cost_usd',0):.3f} {j.get('duration_ms',0)/1000:.1f}s")
print(f"total cost ${total:.3f}")
