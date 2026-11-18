"""verify.py: plain Python. The model is the sensor, this file is the judge.
Usage: python verify.py runs/<run>   -> prints verdicts, writes runs/<run>/report.md"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "kiran-sites" / "data"
PHONE = "+92 300 0000000"
EVIDENCE = ["seen_text", "evidence_url", "screenshot"]
INJECTION = re.compile(r"(?i)\b(AI|assistant|LLM|bot)s?\b.{0,40}\b(testers?|mark|ignore|PASS)\b")

def norm(s):
    return re.sub(r"\s+", " ", s).strip()

def client_of(url):
    return next((c for c in truth if f"/{c}/" in url), None)

def recheck(client, seen):
    """Recompute PASS/FAIL from the quoted text alone. None = nothing checkable in the quote."""
    d, bad, checked = truth[client], [], False
    for p in d["prices"]:
        for m in re.finditer(r"(?<!\w)%s(?!\w)[\s\S]{0,40}?PKR\s*([\d,]+)" % re.escape(p["item"]), seen):
            checked = True
            if int(m.group(1).replace(",", "")) != p["pkr"]:
                bad.append(f"{p['item']}: page PKR {m.group(1)}, data PKR {p['pkr']}")
    for day, hrs in d["hours"].items():
        m = re.search(r"\b%s: (\S+)" % re.escape(day), seen)
        if m:
            checked = True
            if m.group(1) != hrs:
                bad.append(f"{day}: page {m.group(1)}, data {hrs}")
    for ph in re.findall(r"\+\d[\d ]{8,14}\d", seen):
        checked = True
        if ph != PHONE:
            bad.append(f"phone {ph} is not the placeholder")
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
        elif not (ROOT / f["screenshot"]).exists():
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

truth = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted(DATA.glob("*.json"))}

if __name__ == "__main__":
    run_dir = Path(sys.argv[1]).resolve()
    run, sites = verify(run_dir)
    for c, v in write_report(run_dir, run, sites).items():
        print(f"VERDICT {c}: {v}" + "".join(f"\n   - {i['issue']}" for i in sites[c]["issues"]))
