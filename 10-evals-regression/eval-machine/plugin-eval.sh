#!/bin/bash
# claude plugin eval for kiran-core's own skill case, on the eval machine (WSL distro or Linux box).
# MODE=shell  -> grants Bash(cat data/*) so the skill's !`cat` line can run. On this eval machine it is REFUSED (V6):
#                the managed sandbox block sets autoAllowBashIfSandboxed, see results/plugin-eval/v6-plugin-eval-shell-refused.txt
# MODE=noshell (default, used on screen) -> no shell grant; the skill's data line cannot run, Claude may still Read the file.
HERE="$(cd "$(dirname "$0")" && pwd)"; source "$HERE/env.sh"; cd "$HERE/.."
MODE="${1:-noshell}"
OUT=results/plugin-eval-$MODE; mkdir -p $OUT
GRANT=(); [ "$MODE" = shell ] && GRANT=(--allow-tools "Bash(cat data/*)")
claude plugin eval ./kiran-core --trust-plugin --scaffold "${GRANT[@]}" \
  --model claude-haiku-5-5 --judge-model claude-sonnet-5-5 --max-cost-usd 0.40 --runs 3 --no-publish \
  --json $OUT/results.json --report $OUT/report.html --output-dir $OUT/aggregate < /dev/null
echo "exit=$?"
