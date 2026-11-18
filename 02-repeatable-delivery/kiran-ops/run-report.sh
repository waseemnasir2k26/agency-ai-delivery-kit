#!/bin/bash
# Kiran Studio 7 AM report robot (macOS / Linux / WSL twin of run-report.cmd, for cron).
# Runs headless Claude, validates the result, writes reports/<date>.json or a
# reports/FAILED-<time>.txt receipt. Never fakes success.
#
# NOTE: This run needs skills and hooks, so it must NOT run in bare mode. Claude Code docs say
# bare mode is planned to become the default for `claude -p`. If an update flips it, the
# validator writes a FAILED receipt: check the flags first. Unattended runs: consider
# `--permission-prompts none` so a prompt is denied instead of waited on.
#
# Setup: cp .robot.env.example .robot.env   (ROBOT_CLIENT, ROBOT_BUDGET in USD)
# Needs: claude on PATH and logged in for the cron user, python3 with jsonschema.
# Cron (crontab -e), 07:00 every day. cron has a tiny PATH: put the full path to claude in PATH below.
#   0 7 * * * /bin/bash <your-project>/run-report.sh >> <your-project>/reports/cron.log 2>&1
set -u
cd "$(dirname "$0")" || exit 1
mkdir -p reports
# export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"   # uncomment / adjust for cron
if [ ! -f .robot.env ]; then
  echo "FAILED: .robot.env not found. Copy .robot.env.example to .robot.env" > "reports/FAILED-no-robot-env.txt"
  exit 1
fi
set -a; . ./.robot.env; set +a
SCHEMA=$(cat schema.json)
claude -p "/client-report ${ROBOT_CLIENT}" --model sonnet --setting-sources project --strict-mcp-config \
  --no-session-persistence --output-format json --json-schema "$SCHEMA" \
  --max-budget-usd "${ROBOT_BUDGET}" > reports/_last.json 2> reports/_last.err
CLAUDE_EXIT=$?
PY="$(command -v python3 || command -v python)"
"$PY" scripts/validate-report.py "$CLAUDE_EXIT" "$ROBOT_CLIENT"
exit $?
