#!/usr/bin/env python3
"""run_job.py - capped headless job runner (Episode 6, AI Cost Kit).

Wraps `claude -p "/site-refresh for client <client>"` for one Kiran Studio job and
saves one JSON record per run. Kiran Studio and its clients are fictional; all data
is synthetic.

Caps (all enforced, none optional):
  --cap        dollar cap per run  -> claude --max-budget-usd   (refuses to start without it,
                                      unless --uncapped-test, which still needs --backstop)
  --max-turns  turn cap per run    -> claude --max-turns
  --timeout    wall-clock seconds  -> the runner kills the whole process tree
  --total-cap  spend ledger: refuses a run if (spent so far in runs/ + this run's cap) > total

Pre-flight (fails loudly, kills the run before the first model reply):
  the session's init event must show the Workflow tool, the job's workflow, its four
  agents, its required skills and plugins, and the project SessionStart hook must fire.
  A future `--bare` default for -p skips CLAUDE.md, skills, plugins, hooks and .mcp.json;
  this check turns that into a loud failure instead of a silently wrong measurement.

Credential: an API key (ANTHROPIC_API_KEY) in its own workspace gives cost-per-job numbers.
On a subscription login the dollar figure is a LOCAL ESTIMATE AT LIST PRICE, NOT A BILL;
the runner refuses unless --allow-subscription-estimate is passed, and labels the record.

Usage:
  python run_job.py --client mehr-bakery --job site-refresh --setup D --runs 1 --cap 0.50
  python run_job.py --client mehr-bakery --job site-refresh --setup STUCK --runs 1 --cap 0.10
"""
import argparse, json, os, re, shutil, subprocess, sys, threading, time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE / "kiran-sites"
SETUPS = HERE / "setups"
RUNS = HERE / "runs"

JOBS = {
    "site-refresh": {
        "prompt": "/site-refresh for client {client}",
        # Job contract for the main loop: it only launches the workflow and reports. Without this,
        # a recorded run re-edited the page itself after the critic rejected it (uncontrolled extra spend).
        "contract": ("You are running an unattended, measured job. Run the site-refresh workflow exactly once, "
                     "wait for it, then reply with its result: the critic verdict and the report path. "
                     "Do not edit files, re-run stages or fix anything yourself; a human reviews the report."),
        # Named one by one. In a never-trusted folder -p ignores the project allow rules,
        # so the runner passes the job's tools itself.
        "allowed_tools": ["Workflow(site-refresh)", "Read", "Glob", "Edit(sites/**)",
                          "Edit(reports/**)", "Bash(python check-site.py *)"],
        "required": {
            "tools": ["Workflow"],
            "workflows": ["site-refresh"],          # shows up in the init slash_commands list
            "agents": ["reader", "builder", "critic", "reporter"],
            "skills": ["pr-review", "deploy-steps", "brand-voice"],
            "plugins": [],                          # e.g. ["kiran-core"] once Episode 7 ships it
            "hooks": ["session-marker"],            # project SessionStart hook writes a marker
        },
    }
}

HOME = str(Path.home())


def sanitize(text):
    """Strip personal paths and e-mail addresses before anything is written to disk."""
    variants = {HOME, HOME.replace("\\", "/"), HOME.replace("\\", "\\\\"), HOME.replace("\\", "/").lower(),
                HOME.lower(), HOME.replace("\\", "\\\\").lower()}
    for v in sorted(variants, key=len, reverse=True):
        text = text.replace(v, "<HOME>")
    # any escaping depth (JSON inside JSON doubles the backslashes each time), either slash, any case
    parts = [re.escape(x) for x in re.split(r"[\\/]", HOME) if x]
    text = re.sub(r"(?i)" + r"(?:\\+|/)".join(parts), "<HOME>", text)
    enc = re.sub(r"[^A-Za-z0-9]", "-", HOME)  # how Claude Code encodes project dirs
    text = text.replace(enc, "<HOME-ENC>")
    text = re.sub(r"[\w.+-]+@[\w-]+\.[A-Za-z][\w.]*", "<EMAIL>", text)
    return text


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(sanitize(text), encoding="utf-8")


