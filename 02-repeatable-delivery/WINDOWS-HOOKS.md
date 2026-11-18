# WINDOWS-HOOKS: make the hooks fire on Windows, for both shell tools

## 1. Prerequisite: Git for Windows

Claude Code on native Windows uses Git for Windows for its Bash tool, and both hooks in this pack
are run with `bash`. Check in PowerShell:

```powershell
git --version
bash --version
python --version      # the commit gate uses Python to read the command
```

If `bash` is not found, install Git for Windows and open a new terminal. In WSL, macOS or Linux,
`bash` is already there.

## 2. Why a `Bash` matcher misses PowerShell

With Git for Windows installed, Claude Code can run commands through two tools: `Bash` and
`PowerShell`. A `PreToolUse` hook only runs for tools its `matcher` names. The matcher is the tool
name, not the language of the command:

| Matcher              | Claude runs `cat .env` (Bash tool) | Claude runs `Get-Content .env` (PowerShell tool) |
| -------------------- | ---------------------------------- | ------------------------------------------------ |
| `"Bash"`             | hook runs, blocked                 | **hook never runs, file is read**                |
| `"Bash\|PowerShell"` | hook runs, blocked                 | hook runs, blocked                               |

We measured this (see `RETEST-LOG.md`): with the old `Bash` matcher, both PowerShell cases got
through. Claude picks the tool, so you cannot count on it choosing Bash.

## 3. The fix: `"matcher": "Bash|PowerShell"`

`kiran-ops/.claude/settings.json` registers both hooks once, for both tools:

```json
"PreToolUse": [
  {
    "matcher": "Bash|PowerShell",
    "hooks": [
      { "type": "command", "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/secret-firewall.sh\"" },
      { "type": "command", "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/commit-gate.sh\"" }
    ]
  }
]
```

Both tools put the command text in `tool_input.command`, so the same scripts read both. The scripts
also know PowerShell spellings (`Get-Content`, `gc`, `type`, `cat`, `Select-String`, `Copy-Item`,
`Set-Content`, `Out-File`, `& git commit`).

Open `/hooks` inside Claude Code to see that both hooks are loaded for `Bash|PowerShell`.

## 4. Live block test, once per tool (needs your Claude login; a small model cost)

From the `kiran-ops` folder (initialise git first, see the module README):

```powershell
Copy-Item .env.example .env      # FAKE values only
claude
```

Then ask, one at a time:

1. `Use the PowerShell tool to run exactly: Get-Content .env`
2. `Use the Bash tool to run exactly: cat .env`
3. Stage any small change (`git add`), then: `Use the PowerShell tool to run exactly: git commit -m 'hook test'`
4. `Use the Bash tool to run exactly: git commit -m 'hook test'`

How to read your own message. A block looks like this in the transcript:

```
PreToolUse:PowerShell hook error: [bash ".../secret-firewall.sh"]: BLOCKED by secret-firewall: ...
PreToolUse:Bash hook error: [bash ".../commit-gate.sh"]: COMMIT BLOCKED by commit-gate: no review on file. ...
```

- The word after `PreToolUse:` is the tool that was stopped. You want to see both `Bash` and `PowerShell`.
- If you see the FAKE value from `.env`, or a new commit in `git log`, the hook did not run for that
  tool. Check the matcher, check `bash --version`, and check `/hooks`.
- If Claude says "File is in a directory that is denied by your permission settings", that is the
  `Read(./.env)` deny rule stopping the Read tool. Good, but it is not the hook. Ask for the shell
  command again to test the hook itself.
- Delete the `.env` afterwards: `Remove-Item .env`.

Offline (no login): `bash bypass-tests/run-bypass-tests.sh` feeds the hooks the same JSON for both
tool names and checks the exit codes.

## 5. Bash only? A team decision, not a fix

You can switch the PowerShell tool off so Claude only uses Bash:

```powershell
$env:CLAUDE_CODE_USE_POWERSHELL_TOOL = "0"     # this terminal only
```

or put `"CLAUDE_CODE_USE_POWERSHELL_TOOL": "0"` in the `env` block of a settings file. Do this only if
your team wants one shell everywhere. It does not replace the `Bash|PowerShell` matcher: a teammate
without the variable still gets the PowerShell tool. Keep the matcher either way.

## Re-test after every Claude Code update

Tool names and defaults can change between releases. Re-run step 4 (or at least the offline battery)
after each update, and record the result next to `RETEST-LOG.md`.
