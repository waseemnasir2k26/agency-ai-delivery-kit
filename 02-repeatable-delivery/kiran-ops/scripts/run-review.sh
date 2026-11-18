#!/bin/bash
# Human-run, from the project root: asks the read-only reviewer agent (headless) to review the
# staged diff, then records its verdict + the diff hash in .claude/review.json.
# The model never writes the hash: record-review.sh computes it from `git diff --cached`.
# Needs your Claude login (this is a real model call, capped at $0.50 by --max-budget-usd).
diff=$(git diff --cached)
[ -n "$diff" ] || { echo "nothing staged"; exit 1; }
prompt="Review this staged diff. Read the changed files for context. End your answer with exactly one line: VERDICT: APPROVED or VERDICT: REJECTED.

$diff"
claude -p "$prompt" --agent reviewer --model sonnet --setting-sources project --strict-mcp-config --no-session-persistence --max-budget-usd 0.5 2>/dev/null | tee /dev/stderr | bash scripts/record-review.sh
