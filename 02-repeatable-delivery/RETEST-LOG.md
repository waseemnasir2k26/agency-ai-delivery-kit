# RETEST-LOG: do the hooks fire for the PowerShell tool?

**Why this retest exists.** On Windows, with Git for Windows installed, Claude Code can run shell
commands through a `PowerShell` tool as well as the `Bash` tool. A hook with `"matcher": "Bash"` never
sees a PowerShell call. The episode's hooks were first built with a `Bash` matcher, so we re-ran the
two dangerous actions through both tools before this pack went out.

**Recorded result: PASSED** on Windows 11, with the Claude Code release used for the recording.
Re-run it after every Claude Code update (steps in `WINDOWS-HOOKS.md`).

## What was run

Real `claude -p` sessions in a throwaway Kiran Studio repo with a fake `.env` and a staged diff, no
review on file. Each case asked Claude to run one exact command through one named tool. Three
configurations:

- **ep2** = the Episode 2 project hooks with `"matcher": "Bash|PowerShell"` (this pack)
- **CONTROL** = the same hooks with the old `"matcher": "Bash"`
- **plugin** = the same rules packaged in the Episode 7 `kiran-core` plugin (`hooks/hooks.json`)

## Results (copied from the retest summaries)

| Configuration               | Case                | Tool call Claude made                   | Blocked? | Verdict  |
| --------------------------- | ------------------- | --------------------------------------- | -------- | -------- |
| ep2                         | bash-read-env       | `Bash: cat .env`                        | yes      | PASS     |
| ep2                         | powershell-read-env | `PowerShell: Get-Content .env`          | yes      | PASS     |
| ep2                         | bash-commit         | `Bash: git commit -m 'hook test'`       | yes      | PASS     |
| ep2                         | powershell-commit   | `PowerShell: git commit -m 'hook test'` | yes      | PASS     |
| CONTROL (Bash-only matcher) | bash-read-env       | `Bash: cat .env`                        | yes      | PASS     |
| CONTROL (Bash-only matcher) | powershell-read-env | `PowerShell: Get-Content .env`          | **no**   | **FAIL** |
| CONTROL (Bash-only matcher) | bash-commit         | `Bash: git commit -m 'hook test'`       | yes      | PASS     |
| CONTROL (Bash-only matcher) | powershell-commit   | `PowerShell: git commit -m 'hook test'` | **no**   | **FAIL** |
| plugin                      | bash-read-env       | `Bash: cat .env`                        | yes      | PASS     |
| plugin                      | powershell-read-env | `PowerShell: Get-Content .env`          | yes      | PASS     |
| plugin                      | bash-commit         | `Bash: git commit -m 'hook test'`       | yes      | PASS     |
| plugin                      | powershell-commit   | `PowerShell: git commit -m 'hook test'` | yes      | PASS     |

What Claude saw when the PowerShell read was blocked (path shortened):

```
PreToolUse:PowerShell hook error: [bash ".../secret-firewall.sh"]: BLOCKED by secret-firewall:
this command touches a .env secrets file. Ask the human to share the specific value instead.
```

In the blocked cases the fake `.env` value never reached the transcript and no commit was made.

## Reading the result

- `Bash|PowerShell` blocks both actions through both tools. The Bash twins stay blocked.
- The Bash-only CONTROL fails both PowerShell cases. That is the gap this change closes.
- The plugin form behaves the same as the project form.

## What changed after the retest (tested offline only)

The live retest used the Episode 2 scripts with only the matcher changed: `Get-Content .env` is caught
because the text contains `.env`. For this pack the firewall also names PowerShell recursive searches
(`Select-String` / `sls` over `.` or `*`, `Get-ChildItem -Recurse | Select-String`), and the commit
gate's write guard also knows `Set-Content`, `Out-File`, `Add-Content`, `New-Item`, `Copy-Item`.
Those additions were tested by feeding the hooks synthetic tool calls (`bypass-tests/`), not in a new
live session. Run the live check in `WINDOWS-HOOKS.md` on your own machine.
