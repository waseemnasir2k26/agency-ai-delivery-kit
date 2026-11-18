#!/usr/bin/env python3
"""run_suite.py - Kiran Studio regression suite (Episode 10, Regression Pack). FICTIONAL agency, synthetic data.

No framework. For each case, for each run, four steps:
  1. copy the frozen input into a fresh, empty folder
  2. run the job headless, the way a scheduled job would: `claude -p` (or that episode's own script)
  3. read the result (the receipt: total_cost_usd, modelUsage, num_turns)
  4. run the case's check.py  ->  PASS / FAIL.  Only code hands out a pass.

Limits (printed FIRST, before any run): a cost cap for the whole suite and a time limit. Hit either one and the
suite stops and says so. Costs are client-side estimates at list price, not an invoice.

Startup self-check (fails loudly, never trusts `-p` defaults):
  * case 00-hooks-alive runs first: kiran-core's secret-firewall hook must block a fake-key write
    (FORCED TEST, scripted stand-in model, no spend). Miss -> "PREFLIGHT FAILED: kit or hooks not loaded", exit 3.
  * before scoring every claude -p run: system/init.plugins must contain each plugin the case needs, loaded from
    the folder under test; plugin_errors must be absent; mcp_servers must match what the case expects.
  * the receipt's modelUsage must contain the pinned full model name (other keys are listed: helper calls).

Where it runs: the EVAL MACHINE (eval-machine/: Episode 8 policy minus disableSideloadFlags, so `--plugin-dir`
works; each case's tools are managed allow rules in that policy, not --allowedTools, which the policy ignores).
Source eval-machine/env.sh first (isolated CLAUDE_CONFIG_DIR).

Usage:
  python3 evals/run_suite.py --runs 1 --max-suite-usd 0.40 --timeout-min 30 --out evals/baseline.json
  python3 evals/run_suite.py --runs 5 --max-suite-usd 1.00 --timeout-min 60 --out evals/runs/five.json
  python3 evals/run_suite.py --case judge-test --runs 5 ...
Exit: 0 every case at/above its pass mark · 1 a case below its mark · 3 pre-flight failed · 4 stopped by a limit
"""
import argparse, hashlib, json, math, os, re, shutil, signal, socket, subprocess, sys, threading, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path

EVALS = Path(__file__).resolve().parent
ROOT = EVALS.parent
CASES = EVALS / "cases"
EXPECTED = EVALS / "expected"          # runner-side answers: never copied into the agent's workspace
WS_ROOT = Path("/tmp/ep10-ws")
SVC_ROOT = Path("/tmp/ep10-svc")
NOOR_PLUGIN = Path(os.environ.get("NOOR_PLUGIN", "/opt/kiran/kiran-marketplace/plugins/kiran-noor"))   # admin-installed copy (matches allowedMcpServers)
# Episode 5 booking app (case 06). Default = the kit module next door; set NOOR_APP_SRC to use another copy.
NOOR_APP_SRC = Path(os.environ.get("NOOR_APP_SRC", str(ROOT.parent / "05-business-connector" / "noor-booking-app")))
VENV_PY = Path.home() / "ep10-venv" / "bin" / "python"
MOCK_PORT = 8788
CLAUDE = shutil.which("claude") or str(Path.home() / ".local/bin/claude")
PIN = json.loads((EVALS / "pin.json").read_text(encoding="utf-8"))
HOME = str(Path.home())
BUILTIN_SOURCES = ("@builtin",)


def sanitize(text):
    for v in (HOME, str(ROOT), str(ROOT.parent.parent)):
        text = text.replace(v, "<" + ("home" if v == HOME else "project") + ">")
    text = re.sub(r"/mnt/[a-z]/Users/[^/\"\\]+", "<winhome>", text)
    return re.sub(r"[\w.+-]+@[\w-]+\.[A-Za-z][\w.]*", "<email>", text)


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(sanitize(text), encoding="utf-8")


