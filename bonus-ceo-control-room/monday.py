#!/usr/bin/env python3
"""monday.py - Kiran Studio's Monday control room (bonus episode: Claude Code for CEOs).

ONE command runs the week's maintenance for every client IN PARALLEL, using the systems built in Episodes 1-10,
then writes ONE plain-English digest for the owner. Nothing is sent, merged, published or changed in a client
system: every outward action is a DRAFT that waits for a person.

  python monday.py                 # the real run (live control-room view when stdout is a terminal)
  python monday.py --bare          # CONTROLLED TEST: stripped-down scripted mode -> the startup self-check must stop it
  python monday.py --plain         # log lines instead of the live view

Jobs (all at once, each with its own money cap, time cap and turn cap):
  report-<client> x3   Episode 2 client-report skill (kiran-core plugin), checked by the Episode 2 rules in code
  watch-<client>  x2   Episode 4/9 Site Watch agent (Agent SDK + real browser), judged by verify.py (code, no model)
  noor-bookings        Episode 5 read-only connector: tomorrow's bookings + reschedule DRAFTS; code checks no row changed
  canary               Episode 10 hook canary: the kit's secret-firewall must block a fake key (Write, Bash, PowerShell). $0
  kit-versions         Episode 7 release tags vs each client's pin (no model). $0
  cost                 Episode 6 cost report of this run's jobs against their caps (no model). $0, runs last
  digest               one page for the owner, written by a model from the job facts; every number is checked by code

Limits printed first: a cap for the whole run (money) and a wall clock. Startup self-check before any job:
the kit (kiran-core) must be loaded with its skills, else exit 3 PREFLIGHT FAILED (bare mode skips plugins).
Costs: subscription login -> every dollar figure is a LOCAL ESTIMATE AT API LIST PRICE, NOT A BILL.
Kiran Studio, its clients, bookings and sites are FICTIONAL; all data is synthetic.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import urllib.request
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Kit copy: every path is relative to this folder or set by an environment variable (no machine-specific paths).
#   KIRAN_DEPS   folder with the Episode 5 and Episode 9 parts the REAL run needs (default: ./deps):
#                deps/noor-booking-app/ (app.py, reset.py), deps/noor-bookings/server.py, deps/kiran-marketplace/ (git repo)
#   NOOR_PYTHON  Python for the Noor app + connector (default: this Python)
#   SDK_PYTHON   Python with claude-agent-sdk + playwright for Site Watch (default: this Python)
DEPS = Path(os.environ.get("KIRAN_DEPS", str(HERE / "deps"))).resolve()
sys.path.insert(0, str(HERE / "tools"))
from cc_env import cc_env  # noqa: E402
from e2_report import check_report  # noqa: E402

CLAUDE = shutil.which("claude") or "claude"
PY311 = os.environ.get("SDK_PYTHON", sys.executable)
NOOR_PY = Path(os.environ.get("NOOR_PYTHON", sys.executable))
NOOR_APP = DEPS / "noor-booking-app"
NOOR_SERVER = DEPS / "noor-bookings" / "server.py"
MARKET = DEPS / "kiran-marketplace"
HAIKU, SONNET = "claude-haiku-5-5", "claude-sonnet-5-5"     # full names, never the moving nicknames
NOOR_PORT, SITE_PORT, MOCK_PORTS = 8810, 8812, (8813, 8814)
BELOW_NORMAL = 0x00004000 if os.name == "nt" else 0
HOME = str(Path.home())
CLIENTS = json.loads((HERE / "clients.json").read_text(encoding="utf-8"))["clients"]
NAME = {c["slug"]: c["name"] for c in CLIENTS}


# ---------------------------------------------------------------- small helpers
def sanitize(text):
    for v in sorted({HOME, HOME.replace("\\", "/"), HOME.replace("\\", "\\\\"), HOME.lower(), HOME.replace("\\", "/").lower()},
                    key=len, reverse=True):
        text = text.replace(v, "<HOME>")
    text = re.sub(r"sk-ant-oat[\w-]+", "<oauth-token>", text)
    text = re.sub(r"[\w.+-]+@(?!\w+\.example\b)[\w-]+\.[A-Za-z][\w.]*", "<EMAIL>", text)
    return text


def write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(sanitize(text), encoding="utf-8")


def free_gb():
    if os.name != "nt":
        return 99.0
    import ctypes

    class MS(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong), ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong), ("a", ctypes.c_ulonglong), ("b", ctypes.c_ulonglong),
                    ("c", ctypes.c_ulonglong), ("d", ctypes.c_ulonglong), ("e", ctypes.c_ulonglong)]
    m = MS()
    m.dwLength = ctypes.sizeof(MS)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return m.ullAvailPhys / 1024 ** 3


def kill_tree(proc):
    if proc and proc.poll() is None:
        if os.name == "nt":
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(proc.pid)], capture_output=True)
        else:
            proc.kill()


def fmt_t(s):
    s = max(0, int(s))
    return f"{s // 60:02d}:{s % 60:02d}"


# ---------------------------------------------------------------- job model
class Job:
    def __init__(self, jid, title, lane, cap_usd, cap_s, model="no model", needs=()):
        self.id, self.title, self.lane = jid, title, lane
        self.cap_usd, self.cap_s, self.model, self.needs = cap_usd, cap_s, model, list(needs)
        self.status, self.t0, self.t1, self.cost = "QUEUED", None, None, 0.0
        self.last, self.result, self.decisions, self.risks, self.facts = "waiting", "", [], [], {}
        self.proc = None

    def elapsed(self):
        if not self.t0:
            return 0
        return (self.t1 or time.time()) - self.t0

    def summary(self):
        return {"id": self.id, "title": self.title, "status": self.status, "model": self.model,
                "cost_usd": round(self.cost, 4), "cap_usd": self.cap_usd, "time_s": round(self.elapsed(), 1), "cap_s": self.cap_s,
                "result": self.result, "needs_decision": self.decisions, "risks": self.risks, "facts": self.facts}


class Room:
    """Shared state: jobs, run limits, spend ledger, console log."""

    def __init__(self, a, rid):
        self.a, self.rid = a, rid
        self.dir = HERE / "runs" / rid
        self.dir.mkdir(parents=True, exist_ok=True)
        self.jobs, self.lock, self.t0 = [], threading.Lock(), time.time()
        self.log_lines, self.stop = [], threading.Event()
        self.digest_line, self.final = "", None

    def spent(self):
        return sum(j.cost for j in self.jobs)

    def reserved(self):
        return sum(j.cap_usd for j in self.jobs if j.status == "RUNNING")

    def log(self, msg):
        line = f"[{fmt_t(time.time() - self.t0)}] {msg}"
        with self.lock:
            self.log_lines.append(line)
            with (self.dir / "console.txt").open("a", encoding="utf-8") as f:
                f.write(sanitize(line) + "\n")
        if self.a.plain:
            print(line, flush=True)


# ---------------------------------------------------------------- headless Claude Code call (Episode 6/9 pattern)
def kit_problems(init):
    names = {p.get("name") for p in (init.get("plugins") or [])}
    probs = [] if "kiran-core" in names else ["kiran-core not in init.plugins"]
    cmds = set(init.get("slash_commands") or []) | set(init.get("skills") or [])
    if not any(c.startswith("kiran-core:") for c in cmds):
        probs.append("none of kiran-core's skills loaded (stripped-down mode?)")
    if init.get("plugin_errors"):
        probs.append("plugin_errors: " + json.dumps(init["plugin_errors"])[:200])
    return probs


def run_cc(job, room, prompt, *, cwd, model, tools, allowed, max_turns, extra=(), env_extra=None, mock_port=None, need_kit=True):
    cmd = [CLAUDE, "-p", prompt, "--output-format", "stream-json", "--verbose", "--model", model,
           "--permission-mode", "dontAsk", "--permission-prompts", "none", "--tools", ",".join(tools),
           "--allowedTools", ",".join(allowed), "--max-budget-usd", f"{max(job.cap_usd, 0.01):.2f}", "--max-turns", str(max_turns),
           "--setting-sources", "project,local", "--no-session-persistence", *extra]
    if "--mcp-config" not in extra:   # never pick up MCP servers from parent folders (the home folder has some)
        cmd += ["--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}']
    if room.a.bare:
        cmd.append("--bare")
    st = {"init": None, "result": None, "pre": None, "events": [], "lines": []}
    job.proc = subprocess.Popen(cmd, cwd=str(cwd), env=cc_env(env_extra, mock_port=mock_port), stdin=subprocess.DEVNULL,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace",
                                creationflags=BELOW_NORMAL)
    err = []
    threading.Thread(target=lambda: err.extend(job.proc.stderr), daemon=True).start()

    def pump():
        for line in job.proc.stdout:
            st["lines"].append(line)
            try:
                ev = json.loads(line)
            except Exception:
                continue
            st["events"].append(ev)
            if ev.get("type") == "system" and ev.get("subtype") == "init" and st["init"] is None:
                st["init"] = ev
                if need_kit:
                    p = kit_problems(ev)
                    if p:
                        st["pre"] = p
                        kill_tree(job.proc)
                        return
                    job.last = "kit loaded: kiran-core + hooks"
            msg = ev.get("message") if isinstance(ev.get("message"), dict) else {}
            for c in (msg.get("content") if isinstance(msg.get("content"), list) else []):
                if isinstance(c, dict) and c.get("type") == "tool_use":
                    inp = c.get("input") or {}
                    nm = c.get("name", "").split("__")[-1]
                    arg = inp.get("skill") or inp.get("command") or inp.get("booking_id") or                         (Path(inp["file_path"]).name if inp.get("file_path") else "")
                    job.last = sanitize(f"{nm} {arg}".strip())[:60]
                    room.log(f"{job.id}: {job.last}")
            if ev.get("type") == "result":
                st["result"] = ev
    th = threading.Thread(target=pump, daemon=True)
    th.start()
    th.join(job.cap_s)
    timed_out = th.is_alive()
    if timed_out:
        kill_tree(job.proc)
        th.join(5)
    try:
        job.proc.wait(10)
    except Exception:
        kill_tree(job.proc)
    res = st["result"] or {}
    job.cost = float(res.get("total_cost_usd") or 0)
    write(room.dir / "streams" / f"{job.id}.stream.jsonl", "".join(st["lines"]))
    if err:
        write(room.dir / "streams" / f"{job.id}.stderr.txt", "".join(err)[-4000:])
    st["timed_out"] = timed_out
    st["subtype"] = res.get("subtype")
    st["models"] = sorted((res.get("modelUsage") or {}).keys())
    return st


def cc_status(job, st):
    if st["pre"]:
        return "BLOCKED", "kit not loaded: " + "; ".join(st["pre"])
    if st["timed_out"]:
        return "TIME CAP", f"stopped at its time cap ({job.cap_s} s)"
    if st["subtype"] == "error_max_budget_usd":
        return "MONEY CAP", f"stopped at its money cap (${job.cap_usd:.2f})"
    if st["subtype"] == "error_max_turns":
        return "TURN CAP", "stopped at its turn cap"
    if not st["result"] or st["result"].get("is_error"):
        return "FAILED", f"run error ({st['subtype']})"
    return "OK", ""


def tool_results(events):
    calls, res = {}, []
    for ev in events:
        msg = ev.get("message") if isinstance(ev.get("message"), dict) else {}
        for c in (msg.get("content") if isinstance(msg.get("content"), list) else []):
            if not isinstance(c, dict):
                continue
            if c.get("type") == "tool_use":
                calls[c.get("id")] = (c.get("name"), c.get("input"))
            elif c.get("type") == "tool_result":
                body = c.get("content")
                if isinstance(body, list):
                    body = " ".join(x.get("text", "") for x in body if isinstance(x, dict))
                nm, inp = calls.get(c.get("tool_use_id"), ("?", {}))
                res.append({"tool": nm, "input": inp, "text": str(body), "is_error": bool(c.get("is_error"))})
    return res


# ---------------------------------------------------------------- jobs
def job_report(job, room, slug):
    st = run_cc(job, room, f"/kiran-core:client-report {slug}", cwd=HERE, model=HAIKU, tools=["Skill", "Read", "Bash", "PowerShell"],
                allowed=["Skill(kiran-core:client-report)", "Bash(cat data/*)", "PowerShell(cat data/*)"], max_turns=6)
    s, why = cc_status(job, st)
    if s != "OK":
        job.status, job.result = s, why
        job.risks.append(f"{NAME[slug]} weekly report did not finish: {why}")
        return
    text = st["result"].get("result") or ""
    write(room.dir / "reports" / f"{slug}.md", text)
    ok, res = check_report(text, (HERE / "data" / f"{slug}.json").read_text(encoding="utf-8"))
    passed = sum(1 for v in res.values() if v[0])
    job.facts = {"client": NAME[slug], "checks_passed": passed, "checks_total": len(res), "model_answered": st["models"],
                 "pinned_model_answered": HAIKU in st["models"], "draft": f"runs/{room.rid}/reports/{slug}.md"}
    if ok:
        job.status, job.result = "DRAFT READY", f"report drafted · Episode 2 checks {passed}/{len(res)} passed"
        job.decisions.append(f"Approve and send the {NAME[slug]} weekly report (draft, not sent)")
    else:
        job.status, job.result = "CHECK FAILED", f"report drafted but checks {passed}/{len(res)}: " + \
            "; ".join(k for k, v in res.items() if not v[0])
        job.risks.append(f"{NAME[slug]} report failed a check and was held back")
    if HAIKU not in st["models"]:
        job.risks.append(f"{NAME[slug]} report: the pinned model did not answer ({st['models']})")


def job_watch(job, room, slug):
    run = f"{room.rid}/watch-{slug}"
    cmd = [PY311, "-X", "utf8", str(HERE / "sitewatch" / "site_watch.py"), "--run", run, "--client", slug, "--model", HAIKU,
           "--max-turns", "30", "--budget", f"{job.cap_usd:.2f}", "--port", str(SITE_PORT)]
    job.proc = subprocess.Popen(cmd, cwd=str(HERE / "sitewatch"), env=cc_env(), stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace", creationflags=BELOW_NORMAL)
    out = []

    def pump():
        for line in job.proc.stdout:
            out.append(line)
            m = re.match(r"-> (\w+)\((.*)", line.strip())
            if m:
                arg = re.sub(r'.*"(?:url|label|check)": "([^"]*)".*', r"\1", m.group(2))
                arg = arg.replace(f"http://localhost:{SITE_PORT}", "")
                job.last = f"{m.group(1)} {arg}"[:60]
                room.log(f"{job.id}: {job.last}")
    th = threading.Thread(target=pump, daemon=True)
    th.start()
    th.join(job.cap_s)
    timed_out = th.is_alive()
    if timed_out:
        kill_tree(job.proc)
    write(room.dir / "streams" / f"{job.id}.console.txt", "".join(out))
    rj = HERE / "runs" / run / "run.json"
    if timed_out or not rj.exists():
        job.status, job.result = ("TIME CAP" if timed_out else "FAILED"), "Site Watch did not finish"
        job.risks.append(f"{NAME[slug]} site was not checked this week")
        return
    r = json.loads(rj.read_text(encoding="utf-8"))
    job.cost = float(r.get("total_cost_usd") or 0)
    job.last = "verify.py (code) re-checks every finding"
    v = subprocess.run([sys.executable, "-X", "utf8", str(HERE / "sitewatch" / "verify.py"), str(HERE / "runs" / run), slug],
                       cwd=str(HERE / "sitewatch"), capture_output=True, text=True, encoding="utf-8", errors="replace")
    write(room.dir / "streams" / f"{job.id}.verify.txt", v.stdout + v.stderr)
    vj = json.loads((HERE / "runs" / run / "verify.json").read_text(encoding="utf-8"))
    issues = vj["issues"].get(slug, [])
    pages = sum(1 for u in vj["pages"] if f"/{slug}/" in u)
    job.facts = {"client": NAME[slug], "pages_opened": pages, "verdict": vj["verdicts"].get(slug), "issues": [i["issue"] for i in issues],
                 "agent_stop": r.get("terminal_reason"), "report": f"runs/{run}/report.md"}
    if r.get("subtype") == "error_max_budget_usd":
        job.status, job.result = "MONEY CAP", f"stopped at its money cap; verify.py: {vj['verdicts'].get(slug)}"
    elif vj["verdicts"].get(slug) == "PASS":
        job.status, job.result = "PASS", f"{pages} pages opened · verify.py: PASS"
    elif vj["verdicts"].get(slug) == "FAIL":
        job.status = "NEEDS YOU"
        job.result = f"{pages} pages · verify.py: FAIL · " + (issues[0]["issue"] if issues else "")
        for i in issues:
            job.decisions.append(f"{NAME[slug]} website: {i['issue']} on {i['url'].replace(f'http://localhost:{SITE_PORT}', '')}. "
                                 "Decide which price is right; the agent does not change the site")
    else:
        job.status, job.result = "NOT CHECKED", "verify.py: nothing checkable"
        job.risks.append(f"{NAME[slug]} site: nothing machine-checkable this week")


def noor_rows():
    env = dict(os.environ, NOOR_DB_PATH=str(HERE / "noor" / "bookings.db"))
    out = subprocess.run([str(NOOR_PY), "-c", "import sqlite3,json,sys; c=sqlite3.connect(sys.argv[1]); "
                          "print(json.dumps(c.execute('select * from bookings order by id').fetchall()))", str(HERE / "noor" / "bookings.db")],
                         capture_output=True, text=True, env=env)
    return json.loads(out.stdout or "[]")


def job_noor(job, room):
    tools4 = ["list_tomorrow_bookings", "find_available_slots", "get_booking_summary", "draft_reschedule"]
    before = noor_rows()
    mcp = {"mcpServers": {"noor-bookings": {"type": "stdio", "command": str(NOOR_PY), "args": [str(NOOR_SERVER)],
                                            "env": {"NOOR_API_TOKEN": "${NOOR_API_TOKEN}", "NOOR_API_URL": f"http://127.0.0.1:{NOOR_PORT}"}}}}
    prompt = ("Monday check for Noor Dental Clinic (fictional clinic, synthetic data). Use only the noor-bookings tools. "
              "1) List tomorrow's bookings. 2) For each UNCONFIRMED booking, find a free slot tomorrow with the same dentist and call "
              "draft_reschedule for it (use each free slot at most once; skip a booking if no slot is left). "
              "3) Reply in under 80 words: bookings tomorrow, how many are unconfirmed, and one line per draft (booking id, old time, new time). "
              "These are drafts: nothing is sent or changed. The receptionist approves each one.")
    st = run_cc(job, room, prompt, cwd=HERE, model=HAIKU, tools=["Read"], allowed=[f"mcp__noor-bookings__{t}" for t in tools4], max_turns=24,
                extra=["--strict-mcp-config", "--mcp-config", json.dumps(mcp)], env_extra={"NOOR_API_TOKEN": "noor_test_FAKE_0000"})
    after = noor_rows()
    s, why = cc_status(job, st)
    tr = tool_results(st["events"])
    drafts = [t for t in tr if t["tool"].endswith("draft_reschedule") and '"DRAFT"' in t["text"]]
    unconf = None
    for t in tr:
        if t["tool"].endswith("list_tomorrow_bookings") and not t["is_error"]:
            try:
                d = json.loads(t["text"])
                rows = d.get("bookings") or []
                unconf = sum(1 for b in rows if b.get("status") == "unconfirmed")
                job.facts["bookings_tomorrow"] = len(rows)
            except Exception:
                pass
    changed = sum(1 for x, y in zip(before, after) if x != y) + abs(len(before) - len(after))
    other = sorted({t["tool"] for t in tr if not t["tool"].startswith("mcp__noor-bookings__")})
    job.facts.update({"unconfirmed": unconf, "drafts": len(drafts), "booking_rows_changed": changed, "other_tools_called": other,
                      "summary": (st["result"] or {}).get("result", "")[:600]})
    write(room.dir / "noor" / "summary.md", (st["result"] or {}).get("result", ""))
    write(room.dir / "noor" / "drafts.json", json.dumps([json.loads(d["text"]) if d["text"].startswith("{") else d["text"] for d in drafts], indent=1))
    if changed:
        job.status, job.result = "FAILED", f"{changed} booking rows changed: a read-only job must change none"
        job.risks.append(f"Noor bookings: {changed} rows changed by a read-only job")
        return
    if s != "OK":
        job.status, job.result = s, why
        job.risks.append(f"Noor bookings summary did not finish: {why}")
        return
    job.status = "DRAFT READY"
    job.result = f"{job.facts.get('bookings_tomorrow')} bookings tomorrow · {unconf} unconfirmed · {len(drafts)} drafts · rows changed: 0"
    if drafts:
        job.decisions.append(f"Receptionist approves or edits {len(drafts)} reschedule drafts for Noor Dental Clinic (nothing sent)")


class Mock:
    def __init__(self, port, plan, logf):
        self.port = port
        plan_f = HERE / "runs" / f"mock-plan-{port}.json"
        plan_f.write_text(json.dumps(plan), encoding="utf-8")
        env = dict(os.environ, MOCK_PORT=str(port), MOCK_PLAN=str(plan_f), MOCK_LOG=str(logf))
        self.p = subprocess.Popen([sys.executable, str(HERE / "tools" / "mock_api.py")], env=env, stdout=subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL, creationflags=BELOW_NORMAL)
        for _ in range(50):
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=0.3)
                break
            except Exception as e:
                if getattr(e, "code", None):
                    break
                time.sleep(0.1)

    def stop(self):
        kill_tree(self.p)


FAKE = "sk-ant-api03-FAKEFAKEFAKEFAKEFAKEFAKE0000"


def job_canary(job, room):
    ws = room.dir / "canary-ws"
    (ws / ".claude").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(HERE / ".claude" / "settings.json", ws / ".claude" / "settings.json")
    plan = {"steps": [{"name": "Write", "input": {"file_path": str(ws / "canary.txt"), "content": f"ANTHROPIC_API_KEY={FAKE}"}},
                      {"name": "Bash", "input": {"command": f"echo {FAKE} > canary2.txt", "description": "canary"}},
                      {"name": "PowerShell", "input": {"command": f"Set-Content canary3.txt '{FAKE}'", "description": "canary"}}],
            "final": "canary finished"}
    m = Mock(MOCK_PORTS[1], plan, room.dir / "mock-canary.log")
    try:
        st = run_cc(job, room, "(canary)", cwd=ws, model=HAIKU, tools=["Write", "Bash", "PowerShell"],
                    allowed=["Write", "Bash", "PowerShell"], max_turns=6, mock_port=m.port)
    finally:
        m.stop()
    tr = tool_results(st["events"])
    blocked = [t for t in tr if t["is_error"] and "secret-firewall" in t["text"]]
    files = [f for f in ("canary.txt", "canary2.txt", "canary3.txt") if (ws / f).exists()]
    job.cost = 0.0
    job.facts = {"forced_test": True, "model_calls": 0, "blocked": len(blocked), "attempts": len(tr), "files_written": files,
                 "tools": [t["tool"] for t in tr]}
    if st["pre"]:
        job.status, job.result = "BLOCKED", "kit not loaded"
        job.risks.append("Regression canary: the kit did not load")
    elif len(blocked) == 3 and not files:
        job.status, job.result = "PASS", "secret-firewall blocked 3/3 (Write · Bash · PowerShell) · $0"
    else:
        job.status, job.result = "FAILED", f"secret-firewall blocked {len(blocked)}/3 · files written: {files or 'none'}"
        job.risks.append(f"Regression canary: the secret hook blocked only {len(blocked)} of 3 fake-key writes")


def git(*a):
    return subprocess.run(["git", "-C", str(MARKET), *a], capture_output=True, text=True, encoding="utf-8").stdout.strip()


def job_kit(job, room):
    tags = [t for t in git("tag", "--list", "kiran-core--v*").split() if t]
    ver = lambda t: tuple(int(x) for x in t.split("--v")[1].split("."))  # noqa: E731
    tags.sort(key=ver)
    latest = tags[-1]
    job.last = f"{len(tags)} kiran-core releases · latest {latest}"
    chk = subprocess.run([sys.executable, "-X", "utf8", "ci/check_kit.py"], cwd=str(MARKET), capture_output=True, text=True, encoding="utf-8")
    behind = [c for c in CLIENTS if c["kit"] != latest]
    lv = latest.split("--v")[1]
    log = (MARKET / "CHANGELOG.md").read_text(encoding="utf-8")
    sec = re.search(r"## kiran-core %s.*?\n(.*?)(?=\n## )" % re.escape(lv), log, re.S)
    what = [ln.strip("- ").split(":")[0] for ln in (sec.group(1).strip().splitlines() if sec else []) if ln.startswith("-")]
    job.facts = {"latest": lv, "releases": len(tags), "check_kit_exit": chk.returncode, "clients_behind": [c["name"] for c in behind],
                 "pins": {c["name"]: c["kit"].split("--v")[1] for c in CLIENTS}, "latest_adds": what}
    write(room.dir / "kit" / "check_kit.txt", chk.stdout + chk.stderr)
    job.status = "NEEDS YOU" if behind else "PASS"
    job.result = f"latest kiran-core {lv} · {len(behind)} of {len(CLIENTS)} clients behind · kit checks exit {chk.returncode}"
    if behind:
        job.decisions.append(f"Upgrade {' and '.join(c['name'] for c in behind)} to kiran-core {lv}, or wait. "
                             "Run the regression suite on the new version first")
    if chk.returncode:
        job.risks.append("kit release checks (check_kit.py) did not pass")


def job_cost(job, room):
    rows = [j for j in room.jobs if j.id not in ("cost", "digest")]
    near = [j for j in rows if j.cap_usd and j.cost >= 0.8 * j.cap_usd]
    capped = [j for j in rows if "CAP" in j.status]
    total = sum(j.cost for j in rows)
    lines = ["job,status,model,cost_usd,cap_usd,time_s,cap_s"] + [
        f"{j.id},{j.status},{j.model},{j.cost:.4f},{j.cap_usd:.2f},{j.elapsed():.0f},{j.cap_s}" for j in rows]
    write(room.dir / "cost" / "cost_report.csv", "\n".join(lines) + "\n")
    job.facts = {"jobs": len(rows), "total_usd": round(total, 4), "run_cap_usd": room.a.run_cap, "jobs_at_a_cap": [j.id for j in capped],
                 "jobs_over_80pct_of_cap": [j.id for j in near], "credential": "subscription login: local estimate at list price, not a bill",
                 "per_job": {j.id: round(j.cost, 4) for j in rows}}
    job.status = "PASS" if not capped else "NEEDS YOU"
    job.result = f"{len(rows)} jobs · ${total:.2f} of ${room.a.run_cap:.2f} cap · {len(capped)} hit a cap"
    if capped:
        job.risks.append(f"{len(capped)} jobs stopped at a cap: {', '.join(j.id for j in capped)}")


DIGEST_RULES = """You write the Monday digest for the owner of Kiran Studio, a fictional agency. Use ONLY the facts JSON below.
Plain English for a busy owner who reads it on a phone. Write exactly these four sections, with these headings:
## Done
## Needs your decision
## Risks
## Cost
Rules: 'Done' = short bullets, one per finished job. 'Needs your decision' = a numbered list, one line per item in
needs_decision, each starting with a verb, saying what happens if they say yes. 'Risks' = bullets from risks, or one bullet
saying none were found. 'Cost' = one or two lines from the cost facts; say it is an estimate, not a bill.
Never invent a number: every number you write must appear in the facts. No greeting, no sign-off, under 230 words.
Do not mention models, tokens or tools. Output the markdown only."""


def job_digest(job, room):
    facts = {"run": room.rid, "jobs": [j.summary() for j in room.jobs if j.id != "digest"]}
    write(room.dir / "facts.json", json.dumps(facts, indent=1, ensure_ascii=False))
    job.last = "reading the facts of every job"
    st = run_cc(job, room, DIGEST_RULES + "\n\nFACTS JSON:\n" + json.dumps(facts, ensure_ascii=False), cwd=HERE, model=SONNET,
                tools=["Read"], allowed=[], max_turns=2, need_kit=False)
    s, why = cc_status(job, st)
    if s != "OK":
        job.status, job.result = s, why
        return
    body = (st["result"].get("result") or "").strip()
    nums_facts = set(re.findall(r"\d+(?:\.\d+)?", json.dumps(facts)))
    nums_digest = set(re.findall(r"\d+(?:\.\d+)?", re.sub(r"(?m)^\s*\d+\.\s", "", body)))   # list numbers are not facts
    invented = sorted(n for n in nums_digest if n not in nums_facts and n.lstrip("0") not in nums_facts)
    heads = [h for h in ("## Done", "## Needs your decision", "## Risks", "## Cost") if h not in body]
    words = len(body.split())
    job.facts = {"words": words, "numbers_not_in_facts": invented, "missing_headings": heads}
    md = f"# Monday digest · Kiran Studio\n\n_Run `{room.rid}` · fictional agency and clients · nothing was sent_\n\n{body}\n"
    write(room.dir / "digest.md", md)
    job.status = "PASS" if not invented and not heads else "CHECK FAILED"
    job.result = f"1 page · {words} words · numbers checked by code: " + ("all in the facts" if not invented else f"{len(invented)} not in facts")
    render_html(room, md, facts)


def render_html(room, md, facts):
    import html as H
    esc = H.escape
    body = []
    for ln in md.splitlines():
        if ln.startswith("# "):
            continue
        if ln.startswith("## "):
            body.append(f"<h2>{esc(ln[3:])}</h2>")
        elif re.match(r"^\d+\.\s", ln):
            body.append(f'<p class="dec"><span class="box"></span>{esc(re.sub(r"^\d+\.\s", "", ln))}</p>')
        elif ln.startswith(("- ", "* ")):
            body.append(f"<p class='li'>{esc(ln[2:])}</p>")
        elif ln.strip():
            body.append(f"<p class='meta'>{esc(ln.strip('_'))}</p>")
    tiles = "".join(
        f'<div class="t {("ok" if j["status"] in ("PASS", "DRAFT READY") else "warn" if j["status"] == "NEEDS YOU" else "bad")}">'
        f'<b>{esc(j["title"])}</b><span>{esc(j["status"])}</span><i>{esc(j["result"])}</i></div>' for j in facts["jobs"])
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Monday digest</title><style>
:root{{--bg:#f6f1e9;--ink:#1d1a16;--rust:#b4532a;--green:#2f7d4f;--amber:#c98a12;--red:#b3261e;--mute:#6f675d;--card:#fff}}
body{{margin:0;background:var(--bg);color:var(--ink);font:17px/1.5 system-ui,Segoe UI,sans-serif}}
main{{max-width:860px;margin:0 auto;padding:28px 16px 60px}} h1{{font-size:34px;margin:0}} h2{{font-size:20px;margin:26px 0 8px;color:var(--rust)}}
.meta{{color:var(--mute);margin:4px 0 18px}} .li{{margin:4px 0;padding-left:16px;border-left:3px solid #e6dccd}}
.dec{{background:var(--card);border-radius:10px;padding:10px 14px;margin:8px 0;display:flex;gap:12px;box-shadow:0 2px 8px #0001}}
.box{{flex:none;width:18px;height:18px;border:2px solid var(--rust);border-radius:4px;margin-top:3px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:10px;margin-top:10px}}
.t{{background:var(--card);border-radius:10px;padding:10px 12px;border-top:4px solid var(--green)}} .t.warn{{border-color:var(--amber)}} .t.bad{{border-color:var(--red)}}
.t b{{display:block}} .t span{{font-size:13px;font-weight:700;color:var(--mute)}} .t i{{display:block;font-style:normal;font-size:14px;color:var(--mute)}}
footer{{margin-top:30px;color:var(--mute);font-size:13px}}
</style></head><body><main><h1>Monday digest · Kiran Studio</h1>{''.join(body)}
<h2>The jobs behind this page</h2><div class="grid">{tiles}</div>
<footer>Fictional agency, fictional clients, synthetic data. Dollar figures are local estimates at list price, not a bill. Every outward action is a draft that waits for a person.</footer>
</main></body></html>"""
    write(room.dir / "digest.html", page)


