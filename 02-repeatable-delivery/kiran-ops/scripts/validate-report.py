#!/usr/bin/env python3
"""validate-report.py <claude_exit> <client-slug>. Validates claude's JSON output; never fakes success.
OK  -> reports/<date>.json, exit 0.   Anything else -> reports/FAILED-<ts>.txt, exit 1."""
import json, re, sys, datetime, pathlib
import jsonschema
root = pathlib.Path(__file__).resolve().parent.parent
rep = root / "reports"; rep.mkdir(exist_ok=True)
cexit = int(sys.argv[1]); slug = sys.argv[2]
now = datetime.datetime.now()

def fail(reason, extra=""):
    err = (rep / "_last.err").read_text(errors="replace").splitlines() if (rep / "_last.err").exists() else []
    keep = [l for l in err if not re.search(r"hook|[A-Za-z]:\|@|key|token|secret|password", l, re.I)]
    f = rep / f"FAILED-{now:%Y%m%d-%H%M%S}.txt"
    f.write_text(f"FAILED at {now:%Y-%m-%d %H:%M:%S}\nclient: {slug}\nclaude exit code: {cexit}\nreason: {reason}\n{extra}"
                 f"stderr tail (filtered, {len(err)-len(keep)} lines withheld):\n" + "\n".join(keep[-5:]) + "\n", encoding="utf-8")
    print(f"FAILED: {reason} -> {f.name}")
    sys.exit(1)

raw = (rep / "_last.json").read_text(encoding="utf-8", errors="replace") if (rep / "_last.json").exists() else ""
try:
    j = json.loads(raw)
except Exception:
    fail("claude produced no valid JSON output")
msg = re.sub(r"[A-Za-z]:\\\S+|\S+@\S+", "<redacted>", str(j.get("result") or ""))[:200].replace("\n", " | ")
extra = f"terminal_reason: {j.get('terminal_reason')}\ncost_usd: {j.get('total_cost_usd')}\nclaude said: {msg}\n"
if cexit != 0 or j.get("is_error"):
    fail(f"claude failed ({j.get('subtype') or 'error'})", extra)
if j.get("terminal_reason") not in (None, "completed"):
    fail(f"run did not complete: {j.get('terminal_reason')}", extra)
so = j.get("structured_output")
if so is None:
    fail("no structured_output in claude result", extra)
try:
    jsonschema.validate(so, json.loads((root / "schema.json").read_text()))
except jsonschema.ValidationError as e:
    fail(f"schema validation failed: {e.message[:120]}", extra)
data = json.loads((root / "data" / f"{slug}.json").read_text())
m = data["metrics"]
if (so["site_visits"], so["leads"], so["revenue_pkr"]) != (m["site_visits"], m["leads"], m["revenue_pkr"]):
    fail("numbers do not match the data file", extra)
out = rep / f"{now:%Y-%m-%d}.json"
out.write_text(json.dumps(so, indent=2), encoding="utf-8")
print(f"OK: {out.name} (cost ${j.get('total_cost_usd'):.3f})")
