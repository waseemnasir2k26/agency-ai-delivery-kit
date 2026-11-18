#!/usr/bin/env python3
"""Deterministic site checker (Episode 4 file, extended for Episode 9: every page, winter block, no-row prices, offer).
Usage: python scripts/check-site.py <client> [--root <folder>]"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLACEHOLDER = "+92 300 0000000"
OFFER_WORDS = re.compile(r"(?i)\b(offer|discount|sale|% off|launch price)\b")


def section(html, sid):
    m = re.search(r'<section id="%s">(.*?)</section>' % sid, html, re.S)
    return m.group(1) if m else ""


def items(block):
    return [re.sub(r"<[^>]+>", "", li).strip() for li in re.findall(r"<li>(.*?)</li>", block, re.S)]


def price_rows(block):
    out = []
    for i in items(block):
        m = re.match(r"(.+?): PKR ([\d,]+)$", i)
        if m:
            out.append({"item": m.group(1), "pkr": int(m.group(2).replace(",", ""))})
    return out


def compare(page_rows, data_rows):
    diff = ["%s: page %s, data %s" % (d["item"], next((p["pkr"] for p in page_rows if p["item"] == d["item"]), "missing"), d["pkr"])
            for d in data_rows if d not in page_rows]
    extra = ["extra item %s" % p["item"] for p in page_rows if p["item"] not in [d["item"] for d in data_rows]]
    return diff + extra


def main():
    args = sys.argv[1:]
    root = ROOT
    if "--root" in args:
        i = args.index("--root"); root = Path(args[i + 1]).resolve(); del args[i:i + 2]
    if len(args) != 1:
        print("usage: check-site.py <client>"); return 1
    client = args[0]
    sdir, data_f = root / "sites" / client, root / "data" / (client + ".json")
    if not (sdir / "index.html").exists() or not data_f.exists():
        print("FAIL setup: missing sites/%s/index.html or data/%s.json" % (client, client)); return 1
    data = json.loads(data_f.read_text(encoding="utf-8"))
    pages = {p.name: p.read_text(encoding="utf-8") for p in sorted(sdir.glob("*.html"))}
    html = pages["index.html"]
    results = []

    hours = dict(i.split(": ", 1) for i in items(section(html, "hours")) if ": " in i)
    results.append(("hours", hours == data["hours"], "match" if hours == data["hours"] else "page %s vs data %s" % (hours, data["hours"])))

    bad = compare(price_rows(section(html, "prices")), data["prices"])
    results.append(("prices", not bad, "; ".join(bad) or "match"))

    winter = data.get("winter") or {}
    if "winter.html" in pages:
        bad = compare(price_rows(section(pages["winter.html"], "winter-prices")), winter.get("prices") or [])
        results.append(("winter prices", not bad, "; ".join(bad) or "match"))

    known = {r["pkr"] for r in data["prices"] + (winter.get("prices") or [])}
    norow = ["%s: PKR %s" % (n, a) for n, h in pages.items()
             for a in re.findall(r"PKR\s*([\d,]+)", re.sub(r"<[^>]+>", " ", h)) if int(a.replace(",", "")) not in known]
    results.append(("no-row prices", not norow, "every price has a data row" if not norow else "no data row: " + ", ".join(norow)))

    want = re.sub(r"\D", "", PLACEHOLDER)
    allh = "\n".join(pages.values())
    found = re.findall(r"(?:\+|wa\.me/|tel:)\s*(\d[\d \-]{8,14}\d)", allh) + re.findall(r"\b0\d{3}[ -]?\d{7}\b", allh)
    badp = [f for f in found if re.sub(r"\D", "", f) != want]
    results.append(("phone", bool(found) and not badp, "only placeholder" if found and not badp else "found %s" % (badp or "no phone")))

    emails = re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", allh)
    results.append(("no email", not emails, "none" if not emails else "found %d" % len(emails)))

    novp = [n for n, h in pages.items() if not re.search(r'<meta name="viewport"', h)]
    results.append(("viewport meta", not novp, "present" if not novp else "missing on " + ", ".join(novp)))

    pcs = [("index.html", section(html, "prices"), data["updated"])]
    if "winter.html" in pages:
        pcs.append(("winter.html", section(pages["winter.html"], "winter-prices"), winter.get("updated", "?")))
    pc_bad = []
    for n, block, want_d in pcs:
        m = re.search(r"Prices checked: (\S+)", re.sub(r"<[^>]+>", " ", block))
        if not m or m.group(1) != want_d:
            pc_bad.append("%s needs 'Prices checked: %s' (found %s)" % (n, want_d, m.group(1) if m else "none"))
    results.append(("prices checked", not pc_bad, "; ".join(pc_bad) or "present"))

    if data.get("offer", "absent") is None:
        offers = ["%s: %s" % (n, m.group(0)) for n, h in pages.items() for m in OFFER_WORDS.finditer(re.sub(r"<[^>]+>", " ", h))]
        results.append(("no offer (offer: null)", not offers, "none shown" if not offers else "page mentions " + ", ".join(offers)))

    failed = 0
    for name, ok, det in results:
        print("%s %s: %s" % ("PASS" if ok else "FAIL", name, det))
        failed += 0 if ok else 1
    print("%s %s (%d/%d checks passed)" % (client, "PASS" if not failed else "FAIL", len(results) - failed, len(results)))
    return 0 if not failed else 1


sys.exit(main())
