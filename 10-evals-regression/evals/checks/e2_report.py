"""Episode 2 client-report checks for ONE report (same rules as OUT-P2 tests/run-checks.py, the rendered Ep2 grader).
1 WINS: a section headed "Wins" with exactly 3 bullet lines.  2 NO EMAIL.  3 NUMBERS: site visits, leads, revenue appear
exactly; no other figure >= 10 that is not in the data file.  4 LENGTH: 150 words or fewer."""
import json, re


def digits_in(text):
    return {n.replace(",", "") for n in re.findall(r"\d[\d,]*\.?\d*", text)}


def check_report(rep, data_text):
    data = json.loads(data_text)
    res = {}
    m = re.search(r"(?im)^[#*\s]*wins[*:\s]*$([\s\S]*?)(?=^\s*#|^\s*\*\*[^\n]*\*\*\s*$|\Z)", rep)
    bullets = [l for l in (m.group(1).splitlines() if m else []) if re.match(r"\s*(-|\*|\d+\.)\s+\S", l)]
    res["wins=3"] = (len(bullets) == 3, f"{len(bullets)} bullets" if m else "no Wins section")
    em = re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", rep)
    res["no-email"] = (not em, "found address" if em else "ok")
    rep_d, data_d = digits_in(rep), digits_in(data_text)
    mt = data["metrics"]
    need = [mt["site_visits"], mt["leads"], mt["revenue_pkr"]]
    missing = [n for n in need if n and str(n) not in rep_d and f"{n:,}".replace(",", "") not in rep_d]
    extra = sorted(n for n in rep_d if n.replace(".", "").isdigit() and float(n) >= 10 and n not in data_d
                   and not re.fullmatch(r"20\d\d", n))
    res["numbers"] = (not missing and not extra, f"missing={missing} unknown={extra}")
    wc = len(rep.split())
    res["<=150 words"] = (wc <= 150, f"{wc} words")
    return all(v[0] for v in res.values()), res
