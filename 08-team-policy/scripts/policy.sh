#!/bin/bash
# Install one LAB policy variant as the WSL / Linux managed file. Run INSIDE WSL as root, on a lab machine only:
#   wsl -d "$DISTRO" -u root -- bash <kit>/08-team-policy/scripts/policy.sh pre-fix|post-fix|lock1-off|none
# This binds every Claude Code session on that Linux/WSL install. 'none' removes it.
set -euo pipefail
EP8="$(cd "$(dirname "$0")/.." && pwd)"
F=/etc/claude-code/managed-settings.json
mkdir -p /etc/claude-code
case "${1:-}" in
  pre-fix)   cp "$EP8/policy/managed-settings.wsl.pre-fix.json" "$F" ;;
  post-fix)  cp "$EP8/policy/managed-settings.wsl.json" "$F" ;;
  lock1-off) cp "$EP8/policy/managed-settings.wsl.LOCK1-OFF.json" "$F" ;;
  none)      rm -f "$F"; echo "policy removed"; exit 0 ;;
  *) echo "usage: policy.sh pre-fix|post-fix|lock1-off|none" >&2; exit 2 ;;
esac
chmod 644 "$F"
echo "installed $1 -> $F ($(sha256sum "$F" | cut -c1-12))"
