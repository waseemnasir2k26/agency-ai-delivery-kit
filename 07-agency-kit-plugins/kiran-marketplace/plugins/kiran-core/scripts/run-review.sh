#!/bin/bash
# Human-run, from the client repo root: asks the kit's read-only critic agent (headless) to review
# the staged diff, then records its verdict + the diff hash in .claude/review.json.
# The model never writes the hash.
here="$(cd "$(dirname "$0")" && pwd)"
diff=$(git diff --cached)
[ -n "$diff" ] || { echo "nothing staged"; exit 1; }
prompt="Review this staged diff. Read the changed files for context. End your answer with exactly one line: VERDICT: APPROVED or VERDICT: REJECTED.

$diff"
claude -p "$prompt" --agent kiran-core:critic --strict-mcp-config --no-session-persistence --max-budget-usd 0.5 2>/dev/null | tee /dev/stderr | bash "$here/record-review.sh"
