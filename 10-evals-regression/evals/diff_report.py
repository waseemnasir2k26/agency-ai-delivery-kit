#!/usr/bin/env python3
"""diff_report.py - before/after report for two run_suite.py results (Episode 10, Regression Pack).

The script prints EVIDENCE. It never decides. The decision line stays empty until a person fills it in.

Usage:  python3 evals/diff_report.py evals/baseline.json evals/runs/after-change.json [--md out.md]

STATUS per case:
  BELOW MARK  the after run is below the case's written pass mark
  MOVED       the pass rate changed, or cost / duration moved by more than 25 %, but the case is still at/above its mark
  HELD        same pass rate, cost and duration within 25 %
Key printed for the person (not applied by the script):
  KEEP        every case at or above its mark
  INVESTIGATE a case moved but stayed at/above its mark, or cost or duration moved
  ROLL BACK   a must-pass case fell below its mark
"""
import json, sys
from pathlib import Path


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def moved(a, b, tol=0.25):
    if a in (None, 0) or b is None:
        return a != b
    return abs(b - a) / a > tol


def main(argv):
    if len(argv) < 2:
        print(__doc__); return 2
    before, after = load(argv[0]), load(argv[1])
    md = argv[argv.index("--md") + 1] if "--md" in argv else None
    hb, ha = before["header"], after["header"]
    lines = []
    p = lines.append
    p("REGRESSION REPORT  (fictional data · costs are client-side estimates at list price, not an invoice)")
    p(f"model         {hb['model_pinned']}  ->  {ha['model_pinned']}" + (f"   one-stage override: {ha['case_models']}" if ha.get("case_models") else ""))
    p(f"claude code   {hb['claude_code_version']}  ->  {ha['claude_code_version']}")
    p(f"plugin        {hb['plugin']} {hb['plugin_version']}  ->  {ha['plugin']} {ha['plugin_version']}")
    p(f"fixtures      {hb['fixture_version']}  ->  {ha['fixture_version']}")
    if hb.get("plugin_description_client_report") != ha.get("plugin_description_client_report"):
        p(f"client-report description:\n   before: {hb.get('plugin_description_client_report')}\n   after:  {ha.get('plugin_description_client_report')}")
    p("")
    p(f"{'CASE':<20} {'PASS RATE':<11} {'MARK':<5} {'COST/RUN before -> after':<26} {'WALL before -> after':<20} {'ERR':<5} STATUS")
    statuses = {}
    for cid in sorted(set(before["cases"]) | set(after["cases"])):
        b, a = before["cases"].get(cid), after["cases"].get(cid)
        if not b or not a:
            p(f"{cid:<20} {'(missing in ' + ('before' if not b else 'after') + ')'}")
            statuses[cid] = "MISSING"
            continue
        rate_b, rate_a = b["passes"] / b["runs"] if b["runs"] else 0, a["passes"] / a["runs"] if a["runs"] else 0
        if not a["at_or_above_mark"]:
            st = "BELOW MARK"
        elif rate_a != rate_b or moved(b["mean_cost_usd"], a["mean_cost_usd"]) or moved(b["mean_wall_s"], a["mean_wall_s"]):
            st = "MOVED"
        else:
            st = "HELD"
        if a["must_pass"] and not a["at_or_above_mark"]:
            st += " (must pass)"
        statuses[cid] = st
        cost = f"${b['mean_cost_usd']:.4f} -> ${a['mean_cost_usd']:.4f}"
        wall = f"{b['mean_wall_s']:.1f}s -> {a['mean_wall_s']:.1f}s"
        p(f"{cid:<20} {b['pass_rate'] + ' -> ' + a['pass_rate']:<11} {a['pass_mark']:<5} {cost:<26} {wall:<20} {b['errors']}->{a['errors']:<3} {st}")
    sb, sa = before["summary"], after["summary"]
    p("")
    p(f"suite: {sb['at_or_above_mark']}/{sb['cases']} -> {sa['at_or_above_mark']}/{sa['cases']} cases at or above their mark · "
      f"errors {sb['errors']} -> {sa['errors']} · suite cost ${sb['suite_cost_usd']:.4f} -> ${sa['suite_cost_usd']:.4f} · "
      f"wall {sb['suite_wall_s'] / 60:.1f} -> {sa['suite_wall_s'] / 60:.1f} min")
    below = [k for k, v in statuses.items() if v.startswith("BELOW")]
    mv = [k for k, v in statuses.items() if v == "MOVED"]
    p(f"headline: {len(below)} below mark{(' (' + ', '.join(below) + ')') if below else ''} · {len(mv)} moved{(' (' + ', '.join(mv) + ')') if mv else ''} · "
      f"{sum(v == 'HELD' for v in statuses.values())} held")
    p("")
    p("KEY (for the person, not applied by this script):")
    p("  KEEP = every case at or above its mark · INVESTIGATE = a case moved but stayed at/above its mark, or cost/duration moved")
    p("  ROLL BACK = a must-pass case fell below its mark")
    p("")
    p("DECISION: ________________   BY: ________________   DATE: ________________")
    text = "\n".join(lines)
    print(text)
    if md:
        Path(md).write_text("```\n" + text + "\n```\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
