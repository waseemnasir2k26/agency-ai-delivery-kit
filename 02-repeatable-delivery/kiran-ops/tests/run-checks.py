#!/usr/bin/env python3
"""Deterministic grader. usage: run-checks.py <outdir>  (reads tests/caseN/input.txt + <outdir>/caseN.txt)"""
import json, re, sys, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
out = pathlib.Path(sys.argv[1]); fails_total = 0

def digits_in(text):
    return {n.replace(",", "") for n in re.findall(r"\d[\d,]*\.?\d*", text)}

for case in sorted((root / "tests").glob("case*")):
    slug = (case / "input.txt").read_text().strip()
    data_text = (root / "data" / f"{slug}.json").read_text()
    data = json.loads(data_text)
    f = out / f"{case.name}.txt"
    rep = f.read_text(encoding="utf-8") if f.exists() else ""
    res = {}
    # 1 wins section
    m = re.search(r"(?im)^[#*\s]*wins[*:\s]*$([\s\S]*?)(?=^\s*#|^\s*\*\*[^\n]*\*\*\s*$|\Z)", rep)
    bullets = [l for l in (m.group(1).splitlines() if m else []) if re.match(r"\s*(-|\*|\d+\.)\s+\S", l)]
    res["wins=3"] = (len(bullets) == 3, f"{len(bullets)} bullets" if m else "no Wins section")
    # 2 email
    em = re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", rep)
    res["no-email"] = (not em, "found address" if em else "ok")
    # 3 numbers
    rep_d = digits_in(rep); data_d = digits_in(data_text)
    mt = data["metrics"]
    need = [mt["site_visits"], mt["leads"], mt["revenue_pkr"]]
    missing = [n for n in need if n and str(n) not in rep_d and f"{n:,}".replace(",", "") not in rep_d]
    extra = sorted(n for n in rep_d if n.replace(".", "").isdigit() and float(n) >= 10 and n not in data_d and not re.fullmatch(r"20\d\d", n))
    res["numbers"] = (not missing and not extra, f"missing={missing} unknown={extra}")
    # 4 length
    wc = len(rep.split())
    res["<=150 words"] = (wc <= 150, f"{wc} words")
    ok = all(v[0] for v in res.values())
    fails_total += 0 if ok else 1
    print(f"{case.name} [{slug}]: {'PASS' if ok else 'FAIL'}")
    for k, (p, d) in res.items():
        print(f"   {'ok  ' if p else 'FAIL'} {k}: {d}")
print(f"RESULT: {3 - fails_total}/3 PASS")
sys.exit(1 if fails_total else 0)
