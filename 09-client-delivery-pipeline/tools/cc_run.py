"""Capped headless Claude Code call (the Episode 6 run_job.py pattern, reused by pipeline.py).

Every call:
  - claude -p ... --output-format stream-json --verbose  (the init event arrives before any model reply)
  - caps: --max-budget-usd, --max-turns, wall-clock timeout (kills the process tree), a spend LEDGER over
    runs/ledger.jsonl that refuses a call when (spent + this call's cap) > SPEND_CAP
  - startup self-check on the init event: `kiran-core` must be in init.plugins and plugin_errors must be empty,
    else the process is killed before the first reply (exit 3 upstream: PREFLIGHT FAILED)
  - --setting-sources project,local (user settings and the owner's ~/.claude never load; CLAUDE_CONFIG_DIR is isolated)
  - --permission-prompts none: anything that would prompt is denied and Claude is told not to retry
  - no --plugin-dir: kiran-core comes from the marketplace install recorded in .claude/settings.json
"""
import json, os, re, subprocess, threading, time
from datetime import datetime, timezone
from pathlib import Path

from cc_env import cc_env

HERE = Path(__file__).resolve().parent.parent
LEDGER = HERE / "runs" / "ledger.jsonl"
SPEND_CAP = float(os.environ.get("EP9_SPEND_CAP", "3.00"))
HOME = str(Path.home())


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sanitize(text):
    for v in sorted({HOME, HOME.replace("\\", "/"), HOME.replace("\\", "\\\\"), HOME.lower(),
                     HOME.replace("\\", "/").lower(), HOME.replace("\\", "\\\\").lower()}, key=len, reverse=True):
        text = text.replace(v, "<HOME>")
    parts = [re.escape(x) for x in re.split(r"[\\/]", HOME) if x]
    text = re.sub(r"(?i)" + r"(?:\\+|/)".join(parts), "<HOME>", text)
    text = text.replace(re.sub(r"[^A-Za-z0-9]", "-", HOME), "<HOME-ENC>")
    text = re.sub(r"sk-ant-oat[\w-]+", "<oauth-token>", text)
    text = re.sub(r"[\w.+-]+@(?!kiran\.invalid)[\w-]+\.[A-Za-z][\w.]*", "<EMAIL>", text)
    return text


def write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(sanitize(text), encoding="utf-8")


def spent():
    if not LEDGER.exists():
        return 0.0
    tot = 0.0
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        try:
            tot += float(json.loads(line).get("cost_usd") or 0)
        except Exception:
            pass
    return tot


def ledger_add(rec):
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def kill_tree(proc):
    if proc.poll() is None:
        if os.name == "nt":
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(proc.pid)], capture_output=True)
        else:
            proc.kill()


def kit_problems(init, need=("kiran-core",)):
    names = {p.get("name") for p in (init.get("plugins") or [])}
    probs = [f"plugin not loaded: {n}" for n in need if n not in names]
    # Found while building Episode 9: under --bare, init.plugins STILL lists kiran-core, but none of its commands, skills or agents
    # load (and hooks do not run). So the plugins list alone is not proof: require the kit's own commands too.
    cmds = set(init.get("slash_commands") or []) | set(init.get("skills") or [])
    for n in need:
        if n in names and not any(c.startswith(n + ":") for c in cmds):
            probs.append(f"{n} listed in init.plugins but none of its commands/skills loaded (bare mode?)")
    if init.get("plugin_errors"):
        probs.append(f"plugin_errors: {json.dumps(init['plugin_errors'])[:300]}")
    return probs


