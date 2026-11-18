#!/bin/bash
# Episode 10 eval machine (WSL distro or Linux box). Swaps the Episode 8 seat policy for the eval-machine variant
# (= Episode 8 post-fix file minus disableSideloadFlags, plus the suite's per-case managed allow rules).
# Run as root:  wsl -d <distro> -u root -- bash eval_policy.sh on|off|status
# Never touches the Windows host policy (C:\Program Files\ClaudeCode) or the host ~/.claude.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
DST=/etc/claude-code/managed-settings.json
BAK=/etc/claude-code/managed-settings.json.ep08-seat-backup
case "$1" in
  on)  [ -f "$BAK" ] || cp "$DST" "$BAK"; cp "$HERE/managed-settings.eval.json" "$DST"; chmod 644 "$DST"; echo "EVAL MACHINE policy installed (seat policy saved to $BAK)";;
  off) [ -f "$BAK" ] && mv "$BAK" "$DST"; echo "seat policy restored";;
  status) cmp -s "$DST" "$HERE/managed-settings.eval.json" && echo "EVAL MACHINE policy active" || echo "seat (or other) policy active";;
  *) echo "usage: $0 on|off|status"; exit 1;;
esac