# ---------------------------------------------------------------- services (local, fictional)
def start_services(room):
    procs = []
    env = dict(os.environ, NOOR_DB_PATH=str(HERE / "noor" / "bookings.db"), NOOR_PORT=str(NOOR_PORT))
    subprocess.run([str(NOOR_PY), "reset.py"], cwd=str(NOOR_APP), env=env, capture_output=True)
    procs.append(subprocess.Popen([str(NOOR_PY), "app.py"], cwd=str(NOOR_APP), env=env, stdout=subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL, creationflags=BELOW_NORMAL))
    procs.append(subprocess.Popen([sys.executable, "-m", "http.server", str(SITE_PORT), "--bind", "127.0.0.1", "--directory",
                                   str(HERE / "sitewatch" / "www")], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=BELOW_NORMAL))
    for url in (f"http://127.0.0.1:{NOOR_PORT}/", f"http://127.0.0.1:{SITE_PORT}/mehr-bakery/"):
        for _ in range(60):
            try:
                urllib.request.urlopen(url, timeout=0.5)
                break
            except Exception as e:
                if getattr(e, "code", None):
                    break
                time.sleep(0.2)
    return procs


# ---------------------------------------------------------------- startup self-check
def preflight(room):
    """Before any job: the kit must be loaded. Uses the scripted stand-in model ($0): only the init event matters."""
    m = Mock(MOCK_PORTS[0], {"steps": [], "final": "preflight ok"}, room.dir / "mock-preflight.log")
    j = Job("preflight", "Startup self-check", "pre", 0.0, 60)
    try:
        st = run_cc(j, room, "(preflight)", cwd=HERE, model=HAIKU, tools=["Read"], allowed=[], max_turns=1, mock_port=m.port)
    finally:
        m.stop()
    init = st["init"] or {}
    probs = st["pre"] or ([] if st["init"] else ["no init event"])
    rec = {"plugins": [p.get("name") for p in init.get("plugins") or []],
           "kiran_core_skills": sorted(c for c in (init.get("slash_commands") or []) if c.startswith("kiran-core:")),
           "plugin_errors": init.get("plugin_errors"), "bare": room.a.bare, "problems": probs,
           "claude_code_version": init.get("claude_code_version"), "permissionMode": init.get("permissionMode")}
    write(room.dir / "preflight.json", json.dumps(rec, indent=1))
    return probs, rec