def mark_ok(passes, runs, mark):
    a, b = (int(x) for x in mark.split("/"))
    return runs > 0 and passes * b >= a * runs


def fixture_version():
    h = hashlib.sha256()
    for p in sorted(CASES.rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts:
            h.update(str(p.relative_to(CASES)).encode()); h.update(p.read_bytes())
    for p in sorted(EXPECTED.glob("*.json")):
        h.update(p.name.encode()); h.update(p.read_bytes())
    return "fx-" + h.hexdigest()[:10]


def port_open(port):
    with socket.socket() as s:
        s.settimeout(0.3)
        return s.connect_ex(("127.0.0.1", port)) == 0


def wait_port(port, secs=15):
    end = time.time() + secs
    while time.time() < end:
        if port_open(port):
            return True
        time.sleep(0.2)
    return False


def kill(proc):
    if proc and proc.poll() is None:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except Exception:
            proc.kill()
        proc.wait()


# ---------------------------------------------------------------- services
class Services:
    def __init__(self):
        self.procs = []

    def start_mock(self, plan_file):
        if port_open(MOCK_PORT):
            return True
        env = dict(os.environ, MOCK_PLAN=str(plan_file), MOCK_PORT=str(MOCK_PORT), MOCK_LOG=str(SVC_ROOT / "mock.log"))
        self.procs.append(subprocess.Popen([sys.executable, str(EVALS / "tools" / "mock_api.py")], env=env,
                                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True))
        return wait_port(MOCK_PORT)

    def noor_up(self):
        """Fresh clinic database for every run: copy the app, reseed (relative dates), start it on 8800."""
        if port_open(8800):
            raise RuntimeError("port 8800 busy: stop the other noor-booking-app first")
        app = SVC_ROOT / "noor-app"
        shutil.rmtree(app, ignore_errors=True)
        shutil.copytree(NOOR_APP_SRC, app, ignore=shutil.ignore_patterns("bookings.db", "__pycache__"))
        env = dict(os.environ, NOOR_DB_PATH=str(app / "bookings.db"), NOOR_PORT="8800")
        subprocess.run([sys.executable, "reset.py"], cwd=app, env=env, check=True, capture_output=True)
        p = subprocess.Popen([sys.executable, "app.py"], cwd=app, env=env, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, start_new_session=True)
        self.procs.append(p)
        if not wait_port(8800):
            raise RuntimeError("noor-booking-app did not start")
        return p

    def noor_rows(self):
        import sqlite3
        con = sqlite3.connect(str(SVC_ROOT / "noor-app" / "bookings.db"))
        con.row_factory = sqlite3.Row
        rows = [dict(r) for r in con.execute("SELECT * FROM bookings ORDER BY id")]
        con.close()
        return rows

    def www_up(self, ws):
        if port_open(8090):
            raise RuntimeError("port 8090 busy")
        subprocess.run([sys.executable, "make_www.py"], cwd=ws, check=True, capture_output=True)
        p = subprocess.Popen([sys.executable, "serve.py", "8090"], cwd=ws, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, start_new_session=True)
        self.procs.append(p)
        if not wait_port(8090):
            raise RuntimeError("Site Watch web server did not start")
        return p

    def stop(self, p):
        kill(p)
        if p in self.procs:
            self.procs.remove(p)

    def stop_all(self):
        for p in list(self.procs):
            kill(p)
        self.procs.clear()


# ---------------------------------------------------------------- one headless claude run
def parse_stream(stream):
    out = {"init": None, "result": None, "tool_uses": [], "tool_results": []}
    for line in stream.splitlines():
        try:
            ev = json.loads(line)
        except Exception:
            continue
        t = ev.get("type")
        if t == "system" and ev.get("subtype") == "init" and out["init"] is None:
            out["init"] = ev
        elif t == "assistant":
            for b in (ev.get("message") or {}).get("content") or []:
                if isinstance(b, dict) and b.get("type") == "tool_use":
                    out["tool_uses"].append({"name": b.get("name"), "input": b.get("input")})
        elif t == "user":
            for b in (ev.get("message") or {}).get("content") or []:
                if isinstance(b, dict) and b.get("type") == "tool_result":
                    c = b.get("content")
                    if isinstance(c, list):
                        c = " ".join(x.get("text", "") for x in c if isinstance(x, dict))
                    out["tool_results"].append({"is_error": bool(b.get("is_error")), "text": str(c)[:1500]})
        elif t == "result":
            out["result"] = ev
    return out


def run_claude(cmd, cwd, env, timeout):
    t0 = time.time()
    p = subprocess.Popen(cmd, cwd=cwd, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace", start_new_session=True)
    timer = threading.Timer(timeout, lambda: kill(p))
    timer.start()
    try:
        out, err = p.communicate()
    finally:
        timer.cancel()
    wall = time.time() - t0
    return p.returncode, out or "", err or "", wall, wall >= timeout - 0.5


def load_assertion(init, case, plugin_dirs):
    """The startup self-check for one run. Returns a list of problems (empty = loaded as the case expects)."""
    if not init:
        return ["no system/init event"]
    problems = []
    loaded = {p.get("name"): p for p in init.get("plugins") or []}
    for name in case.get("plugins", []):
        want = os.path.realpath(plugin_dirs[name])
        got = loaded.get(name)
        if not got:
            problems.append(f"plugin not loaded: {name}")
        elif os.path.realpath(got.get("path", "")) != want:
            problems.append(f"plugin {name} loaded from {got.get('path')} (not the folder under test)")
    if init.get("plugin_errors"):
        problems.append("plugin_errors: " + json.dumps(init["plugin_errors"])[:300])
    mcp = {m.get("name"): m.get("status") for m in init.get("mcp_servers") or []}
    for srv, status in (case.get("mcp_expect") or {}).items():
        if mcp.get(srv) != status:
            problems.append(f"mcp server {srv}: {mcp.get(srv)} (expected {status})")
    return problems


def extra_plugins(init, case):
    return sorted(p.get("source") or p.get("name") for p in (init or {}).get("plugins") or []
                  if p.get("name") not in case.get("plugins", []) and not str(p.get("source", "")).endswith(BUILTIN_SOURCES))


def claude_env(extra=None):
    env = dict(os.environ)
    env["ENABLE_CLAUDEAI_MCP_SERVERS"] = "false"
    env["CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS"] = "0"
    env.update(extra or {})
    return env


# ---------------------------------------------------------------- case kinds
def job_canary(case, ws, a, svc, plugin_dirs):
    plan = json.loads(json.dumps(case["plan"]).replace("{workspace}", str(ws)))
    plan_file = SVC_ROOT / "canary-plan.json"
    plan_file.write_text(json.dumps(plan), encoding="utf-8")
    if not svc.start_mock(plan_file):
        return {"subtype": "mock_not_started", "is_error": True}, ""
    cmd = [CLAUDE, "-p", "(canary)", "--output-format", "stream-json", "--verbose", "--model", a.model,
           "--permission-mode", "dontAsk", "--tools", ",".join(case["tools"]), "--no-session-persistence"]
    cmd += [x for n in case["plugins"] for x in ("--plugin-dir", plugin_dirs[n])]
    if a.bare:
        cmd.append("--bare")
    env = claude_env({"ANTHROPIC_BASE_URL": f"http://127.0.0.1:{MOCK_PORT}", "ANTHROPIC_API_KEY": "sk-ant-mock-not-a-real-key"})
    code, out, err, wall, to = run_claude(cmd, ws, env, case["timeout_s"])
    s = parse_stream(out)
    rec = {"subtype": (s["result"] or {}).get("subtype", "timeout" if to else "no_result"), "exit_code": code,
           "tool_results": s["tool_results"], "tool_uses": s["tool_uses"], "total_cost_usd": 0.0,
           "load_problems": load_assertion(s["init"], case, plugin_dirs), "wall_s": round(wall, 1),
           "init_excerpt": excerpt_init(s["init"]), "stderr_tail": err[-600:]}
    return rec, out


def excerpt_init(init):
    if not init:
        return None
    return {k: init.get(k) for k in ("model", "permissionMode", "claude_code_version", "plugins", "plugin_errors",
                                     "mcp_servers", "apiKeySource")}


def job_claude(case, ws, a, svc, plugin_dirs):
    model = a.case_model.get(case["id"], a.model)
    cmd = [CLAUDE, "-p", case["prompt"], "--output-format", "stream-json", "--verbose", "--model", model,
           "--max-budget-usd", "%g" % case["max_budget_usd"], "--permission-mode", "dontAsk",
           "--tools", ",".join(case["tools"]), "--no-session-persistence"]
    cmd += [x for n in case["plugins"] for x in ("--plugin-dir", plugin_dirs[n])]
    if case.get("json_schema"):
        cmd += ["--json-schema", json.dumps(case["json_schema"])]
    if a.bare:
        cmd.append("--bare")
    noor, before = None, None
    if case.get("service") == "noor-app":
        noor = svc.noor_up()
        before = svc.noor_rows()
        write(ws.parent / (ws.name + ".bookings-before.json"), json.dumps(before, indent=1))
    try:
        code, out, err, wall, to = run_claude(cmd, ws, claude_env(), case["timeout_s"])
    finally:
        if noor:
            write(ws.parent / (ws.name + ".bookings-after.json"), json.dumps(svc.noor_rows(), indent=1))
            svc.stop(noor)
    s = parse_stream(out)
    r = s["result"] or {}
    mu = r.get("modelUsage") or {}
    rec = {"subtype": r.get("subtype", "timeout" if to else "no_result"), "is_error": bool(r.get("is_error")) or not r,
           "exit_code": code, "result": r.get("result"), "structured_output": r.get("structured_output"),
           "total_cost_usd": float(r.get("total_cost_usd") or 0.0), "model_requested": model,
           "model_usage_keys": sorted(mu), "model_usage_cost": {k: v.get("costUSD") for k, v in mu.items()},
           "num_turns": r.get("num_turns"), "permission_denials": r.get("permission_denials"),
           "tool_uses": s["tool_uses"], "tool_results": s["tool_results"], "wall_s": round(wall, 1),
           "timed_out": to, "load_problems": load_assertion(s["init"], case, plugin_dirs),
           "extra_plugins": extra_plugins(s["init"], case), "init_excerpt": excerpt_init(s["init"]),
           "stderr_tail": err[-600:], "command": ["claude"] + cmd[1:]}
    if r and model not in mu:
        rec["load_problems"].append(f"pinned model {model} not in modelUsage {sorted(mu)}")
    return rec, out


def job_script(case, ws, a, svc, plugin_dirs):
    lab = case.get("lab_config")
    cwd = Path(os.path.expanduser(case["cwd"])) if case.get("cwd") else ws
    outf = ws / "script-out.json"
    model = a.case_model.get(case["id"], a.model)
    sub = {"{out}": str(outf), "{venv_python}": str(VENV_PY), "{model}": model,
           "{max_budget_usd}": "%g" % case.get("max_budget_usd", 0)}
    cmd = [sub.get(x, x) for x in case["command"]]
    env = claude_env()
    if lab:   # Episode 8 lab profile (plugins installed from the admin marketplace); not the isolated eval config
        env.pop("CLAUDE_CONFIG_DIR", None); env.pop("CLAUDE_SECURESTORAGE_CONFIG_DIR", None)
    www = svc.www_up(ws) if case.get("service") == "sitewatch-www" else None
    try:
        t0 = time.time()
        try:
            p = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=case["timeout_s"],
                               stdin=subprocess.DEVNULL)
            code, so, se, to = p.returncode, p.stdout, p.stderr, False
        except subprocess.TimeoutExpired as e:
            code, so, se, to = None, (e.stdout or b"").decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or ""), "TIMEOUT", True
        wall = time.time() - t0
    finally:
        if www:
            svc.stop(www)
    rec = {"subtype": "timeout" if to else ("success" if code == 0 else f"exit_{code}"), "exit_code": code,
           "is_error": to or code is None, "wall_s": round(wall, 1), "stdout_tail": so[-3000:], "stderr_tail": se[-800:],
           "total_cost_usd": 0.0, "model_requested": model if "{model}" in case["command"] else None,
           "command": cmd, "load_problems": [], "tool_uses": []}
    if outf.exists():
        try:
            rec["policy_rows"] = json.loads(outf.read_text())["rows"]
        except Exception:
            pass
    if case.get("result_file") and (ws / case["result_file"]).exists():
        rj = json.loads((ws / case["result_file"]).read_text(encoding="utf-8"))
        rec.update({"total_cost_usd": float(rj.get("total_cost_usd") or 0), "model_usage_keys": rj.get("models_used"),
                    "num_turns": rj.get("num_turns"), "subtype": rj.get("subtype"), "is_error": bool(rj.get("is_error")),
                    "result": json.dumps(rj.get("summary"))})
        if model not in (rj.get("models_used") or []):
            rec["load_problems"].append(f"pinned model {model} not in models_used {rj.get('models_used')}")
    if case.get("post"):
        pp = subprocess.run(case["post"], cwd=ws, capture_output=True, text=True, timeout=120)
        rec["post_stdout"] = pp.stdout[-4000:]
    return rec, so


