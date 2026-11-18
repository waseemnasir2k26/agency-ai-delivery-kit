# Environment checklist — one per seat, before client work

Tick every line on every seat, and again after every Claude Code update and every policy edit.

## 1. Where the managed file lives (three system paths)

| System        | Path                                                            | Who can change it                                              |
| :------------ | :-------------------------------------------------------------- | :------------------------------------------------------------- |
| Windows       | `C:\Program Files\ClaudeCode\managed-settings.json`             | admin only                                                     |
| macOS         | `/Library/Application Support/ClaudeCode/managed-settings.json` | admin only                                                     |
| Linux and WSL | `/etc/claude-code/managed-settings.json`                        | root on Linux; **on WSL this folder is user-writable as well** |

- [ ] The file for this seat's system is in place (copy from `managed-settings.template*.json` **after** replacing `<org>` and `<collector>` and testing on a lab machine).
- [ ] **WSL:** the WSL user can usually become root inside their own distro, so a WSL-only policy is easy to change. `wslInheritsWindowsSettings: true` in the Windows file (or in HKLM) makes WSL follow the Windows policy chain instead. This line is **not tested** on the build: until you test it on your machine (steps in `README.md`), give WSL its own copy and check it on every seat.

## 2. Did it load?

- [ ] In a session, `/status` lists the setting sources. The managed entry (e.g. `Enterprise managed settings (file)`) must be there. **No managed entry = no policy on that machine.**
- [ ] `claude doctor` runs clean (installation, settings errors).
- [ ] Under a managed sandbox block, `/sandbox` does not open (it says the settings are overridden by a higher-priority configuration). That is expected. Prove the wall instead: in a session, ask for `touch ~/x` → `Read-only file system`.

## 3. Sandbox prerequisites (WSL2 / Linux / macOS)

- [ ] **WSL2, not WSL1:** `wsl -l -v` in PowerShell shows `VERSION 2` for the distro. The sandbox does not run on WSL1.
- [ ] **Linux / WSL2:** `bubblewrap` and `socat` installed: `sudo apt-get install bubblewrap socat` (Debian/Ubuntu). Check: `command -v bwrap socat`.
- [ ] **macOS:** built-in sandbox, nothing to install.
- [ ] With `sandbox.failIfUnavailable: true`, a missing prerequisite means Claude Code refuses to start. That is the policy working.

## 4. Native Windows

At recording, the sandbox ran on macOS, Linux and WSL2 only. In a normal Windows terminal, shell commands ran with **no sandbox**; permission rules still applied, the wall did not. With `failIfUnavailable: true`, Claude Code on native Windows refuses to start: client work runs inside WSL2. Whether the permission rules alone hold on native Windows is **not yet tested** (see `results/WINDOWS-RUN-PENDING.md`). Re-check the sandbox docs after every update: this may change.

## 5. Server-managed settings (company plans)

A cloud session never sees a file on a laptop. If your organisation is on a company plan with an admin console (Team or Enterprise), server-managed settings deliver policy from the console to every signed-in seat, including cloud sessions. This pack uses the file route because Kiran Studio is small; the keys are the same. Check the managed-settings docs for which keys the console supports.

## 6. Device ownership — the upgrade path

| Seat                    | What you can rely on                                                                                                                                                                                  |
| :---------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Freelancer-owned laptop | Policy file + `policy_test.py` result. A local admin (the freelancer) can edit the file: it is a guardrail for honest mistakes and injected instructions, not a lock against the owner of the device. |
| Agency-owned laptop     | Same, **plus** MDM (Intune, Jamf, …) deploys the file and puts it back if it changes, and the freelancer has no admin rights.                                                                         |

- [ ] Write down which kind each seat is, in `POLICY-OWNER.md`.

## 7. Last line

- [ ] `python3 policy_test.py` on this seat: `10/10 PASS | 0 NOT BLOCKED | 0 ERRORED`. Save the output with the seat name. Date it in `TEAM-POLICY.md`.