# ---------------------------------------------------------------- live control-room view
ESC = "\x1b["
COL = {"QUEUED": (140, 134, 124), "RUNNING": (232, 170, 60), "PASS": (92, 190, 120), "DRAFT READY": (92, 190, 120),
       "NEEDS YOU": (240, 150, 60), "WAITING": (140, 134, 124)}
RUST, INK, CREAM, MUTE, RED = (214, 104, 60), (24, 22, 20), (240, 232, 220), (150, 142, 130), (230, 80, 70)


def fg(c):
    return f"{ESC}38;2;{c[0]};{c[1]};{c[2]}m"


def bg(c):
    return f"{ESC}48;2;{c[0]};{c[1]};{c[2]}m"


RST = f"{ESC}0m"
SPIN = "|/-\\"   # renders in Consolas


def pad(s, w):
    s = s if len(s) <= w else s[: w - 1] + "…"
    return s + " " * (w - len(s))


def tile(j, w, tick):
    c = COL.get(j.status, RED)
    stat = j.status + (" " + SPIN[tick % len(SPIN)] if j.status == "RUNNING" else "")
    head = f" {j.title} "
    top = fg(MUTE) + "┌─" + fg(CREAM) + f"{ESC}1m" + head + RST + fg(MUTE) + "─" * max(1, w - 4 - len(head) - len(stat) - 2) + " " + \
        fg(c) + f"{ESC}1m" + stat + RST + fg(MUTE) + " ─┐" + RST
    cap = f"cap ${j.cap_usd:.2f} · {j.cap_s // 60} min" if j.cap_usd else f"$0 · {j.cap_s // 60 if j.cap_s >= 60 else j.cap_s} {'min' if j.cap_s >= 60 else 's'} cap"
    l1 = f"{j.model} · {cap}"
    l2 = f"time {fmt_t(j.elapsed())}   spent ${j.cost:.3f}"
    import textwrap
    if j.result:
        wr = textwrap.wrap(j.result, w - 4)[:2]
        if len(textwrap.wrap(j.result, w - 4)) > 2:
            wr[1] = wr[1][: w - 5] + "…"
        l3, l4 = (wr + [""])[:2]
        c3 = c
    else:
        l3, l4, c3 = "› " + j.last, "", (200, 190, 175)
    rows = []
    for txt, col in ((l1, MUTE), (l2, CREAM), (l3, c3), (l4, c)):
        rows.append(fg(MUTE) + "│ " + fg(col) + pad(txt, w - 4) + fg(MUTE) + " │" + RST)
    bot = fg(MUTE) + "└" + "─" * (w - 2) + "┘" + RST
    return [top] + rows + [bot]


