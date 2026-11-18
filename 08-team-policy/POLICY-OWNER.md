# POLICY-OWNER — who changes the rules, and how

**Policy owner:** `<name>` · **Backup:** `<name>` · Only the policy owner edits `TEAM-POLICY.md` and the managed settings file.

## 1. Requesting a new allow rule (freelancer → owner)

Copy, fill in, send to the policy owner. One request per rule.

| Field                                                                                                                         | Answer |
| :---------------------------------------------------------------------------------------------------------------------------- | :----- |
| Requested by / date                                                                                                           |        |
| Client project(s)                                                                                                             |        |
| The exact rule(s), with the Bash **and** PowerShell twin (e.g. `Bash(python verify.py *)` + `PowerShell(python verify.py *)`) |        |
| Why it is needed (which job, which step)                                                                                      |        |
| What it could do if misused (files it touches, hosts it reaches)                                                              |        |
| Narrower alternative considered                                                                                               |        |
| Allow, or ask (a person decides each time)?                                                                                   |        |
| Owner decision (approve / narrow / refuse) and reason                                                                         |        |
| `policy_test.py` rerun after the change: result                                                                               |        |

Rules for the owner: name commands, not whole tools (`Bash(git status)`, never `Bash`). No wildcard for a whole connector: one line per MCP tool. Network: add a host to `sandbox.network.allowedDomains` only for a named reason; broad domains (whole cloud providers) are refused.

## 2. Auto mode decision record

Auto mode hands the permission question to an automatic reviewer instead of a person.

|                                 |                                                                                                                                               |
| :------------------------------ | :-------------------------------------------------------------------------------------------------------------------------------------------- |
| Decision                        | **Off** on every seat for client work (`permissions.disableAutoMode: "disable"`; bypass also off: `disableBypassPermissionsMode: "disable"`). |
| Why                             | On client work a person answers. A reviewer that approves most actions is useful on your own experiments, not on a client's files.            |
| Where it may be on              | Own experiments on a machine without this policy. Never on a seat with client repos.                                                          |
| How it is checked               | `policy_test.py` T5 (session asked for auto; the call still needed a person).                                                                 |
| Decided by / date / review date |                                                                                                                                               |

## 3. The rerun rule

`policy_test.py` is rerun, and the result saved with the seat name:

- after **every Claude Code update** on a seat,
- after **every policy edit** (including a new allow rule),
- on **every new seat** before its first client job.

Only `10/10 PASS | 0 NOT BLOCKED | 0 ERRORED` counts. An `ERRORED` line is never a pass: a test that did not run proved nothing. Then update the **LAST TEST PASSED** line in `TEAM-POLICY.md`.

## 4. Seat register

| Seat         | Person | Device owner (freelancer / agency + MDM) | OS / WSL2 | Last `policy_test.py` result + date |
| :----------- | :----- | :--------------------------------------- | :-------- | :---------------------------------- |
| freelancer-1 |        |                                          |           |                                     |
| freelancer-2 |        |                                          |           |                                     |
