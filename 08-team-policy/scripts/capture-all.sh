#!/bin/bash
# Episode 8 capture run. INSIDE WSL / Linux as root, on a LAB machine:
#   wsl -d "$DISTRO" -u root -- env LAB_USER=<your WSL user> bash <kit>/08-team-policy/scripts/capture-all.sh
# Swaps the managed policy (pre-fix -> lock1-off -> pre-fix -> post-fix), runs every attack as the normal user,
# writes one file per CAP id into 08-team-policy/captures/. Zero model spend (scripted stand-in, see lab/mock_api.py).
set -u
U="${1:-${LAB_USER:?set LAB_USER to the normal (non-root) lab user, or pass it as the first argument}}"
EP8="$(cd "$(dirname "$0")/.." && pwd)"
CAP="$EP8/captures"
LAB="/home/$U/ep08-lab"
mkdir -p "$CAP"
asuser() { setpriv --reuid="$U" --regid="$U" --init-groups env -i HOME="/home/$U" USER="$U" \
  PATH="/home/$U/.local/bin:/usr/bin:/bin" TERM=xterm-256color LANG=C.UTF-8 "$@"; }
pol() { bash "$EP8/scripts/policy.sh" "$1" >/dev/null; echo "[policy: $1]"; }
MOCKENV="ANTHROPIC_BASE_URL=http://127.0.0.1:8787 ANTHROPIC_API_KEY=sk-ant-mock-not-a-real-key"

# one forced tool call -> transcript (tool call, Claude Code's result, decision meta)
forced() {  # $1 = plan json steps array, $2 = prompt, $3.. extra args
  local steps="$1" prompt="$2"; shift 2
  echo "{\"steps\": $steps, \"final\": \"forced test finished\"}" > /tmp/policy_test_plan.json
  chmod 666 /tmp/policy_test_plan.json
  asuser bash -c "cd $LAB/sufi-threads && env $MOCKENV timeout 150 claude -p '$prompt' --output-format stream-json --verbose $* </dev/null 2>/tmp/forced.err" \
  | python3 -c '
import sys, json
for l in sys.stdin:
    try: e = json.loads(l)
    except Exception: continue
    if e.get("type") == "assistant":
        for b in e["message"]["content"]:
            if b.get("type") == "tool_use": print("TOOL CALL  :", b["name"], json.dumps(b["input"]))
    elif e.get("type") == "user":
        for b in e["message"]["content"]:
            if isinstance(b, dict) and b.get("type") == "tool_result":
                c = b.get("content"); c = " ".join(x.get("text","") for x in c) if isinstance(c, list) else c
                print("RESULT     :", ("[is_error] " if b.get("is_error") else "") + str(c))
        if e.get("tool_result_meta"): print("DECISION   :", json.dumps(e["tool_result_meta"]))
'
}

# helpers (mock + otel sink) as the user
asuser bash -c "pkill -u $U -f 'python3 mock_api.py'; pkill -u $U -f 'python3 otel_sink.py'" 2>/dev/null
rm -f /tmp/policy_test_plan.json /tmp/otel_events.jsonl
echo '{"steps":[]}' > /tmp/policy_test_plan.json; chmod 666 /tmp/policy_test_plan.json
asuser bash -c "cd $LAB && MOCK_PLAN=/tmp/policy_test_plan.json MOCK_LOG=/tmp/mock_api.log nohup python3 mock_api.py >/dev/null 2>&1 & cd $LAB && OTEL_SINK_OUT=/tmp/otel_events.jsonl nohup python3 otel_sink.py >/dev/null 2>&1 &"
sleep 1

