#!/bin/bash
# kiran-core commit-gate: PreToolUse hook for Bash|PowerShell.
# Blocks a `git commit` unless .claude/review.json in the project holds an approval stamped with the
# sha256 of the CURRENT staged diff, and that staged diff is the whole change.
# A workflow review gate, NOT a secret scanner and NOT a security boundary (Episode 2).
here="$(cd "$(dirname "$0")" && pwd)"
review_cmd="bash \"$here/run-review.sh\""
input=$(cat)
cmdtext=$(printf '%s' "$input" | tr '\n' ' ')
writeish='>|tee|sed[[:space:]]+-i|set-content|out-file|add-content|new-item|(cp|mv|rm|dd|truncate|printf|echo|python|python3|node|perl|ruby|powershell|pwsh)[[:space:]]'
if printf '%s' "$cmdtext" | grep -Eq 'review\.json' && printf '%s' "$cmdtext" | grep -Eiq "$writeish"; then
  echo "BLOCKED by commit-gate: only the kit's run-review.sh may write .claude/review.json." >&2
  exit 2
fi
PY="$(command -v python || command -v python3)"
if [ -z "$PY" ]; then
  echo "COMMIT BLOCKED by commit-gate: python not found, cannot read the command." >&2
  exit 2
fi
shape=$(printf '%s' "$input" | "$PY" "$here/commit-shape.py" 2>/dev/null)
[ "$shape" = "none" ] && exit 0
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0
block() { echo "COMMIT BLOCKED by commit-gate: $1" >&2; exit 2; }
sha256() { if command -v sha256sum >/dev/null 2>&1; then sha256sum; else shasum -a 256; fi | cut -d' ' -f1; }
case "$shape" in
  plain) ;;
  all) block "do not use commit -a; stage explicitly with git add so the reviewed diff is the committed diff." ;;
  paths) block "commit names paths (or --include/-o): that commits working-tree files, not the reviewed staged diff. git add them, re-review, then plain git commit." ;;
  alias) block "git -c alias.* can hide a commit from this gate. Run git commit directly." ;;
  *) block "could not parse this command, so it is treated as a commit. Run git commit directly." ;;
esac
[ -s .claude/review.json ] || block "no review on file. Run: $review_cmd"
rj=$(tr -d '\n\r' < .claude/review.json)
printf '%s' "$rj" | grep -Eq '^[[:space:]]*\{.*"verdict"[[:space:]]*:[[:space:]]*"(approved|rejected)".*"diff_sha"[[:space:]]*:[[:space:]]*"[0-9a-f]{64}".*\}[[:space:]]*$' || block "review.json is malformed. Re-run: $review_cmd"
verdict=$(printf '%s' "$rj" | sed -E 's/.*"verdict"[[:space:]]*:[[:space:]]*"([a-z]+)".*/\1/')
sha=$(printf '%s' "$rj" | sed -E 's/.*"diff_sha"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})".*/\1/')
[ -n "$(git diff --cached --name-only)" ] || block "nothing is staged."
git diff --quiet || block "unstaged edits: stage them and re-review. The critic only saw the staged diff."
now=$(git diff --cached | sha256)
[ "$sha" = "$now" ] || block "approval is stale: the staged diff changed after the review. Re-run: $review_cmd"
[ "$verdict" = "approved" ] || block "the critic REJECTED this diff. Fix the findings, git add, re-review."
exit 0
