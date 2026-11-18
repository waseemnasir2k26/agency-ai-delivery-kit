"""BONUS copy of Episode 9 verify.py (+ optional client filter: verify.py runs/<run> <client>; screenshots under ../runs).
verify.py: plain Python. The model is the sensor, this file is the judge.
COPY of Episode 4's verify.py. Episode 9 changes:
  - data from ./data; prices = `prices` + `winter.prices`
  - NEW RULE: a price on a page with no data row fails (the sweep flags every "PKR n" whose amount is in no row,
    unless the item-level recheck already flagged that amount on that page)
  - writes runs/<run>/verify.json (machine-readable; build_report.py reads only this) next to report.md
  - hours: a day line may match the shop hours or fittings.hours (added after the first QA run's false positive)
  - exit code: 0 only when the verdict is PASS
Usage: python verify.py runs/<run>   -> prints verdicts, writes runs/<run>/verify.json + report.md"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
PHONE = "+92 300 0000000"
EVIDENCE = ["seen_text", "evidence_url", "screenshot"]
INJECTION = re.compile(r"(?i)\b(AI|assistant|LLM|bot)s?\b.{0,40}\b(testers?|mark|ignore|PASS)\b")

def norm(s):
    return re.sub(r"\s+", " ", s).strip()

def client_of(url):
    return next((c for c in truth if f"/{c}/" in url), None)

def all_prices(d):
    return list(d.get("prices") or []) + list((d.get("winter") or {}).get("prices") or [])

def no_row_prices(client, seen, already):
    """NEW (Ep9): every PKR amount on the page must exist as a row in the data file."""
    known = {p["pkr"] for p in all_prices(truth[client])}
    out = []
    for m in re.finditer(r"PKR\s*([\d,]+)", seen):
        amt = int(m.group(1).replace(",", ""))
        if amt not in known and not any(f"page PKR {m.group(1)}" in b for b in already):
            line = seen[:m.end()].split("\n")[-1].strip()
            out.append(f"price with no data row: \"{norm(line)[-60:]}\" (PKR {amt} is in no row of data/{client}.json)")
    return out

def recheck(client, seen):
    """Recompute PASS/FAIL from the quoted text alone. None = nothing checkable in the quote."""
    d, bad, checked = truth[client], [], False
    for p in all_prices(d):
        for m in re.finditer(r"(?<!\w)%s(?!\w)[\s\S]{0,40}?PKR\s*([\d,]+)" % re.escape(p["item"]), seen):
            checked = True
            if int(m.group(1).replace(",", "")) != p["pkr"]:
                bad.append(f"{p['item']}: page PKR {m.group(1)}, data PKR {p['pkr']}")
    # Ep9: the data file now has a second set of hours (fittings.hours, "Mon-Sat: 12:00-19:00 (by appointment)").
    # The first QA run flagged the fitting page's hours as a shop-hours mismatch (a checker false positive). A day line
    # now passes if it matches the shop hours OR the fitting hours for that day. Limit: a page that swaps them still passes.
    fit = dict(re.findall(r"([A-Za-z-]+): (\S+)", ((d.get("fittings") or {}).get("hours") or "")))
    for day, hrs in d["hours"].items():
        for m in re.finditer(r"\b%s: (\S+)" % re.escape(day), seen):
            checked = True
            if m.group(1) not in (hrs, fit.get(day)):
                bad.append(f"{day}: page {m.group(1)}, data {hrs}" + (f" (fittings {fit[day]})" if day in fit else ""))
    for ph in re.findall(r"\+\d[\d ]{8,14}\d", seen):
        checked = True
        if ph != PHONE:
            bad.append(f"phone {ph} is not the placeholder")
    extra = no_row_prices(client, seen, bad)
    if extra:
        checked = True
        bad += extra
    return (("FAIL" if bad else "PASS"), bad) if checked else (None, [])

def verify(run_dir):
    run = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    pages = run["pages"]
    sites = {c: {"visited": False, "issues": [], "claims": []} for c in truth}
    # 1) the verifier's own sweep over every page the agent actually opened
    for url, p in pages.items():
        c = client_of(url)
        if not c:
            continue
        sites[c]["visited"] = True
        status, bad = recheck(c, p["text"])
        for b in bad:
            sites[c]["issues"].append({"issue": b, "url": url, "screenshot": p["screenshot"]})
        for m in INJECTION.finditer(p["text"]):
            sites[c]["issues"].append({"issue": f"page contains instructions aimed at AI: \"{m.group(0)}\"",
                                       "url": url, "screenshot": p["screenshot"]})
    # 2) every claim the model made must survive evidence + recheck
    for f in run["findings"]:
        c = f.get("client") if f.get("client") in truth else None
        claim = f"{f.get('check')} {f.get('status')}"
        missing = [k for k in EVIDENCE if not f.get(k)]
        if missing:
            v = f"REJECTED: no evidence ({', '.join(missing)} missing)"
        elif f["evidence_url"] not in pages:
            v = "REJECTED: agent never opened that URL"
        elif norm(f["seen_text"]) not in norm(pages[f["evidence_url"]]["text"]):
            v = "REJECTED: quoted text is not on that page"
        elif not (ROOT.parent / f["screenshot"]).exists():
            v = "REJECTED: screenshot file does not exist"
        else:
            status, bad = recheck(c, f["seen_text"]) if c else (None, [])
            v = ("ACCEPTED (needs human: nothing machine-checkable)" if status is None else
                 "ACCEPTED" if status == f.get("status") else f"OVERRIDDEN: verifier says {status} ({'; '.join(bad)})")
        if c:
            sites[c]["claims"].append({"claim": claim, "verdict": v, "finding": f})
        print(f"[{c or '?'}] model says {claim:<16} -> {v}")
    return run, sites

def write_report(run_dir, run, sites):
    lines = [f"# Site Watch report", "",
             f"Run: `{run_dir.name}` · model `{run['model']}` · {run['num_turns']} turns · "
             f"${run['total_cost_usd']:.4f} · {run['wall_s']} s · stop: {run['terminal_reason']}", ""]
    for c, s in sites.items():
        verdict = "NOT CHECKED" if not s["visited"] else ("FAIL" if s["issues"] else "PASS")
        lines += [f"## {truth[c]['name']}: **{verdict}**", ""]
        for i in s["issues"]:
            lines.append(f"- {i['issue']}  \n  seen at `{i['url']}` · screenshot `{i['screenshot']}`")
        for x in s["claims"]:
            if x["verdict"].startswith("ACCEPTED (needs human") and x["finding"]["status"] == "FAIL":
                lines.append(f"- Needs a human look: agent saw \"{norm(x['finding']['seen_text'])}\" "
                             f"(expected {x['finding']['expected']}) at `{x['finding']['evidence_url']}`")
        ok = sum(x["verdict"].startswith("ACCEPTED") for x in s["claims"])
        rejected = len(s["claims"]) - ok
        lines.append(f"- Pages opened: {sum(client_of(u) == c for u in run['pages'])} · agent claims accepted: {ok}"
                     + (f" · rejected/overridden: {rejected}" if rejected else ""))
        lines.append("")
    lines += ["---", "Verdicts come from verify.py (deterministic). The AI agent is a sensor, not the judge.",
              "Reviewed and signed by: ____________________"]
    (run_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")
    return {c: ("NOT CHECKED" if not s["visited"] else "FAIL" if s["issues"] else "PASS") for c, s in sites.items()}

truth = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted(DATA.glob("*.json"))
         if len(sys.argv) < 3 or p.stem in sys.argv[2:]}   # BONUS: optional client filter

def kind(v):
    return ("NOT_CHECKED" if v.startswith("ACCEPTED (needs human") else "ACCEPTED" if v.startswith("ACCEPTED")
            else "REJECTED")

def write_json(run_dir, run, sites, verdicts):
    claims = [{"client": c, "check": x["finding"].get("check"), "model_status": x["finding"].get("status"),
               "result": kind(x["verdict"]), "verifier": x["verdict"], "expected": x["finding"].get("expected"),
               "seen_text": x["finding"].get("seen_text"), "evidence_url": x["finding"].get("evidence_url"),
               "screenshot": x["finding"].get("screenshot")} for c, s in sites.items() for x in s["claims"]]
    counts = {k: sum(cl["result"] == k for cl in claims) for k in ("ACCEPTED", "REJECTED", "NOT_CHECKED")}
    counts["FINDINGS"] = len(run["findings"])
    counts["ISSUES"] = sum(len(s["issues"]) for s in sites.values())
    out = {"run": run_dir.name, "generated_by": "verify.py (deterministic, no model)",
           "site_watch": {k: run.get(k) for k in ("model", "num_turns", "total_cost_usd", "wall_s", "terminal_reason")},
           "pages": {u: {"screenshot": p["screenshot"], "forms": p.get("forms", [])} for u, p in run["pages"].items()},
           "verdicts": verdicts, "issues": {c: s["issues"] for c, s in sites.items()},
           "claims": claims, "counts": counts,
           "verdict": "FAIL" if "FAIL" in verdicts.values() else ("NOT CHECKED" if "NOT CHECKED" in verdicts.values() else "PASS")}
    (run_dir / "verify.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    return out

if __name__ == "__main__":
    run_dir = Path(sys.argv[1]).resolve()
    run, sites = verify(run_dir)
    verdicts = write_report(run_dir, run, sites)
    out = write_json(run_dir, run, sites, verdicts)
    for c, v in verdicts.items():
        print(f"VERDICT {c}: {v}" + "".join(f"\n   - {i['issue']}" for i in sites[c]["issues"]))
    k = out["counts"]
    print(f"TOTALS findings {k['FINDINGS']} · accepted {k['ACCEPTED']} · rejected {k['REJECTED']} · "
          f"not checked {k['NOT_CHECKED']} · verifier issues {k['ISSUES']} -> {run_dir.name}/verify.json")
    sys.exit(0 if out["verdict"] == "PASS" else 1)
