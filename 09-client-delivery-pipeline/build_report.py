#!/usr/bin/env python3
"""build_report.py: the client report, built from the checker's results file and nothing else (Episode 9).

  reads:    runs/<run>/verify.json          (nothing else: no model, no run.json, no summary)
  headline: ACCEPTED n · REJECTED n · NOT CHECKED n
  rule:     NOT CHECKED is never PASS
  rule:     every row = check · result · page URL · quoted text · screenshot
  rule:     exit 1 if "passed" appears where counts disagree

Usage:
  python build_report.py runs/sufi-winter [--out jobs/sufi-winter/report.md]   build the report
  python build_report.py runs/sufi-winter --check <file>                       test any text (a summary, an edited report)
  python build_report.py runs/sufi-winter --notes <file>                       add a human note, then the same check
"""
import argparse, json, re, sys
from pathlib import Path

PASS_WORDS = re.compile(r"(?i)\b(all (?:the )?(?:checks|tests) (?:have )?passed|passed|all clear|no (?:issues|problems) (?:were )?found|everything (?:is )?correct)\b")


def clean(v):
    """True only when the checker itself says there is nothing to disclose."""
    k = v["counts"]
    return v["verdict"] == "PASS" and k["REJECTED"] == 0 and k["NOT_CHECKED"] == 0 and k["ISSUES"] == 0


def headline(v):
    k = v["counts"]
    return f"ACCEPTED {k['ACCEPTED']} · REJECTED {k['REJECTED']} · NOT CHECKED {k['NOT_CHECKED']}"


def false_pass(text, v):
    """Lines that say 'passed' (or similar) while the counts disagree."""
    if clean(v):
        return []
    return [l.strip() for l in text.splitlines() if PASS_WORDS.search(l)]


def build(v):
    k = v["counts"]
    cell = lambda s: (s or "").replace("|", "/").replace("\n", " ").strip()
    out = [f"# Client report: {v['run']}", "",
           f"**{headline(v)}**  ", f"Checker verdict: **{v['verdict']}** · verifier issues: {k['ISSUES']} · findings filed: {k['FINDINGS']}  ",
           "Source: `verify.json` from verify.py (plain Python, no model). NOT CHECKED never counts as a pass.", "",
           "## Built", ""]
    for url, p in v["pages"].items():
        forms = "; ".join(f"form {f['method']} → {f['action']}" for f in p.get("forms") or [])
        out.append(f"- {url} · screenshot `{p['screenshot']}`" + (f" · {forms}" if forms else ""))
    out += ["", "## Checked", "", "| Check | Result | Page | Quoted text | Screenshot |", "| --- | --- | --- | --- | --- |"]
    for c in v["claims"]:
        res = c["result"].replace("_", " ")
        out.append(f"| {cell(c['check'])} (model: {c['model_status']}) | {res} | {cell(c['evidence_url']) or '-'} | "
                   f"\"{cell(c['seen_text'])[:90]}\" | {cell(c['screenshot']) or '-'} |")
    out += ["", "## Needs a human look", ""]
    human = []
    for cl, issues in v["issues"].items():
        for i in issues:
            human.append(f"- CHECKER ISSUE ({cl}): {i['issue']} · page {i['url']} · screenshot `{i['screenshot']}`")
    for c in v["claims"]:
        if c["result"] != "ACCEPTED":
            human.append(f"- {c['result'].replace('_', ' ')}: {c['check']}: {c['verifier']} · quoted \"{cell(c['seen_text'])[:90]}\" · page {c['evidence_url'] or '-'}")
    out += human or ["- Nothing. Every finding was accepted by the checker."]
    out += ["", "## Approval", "",
            "Approved by (owner, not the builder): ____ · role: ____ · report version (commit): ____ · recorded: ____  ",
            "The approver opened the page themselves, every line above has evidence, and every human-look item is fixed or told to the client.",
            "A recorded approval in `jobs/<job>/gates.md` row 4. Not a legal signature."]
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--out")
    ap.add_argument("--check", help="check an existing text against verify.json; exit 1 on a false 'passed'")
    ap.add_argument("--notes", help="append this text to the report, then check")
    a = ap.parse_args()
    vf = Path(a.run) / "verify.json"
    if not vf.exists():
        print(f"FAILED: {vf} not found. The report is built from the checker's results only.")
        return 2
    v = json.loads(vf.read_text(encoding="utf-8"))
    if a.check:
        bad = false_pass(Path(a.check).read_text(encoding="utf-8"), v)
        print(f"checker: {headline(v)} · verdict {v['verdict']}")
        if bad:
            print(f"FAILED: \"passed\" where the counts disagree ({len(bad)} line(s)):")
            for b in bad:
                print(f"  > {b}")
            return 1
        print("OK: no pass wording the counts do not support")
        return 0
    text = build(v)
    if a.notes:
        text += "\n## Notes\n\n" + Path(a.notes).read_text(encoding="utf-8").strip() + "\n"
    bad = false_pass(text, v)
    out = Path(a.out) if a.out else Path(a.run) / "report.md"
    if bad:
        print(f"FAILED: \"passed\" where the counts disagree, report NOT written:")
        for b in bad:
            print(f"  > {b}")
        return 1
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"{headline(v)} · verdict {v['verdict']} -> {out.as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
