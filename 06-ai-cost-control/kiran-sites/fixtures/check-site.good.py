#!/usr/bin/env python3
"""Job checker for the monthly site refresh (mechanical checks only).

Usage: python check-site.py <client>

Checks: opening hours match data/<client>.json, only the placeholder phone,
no email, viewport meta, and the "Prices checked: <updated>" line.
Price VALUES are deliberately not checked here: deciding whether a price on
the page is right is the critic's job (it compares the page to the data file).
Every call is appended to check-calls.log (one line per call).
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PLACEHOLDER = "+92 300 0000000"


def section(html, sid):
    m = re.search(r'<section id="%s">(.*?)</section>' % sid, html, re.S)
    return m.group(1) if m else ""


def items(block):
    return [re.sub(r"<[^>]+>", "", li).strip() for li in re.findall(r"<li>(.*?)</li>", block, re.S)]


def main():
    if len(sys.argv) != 2:
        print("usage: python check-site.py <client>")
        return 2
    client = sys.argv[1]
    page = ROOT / "sites" / client / "index.html"
    data_f = ROOT / "data" / (client + ".json")
    if not page.exists() or not data_f.exists():
        print("FAIL setup: missing sites/%s/index.html or data/%s.json" % (client, client))
        return 1
    html = page.read_text(encoding="utf-8")
    data = json.loads(data_f.read_text(encoding="utf-8"))
    res = []
    hours = dict(i.split(": ", 1) for i in items(section(html, "hours")) if ": " in i)
    res.append(("hours", hours == data["hours"], "match" if hours == data["hours"] else "page %s vs data %s" % (hours, data["hours"])))
    want = re.sub(r"\D", "", PLACEHOLDER)
    found = re.findall(r"(?:\+|wa\.me/|tel:)\s*(\d[\d \-]{8,14}\d)", html) + re.findall(r"\b0\d{3}[ -]?\d{7}\b", html)
    bad = [f for f in found if re.sub(r"\D", "", f) != want]
    res.append(("phone", bool(found) and not bad, "only placeholder" if found and not bad else "found %s" % (bad or "no phone")))
    emails = re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", html)
    res.append(("no email", not emails, "none" if not emails else "found %d" % len(emails)))
    vp = bool(re.search(r'<meta name="viewport"', html))
    res.append(("viewport meta", vp, "present" if vp else "missing"))
    text = re.sub(r"<[^>]+>", " ", section(html, "prices"))
    m = re.search(r"Prices checked: (\S+)", text)
    ok = bool(m) and m.group(1) == data["updated"]
    res.append(("prices checked line", ok, "Prices checked: %s" % data["updated"] if ok else
                "price section needs 'Prices checked: %s' (found %s)" % (data["updated"], m.group(1) if m else "none")))
    failed = sum(0 if ok else 1 for _, ok, _ in res)
    for name, ok, det in res:
        print("%s %s: %s" % ("PASS" if ok else "FAIL", name, det))
    verdict = "PASS" if not failed else "FAIL"
    print("%s %s (%d/%d checks passed)" % (client, verdict, len(res) - failed, len(res)))
    with open(ROOT / "check-calls.log", "a", encoding="utf-8") as f:
        f.write("%s %s\n" % (client, verdict))
    return 0 if not failed else 1


sys.exit(main())
