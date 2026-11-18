# 08 · Team policy — Team Policy Pack

**For the owner:** a client's security questionnaire asks what your AI tools may do with their files, and today the honest answer is "it depends whose laptop". This pack gives you a one-page policy you can attach, Claude Code managed settings that enforce it in four layers, and a regression test that proves it on each seat after every update.

**Shown in:** Episode 8, "The page, and the four layers", "Layer two: managed settings, one file for Windows and WSL", "Layer three: the sandbox", "Layer four: the activity record", "Test 1: a client project tries to loosen a rule", "Test 2: the README that talks to the AI", "Fail closed, then the same test again", "policy_test.py: the test that stays", "The page, updated".

**Prerequisites:** Claude Code, admin rights on your own machine to place the managed file, and WSL2 if you are on Windows (with `bubblewrap` + `socat`). Python 3 inside WSL/Linux/macOS. Module `07-agency-kit-plugins` next to this folder (the lab builds its plugins from it). Kiran Studio, Sufi Threads and Noor Dental Clinic are fictional; all data is synthetic.

> **The managed-settings files are EXAMPLES. Never apply them as they stand.** A managed file binds every Claude Code session on the machine, yours included. Use a lab machine, back up first, keep the rollback command ready.

## What's inside

| Path                                                                          | What it is                                                                                                                                                                                                                 |
| :---------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `TEAM-POLICY.md`                                                              | The one-page policy, v1 (before) and v2 (after the fix), the five questions, the owner line, test line per row.                                                                                                            |
| `policy-matrix.md`                                                            | Role × action × data table behind the page, with the test line for each cell.                                                                                                                                              |
| `managed-settings.template.json`                                              | EXAMPLE Windows managed file (with `wslInheritsWindowsSettings`), placeholders `<org>` and `<collector>`.                                                                                                                  |
| `managed-settings.template.linux-macos.json`                                  | EXAMPLE Linux/macOS variant, without the WSL line.                                                                                                                                                                         |
| `managed-settings.annotated.md`                                               | One note per key: what it stops, what it does NOT stop, which test answered it, docs link.                                                                                                                                 |
| `ENVIRONMENT-CHECKLIST.md`                                                    | Per-seat checklist: three system paths, WSL folder + `wslInheritsWindowsSettings`, `/status` + `claude doctor`, WSL2 check, `bubblewrap` + `socat`, server-managed settings, native Windows, device ownership + MDM.       |
| `HEADLESS-NOTE.md`                                                            | What the policy does to scripted runs (`--allowedTools` ignored; `--plugin-dir`, `--agents`, `--mcp-config` rejected) and how the Episode 6, 9 and 10 runners are set up for it.                                           |
| `policy_test.py`                                                              | The regression test: one line per attack, BLOCKED / NOT BLOCKED / ERRORED; only BLOCKED is PASS. Exit 0 all pass · 1 any NOT BLOCKED · 2 any ERRORED · 3 preflight failed. `--help` prints usage without running anything. |
| `lab/mock_api.py`                                                             | Scripted local stand-in for the model (FORCED TEST): Claude Code decides every result, no model calls, no spend.                                                                                                           |
| `lab/otel_sink.py`                                                            | Tiny local OpenTelemetry log server (OTLP HTTP/JSON on `127.0.0.1:4318`), stdlib only.                                                                                                                                     |
| `fixture/sufi-threads/`                                                       | Client repo fixture: planted README injection comment, fake `.env` (`DEMO_KEY=not-a-real-key`), `.env.example`, planted `.claude/settings.json`, `leak.py`, `read_probe.py`, `send_probe.py`.                              |
| `fixture/friends-plugin/`                                                     | Throwaway "plugin a friend zipped up" for the sideload test.                                                                                                                                                               |
| `policy/managed-settings.wsl*.json`                                           | The three tested LAB policies: `pre-fix`, post-fix (`managed-settings.wsl.json`), `LOCK1-OFF` (wrong on purpose). `directory` marketplace at `/opt/kiran`.                                                                 |
| `scripts/setup-root.sh`                                                       | Admin side of the lab: `/opt/kiran` venv, marketplace mirror, fixed connector launcher `/opt/kiran/bin/noor-bookings`.                                                                                                     |
| `scripts/setup-user.sh`                                                       | User side: `~/ep08-lab` with the test, helpers, fixture git repo, throwaway remote, trust flag.                                                                                                                            |
| `scripts/policy.sh`                                                           | Installs a lab policy variant: `pre-fix` / `post-fix` / `lock1-off` / `none`.                                                                                                                                              |
| `scripts/capture-all.sh`                                                      | Full capture run (policy swaps + every attack) into `captures/`.                                                                                                                                                           |
| `scripts/v1_connector_match.sh`, `scripts/v1b_fixed_form.sh`                  | Probes: which `allowedMcpServers` entry matches a plugin-started connector.                                                                                                                                                |
| `otel-console-setup.md`                                                       | What the activity record keeps and leaves out, setup, and the one-page detail logging decision form.                                                                                                                       |
| `otel/collector-config.yaml`                                                  | Example OpenTelemetry Collector config (console + local file, retention).                                                                                                                                                  |
| `POLICY-OWNER.md`                                                             | New allow rule request form, auto mode decision record, rerun rule, seat register.                                                                                                                                         |
| `OPTIONAL-LINES.md`                                                           | Off by default, untested: `allowManagedHooksOnly`, `availableModels` + `enforceAvailableModels`, `syncClaudeAiPlugins: false`, `permissions.denyInsteadOfPrompting`.                                                       |
| `results/policy_test.wsl.pre-fix.txt`, `results/policy_test.wsl.post-fix.txt` | Recorded sample results from the WSL2 lab (9/10 then 10/10).                                                                                                                                                               |
| `results/WINDOWS-RUN-PENDING.md`                                              | The native Windows run is not done yet: status and how to run it.                                                                                                                                                          |

