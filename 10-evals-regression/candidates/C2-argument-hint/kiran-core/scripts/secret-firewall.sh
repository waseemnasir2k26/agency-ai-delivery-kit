#!/bin/bash
# kiran-core secret-firewall: PreToolUse hook for Write|Edit|Bash|PowerShell.
# Blocks (exit 2) a tool call that would put a known key format into a file or a command,
# or that touches a .env-style secrets file. Pattern guard on TEXT only: it cannot see what a
# script computes at runtime, and it does not replace a secret scanner in pre-commit + CI.
here="$(cd "$(dirname "$0")" && pwd)"
PY="$(command -v python || command -v python3)"
if [ -z "$PY" ]; then
  echo "BLOCKED by secret-firewall: python not found, so this call could not be checked. Install Python 3 or disable kiran-core." >&2
  exit 2
fi
exec "$PY" "$here/secret_firewall.py"
