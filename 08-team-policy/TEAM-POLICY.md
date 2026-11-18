# TEAM-POLICY — Kiran Studio AI use on client work (fictional agency)

One page the owner can attach to a client's security questionnaire. Two versions: the one written first (v1), and the one after the tests found a gap (v2, the one to send). Each line names the `policy_test.py` line that checks it. Replace Kiran Studio, the plugins and the connector with your own.

## The five questions this page answers

1. What may the AI read?
2. What may it change?
3. What needs a person first?
4. Which add-ons are approved?
5. What gets recorded?

---

## v2 — after the fix (send this one)

**Kiran Studio · AI policy for client work · Claude Code**

|                      | Rule                                                                                                                                                                                      | Checked by                           |
| :------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------- |
| **READ**             | The project folder. Never `.env`, `.env.*` or `secrets/`.                                                                                                                                 | T2a, T2b                             |
| **CHANGE**           | Files inside the project only.                                                                                                                                                            | sandbox (T2b/T2c run inside it)      |
| **ASK A PERSON**     | Anything that leaves the laptop, such as `git push`. A person answers, never an automatic reviewer. Project files cannot loosen this.                                                     | T1a, T1b, T5                         |
| **APPROVED**         | Plugins `kiran-core` and `kiran-noor` from `kiran-marketplace` only. Connector `noor-bookings` (4 named read and draft tools). No other marketplaces, plugin folders, connectors or mods. | T4a, T4b, T4c                        |
| **NETWORK**          | Shell commands reach only the approved short list (package registry, GitHub). Everything else is blocked without a prompt.                                                                | T2c                                  |
| **WHERE**            | Client work runs inside WSL2, macOS or Linux only. Claude Code refuses to start where the sandbox cannot run.                                                                             | T3                                   |
| **RECORDED**         | Tool activity: what ran, and what a hook or a person turned down. Not every blocked file read. Command text and file contents are not recorded by default.                                | record (see `otel-console-setup.md`) |
| **POLICY OWNER**     | `<name>` · only the policy owner changes this page and the managed settings file.                                                                                                         |                                      |
| **LAST TEST PASSED** | `<date>` · `policy_test.py` `10/10 PASS` · approved by `<policy owner>`                                                                                                                   | all                                  |

What this page is: guardrails for honest mistakes and injected instructions, plus an activity record. What it is not: a promise. A person with admin rights on a laptop can get around it; other tools that call the API are outside it; cloud sessions need their own server-managed settings.

---

## v1 — before the fix (kept to show what changed)

**Kiran Studio · AI policy for client work · Claude Code**

|                  | Rule                                                                                                                                 |
| :--------------- | :----------------------------------------------------------------------------------------------------------------------------------- |
| **READ**         | The project folder. Never `.env`, `.env.*` or `secrets/`.                                                                            |
| **CHANGE**       | Files inside the project.                                                                                                            |
| **ASK A PERSON** | `git push`. A person answers, never an automatic reviewer.                                                                           |
| **APPROVED**     | `kiran-core`, `kiran-noor` from `kiran-marketplace` · connector `noor-bookings` (4 named tools) · no other plugins, folders or mods. |
| **RECORDED**     | Tool activity (what ran · hook and prompt refusals) · not every blocked file read.                                                   |
| **POLICY OWNER** | `<name>` · **LAST TEST PASSED:** `<date>`                                                                                            |

**What v1 missed:** nothing said where the work may run. Working inside WSL was a habit, not a rule. The test `T3 sandbox required on this machine` was `NOT BLOCKED` under the v1 policy: a session could start with no sandbox and run commands stopped only by the permission rules. The fix was two lines in the managed file (`sandbox.failIfUnavailable: true`, `sandbox.allowUnsandboxedCommands: false`) and the **WHERE** and **LAST TEST PASSED** lines on this page.
