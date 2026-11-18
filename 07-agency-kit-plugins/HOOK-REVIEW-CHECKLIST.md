# Hook review checklist — read this before you install any plugin

Whatever a plugin runs, it runs as you: on your machine, with your files and your Git login. Read its hooks the way you would read any dependency before you add it. Ours included. Ten minutes, once per new version.

## 1. `hooks/hooks.json`

- [ ] Which events does it hook (`PreToolUse`, `PostToolUse`, `SessionStart`, …)? A `SessionStart` hook runs every time you open Claude Code.
- [ ] Which tools does each `matcher` cover? Write down the list.
- [ ] **Both shells covered?** Any hook that guards shell commands must match `Bash|PowerShell`. A Bash-only matcher let PowerShell read `.env` and commit in our tests.
- [ ] Does every `command` point inside `${CLAUDE_PLUGIN_ROOT}`? A path outside the plugin folder runs something the plugin does not ship.
- [ ] Shell form (`bash "${CLAUDE_PLUGIN_ROOT}/scripts/x.sh"`) or exec form? Shell form is what we tested (run by Git Bash on Windows). Exec form was not tested; on Windows it resolves `bash` from PATH, where WSL's `bash.exe` can win.

## 2. Each script the hooks call

- [ ] What does it read? (Expected: the hook JSON on stdin only.)
- [ ] What does it write? (Expected: nothing, or one named file. In `kiran-core` only `record-review.sh` writes, to `.claude/review.json`.)
- [ ] Does it call the network (`curl`, `wget`, `urllib`, `requests`, `Invoke-WebRequest`)? A guardrail hook should not.
- [ ] What does it run (`python`, `git`, `node`)? Are those on your PATH, and what happens if they are missing? (`kiran-core` blocks the call rather than letting it through unchecked.)
- [ ] Exit codes: `2` = block the tool call. Any other code lets it through. A hook that crashes with exit 1 lets the call through.
- [ ] Any `eval`, downloaded code, or base64 blobs? Stop and ask the author.

## 3. Line endings and platform

- [ ] Does the repo carry a `.gitattributes` that keeps scripts LF? Windows clones with `core.autocrlf=true` turn them into CRLF and bash fails.
- [ ] Windows: Git Bash and Python 3 on PATH?

## 4. After install

- [ ] Feed one hook a fake call and watch it block (example in `README.md`, "Use it in 5 steps").
- [ ] Note the version you reviewed. When `CHANGELOG.md` moves, review the diff, not the whole plugin again.

## The matchers in this kit

| Hook            | Event      | Matcher                         | Script                                              |
| :-------------- | :--------- | :------------------------------ | :-------------------------------------------------- |
| secret-firewall | PreToolUse | `Write\|Edit\|Bash\|PowerShell` | `scripts/secret-firewall.sh` → `secret_firewall.py` |
| commit-gate     | PreToolUse | `Bash\|PowerShell`              | `scripts/commit-gate.sh` → `commit-shape.py`        |

Both are text guards. `secret-firewall` is not a secret scanner: keep one in pre-commit and CI. `commit-gate` is a workflow review gate, not a security boundary.
