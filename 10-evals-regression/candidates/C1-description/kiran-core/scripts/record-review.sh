#!/bin/bash
# Reads critic output on stdin, takes its final "VERDICT: APPROVED|REJECTED" line,
# and stamps the sha256 of the staged diff into .claude/review.json.
out=$(cat)
v=$(printf '%s\n' "$out" | grep -Eio '^VERDICT:[[:space:]]*(APPROVED|REJECTED)' | tail -1 | grep -Eio 'approved|rejected' | tr 'A-Z' 'a-z')
mkdir -p .claude
if [ -z "$v" ]; then
  echo "record-review: no VERDICT line found; nothing recorded" >&2
  rm -f .claude/review.json
  exit 1
fi
if command -v sha256sum >/dev/null 2>&1; then
  sha=$(git diff --cached | sha256sum | cut -d' ' -f1)
else
  sha=$(git diff --cached | shasum -a 256 | cut -d' ' -f1)
fi
printf '{"verdict": "%s", "diff_sha": "%s"}\n' "$v" "$sha" > .claude/review.json
echo "review recorded: $v for diff ${sha:0:12}"
