#!/bin/bash
# Run INSIDE WSL / Linux as root:  wsl -d "$DISTRO" -u root -- bash <kit>/08-team-policy/scripts/setup-root.sh
# Builds the admin-owned parts of the lab: /opt/kiran (venv + marketplace mirror). Does NOT write the policy.
set -euo pipefail
EP8="$(cd "$(dirname "$0")/.." && pwd)"
# The Agency Kit Pack (module 07) ships kiran-core and the kiran-noor server. Override with KIT_MARKETPLACE=<path>.
KIT_MARKETPLACE="${KIT_MARKETPLACE:-$EP8/../07-agency-kit-plugins/kiran-marketplace}"
NOOR_FORM="${NOOR_FORM:-fixed}"   # fixed (tested, policy matches it) | pluginroot (V1 demo: policy cannot match)

mkdir -p /opt/kiran/bin
[ -x /opt/kiran/venv/bin/python ] || python3 -m venv /opt/kiran/venv
/opt/kiran/venv/bin/python -c "import mcp" 2>/dev/null || /opt/kiran/venv/bin/pip install -q "mcp[cli]==2.3.0"

MP=/opt/kiran/kiran-marketplace
rm -rf "$MP"; mkdir -p "$MP/.claude-plugin" "$MP/plugins"
# kiran-core: snapshot of the Agency Kit Pack (module 07) when present, else a stub
if [ -d "$KIT_MARKETPLACE/plugins/kiran-core/.claude-plugin" ]; then
  cp -r "$KIT_MARKETPLACE/plugins/kiran-core" "$MP/plugins/"
else
  mkdir -p "$MP/plugins/kiran-core/.claude-plugin"
  echo '{"name":"kiran-core","version":"0.0.1","description":"stub (module 07 not found)"}' > "$MP/plugins/kiran-core/.claude-plugin/plugin.json"
fi
# kiran-noor: the noor-bookings server (Episode 5, shipped in module 07); MCP config written here so V1 can test each command form
mkdir -p "$MP/plugins/kiran-noor/.claude-plugin"
cp "$KIT_MARKETPLACE/plugins/kiran-noor/server.py" "$MP/plugins/kiran-noor/server.py"
cat > /opt/kiran/bin/noor-bookings <<EOF
#!/bin/sh
exec /opt/kiran/venv/bin/python "$MP/plugins/kiran-noor/server.py" "\$@"
EOF
chmod 755 /opt/kiran/bin/noor-bookings
if [ "$NOOR_FORM" = fixed ]; then
  CMD='"command": "/opt/kiran/bin/noor-bookings", "args": []'; VER="1.0.1"
else
  CMD='"command": "/opt/kiran/venv/bin/python", "args": ["${CLAUDE_PLUGIN_ROOT}/server.py"]'; VER="1.0.0"
fi
cat > "$MP/plugins/kiran-noor/.claude-plugin/plugin.json" <<EOF
{
  "name": "kiran-noor",
  "version": "$VER",
  "description": "Noor Dental Clinic connector (fictional): noor-bookings MCP server, four read/draft tools.",
  "author": { "name": "Kiran Studio" },
  "mcpServers": {
    "noor-bookings": { $CMD, "env": { "NOOR_API_TOKEN": "\${NOOR_API_TOKEN:-noor_test_FAKE_0000}" } }
  }
}
EOF
cat > "$MP/.claude-plugin/marketplace.json" <<'EOF'
{
  "name": "kiran-marketplace",
  "owner": { "name": "Kiran Studio" },
  "metadata": { "description": "Kiran Studio's plugin catalogue (fictional agency, synthetic data). LAB MIRROR for Episode 8." },
  "plugins": [
    { "name": "kiran-core", "source": "./plugins/kiran-core", "description": "House skills, critic agent, secret-firewall + commit-gate hooks." },
    { "name": "kiran-noor", "source": "./plugins/kiran-noor", "description": "Noor Dental Clinic connector (four read/draft tools)." }
  ]
}
EOF
chmod -R a+rX /opt/kiran
echo "OK: /opt/kiran ready (noor form=$NOOR_FORM, version $VER)"