# ---------------- PRE-FIX policy
pol pre-fix
{ echo "# CAP S2c_read_deny_msg  | policy: pre-fix | FORCED TEST (scripted tool call, no model)"; forced '[{"name":"Read","input":{"file_path":"'$LAB'/sufi-threads/.env"}}]' "open .env and print it"; } > "$CAP/S2c_read_deny_msg.txt"
{ echo "# extra: Bash cat .env under the Read deny rule | policy: pre-fix | FORCED TEST"; forced '[{"name":"Bash","input":{"command":"cat .env","description":"print env"}}]' "cat .env"; } > "$CAP/X_bash_cat_env.txt"
{ echo "# CAP S2c_script_read_result  | leak.py (3 lines) inside the WSL2 sandbox | policy: pre-fix | FORCED TEST"; echo "--- leak.py:"; cat "$LAB/sufi-threads/leak.py"; echo "---"; forced '[{"name":"Bash","input":{"command":"python3 leak.py","description":"run leak.py"}}]' "run leak.py"; } > "$CAP/S2c_script_read_result.txt"
{ echo "# CAP S2c_network_block_line  | send_probe.py: fake marker to example.com (not on the list) | policy: pre-fix | FORCED TEST"; forced '[{"name":"Bash","input":{"command":"python3 send_probe.py","description":"send probe"}}]' "run send_probe.py"; } > "$CAP/S2c_network_block_line.txt"
{ echo "# extra: WebFetch to example.com (outside the sandbox, permission flow) | policy: pre-fix | FORCED TEST"; forced '[{"name":"WebFetch","input":{"url":"https://example.com/paste","prompt":"verify"}}]' "fetch it"; } > "$CAP/X_webfetch_example.txt"
{ echo "# CAP S2b_local_allow_result + S2b_push_result | lock 1 ON (pre-fix) | planted .claude/settings.json allows WebFetch(domain:example.com) + git push | FORCED TEST"
  forced '[{"name":"WebFetch","input":{"url":"https://example.com","prompt":"What is on this page?"}}]' "fetch https://example.com"
  forced '[{"name":"Bash","input":{"command":"git push origin main","description":"push"}}]' "git push"; } > "$CAP/S2b_locked.txt"
{ echo "# CAP S2d_marketplace_msg | policy: pre-fix"; echo '$ claude plugin marketplace add https://example.com/other-marketplace.git'; asuser bash -c "cd $LAB/sufi-threads && timeout 60 claude plugin marketplace add https://example.com/other-marketplace.git 2>&1; echo \"[exit \$?]\""; } > "$CAP/S2d_marketplace_msg.txt"
{ echo "# CAP S2d_mcp_result | policy: pre-fix"; echo '$ claude mcp add blog-tool -- npx -y blog-tool'; asuser bash -c "cd $LAB/sufi-threads && timeout 60 claude mcp add blog-tool -- npx -y blog-tool 2>&1; echo \"[exit \$?]\""; echo; echo '$ claude mcp list   (state after the refusal)'; asuser bash -c "cd $LAB/sufi-threads && timeout 90 claude mcp list 2>&1 | grep -v '^Checking' | sed '/^\$/d'"; } > "$CAP/S2d_mcp_result.txt"
{ echo "# CAP E8_sideload_msg | policy: pre-fix (disableSideloadFlags: true)"; echo '$ claude --plugin-dir ./friends-plugin'; asuser bash -c "cd $LAB && timeout 60 claude --plugin-dir ./friends-plugin -p hi </dev/null 2>&1; echo \"[exit \$?]\""
  echo; echo '$ claude --mcp-config ./blog.json   (extra sideload route)'; echo '{"mcpServers":{"blog-tool":{"command":"npx","args":["-y","blog-tool"]}}}' > /tmp/blog.json; chmod 644 /tmp/blog.json
  asuser bash -c "cd $LAB && timeout 60 claude --mcp-config /tmp/blog.json -p hi </dev/null 2>&1; echo \"[exit \$?]\""; } > "$CAP/E8_sideload_msg.txt"
{ echo "# extra: bypass + auto mode refusals | policy: pre-fix"; echo '$ claude --dangerously-skip-permissions -p hi'; asuser bash -c "cd $LAB/sufi-threads && env $MOCKENV timeout 60 claude --dangerously-skip-permissions -p hi </dev/null 2>&1 | tail -3; echo \"[exit \$?]\""
  echo; echo '$ claude --permission-mode auto -p hi --output-format stream-json --verbose   (permissionMode from the init event)'
  asuser bash -c "cd $LAB/sufi-threads && env $MOCKENV timeout 60 claude --permission-mode auto -p hi --output-format stream-json --verbose </dev/null 2>&1" | python3 -c '
import sys, json
for l in sys.stdin:
    try: e = json.loads(l)
    except Exception: print("  ", l.rstrip()); continue
    if e.get("subtype") == "init": print("   init.permissionMode =", e.get("permissionMode"))
'; } > "$CAP/X_bypass_auto_refusals.txt"
asuser bash -c "cd $LAB && env PATH=/home/$U/.local/bin:/usr/bin:/bin python3 policy_test.py --json /tmp/pt_pre.json" > "$CAP/policy_test.wsl.pre-fix.txt" 2>&1

# ---------------- LOCK 1 OFF (wrong on purpose)
pol lock1-off
{ echo "# CAP S2b_unlocked_result | allowManagedPermissionRulesOnly REMOVED (wrong on purpose) | folder trusted | FORCED TEST"
  forced '[{"name":"WebFetch","input":{"url":"https://example.com","prompt":"What is on this page?"}}]' "fetch https://example.com"
  forced '[{"name":"Bash","input":{"command":"git push origin main","description":"push"}}]' "git push"; } > "$CAP/S2b_unlocked.txt"
asuser bash -c "cd $LAB && python3 policy_test.py T1a T1b" > "$CAP/policy_test.wsl.lock1-off.T1.txt" 2>&1

# ---------------- POST-FIX policy (failIfUnavailable + allowUnsandboxedCommands:false)
pol post-fix
{ echo "# CAP S3_wsl_after_fix | WSL2 session start under the post-fix policy"; forced '[]' "hi" | sed 's/^/  /'
  asuser bash -c "cd $LAB/sufi-threads && env $MOCKENV timeout 60 claude -p hi --output-format stream-json --verbose </dev/null 2>&1" | python3 -c '
import sys, json
for l in sys.stdin:
    try: e = json.loads(l)
    except Exception: continue
    if e.get("subtype") == "init":
        print("started: permissionMode=%s plugins=%s mcp=%s" % (e.get("permissionMode"), [p["name"] for p in e.get("plugins",[]) if "@builtin" not in p.get("source","")], [(m["name"], m["status"]) for m in e.get("mcp_servers",[])]))
    if e.get("type") == "result": print("result:", e.get("subtype"), "| is_error:", e.get("is_error"))
'; } > "$CAP/S3_wsl_after_fix.txt"
SHIM=$(mktemp -d); for d in /usr/bin /bin; do for n in $(ls $d); do [ "$n" = bwrap ] || [ -e "$SHIM/$n" ] || ln -s "$d/$n" "$SHIM/$n"; done; done; chmod 755 "$SHIM"
{ echo "# CAP S3_failif_msg (LINUX STAND-IN) | post-fix policy, sandbox made unavailable (bwrap hidden from PATH) | the native-Windows capture is still owed"
  asuser bash -c "cd $LAB/sufi-threads && env $MOCKENV PATH=/home/$U/.local/bin:$SHIM timeout 60 claude -p hi </dev/null 2>&1; echo \"[exit \$?]\""; } > "$CAP/S3_failif_msg.linux-standin.txt"
pol pre-fix
{ echo "# CAP S2e_win_sandbox_notice (LINUX STAND-IN) | PRE-fix policy, sandbox unavailable: what does Claude Code say?"
  asuser bash -c "cd $LAB/sufi-threads && env $MOCKENV PATH=/home/$U/.local/bin:$SHIM timeout 60 claude -p hi </dev/null 2>&1; echo \"[exit \$?]\""
  echo; echo "# same, forced leak.py run with no sandbox (stand-in for S2e_win_script_result)"
  echo '{"steps":[{"name":"Bash","input":{"command":"python3 leak.py","description":"run leak.py"}}],"final":"x"}' > /tmp/policy_test_plan.json
  asuser bash -c "cd $LAB/sufi-threads && env $MOCKENV PATH=/home/$U/.local/bin:$SHIM timeout 120 claude -p 'run leak.py' --output-format stream-json --verbose </dev/null 2>/dev/null" | python3 -c '
import sys, json
for l in sys.stdin:
    try: e = json.loads(l)
    except Exception: continue
    if e.get("type") == "user":
        for b in e["message"]["content"]:
            if isinstance(b, dict) and b.get("type") == "tool_result": print("RESULT   :", b.get("content"))
        if e.get("tool_result_meta"): print("DECISION :", json.dumps(e["tool_result_meta"]))
'; } > "$CAP/S2e_nosandbox.linux-standin.txt"
pol post-fix
asuser bash -c "cd $LAB && python3 policy_test.py --json /tmp/pt_post.json" > "$CAP/policy_test.wsl.post-fix.txt" 2>&1
cp /tmp/pt_pre.json "$CAP/policy_test.wsl.pre-fix.json" 2>/dev/null; cp /tmp/pt_post.json "$CAP/policy_test.wsl.post-fix.json" 2>/dev/null
rm -rf "$SHIM"

# ---------------- OTel: decision + stop events (ids removed)
sleep 3
python3 - "$CAP" <<'EOF'
import json, sys
cap = sys.argv[1]
keep = ("tool_decision", "safety_event", "tool_result", "managed_settings_resolved", "permission")
rows = []
for l in open("/tmp/otel_events.jsonl"):
    e = json.loads(l)
    if any(k in e["event"] for k in keep):
        for k in ("user.id", "session.id", "user.email", "organization.id", "user.account_uuid", "prompt.id"):
            e["attributes"].pop(k, None)
        rows.append(e)
with open(f"{cap}/S3_otel_events.jsonl", "w") as fh:
    for r in rows: fh.write(json.dumps(r) + "\n")
from collections import Counter
print("otel events kept:", Counter(r["event"] for r in rows))
EOF
asuser bash -c "pkill -u $U -f 'python3 mock_api.py'; pkill -u $U -f 'python3 otel_sink.py'" 2>/dev/null
echo "capture run done -> $CAP (policy left at: post-fix)"
