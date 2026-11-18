#!/usr/bin/env python3
"""cost_report.py - per-job cost report + full-cost-of-delivery pricing floor sheet (Episode 6, AI Cost Kit).

Reads the records run_job.py saved (runs/<run>.json = the Claude Code result, runs/<run>.meta.json =
runner facts) and writes:
  report/cost_report.md          per-run table, min-max per setup, cost per client per month, source footer
  report/cost_report.csv         same per-run rows, for a spreadsheet
  report/pricing-floor.md/.csv   full cost of delivery worksheet
  report/pricing-worksheet.xlsx  same worksheet, colour-coded (green measured, blue owner, yellow assumption)

Honesty rules built in:
  - a client with no runs prints NOT MEASURED (never 0)
  - no average without the range beside it
  - every dollar figure is labelled: on a subscription login it is a LOCAL ESTIMATE AT API LIST PRICE,
    NOT A BILL; with an API key it is still a client-side estimate, the Console invoice is the bill
  - the pricing sheet fills ONLY measured cells; owner and assumption cells stay empty

Usage: python cost_report.py runs/ --out report/cost_report.md [--floor-setup C]
"""
import argparse, csv, json, zipfile
from collections import defaultdict
from pathlib import Path
from xml.sax.saxutils import escape

CLIENTS = {  # client slug -> (display name, how often this job runs per month)
    "mehr-bakery": ("Mehr Bakery", 1),
    "sufi-threads": ("Sufi Threads", 1),
    "noor-dental": ("Noor Dental Clinic", 1),
}
SETUP_ORDER = ["A", "AT", "C", "D", "STUCK"]


def load(runs_dir):
    rows = []
    for meta_f in sorted(Path(runs_dir).glob("*.meta.json")):
        meta = json.loads(meta_f.read_text(encoding="utf-8"))
        res_f = meta_f.with_name(meta_f.name.replace(".meta.json", ".json"))
        res = json.loads(res_f.read_text(encoding="utf-8")) if res_f.exists() else {}
        mu = res.get("modelUsage") or {}
        rows.append({
            "run": meta["run_id"], "client": meta["client"], "job": meta["job"], "setup": meta["setup"],
            "setup_label": meta.get("setup_label", ""),
            "cost": res.get("total_cost_usd"),
            "wall_s": meta.get("wall_seconds"), "duration_ms": res.get("duration_ms"),
            "num_turns": res.get("num_turns"),
            "per_model": {k: v.get("costUSD") for k, v in mu.items()},
            "tokens": {k: {"in": v.get("inputTokens", 0), "out": v.get("outputTokens", 0),
                           "cache_read": v.get("cacheReadInputTokens", 0),
                           "cache_write": v.get("cacheCreationInputTokens", 0)} for k, v in mu.items()},
            "cost_basis": sorted({v.get("costBasis") for v in mu.values() if v.get("costBasis")}),
            "verdict": meta.get("critic_verdict") or "-",
            "checker_calls": meta.get("checker_calls"),
            "status": meta.get("status"), "subtype": res.get("subtype"),
            "errors": res.get("errors"),
            "cap": (meta.get("caps") or {}).get("max_budget_usd"),
            "credential": (meta.get("preflight") or {}).get("credential", "?"),
            "version": (meta.get("preflight") or {}).get("claude_code_version", "?"),
        })
    return rows


def money(x):
    if x is None:
        return "unknown"
    return "$%.4f" % x if x < 1 else "$%.2f" % x


def rng(vals, fmt):
    vals = [v for v in vals if v is not None]
    if not vals:
        return "NOT MEASURED"
    lo, hi = min(vals), max(vals)
    return fmt(lo) if lo == hi else "%s - %s" % (fmt(lo), fmt(hi))


def basis_line(rows):
    creds = {r["credential"] for r in rows}
    if creds == {"api-key"}:
        return ("API key in its own workspace. Figures are Claude Code's client-side estimates at API list price; "
                "the Console invoice is the bill.")
    return ("**LOCAL ESTIMATE AT API LIST PRICE - NOT A BILL.** These runs used a subscription login: Claude Code "
            "computes the dollar figure on this machine from token counts at list price. It is not what you were "
            "charged. For cost-per-job numbers you can show a client, re-run with an API key in its own workspace.")


