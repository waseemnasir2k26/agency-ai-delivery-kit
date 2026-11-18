# CHANGELOG — kiran-marketplace

Rule: no new version, no release. Every change to a plugin's files bumps its `plugin.json` version and adds one line here, newest first. `ci/check_kit.py` enforces it.

## kiran-core 1.1.0

- New `proposal` skill (Episode 9): brief -> `unknowns.json` (all `open`) + `proposal.md` (Scope · Unknowns · Client provides · Price from sheet).
- `critic` agent: new section "Claims a proposal may never make" (rankings, sales, traffic, deadline results, unfilled prices).

## kiran-core 1.0.0

- First packaged release: `client-report` and `pr-review` skills, `critic` agent, `secret-firewall` (Write|Edit|Bash|PowerShell) and `commit-gate` (Bash|PowerShell) hooks.

## kiran-noor 1.0.0

- First packaged release: `noor-bookings` MCP server (four read and draft tools), token by variable name `NOOR_API_TOKEN` only.