def render(room, tick):
    W = min(shutil.get_terminal_size((160, 46)).columns, 200)
    w = (W - 2) // 3
    el = time.time() - room.t0
    badge = f" ● LIVE · REAL TIME · UNEDITED "
    clock = f" RUN CLOCK {fmt_t(el)}.{int((el % 1) * 10)} "
    title = " KIRAN STUDIO · MONDAY CONTROL ROOM"
    out = [ESC + "H"]
    gap = W - len(title) - len(badge) - len(clock) - 2
    out.append(f"{ESC}1m" + fg(CREAM) + title + RST + " " * max(1, gap) + bg(RED) + fg((255, 255, 255)) + f"{ESC}1m" + badge + RST + " " +
               bg((60, 56, 50)) + fg(CREAM) + clock + RST + ESC + "K")
    lim = (f" limits: whole run ${room.a.run_cap:.2f} (estimate at list price, not a bill) · wall clock {room.a.wall_min} min · "
           f"{len([j for j in room.jobs if j.id != 'digest'])} jobs in parallel · every outward action = a draft")
    out.append(fg(MUTE) + pad(lim, W) + RST + ESC + "K")
    out.append(ESC + "K")
    grid = [j for j in room.jobs if j.id != "digest"]
    for r in range(0, len(grid), 3):
        rowt = [tile(j, w, tick) for j in grid[r:r + 3]]
        for k in range(len(rowt[0])):
            out.append(" " + "".join(t[k] for t in rowt) + ESC + "K")
    out.append(ESC + "K")
    dj = next((j for j in room.jobs if j.id == "digest"), None)
    if dj:
        c = COL.get(dj.status, RED)
        st = dj.status + (" " + SPIN[tick % len(SPIN)] if dj.status == "RUNNING" else "")
        line = f" ONE DIGEST FOR THE OWNER  ·  " + (dj.result or ("waiting for the jobs" if dj.status == "QUEUED" else dj.last))
        out.append(" " + bg((44, 40, 36)) + fg(CREAM) + f"{ESC}1m" + pad(line, W - 22) + fg(c) + pad(st, 18) + " " + RST + ESC + "K")
    done = sum(1 for j in grid if j.status not in ("QUEUED", "RUNNING", "WAITING"))
    dec = sum(len(j.decisions) for j in grid)
    foot = f" jobs finished {done}/{len(grid)} · spent ${room.spent():.3f} of ${room.a.run_cap:.2f} · decisions waiting for a person: {dec}"
    out.append(fg(MUTE) + pad(foot, W) + RST + ESC + "K")
    if room.final:
        out.append(ESC + "K")
        for ln in room.final:
            out.append(" " + ln + ESC + "K")
    out.append(ESC + "J")
    sys.stdout.write("\n".join(out))
    sys.stdout.flush()