def spent_so_far():
    total = 0.0
    # runs/ + one-off test records under captures/ (captures/runs is a copy of runs/: not counted twice)
    files = list(RUNS.glob("*.json")) + [f for f in (HERE / "captures").rglob("*.json")
                                         if (HERE / "captures" / "runs") not in f.parents]
    for f in files:
        if f.name.endswith(".meta.json"):
            continue
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
            total += float(d.get("total_cost_usd") or d.get("ledger_worst_case_usd") or 0)
        except Exception:
            pass
    return total


def set_agent_frontmatter(agent_file, model, effort):
    t = agent_file.read_text(encoding="utf-8")
    t = re.sub(r"(?m)^model: .*$", "model: " + model, t, count=1)
    t = re.sub(r"(?m)^effort: .*$", "effort: " + effort, t, count=1)
    agent_file.write_text(t, encoding="utf-8")


def prepare_workspace(client, setup):
    """Same starting point for every run: pristine page, setup's CLAUDE.md, models, checker."""
    pristine = PROJECT / "fixtures" / "pristine" / "sites" / client / "index.html"
    shutil.copyfile(pristine, PROJECT / "sites" / client / "index.html")
    shutil.copyfile(PROJECT / "fixtures" / ("CLAUDE.%s.md" % setup["claude_md"]), PROJECT / "CLAUDE.md")
    for name, (model, effort) in setup["agents"].items():
        set_agent_frontmatter(PROJECT / ".claude" / "agents" / (name + ".md"), model, effort)
    checker = PROJECT / "check-site.py"
    good = PROJECT / "fixtures" / "check-site.good.py"
    if not good.exists():
        shutil.copyfile(checker, good)
    shutil.copyfile(PROJECT / "fixtures" / ("check-site.stuck.py" if setup["checker"] == "stuck" else "check-site.good.py"), checker)
    for f in ("check-calls.log", "stuck-calls.log"):
        (PROJECT / f).unlink(missing_ok=True)
    rep = PROJECT / "reports" / (client + "-site-refresh.md")
    rep.unlink(missing_ok=True)


def read_workflow_journal(stream):
    """The -p result text is the main loop's summary. The workflow's own per-stage results live in
    its journal (path printed in the Workflow tool result). Read the critic verdict from there."""
    out = {"agents": []}
    tdir = None
    for line in stream.splitlines():
        if "Transcript dir:" not in line:
            continue
        try:
            ev = json.loads(line)
        except Exception:
            continue
        for c in (ev.get("message") or {}).get("content") or []:
            txt = c.get("content") if isinstance(c, dict) else None
            if isinstance(txt, list):
                txt = " ".join(x.get("text", "") for x in txt if isinstance(x, dict))
            if isinstance(txt, str):
                mt = re.search(r"Transcript dir: (.+)", txt)
                if mt:
                    tdir = mt.group(1).strip()
    if not tdir:
        return out
    d = Path(tdir)
    j = d / "journal.jsonl"
    if not j.exists():
        return out
    labels = {}
    for line in j.read_text(encoding="utf-8").splitlines():
        try:
            ev = json.loads(line)
        except Exception:
            continue
        if ev.get("type") == "started":
            labels[ev.get("key")] = ev.get("label")
        elif ev.get("type") == "result":
            lab = labels.get(ev.get("key"))
            if lab == "critic" and isinstance(ev.get("result"), dict):
                out["critic"] = ev["result"]
            elif lab == "reporter":
                out["reporter"] = ev.get("result")
    for mf in sorted(d.glob("agent-*.meta.json")):
        try:
            m = json.loads(mf.read_text(encoding="utf-8"))
            out["agents"].append({"agent": m.get("agentType"), "phase": m.get("workflowPhase")})  # per-model spend: use modelUsage, not pickedEffortModel
        except Exception:
            pass
    out["journal_text"] = j.read_text(encoding="utf-8")
    return out


