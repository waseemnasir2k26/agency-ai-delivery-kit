#!/bin/bash
# secret-firewall: PreToolUse hook for the Bash AND PowerShell tools (matcher "Bash|PowerShell").
# Blocks (exit 2) a command that touches a .env-style secrets file, including glob tricks.
#
# IMPORTANT: this hook reads command text only; a script that builds the name at runtime gets past it.
# Example that is NOT caught: python -c "print(open('.'+'env').read())"
# Keep real secrets out of the project folder (secret manager, OS permissions, sandbox).
# This is a guard rail against honest mistakes and casual attempts, not a security boundary.
#
# What it matches (case-insensitive), after removing the harmless ".env.example":
#   - any ".env" in the text: Bash cat/type/cp/grep, PowerShell Get-Content, gc, type, cat (alias),
#     Select-String, Copy-Item, Get-Item ... on .env or .env.*
#   - glob tricks: .e*  .en?  .[e]nv  *env  ?env
#   - recursive search over the whole folder: grep -r ... .   |   Select-String / sls on . or *
#   - PowerShell recursive listing piped into a reader: Get-ChildItem -Recurse | Select-String ...
input=$(cat)
cmd=$(printf '%s' "$input" | tr '\n' ' ')
# allow the harmless template file
# (the hook input is raw JSON, so quotes arrive as \" : turn them back into plain quotes first)
scrubbed=$(printf '%s' "$cmd" | sed -E 's/\.env\.example//g; s/\\"/"/g')

env_text='\.env|\.e[a-z]{0,2}[*?[]|\.\[e\]|[*?]env'
bash_grep_all='grep[[:space:]]+-[a-zA-Z]*r[a-zA-Z]*[^|;]*[[:space:]]\.([[:space:]"]|$)'
ps_search_all='(select-string|sls)[^|;]*[[:space:]](-path[[:space:]]+|-literalpath[[:space:]]+)?["'"'"']?(\.|\*|\.[\\/]\*)["'"'"']?([[:space:]"}]|$)'
ps_recurse_pipe='(get-childitem|gci|dir|ls)[^|;]*[[:space:]]-r(ecurse)?([[:space:]][^|;]*)?\|[^;]*(select-string|sls|get-content|gc|cat|type|copy-item|cpi)'

if printf '%s' "$scrubbed" | grep -Eiq "$env_text|$bash_grep_all|$ps_search_all|$ps_recurse_pipe"; then
  echo "BLOCKED by secret-firewall: this command touches a .env secrets file. Ask the human to share the specific value instead." >&2
  exit 2
fi
exit 0