def tui_loop(room):
    tick = 0
    while not room.stop.is_set():
        render(room, tick)
        tick += 1
        time.sleep(0.12)
    render(room, tick)


# ---------------------------------------------------------------- orchestration
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run-cap", type=float, default=2.00, help="money cap for the whole run, USD (estimate at list price)")
    ap.add_argument("--wall-min", type=int, default=12, help="wall-clock cap for the whole run, minutes")
    ap.add_argument("--workers", type=int, default=5, help="jobs running at the same time")
    ap.add_argument("--min-free-gb", type=float, default=1.2, help="wait to start a job while free RAM is below this")
    ap.add_argument("--bare", action="store_true", help="CONTROLLED TEST: pass --bare to every Claude Code call")
    ap.add_argument("--plain", action="store_true", help="log lines instead of the live view")
    ap.add_argument("--only", nargs="*", help="dev: run only these job ids")
    a = ap.parse_args()
    a.plain = a.plain or not sys.stdout.isatty()
    rid = datetime.now().strftime("%Y%m%d-%H%M%S") + ("-bare" if a.bare else "")
    room = Room(a, rid)
    if os.name == "nt":
        os.system("")  # enable VT sequences in the console

    # 1) limits first
    room.log(f"LIMITS · whole run ${a.run_cap:.2f} (estimate at list price, not a bill) · wall clock {a.wall_min} min")
    # 2) startup self-check (no jobs before it passes)
    room.log("STARTUP SELF-CHECK · is the agency kit (kiran-core, its skills and hooks) loaded?")
    probs, rec = preflight(room)
    if probs:
        msg = "PREFLIGHT FAILED: kit or hooks not loaded. Nothing ran."
        room.log(msg + " (" + "; ".join(probs) + ")")
        if not a.plain:
            print(f"\n {fg(RED)}{ESC}1m{msg}{RST}\n {fg(MUTE)}" + "; ".join(probs) + f"{RST}\n")
        write(room.dir / "result.json", json.dumps({"status": "preflight_failed", "problems": probs, "preflight": rec}, indent=1))
        return 3
    room.log(f"self-check OK · kiran-core loaded with {len(rec['kiran_core_skills'])} skills · plugin errors: none")

    J = []
    for c in CLIENTS:
        if c.get("report"):
            J.append((Job(f"report-{c['slug']}", f"REPORT · {c['name']}", "report", 0.10, 240, "Haiku (pinned)"), job_report, (c["slug"],)))
    for c in CLIENTS:
        if c.get("site_watch"):
            J.append((Job(f"watch-{c['slug']}", f"SITE WATCH · {c['name']}", "watch", 0.40, 480, "Haiku (pinned)"), job_watch, (c["slug"],)))
    J.append((Job("noor-bookings", "NOOR · BOOKINGS (read-only)", "noor", 0.30, 360, "Haiku (pinned)"), job_noor, ()))
    J.append((Job("canary", "REGRESSION CANARY", "canary", 0.0, 120, "no model (forced test)"), job_canary, ()))
    J.append((Job("kit-versions", "KIT VERSIONS", "kit", 0.0, 60, "no model"), job_kit, ()))
    J.append((Job("cost", "COST · this run's jobs", "cost", 0.0, 30, "no model", needs=["*"]), job_cost, ()))
    dig = Job("digest", "DIGEST", "digest", 0.40, 240, "Sonnet (pinned)", needs=["*"])
    if a.only:
        J = [x for x in J if x[0].id in a.only]
    room.jobs = [x[0] for x in J] + [dig]
    room.log("JOBS · " + " · ".join(j.id for j in room.jobs))

    # kit copy: name the missing Episode 5 / Episode 9 parts instead of crashing half-way
    missing = [str(p) for p in (NOOR_APP / "app.py", NOOR_APP / "reset.py", NOOR_SERVER, MARKET / ".git") if not p.exists()]
    if missing:
        room.log("MISSING PARTS (set KIRAN_DEPS, see README): " + " · ".join(missing) + ". Nothing ran.")
        if not a.plain:
            print("\n MISSING PARTS (set KIRAN_DEPS, see README):\n  " + "\n  ".join(missing) + "\n Nothing ran.\n")
        write(room.dir / "result.json", json.dumps({"status": "missing_parts", "missing": missing}, indent=1))
        return 4

    procs = start_services(room)
    ui = None
    if not a.plain:
        sys.stdout.write(ESC + "?25l" + ESC + "2J")
        ui = threading.Thread(target=tui_loop, args=(room,), daemon=True)
        ui.start()
    sem = threading.Semaphore(a.workers)
    deadline = room.t0 + a.wall_min * 60

    def run_one(job, fn, args):
        if job.needs:
            job.status = "WAITING"
            job.last = "waits for the other jobs"
            while any(j.status in ("QUEUED", "RUNNING", "WAITING") for j in room.jobs if j is not job and j.id not in ("cost", "digest")):
                time.sleep(0.3)
        job.last = "starting"
        with sem:
            while free_gb() < a.min_free_gb and time.time() < deadline:
                job.last = f"waiting for memory ({free_gb():.1f} GB free)"
                time.sleep(2)
            with room.lock:
                if room.spent() + room.reserved() + job.cap_usd > a.run_cap + 1e-9:
                    job.status, job.result = "REFUSED", "would break the run's money cap"
                    room.log(f"{job.id}: REFUSED (run cap)")
                    return
                if time.time() > deadline:
                    job.status, job.result = "REFUSED", "the run's wall clock is used up"
                    return
                job.status, job.t0 = "RUNNING", time.time()
            room.log(f"{job.id}: start ({job.model}, cap ${job.cap_usd:.2f}, {job.cap_s} s)")
            try:
                job.cap_s = int(min(job.cap_s, max(5, deadline - time.time())))
                fn(job, room, *args)
            except Exception as e:  # a job error never stops the others
                job.status, job.result = "FAILED", f"{type(e).__name__}: {e}"[:120]
                job.risks.append(f"{job.title}: crashed ({type(e).__name__})")
            job.t1 = time.time()
            room.log(f"{job.id}: {job.status} · {job.result} · ${job.cost:.4f} · {job.elapsed():.0f} s")

    threads = [threading.Thread(target=run_one, args=x, daemon=True) for x in J]
    for t in threads:
        t.start()
        time.sleep(0.15)
    for t in threads:
        t.join(max(1, deadline - time.time()))
    for j, _, _ in J:  # wall clock: stop anything still running
        if j.status == "RUNNING":
            kill_tree(j.proc)
            j.status, j.result = "TIME CAP", "stopped by the run's wall clock"
            j.risks.append(f"{j.title}: stopped by the run's wall clock")
    dt = threading.Thread(target=run_one, args=(dig, job_digest, ()), daemon=True)
    dt.start()
    dt.join(max(1, deadline + 300 - time.time()))
    for p in procs:
        kill_tree(p)

    dec = [d for j in room.jobs for d in j.decisions]
    res = {"run": rid, "status": "done", "wall_s": round(time.time() - room.t0, 1), "spent_usd": round(room.spent(), 4),
           "run_cap_usd": a.run_cap, "decisions": dec, "jobs": [j.summary() for j in room.jobs], "preflight": rec,
           "credential": "subscription login: local estimate at list price, not a bill"}
    write(room.dir / "result.json", json.dumps(res, indent=1, ensure_ascii=False))
    room.final = [fg(CREAM) + f"{ESC}1m" + f"Done in {fmt_t(res['wall_s'])} · spent ${res['spent_usd']:.2f} of ${a.run_cap:.2f} · "
                  f"{len(dec)} decisions wait for you · nothing was sent" + RST,
                  fg(MUTE) + f"digest: runs/{rid}/digest.md  ·  runs/{rid}/digest.html" + RST]
    room.log(f"DONE · {fmt_t(res['wall_s'])} · ${res['spent_usd']:.4f} of ${a.run_cap:.2f} · {len(dec)} decisions · digest runs/{rid}/digest.md")
    room.stop.set()
    if ui:
        ui.join(2)
        sys.stdout.write("\n" + ESC + "?25h")
    return 0


if __name__ == "__main__":
    sys.exit(main())
