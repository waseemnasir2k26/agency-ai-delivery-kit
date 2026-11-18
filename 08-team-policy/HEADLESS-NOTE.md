# Headless note — what this policy does to scripted runs on a seat

Scripted runs (`claude -p …`, runners, the Agent SDK) obey the same managed file as interactive sessions. Two lines change how they behave.

## What changes

| Policy line                              | Effect on a scripted run                                                                                                                                                                                                                                                                                         |
| :--------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `allowManagedPermissionRulesOnly: true`  | `--allowedTools` is **ignored**, and so are allow rules in user, project and local settings and `--settings`. A tool the run needs that is not a managed allow rule is denied. A headless run starts in Manual mode and asks nobody, so the denial is silent unless you read `permission_denials` in the result. |
| `disableSideloadFlags: true`             | `--plugin-dir`, `--plugin-url`, `--agents`, `--mcp-config` (unless every server is `type: "sdk"`) and Agent SDK `plugins` are **rejected at startup** with a message naming `disableSideloadFlags`.                                                                                                              |
| `sandbox.autoAllowBashIfSandboxed: true` | Shell commands inside the wall run without a prompt, so headless shell work can proceed. Without it, every shell command needed a person and headless runs refused.                                                                                                                                              |
| `sandbox.failIfUnavailable: true`        | No sandbox, no run: the process exits at startup.                                                                                                                                                                                                                                                                |

## How the course runners are set up for it

- **Episode 6 (headless job runner).** Its `--allowedTools` list is ignored on a policy seat. Move each tool the job needs into the managed `permissions.allow` list (Bash + PowerShell twins, file rules as `Edit(…)`), added by the policy owner. Keep `--strict-mcp-config`; drop `--mcp-config` (rejected) unless every server is `type: "sdk"`.
- **Episode 9 (delivery pipeline).** On a seat, `pipeline.py` cannot use `--plugin-dir`, `--agents` or `--mcp-config`, and its `--allowedTools` is ignored. So `kiran-core` comes from the managed install; project edits run with `--permission-mode acceptEdits`; every other command the stages need (`python verify.py *`, `python site_watch.py *`, `git worktree *`, …, Bash + PowerShell twins) is a managed allow rule, added by the policy owner and covered by `policy_test.py`. Plan this before the first clean run, or the build stage is denied silently.
- **Episode 10 (evals).** The eval suite and `claude plugin eval` load the plugin with `--plugin-dir`, which a seat rejects. They run on a separate **eval machine** with this policy minus `disableSideloadFlags`, and the tools each case needs as managed allow rules (no `--allowedTools`). Restore the seat policy after the suite. Note: under the managed sandbox block, `claude plugin eval` refused a shell grant, so the plugin eval ran with no shell.

## Checklist for any new runner

- [ ] List every tool and command it needs. Ask the policy owner to add them as managed allow rules (`POLICY-OWNER.md`).
- [ ] No sideload flags on a seat. If it needs `--plugin-dir`, it runs on an eval machine.
- [ ] Read `permission_denials` in the run's result and fail the run if it is not empty.
- [ ] Re-run `policy_test.py` after the policy edit.