def kill_tree(proc):
    if proc.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(proc.pid)], capture_output=True)
    else:
        proc.kill()


def preflight(init, required, cfg, allow_sub):
    problems = []
    tools, agents = set(init.get("tools") or []), set(init.get("agents") or [])
    skills, cmds = set(init.get("skills") or []), set(init.get("slash_commands") or [])
    plugins = {p.get("name") for p in (init.get("plugins") or [])}
    for t in required["tools"]:
        if t not in tools:
            problems.append("tool missing: " + t)
    for w in required["workflows"]:
        if w not in cmds and w not in skills:
            problems.append("workflow not loaded: " + w)
    for a in required["agents"]:
        if a not in agents:
            problems.append("agent not loaded: " + a)
    for s in required["skills"]:
        if s not in skills:
            problems.append("skill not loaded: " + s)
    for p in required["plugins"]:
        if p not in plugins:
            problems.append("plugin not loaded: " + p)
    src = init.get("apiKeySource")
    credential = "api-key" if src and src != "none" else "subscription"
    if credential == "subscription" and not allow_sub:
        problems.append("credential is a subscription login (apiKeySource=none): dollar figures would be a "
                        "local estimate, not a cost-per-job number. Set ANTHROPIC_API_KEY or pass --allow-subscription-estimate")
    return problems, credential


def wait_for_hook(session_id, seconds=15):
    marker = PROJECT / ".claude" / "run-state" / (session_id + ".hook.json")
    end = time.time() + seconds
    while time.time() < end:
        if marker.exists():
            return True
        time.sleep(0.2)
    return False