## Use it in 5 steps

Run the lab inside WSL2 / Linux. From Windows, open PowerShell and use `wsl -d <distro>`; in Git Bash set `export MSYS_NO_PATHCONV=1` first. Below, `KIT8` is this folder's path **as seen inside WSL**, e.g. `KIT8=/mnt/<drive>/<path-to-kit>/08-team-policy`.

1. **Prerequisites check** (inside WSL/Linux):
   ```bash
   claude --version && python3 --version && command -v bwrap socat   # Linux/WSL2
   ```
   On Windows also `wsl -l -v` → `VERSION 2`. Missing sandbox tools: `sudo apt-get install bubblewrap socat`. Check the offline parts: `python3 $KIT8/policy_test.py --help`.
2. **Build the lab** (admin side as root, then user side; plugins come from `../07-agency-kit-plugins`):
   ```bash
   sudo bash $KIT8/scripts/setup-root.sh
   claude plugin marketplace add /opt/kiran/kiran-marketplace
   claude plugin install kiran-core@kiran-marketplace && claude plugin install kiran-noor@kiran-marketplace
   bash $KIT8/scripts/setup-user.sh
   ```
   (No `sudo` password in WSL? Use `wsl -d <distro> -u root -- bash $KIT8/scripts/setup-root.sh` from PowerShell.)
3. **Install the lab policy and run the test:**
   ```bash
   sudo bash $KIT8/scripts/policy.sh pre-fix   && (cd ~/ep08-lab && python3 policy_test.py)   # expect 9/10, T3 NOT BLOCKED
   sudo bash $KIT8/scripts/policy.sh post-fix  && (cd ~/ep08-lab && python3 policy_test.py)   # expect 10/10 PASS
   sudo bash $KIT8/scripts/policy.sh none                                                     # remove the lab policy
   ```
   Compare with `results/`. Optional full capture: `sudo env LAB_USER=$USER bash $KIT8/scripts/capture-all.sh`.
4. **Write your real policy.** Fill `TEAM-POLICY.md` and `POLICY-OWNER.md`. Copy the right template, replace `<org>` and `<collector>`, adjust allow rules and the connector launcher path, and read every note in `managed-settings.annotated.md`. Place it at the system path for each seat (`ENVIRONMENT-CHECKLIST.md`), and check `/status` shows the managed entry.
5. **Prove it on every seat.** Run `policy_test.py` on each seat after every Claude Code update, every policy edit and every new seat; save the output with the seat name; update **LAST TEST PASSED** in `TEAM-POLICY.md`. Native Windows seats: follow `results/WINDOWS-RUN-PENDING.md`.

**Testing `wslInheritsWindowsSettings` (owner-pending):** place the Windows file at `C:\Program Files\ClaudeCode\managed-settings.json` (elevated), remove the WSL file (`policy.sh none`), then inside WSL run `claude` → `/status` (managed entry present?) and `python3 ~/ep08-lab/policy_test.py`. For this check only, add the lab's `directory` marketplace entry (`/opt/kiran/kiran-marketplace`) to both marketplace keys, or the preflight fails. Roll back afterwards.

## Limits — what it does NOT do

- It is guardrails for honest mistakes and injected instructions, plus a record. It is not a promise.
- A person with admin rights on the laptop can edit or remove the managed file. On a freelancer-owned laptop that is the freelancer. An agency-owned device with MDM can restore the file; this pack does not set up MDM.
- It binds Claude Code only. Other tools that call the API are outside it.
- Cloud sessions never see a laptop file; they need server-managed settings (company plan with an admin console).
- The sandbox covers shell commands and the programs they start, on macOS, Linux and WSL2 at recording. Claude's file tools, connectors and hooks run outside it. Native Windows had no sandbox; the native Windows run is **not done** (see `results/WINDOWS-RUN-PENDING.md`).
- Mods are not sandboxed; the policy refuses every mod except the organisation's and built-in ones (not covered by `policy_test.py`).
- The activity record is not a complete audit trail: a Read deny wrote no event in our runs.
- `wslInheritsWindowsSettings`, the Windows launcher path, the GitHub marketplace form and the optional lines were not tested on the build.
- `policy_test.py` uses a scripted stand-in for the model, so it tests Claude Code's decisions, not what a real model would choose when it reads the planted README.
- The `kiran-noor` plugin in module 07 starts its server from the plugin folder; the connector rule cannot match that path. The lab builds a launcher variant; do the same for production.

## Tested

Offline for the kit: `policy_test.py` compiles and `--help` runs without calling Claude Code; `lab/mock_api.py` and `lab/otel_sink.py` compile and import; every policy JSON parses; template vs tested post-fix policy diffed (only the expected placeholder/WSL differences); every script passes `bash -n`. The full `policy_test.py` run needs WSL + admin and was SKIPPED here; the recorded WSL2 lab results are in `results/`.