def report(rows, floor_setup):
    out = []
    by_setup = defaultdict(list)
    for r in rows:
        by_setup[r["setup"]].append(r)
    setups = sorted(by_setup, key=lambda s: SETUP_ORDER.index(s) if s in SETUP_ORDER else 99)
    out.append("# Kiran Studio · job cost report")
    out.append("")
    out.append("Job: **monthly site refresh** · fictional agency and clients, synthetic data.")
    out.append("")
    out.append("> " + basis_line(rows))
    out.append("")
    out.append("## Runs")
    out.append("")
    out.append("| run | setup | cost (est.) | per model (est.) | wall time | turns | critic verdict | checker calls | status |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    for s in setups:
        for r in by_setup[s]:
            pm = " · ".join("%s %s" % (k.replace("claude-", ""), money(v)) for k, v in sorted(r["per_model"].items())) or "-"
            st = r["status"].upper() if r["status"] == "capped" else r["status"]
            if r["status"] == "capped" and r["errors"]:
                st += " (%s)" % "; ".join(r["errors"])
            out.append("| %s | %s | %s | %s | %ss | %s | %s | %s | %s |" % (
                r["run"], s, money(r["cost"]), pm, r["wall_s"], r["num_turns"], r["verdict"], r["checker_calls"], st))
    out.append("")
    out.append("`turns` = main-loop turns only. The workflow's four stage agents run in the background and do not")
    out.append("add turns, so a turn cap does not limit them; the dollar cap does (their spend is in the cost column).")
    out.append("")
    out.append("## Range per setup (no average without its range)")
    out.append("")
    out.append("| setup | what | runs | cost range (est.) | wall time range | planted wrong price caught |")
    out.append("|---|---|---|---|---|---|")
    for s in setups:
        rs = by_setup[s]
        ok = [r for r in rs if r["status"] in ("done", "capped")]
        caught = sum(1 for r in ok if r["verdict"] == "REJECTED")
        judged = sum(1 for r in ok if r["verdict"] in ("REJECTED", "APPROVED"))
        out.append("| %s | %s | %d | %s | %s | %s |" % (
            s, rs[0]["setup_label"], len(rs), rng([r["cost"] for r in rs], money),
            rng([r["wall_s"] for r in rs], lambda x: "%.0fs" % x),
            "rejected in %d of %d" % (caught, judged) if judged else "-"))
    out.append("")
    n_small = [s for s in setups if len(by_setup[s]) < 3]
    if n_small:
        out.append("Setups with fewer than 3 runs (%s): one run is a story, not a number. Treat as a single reading." % ", ".join(n_small))
        out.append("")
    out.append("## Cost per client per month (setup %s)" % floor_setup)
    out.append("")
    out.append("| client | job runs / month | AI run cost / month (est.) |")
    out.append("|---|---|---|")
    for slug, (name, per_month) in CLIENTS.items():
        rs = [r for r in by_setup.get(floor_setup, []) if r["client"] == slug and r["status"] == "done"]
        val = rng([r["cost"] * per_month for r in rs if r["cost"] is not None], money) if rs else "NOT MEASURED"
        out.append("| %s | %d | %s |" % (name, per_month, val))
    out.append("")
    vers = sorted({r["version"] for r in rows})
    out.append("---")
    out.append("Source: Claude Code %s · `claude -p --output-format stream-json` result records (`total_cost_usd`, "
               "`modelUsage[*].costUSD`, `num_turns`) · wall time measured by run_job.py · %d runs · cost basis: %s · "
               "%s" % (", ".join(vers), len(rows), ", ".join(sorted({b for r in rows for b in r["cost_basis"]})) or "?",
                       "subscription login: LOCAL ESTIMATE, NOT A BILL" if any(r["credential"] != "api-key" for r in rows)
                       else "API key: client-side estimate"))
    return "\n".join(out) + "\n"


FLOOR_ROWS = [
    # (group, line, how it is filled)
    ("MEASURED", "AI run cost per job (top of range, setup {setup})", "from cost_report.py"),
    ("MEASURED", "Human review time per job (minutes, stopwatch)", "stopwatch"),
    ("OWNER", "Human build time per job (minutes)", "your records"),
    ("OWNER", "Your hourly cost (PKR or USD per hour)", "your records"),
    ("OWNER", "Project management per job", "your records"),
    ("OWNER", "Hosting and integrations per job", "your records"),
    ("OWNER", "Support per job", "your records"),
    ("ASSUMPTION", "Failed-run and capped-run allowance", "your assumption"),
    ("ASSUMPTION", "Overhead share per job", "your assumption"),
    ("ASSUMPTION", "Margin", "your assumption"),
]


def floor_values(rows, floor_setup):
    rs = [r for r in rows if r["setup"] == floor_setup and r["status"] == "done" and r["cost"] is not None]
    top = max((r["cost"] for r in rs), default=None)
    return top, len(rs)


def floor_md(rows, floor_setup):
    top, n = floor_values(rows, floor_setup)
    o = ["# Pricing floor worksheet · full cost of delivery", "",
         "Cost is not price. The AI run cost is only the **AI run cost floor**. The job floor is the full cost of delivery.",
         "Green = measured · Blue = you enter from your own records · Yellow = assumption, labelled as one. No prices filled in.", "",
         "| colour | line | value | source |", "|---|---|---|---|"]
    colour = {"MEASURED": "GREEN / MEASURED", "OWNER": "BLUE / OWNER-ENTERED", "ASSUMPTION": "YELLOW / ASSUMPTION"}
    for g, line, src in FLOOR_ROWS:
        val = ""
        if line.startswith("AI run cost"):
            val = ("%s (est., %d run%s)" % (money(top), n, "" if n == 1 else "s")) if top is not None else "NOT MEASURED"
        if line.startswith("Human review"):
            val = "NOT MEASURED (time one review)"
        o.append("| %s | %s | %s | %s |" % (colour[g], line.format(setup=floor_setup), val, src))
    o += ["| - | AI run cost floor (not the job floor) | = AI run cost per job | - |",
          "| - | **FULL COST OF DELIVERY = FLOOR** | = AI run cost + (review + build minutes / 60 x hourly cost) + PM + hosting + support + allowance + overhead, then margin | - |",
          "", "Value check (no figures): hours the job took by hand x your rate = what it is worth. Price on the hours it saves, then check price >= full floor.",
          "", "> " + basis_line(rows)]
    return "\n".join(o) + "\n"


def col(n):
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def write_xlsx(path, rows, floor_setup):
    """Minimal stdlib .xlsx: one sheet, three fills, a SUM-style floor formula. No figures in owner/assumption cells."""
    top, n = floor_values(rows, floor_setup)
    fills = {"MEASURED": 2, "OWNER": 3, "ASSUMPTION": 4, None: 0, "HEAD": 5}
    data = [[("Kiran Studio pricing floor worksheet (fictional agency) - cost is not price", "HEAD")],
            [("Colour", "HEAD"), ("Line", "HEAD"), ("Value", "HEAD"), ("Source", "HEAD")]]
    for g, line, src in FLOOR_ROWS:
        v = None
        if line.startswith("AI run cost") and top is not None:
            v = round(top, 4)
        data.append([({"MEASURED": "GREEN measured", "OWNER": "BLUE owner-entered", "ASSUMPTION": "YELLOW assumption"}[g], g),
                     (line.format(setup=floor_setup), g), (v, g), (src, g)])
    r0 = 3  # first data row
    rr = {line.split(" (")[0]: r0 + i for i, (_, line, _) in enumerate(FLOOR_ROWS)}
    C = lambda name: "C%d" % rr[name]
    ai_floor = "=%s" % C("AI run cost per job")
    full = ("=(%s+(%s+%s)/60*%s+%s+%s+%s+%s+%s)*(1+%s)" % (
        C("AI run cost per job"), C("Human review time per job"), C("Human build time per job"), C("Your hourly cost"),
        C("Project management per job"), C("Hosting and integrations per job"), C("Support per job"),
        C("Failed-run and capped-run allowance"), C("Overhead share per job"), C("Margin")))
    data.append([("", None), ("AI run cost floor (not the job floor)", "HEAD"), (ai_floor, "HEAD"), ("", None)])
    data.append([("", None), ("FULL COST OF DELIVERY = FLOOR (margin: a fraction you choose)", "HEAD"), (full, "HEAD"), ("", None)])
    data.append([("Cost figure: " + ("LOCAL ESTIMATE AT API LIST PRICE, NOT A BILL (subscription login)"
                                     if any(r["credential"] != "api-key" for r in rows) else "API-key estimate; the invoice is the bill"), None)])
    data.append([("Value check: hours by hand x your rate = value. Price on hours saved; price >= full floor.", None)])
    xml_rows = []
    for i, row in enumerate(data, 1):
        cells = []
        for j, (v, g) in enumerate(row, 1):
            ref, s = "%s%d" % (col(j), i), fills[g]
            if v is None or v == "":
                cells.append('<c r="%s" s="%d"/>' % (ref, s))
            elif isinstance(v, (int, float)):
                cells.append('<c r="%s" s="%d"><v>%s</v></c>' % (ref, s, v))
            elif isinstance(v, str) and v.startswith("="):
                cells.append('<c r="%s" s="%d"><f>%s</f></c>' % (ref, s, escape(v[1:])))
            else:
                cells.append('<c r="%s" s="%d" t="inlineStr"><is><t>%s</t></is></c>' % (ref, s, escape(v)))
        xml_rows.append('<row r="%d">%s</row>' % (i, "".join(cells)))
    sheet = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
             '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
             '<cols><col min="1" max="1" width="22" customWidth="1"/><col min="2" max="2" width="62" customWidth="1"/>'
             '<col min="3" max="3" width="16" customWidth="1"/><col min="4" max="4" width="22" customWidth="1"/></cols>'
             '<sheetData>%s</sheetData></worksheet>') % "".join(xml_rows)
    fill = lambda rgb: '<fill><patternFill patternType="solid"><fgColor rgb="FF%s"/><bgColor indexed="64"/></patternFill></fill>' % rgb
    styles = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
              '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
              '<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><name val="Calibri"/></font></fonts>'
              '<fills count="6"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill>'
              + fill("C6EFCE") + fill("DDEBF7") + fill("FFF2CC") + fill("E7E6E6") + '</fills>'
              '<borders count="1"><border/></borders><cellStyleXfs count="1"><xf/></cellStyleXfs>'
              '<cellXfs count="6"><xf/><xf/>'
              '<xf fillId="2" applyFill="1"/><xf fillId="3" applyFill="1"/><xf fillId="4" applyFill="1"/>'
              '<xf fillId="5" fontId="1" applyFill="1" applyFont="1"/></cellXfs></styleSheet>')
    files = {
        "[Content_Types].xml": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/></Types>',
        "_rels/.rels": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>',
        "xl/workbook.xml": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Pricing floor" sheetId="1" r:id="rId1"/></sheets></workbook>',
        "xl/_rels/workbook.xml.rels": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>',
        "xl/worksheets/sheet1.xml": sheet,
        "xl/styles.xml": styles,
    }
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, body in files.items():
            z.writestr(name, body)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("runs", nargs="?", default="runs/")
    ap.add_argument("--out", default="report/cost_report.md")
    ap.add_argument("--floor-setup", default="C", help="setup whose top-of-range cost feeds the pricing floor")
    a = ap.parse_args()
    rows = load(a.runs)
    if not rows:
        raise SystemExit("no run records in %s" % a.runs)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    md = report(rows, a.floor_setup)
    out.write_text(md, encoding="utf-8")
    with open(out.with_suffix(".csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["run", "client", "setup", "total_cost_usd_estimate", "wall_seconds", "num_turns", "critic_verdict",
                    "checker_calls", "status", "result_subtype", "credential", "per_model_cost_usd"])
        for r in rows:
            w.writerow([r["run"], r["client"], r["setup"], r["cost"], r["wall_s"], r["num_turns"], r["verdict"],
                        r["checker_calls"], r["status"], r["subtype"], r["credential"], json.dumps(r["per_model"])])
    (out.parent / "pricing-floor.md").write_text(floor_md(rows, a.floor_setup), encoding="utf-8")
    top, n = floor_values(rows, a.floor_setup)
    with open(out.parent / "pricing-floor.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["colour", "line", "value", "source"])
        for g, line, src in FLOOR_ROWS:
            v = round(top, 4) if line.startswith("AI run cost") and top is not None else ""
            w.writerow([g, line.format(setup=a.floor_setup), v, src])
    write_xlsx(out.parent / "pricing-worksheet.xlsx", rows, a.floor_setup)
    print(md)
    print("wrote %s, %s, pricing-floor.md/.csv, pricing-worksheet.xlsx" % (out, out.with_suffix(".csv")))


if __name__ == "__main__":
    main()