JUDGE_PROMPT = ("You are reviewing a weekly client report before it is sent to the client. Below are the report and the "
                "verifier output that was produced for it.\n\n=== REPORT ===\n{report}\n\n=== VERIFIER OUTPUT ===\n{verify}\n\n"
                "Question: is this report ready to send to the client?")
JUDGE_SCHEMA = {"type": "object", "properties": {"ready": {"type": "boolean"}}, "required": ["ready"]}


def job_judge(case, ws, a, svc, plugin_dirs):
    """Judge test: the code check always runs (free, deterministic). The model judge sees the same two files.
    role 'sole'      -> the judge's verdict alone decides PASS (lazy, wrong on purpose)
    role 'flag_only' -> code decides; a judge 'not ready' only raises a flag for a person."""
    j = case["judge"]
    jmodel = a.model if j.get("model") == "same-as-job" else j["model"]
    prompt = JUDGE_PROMPT.format(report=(ws / "report.md").read_text(encoding="utf-8"),
                                 verify=(ws / "verify.txt").read_text(encoding="utf-8"))
    cmd = [CLAUDE, "-p", prompt, "--output-format", "stream-json", "--verbose", "--model", jmodel, "--max-budget-usd",
           "%g" % case["max_budget_usd"], "--permission-mode", "dontAsk", "--tools", "", "--no-session-persistence",
           "--json-schema", json.dumps(JUDGE_SCHEMA)]
    code, out, err, wall, to = run_claude(cmd, ws, claude_env(), case["timeout_s"])
    s = parse_stream(out)
    r = s["result"] or {}
    so = r.get("structured_output") or {}
    code_chk = subprocess.run([sys.executable, str(CASES / case["id"] / "code_check.py"), str(ws)], capture_output=True, text=True)
    rec = {"subtype": r.get("subtype", "timeout" if to else "no_result"), "is_error": bool(r.get("is_error")) or not r,
           "judge_role": j["role"], "judge_model": jmodel, "judge_ready": so.get("ready"),
           "code_check_ok": code_chk.returncode == 0, "code_check_line": code_chk.stdout.strip(),
           "total_cost_usd": float(r.get("total_cost_usd") or 0), "model_usage_keys": sorted(r.get("modelUsage") or {}),
           "num_turns": r.get("num_turns"), "wall_s": round(wall, 1), "load_problems": [], "tool_uses": s["tool_uses"]}
    return rec, out