def one_run(args, setup, job, n):
    run_id = "%s%s%d-%s" % (setup["setup"], "-NOALLOW" if args.no_allowed_tools else "", n, args.client)
    prepare_workspace(args.client, setup)
    budget = args.backstop if args.uncapped_test else args.cap
    cmd = [shutil.which("claude") or "claude", "-p", job["prompt"].format(client=args.client),
           "--output-format", "stream-json", "--verbose",
           "--model", setup["main_model"],
           *([] if args.no_allowed_tools else ["--allowedTools", ",".join(job["allowed_tools"])]),
           "--append-system-prompt", job["contract"],
           "--permission-prompts", "none",
           "--max-budget-usd", "%g" % budget,
           "--max-turns", str(args.max_turns),
           "--setting-sources", "project,local",           # keep user-level hooks/plugins out
           "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',  # this job needs no MCP server
           "--no-session-persistence"]
    env = dict(os.environ)
    env["CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS"] = "0"   # 10-min background wait off: only the caps stop it
    env["ENABLE_CLAUDEAI_MCP_SERVERS"] = "false"
    t0 = time.time()
    proc = subprocess.Popen(cmd, cwd=PROJECT, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            stdin=subprocess.DEVNULL, text=True, encoding="utf-8", errors="replace")
    lines, init, result = [], None, None
    killed_reason = None
    errbuf = []
    threading.Thread(target=lambda: errbuf.extend(proc.stderr), daemon=True).start()
    timer = threading.Timer(args.timeout, lambda: kill_tree(proc))
    timer.start()
    pre = {"checked": False}
    try:
        for line in proc.stdout:
            lines.append(line)
            try:
                ev = json.loads(line)
            except Exception:
                continue
            if ev.get("type") == "system" and ev.get("subtype") == "init" and init is None:
                init = ev
                problems, credential = preflight(init, job["required"], setup, args.allow_subscription_estimate)
                hook_ok = wait_for_hook(init.get("session_id", "?"))
                if not hook_ok:
                    problems.append("hook did not fire: session-marker (project hooks not loaded)")
                pre = {"checked": True, "passed": not problems, "problems": problems, "credential": credential,
                       "model": init.get("model"), "claude_code_version": init.get("claude_code_version"),
                       "loaded": {"agents": sorted(set(job["required"]["agents"]) & set(init.get("agents") or [])),
                                  "skills": sorted(set(job["required"]["skills"]) & set(init.get("skills") or [])),
                                  "workflow": "site-refresh" in (init.get("slash_commands") or []),
                                  "hook": hook_ok}}
                print("  pre-flight: %s%s" % ("PASS" if not problems else "FAIL", "" if not problems else " -> " + "; ".join(problems)))
                if problems:
                    killed_reason = "preflight_failed"
                    kill_tree(proc)
                    break
            elif ev.get("type") == "result":
                result = ev
    finally:
        proc.wait()
        timer.cancel()
    wall = time.time() - t0
    if killed_reason is None and result is None and wall >= args.timeout - 1:
        killed_reason = "timeout"
    stream = "".join(lines)

    verdict = None
    wf = read_workflow_journal(stream)
    if wf.get("critic"):
        verdict = wf["critic"].get("verdict")
    m = [] if verdict else re.findall(r'critic_verdict\\*"\s*:\s*\\*"(APPROVED|REJECTED)', stream)
    if m:
        verdict = m[-1]
    elif not verdict and result and isinstance(result.get("result"), str):
        mm = re.search(r"\b(APPROVED|REJECTED)\b", result["result"])
        verdict = mm.group(1) if mm else None

    subtype = (result or {}).get("subtype", "")
    if killed_reason:
        status = killed_reason
    elif result and subtype == "success" and not result.get("is_error") and verdict:
        status = "done"
    elif result and subtype == "success" and not result.get("is_error"):
        status = "failed"   # the run ended cleanly but the job did not finish (e.g. a tool was denied)
    elif "budget" in subtype or "max_turns" in subtype:
        status = "capped"
    else:
        status = "failed"

    stuck_log = PROJECT / "stuck-calls.log"
    check_log = PROJECT / ("stuck-calls.log" if setup["checker"] == "stuck" else "check-calls.log")
    meta = {
        "run_id": run_id, "client": args.client, "job": args.job, "setup": setup["setup"], "setup_label": setup["label"],
        "status": status, "result_subtype": subtype or None, "exit_code": proc.returncode,
        "critic_verdict": verdict, "permission_denials": [d.get("tool_name") for d in (result or {}).get("permission_denials") or []],
        "wall_seconds": round(wall, 1),
        "caps": {"max_budget_usd": budget, "uncapped_test": bool(args.uncapped_test), "max_turns": args.max_turns,
                 "timeout_seconds": args.timeout, "bg_wait_ceiling_ms": 0},
        "preflight": pre, "checker_calls": len(check_log.read_text(encoding="utf-8").splitlines()) if check_log.exists() else 0,
        "critic_note": (wf.get("critic") or {}).get("note"), "critic_mismatches": (wf.get("critic") or {}).get("mismatches"),
        "workflow_agents": wf.get("agents"), "reporter_text": wf.get("reporter"),
        "agent_models": setup["agents"], "main_model": setup["main_model"], "claude_md": setup["claude_md"],
        "cost_basis_note": ("LOCAL ESTIMATE AT API LIST PRICE (subscription login), NOT A BILL"
                            if pre.get("credential") == "subscription" else "API key: client-side estimate at list price; the Console invoice is the bill"),
        "started_utc": datetime.fromtimestamp(t0, timezone.utc).isoformat(timespec="seconds"),
        "command": [Path(cmd[0]).name] + cmd[1:],
    }
    # No result event (killed on timeout): the spend is unknown, so the ledger charges the full cap.
    record = result or {"subtype": status, "total_cost_usd": None,
                        "ledger_worst_case_usd": budget if status == "timeout" else 0.0,
                        "note": "killed by run_job.py before Claude Code printed a result; spend unknown"}
    write(RUNS / (run_id + ".json"), json.dumps(record, indent=2))
    write(RUNS / (run_id + ".meta.json"), json.dumps(meta, indent=2))
    write(RUNS / (run_id + ".stream.jsonl"), stream)
    write(RUNS / (run_id + ".stderr.txt"), "".join(errbuf))
    if wf.get("journal_text"):
        write(RUNS / (run_id + ".workflow-journal.jsonl"), wf["journal_text"])
    rep = PROJECT / "reports" / (args.client + "-site-refresh.md")
    if rep.exists():
        write(RUNS / (run_id + ".report.md"), rep.read_text(encoding="utf-8"))
    write(RUNS / (run_id + ".page.html"), (PROJECT / "sites" / args.client / "index.html").read_text(encoding="utf-8"))
    if check_log.exists():
        write(RUNS / (run_id + "." + check_log.name), check_log.read_text(encoding="utf-8"))
    cost = (result or {}).get("total_cost_usd") or 0
    print("  %s  client=%s  cost=$%.4f  wall=%.0fs  turns=%s  status=%s  critic=%s" % (
        run_id, args.client, cost, wall, (result or {}).get("num_turns"), status, verdict))
    return meta, cost


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--client", required=True)
    ap.add_argument("--job", default="site-refresh", choices=sorted(JOBS))
    ap.add_argument("--setup", required=True, help="setups/<name>.json, e.g. A, A-trimmed, C, D, STUCK")
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--start", type=int, default=1, help="first run number (to append runs)")
    ap.add_argument("--cap", type=float, help="dollar cap per run (--max-budget-usd)")
    ap.add_argument("--max-turns", type=int, default=25)
    ap.add_argument("--timeout", type=int, default=900, help="wall-clock seconds per run")
    ap.add_argument("--total-cap", type=float, default=3.0, help="stop if runs/ spend + next cap would pass this")
    ap.add_argument("--uncapped-test", action="store_true", help="CONTROLLED TEST: no job cap (still needs --backstop)")
    ap.add_argument("--backstop", type=float, help="off-screen spend ceiling for --uncapped-test")
    ap.add_argument("--no-allowed-tools", action="store_true",
                    help="CONTROLLED TEST: omit --allowedTools to show the never-trusted-folder trap")
    ap.add_argument("--allow-subscription-estimate", action="store_true",
                    help="allow a subscription login; dollar figures are then a local estimate, not a bill")
    args = ap.parse_args()

    if args.uncapped_test:
        if not args.backstop:
            sys.exit("REFUSED: --uncapped-test still needs an off-screen --backstop")
        print("WARNING: --uncapped-test. No job cap. Off-screen backstop $%.2f only." % args.backstop)
    elif args.cap is None or args.cap <= 0:
        sys.exit("REFUSED: no --cap. Every unattended job runs with a dollar cap (or announce --uncapped-test).")
    setup = json.loads((SETUPS / (args.setup + ".json")).read_text(encoding="utf-8"))
    job = JOBS[args.job]
    print("job=%s client=%s setup=%s (%s)" % (args.job, args.client, setup["setup"], setup["label"]))
    results = []
    for n in range(args.start, args.start + args.runs):
        budget = args.backstop if args.uncapped_test else args.cap
        so_far = spent_so_far()
        if so_far + budget > args.total_cap:
            print("STOP: spend ledger $%.4f + this run's cap $%.2f > total cap $%.2f" % (so_far, budget, args.total_cap))
            break
        meta, _ = one_run(args, setup, job, n)
        results.append(meta)
        if meta["status"] == "preflight_failed":
            sys.exit("PRE-FLIGHT FAILED: the job's context did not load. Nothing measured.")
    print("ledger: $%.4f spent across runs/ (estimate)" % spent_so_far())
    sys.exit(0 if all(r["status"] in ("done", "capped") for r in results) else 1)


if __name__ == "__main__":
    main()
