#!/usr/bin/env python3
"""offline_check.py - $0 self-test of the CEO Monday pack. No model, no Claude Code, no network beyond 127.0.0.1.

  python tools/offline_check.py

1. verify.py (the code judge) on the two sample sites, read straight from sitewatch/www (no browser, no agent):
   Mehr Bakery must FAIL on the planted price (order page PKR 1350, data PKR 1200); Sufi Threads must PASS.
2. e2_report.check_report: a report that follows the Episode 2 rules passes; one with an email address and an
   invented number fails.
3. mock_api.py: start the stand-in on a free local port, send one Messages request with tools, and get back the
   scripted tool call (this is what the forced tests in monday.py run against, so they cost $0).
Writes only into runs/offline-check/ (ignored by git). Exit 0 = all three passed.
"""
import html.parser
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "tools"))
from e2_report import check_report  # noqa: E402


class Text(html.parser.HTMLParser):
    BLOCK = {"p", "h1", "h2", "h3", "li", "footer", "div", "br", "tr", "section"}

    def __init__(self):
        super().__init__()
        self.out, self.skip = [], False

    def handle_starttag(self, tag, attrs):
        self.skip = tag in ("script", "style", "title")
        if tag in self.BLOCK:
            self.out.append("\n")

    def handle_endtag(self, tag):
        self.skip = False
        if tag in self.BLOCK:
            self.out.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.out.append(data)


def visible(path):
    t = Text()
    t.feed(path.read_text(encoding="utf-8"))
    return "\n".join(ln.strip() for ln in "".join(t.out).splitlines() if ln.strip())


def check_verify():
    run = HERE / "runs" / "offline-check"
    run.mkdir(parents=True, exist_ok=True)
    pages = {}
    for f in sorted((HERE / "sitewatch" / "www").glob("*/*.html")):
        url = f"http://localhost:8812/{f.parent.name}/{f.name}"
        pages[url] = {"text": visible(f), "screenshot": "none (offline check)", "forms": []}
    (run / "run.json").write_text(json.dumps({"model": "none (offline check)", "num_turns": 0, "total_cost_usd": 0.0,
                                              "wall_s": 0, "terminal_reason": "offline", "pages": pages, "findings": []},
                                             indent=1), encoding="utf-8")
    v = subprocess.run([sys.executable, "-X", "utf8", str(HERE / "sitewatch" / "verify.py"), str(run)],
                       cwd=str(HERE / "sitewatch"), capture_output=True, text=True, encoding="utf-8")
    vj = json.loads((run / "verify.json").read_text(encoding="utf-8"))
    mehr, sufi = vj["verdicts"].get("mehr-bakery"), vj["verdicts"].get("sufi-threads")
    planted = any("Fruit cake: page PKR 1350, data PKR 1200" in i["issue"] for i in vj["issues"].get("mehr-bakery", []))
    ok = mehr == "FAIL" and planted and sufi == "PASS" and v.returncode == 1
    return ok, f"verify.py: Mehr Bakery {mehr} (planted price found: {planted}) · Sufi Threads {sufi} · exit {v.returncode}"


def check_e2():
    data = (HERE / "data" / "mehr-bakery.json").read_text(encoding="utf-8")
    good = ("# Mehr Bakery weekly report\n\nSite visits 1840, leads 37, revenue PKR 486,500 from 112 orders\n\n## Wins\n"
            "- Gift box page: 21 orders in 3 days\n- 14 new reviews\n- 63 newsletter signups\n\n## Next\n- Photograph winter menu\n")
    bad = good.replace("63 newsletter signups", "77 signups, write to owner@mehrbakery.example")
    ok_good, _ = check_report(good, data)
    ok_bad, res_bad = check_report(bad, data)
    failed = sorted(k for k, v in res_bad.items() if not v[0])
    return ok_good and not ok_bad, f"e2_report: rule-following report passes={ok_good} · bad report fails on {failed}"


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def check_mock():
    port = free_port()
    tmp = Path(tempfile.mkdtemp(prefix="mock-"))
    plan = tmp / "plan.json"
    plan.write_text(json.dumps({"steps": [{"name": "Write", "input": {"file_path": "x.txt", "content": "FAKE"}}],
                                "final": "done"}), encoding="utf-8")
    env = dict(os.environ, MOCK_PORT=str(port), MOCK_PLAN=str(plan), MOCK_LOG=str(tmp / "requests.log"))
    p = subprocess.Popen([sys.executable, str(HERE / "tools" / "mock_api.py")], env=env,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        body = json.dumps({"model": "mock", "max_tokens": 10, "tools": [{"name": "Write"}],
                           "messages": [{"role": "user", "content": "hi"}]}).encode()
        out = None
        for _ in range(50):
            try:
                req = urllib.request.Request(f"http://127.0.0.1:{port}/v1/messages", data=body,
                                             headers={"content-type": "application/json"})
                out = json.loads(urllib.request.urlopen(req, timeout=1).read())
                break
            except Exception:
                time.sleep(0.1)
    finally:
        p.terminate()
        p.wait(5)
    blk = (out or {}).get("content", [{}])[0]
    ok = blk.get("type") == "tool_use" and blk.get("name") == "Write" and out.get("stop_reason") == "tool_use"
    return ok, f"mock_api: scripted reply = {blk.get('type')} {blk.get('name')} · stop {(out or {}).get('stop_reason')} · no model called"


def main():
    results = [check_verify(), check_e2(), check_mock()]
    for ok, line in results:
        print(("PASS  " if ok else "FAIL  ") + line)
    allok = all(ok for ok, _ in results)
    print("OFFLINE CHECK:", "PASS (3/3)" if allok else "FAIL")
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
