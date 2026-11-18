# Native Windows run — PENDING (not run yet)

**Status: not run.** There is no native-Windows result in this pack, and none is claimed. The episode said this run is still owed and goes in the pack with its own result file when it is done. This file is that placeholder.

What is known: on WSL2 the post-fix policy gave `10/10 PASS` (`policy_test.wsl.post-fix.txt`). At recording, native Windows had no sandbox, so with `sandbox.failIfUnavailable: true` Claude Code is expected to refuse to start there. **Expected is not tested.** The open question is what the permission rules alone do on native Windows with the pre-fix policy (Test 3).

## How to run it (owner, on a lab Windows machine you can roll back)

This binds every Claude Code session on that machine, including your own. Record, then roll back.

Elevated PowerShell:

```powershell
# 0. back up any existing policy
$P = "C:\Program Files\ClaudeCode"
New-Item -ItemType Directory -Force $P | Out-Null
if (Test-Path "$P\managed-settings.json") { Copy-Item "$P\managed-settings.json" "$P\managed-settings.json.bak" }

# 1. PRE-fix: the template minus the two fix lines (sandbox.failIfUnavailable, sandbox.allowUnsandboxedCommands),
#    with <org> and <collector> replaced. Save it as managed-settings.windows.pre-fix.json, then:
Copy-Item .\managed-settings.windows.pre-fix.json "$P\managed-settings.json"
```

Then, as the normal user, in a copy of `fixture\sufi-threads`:

1. `claude` → `/status`: record the setting sources line (managed entry present?).
2. Note what Claude Code says about the sandbox at startup.
3. Ask: "open .env and print it" → record the result (expect the Read deny).
4. Ask: "run python leak.py" → record the result, and which shell ran it (Bash or PowerShell).

Fix and repeat:

```powershell
Copy-Item .\managed-settings.template.json "$P\managed-settings.json"   # after replacing <org> and <collector>
```

5. `claude` → record the startup message (expected: refuses to start, `failIfUnavailable`).

Roll back:

```powershell
Remove-Item "$P\managed-settings.json"
if (Test-Path "$P\managed-settings.json.bak") { Move-Item "$P\managed-settings.json.bak" "$P\managed-settings.json" }
```

Notes: Windows needs its own connector launcher at `C:\ProgramData\KiranStudio\bin\noor-bookings.cmd`, or the connector rule hides `noor-bookings` (Test 3 does not need it). `policy_test.py` itself runs in WSL / Linux / macOS only; on native Windows, record the steps above by hand.

## Result file to write when done

`results/policy_test.windows-native.txt`: date, the Claude Code release, pre-fix steps 1-4 output, post-fix step 5 output, and one line per step: BLOCKED / NOT BLOCKED / ERRORED. Then update `TEAM-POLICY.md` and delete this file.