def run_claude(prompt, *, cwd, label, out_dir, model="sonnet", budget=0.30, max_turns=20, timeout=600,
               mode="acceptEdits", agent=None, allowed_tools=None, bare=False, require_kit=True,
               extra=None, job="sufi-winter", stage=""):
    """Returns dict(status, init, result, events, cost, console_path). status: done|failed|preflight_failed|timeout|refused"""
    out_dir = Path(out_dir)
    if spent() + budget > SPEND_CAP:
        return {"status": "refused", "why": f"spend ledger ${spent():.2f} + cap ${budget:.2f} > ${SPEND_CAP:.2f}", "cost": 0}
    cmd = ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose", "--model", model,
           "--permission-mode", mode, "--permission-prompts", "none", "--max-budget-usd", f"{budget:.2f}",
           "--max-turns", str(max_turns), "--setting-sources", "project,local", "--strict-mcp-config",
           "--mcp-config", '{"mcpServers":{}}', "--no-session-persistence"]
    if agent:
        cmd += ["--agent", agent]
    if allowed_tools:
        cmd += ["--allowedTools", ",".join(allowed_tools)]
    if bare:
        cmd += ["--bare"]
    cmd += extra or []
    t0 = time.time()
    proc = subprocess.Popen(cmd, cwd=str(cwd), env=cc_env(), stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    lines, events, state = [], [], {"init": None, "result": None, "pre": None}
    err = []
    threading.Thread(target=lambda: err.extend(proc.stderr), daemon=True).start()

    def pump():
        for line in proc.stdout:
            lines.append(line)
            try:
                ev = json.loads(line)
            except Exception:
                continue
            events.append(ev)
            if ev.get("type") == "system" and ev.get("subtype") == "init" and state["init"] is None:
                state["init"] = ev
                if require_kit:
                    probs = kit_problems(ev)
                    if probs:
                        state["pre"] = probs
                        kill_tree(proc)
                        return
            if ev.get("type") == "result":
                state["result"] = ev
    th = threading.Thread(target=pump, daemon=True)
    th.start()
    th.join(timeout)
    timed_out = th.is_alive()
    if timed_out:
        kill_tree(proc)
        th.join(5)
    try:
        proc.wait(10)
    except Exception:
        kill_tree(proc)
    init, res = state["init"] or {}, state["result"] or {}
    status = ("preflight_failed" if state["pre"] else "timeout" if timed_out else
              "done" if res and not res.get("is_error") else "failed")
    if require_kit and not state["init"] and status != "timeout":
        status, state["pre"] = "preflight_failed", ["no init event"]
    cost = float(res.get("total_cost_usd") or 0)
    stream_path = out_dir / f"{label}.stream.jsonl"
    write(stream_path, "".join(lines))
    rec = {"at": now(), "job": job, "stage": stage, "label": label, "model": model, "status": status,
           "cost_usd": cost, "cap_usd": budget, "num_turns": res.get("num_turns"), "wall_s": round(time.time() - t0, 1),
           "duration_api_ms": res.get("duration_api_ms"), "credential": ("api-key" if init.get("apiKeySource") not in (None, "none")
                                                                       else "subscription (local estimate at list price, NOT a bill)"),
           "models": list((res.get("modelUsage") or {}).keys()), "subtype": res.get("subtype"),
           "plugins": [f"{p.get('name')}" for p in (init.get("plugins") or [])],
           "plugin_errors": init.get("plugin_errors"), "preflight_problems": state["pre"],
           "claude_code_version": init.get("claude_code_version"), "permission_mode": init.get("permissionMode")}
    ledger_add(rec)
    return {"status": status, "init": init, "result": res, "events": events, "cost": cost, "record": rec,
            "stderr": sanitize("".join(err))[-2000:], "stream": str(stream_path), "pre": state["pre"]}


def tool_trace(events):
    """[(tool, input-summary, result-snippet, is_error)] from a stream."""
    calls, results = [], {}
    for ev in events:
        msg = ev.get("message") if isinstance(ev.get("message"), dict) else {}
        content = msg.get("content") if isinstance(msg.get("content"), list) else []
        for c in content:
            if not isinstance(c, dict):
                continue
            if c.get("type") == "tool_use":
                calls.append((c.get("id"), c.get("name"), c.get("input")))
            elif c.get("type") == "tool_result":
                body = c.get("content")
                if isinstance(body, list):
                    body = " ".join(x.get("text", "") for x in body if isinstance(x, dict))
                results[c.get("tool_use_id")] = (str(body), bool(c.get("is_error")))
    out = []
    for cid, name, inp in calls:
        r, e = results.get(cid, ("", False))
        out.append((name, inp, r, e))
    return out


def init_excerpt(init):
    return {"type": "system", "subtype": "init", "claude_code_version": init.get("claude_code_version"),
            "permissionMode": init.get("permissionMode"), "model": init.get("model"),
            "plugins": [{"name": p.get("name"), "path": sanitize(str(p.get("path", "")))} for p in init.get("plugins") or []],
            "plugin_errors": init.get("plugin_errors", "absent"), "mcp_servers": init.get("mcp_servers"),
            "kiran_slash_commands": [c for c in init.get("slash_commands") or [] if "kiran" in c],
            "kiran_agents": [a for a in init.get("agents") or [] if "kiran" in str(a)],
            "apiKeySource": init.get("apiKeySource")}
