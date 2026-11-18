#!/bin/bash
# V1: can a serverCommand allowlist entry match a connector that a PLUGIN starts?
# Run INSIDE WSL as root (writes /etc/claude-code/managed-settings.json, then runs `claude mcp list` as the user).
# Usage: bash v1_connector_match.sh [lab-user]   (default: $LAB_USER; restores the previous managed file at the end)
set -u
U="${1:-${LAB_USER:?set LAB_USER to the normal (non-root) lab user, or pass it as the first argument}}"
F=/etc/claude-code/managed-settings.json
mkdir -p /etc/claude-code
[ -f "$F" ] && cp "$F" /tmp/managed-settings.v1backup
asuser() { setpriv --reuid="$U" --regid="$U" --init-groups env -i HOME="/home/$U" USER="$U" PATH="/home/$U/.local/bin:/usr/bin:/bin" TERM=dumb "$@"; }
PY=/opt/kiran/venv/bin/python
ROOT=/opt/kiran/kiran-marketplace/plugins/kiran-noor
run() {
  local label="$1" entries="$2"
  printf '{ "allowManagedMcpServersOnly": true, "allowedMcpServers": %s }\n' "$entries" > "$F"
  echo "=== $label"
  echo "policy: $entries"
  asuser claude mcp list 2>&1 | grep -v '^Checking' | sed '/^$/d' | sed 's/^/  /'
  echo
}
run "A control: allowlist names some other command"      '[{"serverCommand":["/bin/false"]}]'
run "B literal \${CLAUDE_PLUGIN_ROOT} in the policy entry"  "[{\"serverCommand\":[\"$PY\",\"\${CLAUDE_PLUGIN_ROOT}/server.py\"]}]"
run "C expanded absolute path (what mcp list prints)"     "[{\"serverCommand\":[\"$PY\",\"$ROOT/server.py\"]}]"
run "D serverName noor-bookings (no command entries)"     '[{"serverName":"noor-bookings"}]'
run "E serverName plugin:kiran-noor:noor-bookings"        '[{"serverName":"plugin:kiran-noor:noor-bookings"}]'
run "F serverName noor-bookings + an unrelated command entry" '[{"serverName":"noor-bookings"},{"serverCommand":["/bin/false"]}]'
if [ -f /tmp/managed-settings.v1backup ]; then mv /tmp/managed-settings.v1backup "$F"; else rm -f "$F"; fi