KINDS = {"canary": job_canary, "claude": job_claude, "script": job_script, "judge": job_judge}


def run_check(case, ws, rec_path):
    exp = EXPECTED / (case["id"] + ".json")
    p = subprocess.run([sys.executable, str(CASES / case["id"] / case["check"]), "--workspace", str(ws), "--record",
                        str(rec_path), "--expected", str(exp)], capture_output=True, text=True, timeout=120)
    line = (p.stdout.strip().splitlines() or ["(check printed nothing) " + p.stderr.strip()[-200:]])[-1]
    return p.returncode == 0, line


def fresh_workspace(case):
    ws = WS_ROOT / case["id"]
    shutil.rmtree(ws, ignore_errors=True)
    for f in WS_ROOT.glob(case["id"] + ".*"):
        f.unlink()
    shutil.copytree(CASES / case["id"] / "input", ws)
    if case.get("setup"):
        subprocess.run([sys.executable, str(CASES / case["id"] / case["setup"]), str(ws)], check=True,
                       capture_output=True, text=True)
    return ws


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=int, help="runs per case (overrides case.json runs)")
    ap.add_argument("--max-suite-usd", type=float, required=True, help="cost cap for the WHOLE suite (estimate)")
    ap.add_argument("--timeout-min", type=float, required=True, help="time limit for the whole suite")
    ap.add_argument("--out", required=True)
    ap.add_argument("--case", action="append", help="run only these case ids (prefix match); judge-test runs only when named")
    ap.add_argument("--plugin-dir", default=str(ROOT / "kiran-core"))
    ap.add_argument("--model", default=PIN["model"], help="pinned FULL model name (default from evals/pin.json)")
    ap.add_argument("--case-model", action="append", default=[], help="CASE=MODEL: a different model for one stage only")
    ap.add_argument("--label", default="")
    ap.add_argument("--bare", action="store_true", help="CONTROLLED TEST: add --bare to every run (pre-flight must stop)")
    a = ap.parse_args()
    a.case_model = dict(x.split("=", 1) for x in a.case_model)

    # 1. LIMITS: printed first, before anything runs
    print(f"SUITE COST CAP: ${a.max_suite_usd:.2f} (estimate at list price, not an invoice)")
    print(f"SUITE TIMEOUT: {a.timeout_min:g} min")
    if os.path.realpath(os.environ.get("CLAUDE_CONFIG_DIR", "")) in ("", os.path.realpath(os.path.expanduser("~/.claude"))):
        print("REFUSED: CLAUDE_CONFIG_DIR is not an isolated eval config. Source eval-machine/env.sh first.")
        return 3
    plugin_dirs = {"kiran-core": os.path.realpath(a.plugin_dir), "kiran-noor": str(NOOR_PLUGIN)}
    pj = json.loads((Path(a.plugin_dir) / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    cc_version = subprocess.run([CLAUDE, "--version"], capture_output=True, text=True).stdout.strip()
    policy = Path("/etc/claude-code/managed-settings.json")
    eval_policy = (ROOT / "eval-machine" / "managed-settings.eval.json").read_bytes()
    header = {"label": a.label, "started_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "model_pinned": a.model, "case_models": a.case_model, "claude_code_version": cc_version,
              "plugin": pj["name"], "plugin_version": pj["version"], "plugin_dir": sanitize(plugin_dirs["kiran-core"]),
              "plugin_description_client_report": re.search(r"(?m)^description: (.*)$", (Path(a.plugin_dir) / "skills/client-report/SKILL.md").read_text(encoding="utf-8")).group(1),
              "fixture_version": fixture_version(), "runs_override": a.runs, "max_suite_usd": a.max_suite_usd,
              "timeout_min": a.timeout_min, "bare": a.bare,
              "eval_machine_policy": "eval variant" if policy.exists() and policy.read_bytes() == eval_policy else "OTHER (not the eval variant)"}
    print(f"model {a.model} · {cc_version} · {pj['name']} {pj['version']} · fixtures {header['fixture_version']} · policy: {header['eval_machine_policy']}")
    if header["eval_machine_policy"] != "eval variant":
        print("REFUSED: this machine is not running the eval-machine policy (eval-machine/eval_policy.sh on).")
        return 3

    all_cases = sorted((json.loads((d / "case.json").read_text(encoding="utf-8")) for d in CASES.iterdir()
                        if (d / "case.json").exists()), key=lambda c: c["id"])
    canary = next(c for c in all_cases if c["kind"] == "canary")
    if a.case:
        cases = [c for c in all_cases if any(c["id"].startswith(x) for x in a.case) and c["kind"] != "canary"]
    else:
        cases = [c for c in all_cases if c["kind"] != "canary" and not c["id"].startswith("judge")]
    label = a.label or Path(a.out).stem
    run_dir = EVALS / "runs" / label
    WS_ROOT.mkdir(parents=True, exist_ok=True); SVC_ROOT.mkdir(parents=True, exist_ok=True)
    svc = Services()
    t_start = time.time()
    spent = 0.0
    stopped = None
    results = {}
    try:
        # 2. STARTUP SELF-CHECK: canary first
        ws = fresh_workspace(canary)
        rec, stream = job_canary(canary, ws, a, svc, plugin_dirs)
        rp = run_dir / canary["id"] / "run-1.json"
        write(rp, json.dumps(rec, indent=1)); write(rp.with_suffix(".stream.jsonl"), stream)
        ok, line = run_check(canary, ws, rp)
        if rec["load_problems"]:
            ok, line = False, "load check: " + "; ".join(rec["load_problems"])
        print(f"00-hooks-alive  {'PASS' if ok else 'FAIL'}  {line}")
        if not ok:
            print("PREFLIGHT FAILED: kit or hooks not loaded. Nothing measured.")
            out = {"header": header, "preflight": {"ok": False, "line": line}, "cases": {}, "stopped": "preflight"}
            write(Path(a.out), json.dumps(out, indent=2))
            return 3
        header["preflight"] = {"ok": True, "line": line}
        # 3. CASES
        for case in cases:
            n = a.runs or case["runs"]
            mark = case["pass_mark"]
            runs = []
            for i in range(1, n + 1):
                if spent >= a.max_suite_usd:   # checked before each run; overrun bounded by one run's own --max-budget-usd
                    stopped = f"cost cap: spent ${spent:.4f} >= ${a.max_suite_usd:.2f}"
                    break
                if time.time() - t_start > a.timeout_min * 60:
                    stopped = f"timeout: {a.timeout_min:g} min reached"
                    break
                ws = fresh_workspace(case)
                rec, stream = KINDS[case["kind"]](case, ws, a, svc, plugin_dirs)
                rp = run_dir / case["id"] / f"run-{i}.json"
                write(rp, json.dumps(rec, indent=1)); write(rp.with_suffix(".stream.jsonl"), stream)
                if case["kind"] == "judge":
                    if case["judge"]["role"] == "sole":
                        ok, line = bool(rec.get("judge_ready")), f"judge says ready={rec.get('judge_ready')} (sole judge decides)"
                    else:
                        ok, line = rec["code_check_ok"], rec["code_check_line"] + f" | judge flag: {'none' if rec.get('judge_ready') else 'NOT READY -> person'}"
                else:
                    ok, line = run_check(case, ws, rp)
                if rec.get("load_problems"):
                    ok, line = False, "PRE-FLIGHT: " + "; ".join(rec["load_problems"])
                spent += rec.get("total_cost_usd") or 0.0
                errored = bool(rec.get("is_error")) or rec.get("subtype") not in ("success",)
                runs.append({"run": i, "pass": ok, "check": line, "cost_usd": round(rec.get("total_cost_usd") or 0, 6),
                             "wall_s": rec.get("wall_s"), "subtype": rec.get("subtype"), "errored": errored,
                             "model_usage_keys": rec.get("model_usage_keys"), "num_turns": rec.get("num_turns"),
                             "extra_plugins": rec.get("extra_plugins"), "judge_ready": rec.get("judge_ready")})
                print(f"{case['id']:<20} run {i}/{n}  {'PASS' if ok else 'FAIL'}  ${rec.get('total_cost_usd') or 0:.4f}  "
                      f"{rec.get('wall_s')}s  {line[:150]}")
            passes = sum(r["pass"] for r in runs)
            done_n = len(runs)
            res = {"title": case["title"], "origin": case.get("origin"), "kind": case["kind"], "runs": done_n,
                   "runs_planned": n, "passes": passes, "pass_rate": f"{passes}/{done_n}", "pass_mark": mark,
                   "must_pass": case.get("must_pass", False),
                   "at_or_above_mark": mark_ok(passes, done_n, mark) and done_n == n,
                   "mean_cost_usd": round(sum(r["cost_usd"] for r in runs) / done_n, 6) if done_n else None,
                   "total_cost_usd": round(sum(r["cost_usd"] for r in runs), 6),
                   "mean_wall_s": round(sum(r["wall_s"] or 0 for r in runs) / done_n, 1) if done_n else None,
                   "errors": sum(r["errored"] for r in runs), "run_detail": runs}
            if case["kind"] == "judge":
                res["judge"] = {"role": case["judge"]["role"], "model": runs[0].get("model_usage_keys") if runs else None,
                                "ready_votes": sum(bool(r["judge_ready"]) for r in runs)}
            results[case["id"]] = res
            if stopped:
                break
    finally:
        svc.stop_all()
    wall = time.time() - t_start
    if stopped:
        print(f"SUITE STOPPED: {stopped}")
    summary = {"cases": len(results), "at_or_above_mark": sum(r["at_or_above_mark"] for r in results.values()),
               "must_pass_failed": [k for k, r in results.items() if r["must_pass"] and not r["at_or_above_mark"]],
               "suite_cost_usd": round(spent, 4), "suite_wall_s": round(wall, 1),
               "errors": sum(r["errors"] for r in results.values()),
               "total_runs": sum(r["runs"] for r in results.values())}
    out = {"header": header, "summary": summary, "stopped": stopped, "cases": results}
    write(Path(a.out), json.dumps(out, indent=2))
    print(f"\n{'CASE':<20} {'PASS RATE':<10} {'MARK':<5} {'COST/RUN':>9} {'WALL':>7}  STATUS")
    for k, r in results.items():
        print(f"{k:<20} {r['pass_rate']:<10} {r['pass_mark']:<5} {('$%.4f' % r['mean_cost_usd']) if r['mean_cost_usd'] is not None else '-':>9} "
              f"{r['mean_wall_s'] or 0:>6.1f}s  {'at/above mark' if r['at_or_above_mark'] else 'BELOW MARK'}{' (must pass)' if r['must_pass'] else ''}")
    print(f"\n{summary['at_or_above_mark']}/{summary['cases']} cases at or above their pass mark · errors {summary['errors']} · "
          f"suite cost ${spent:.4f} (estimate) · wall {wall / 60:.1f} min · saved {a.out}")
    if stopped:
        return 4
    return 0 if summary["at_or_above_mark"] == summary["cases"] else 1


if __name__ == "__main__":
    sys.exit(main())
