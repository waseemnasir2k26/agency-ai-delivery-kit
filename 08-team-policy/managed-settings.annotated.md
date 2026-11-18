# managed-settings — annotated

> **EXAMPLE ONLY. Never apply this file as it stands.** It is the Episode 8 policy for a fictional agency, with placeholders `<org>` (your GitHub organisation) and `<collector>` (your telemetry collector host). A managed file binds **every** Claude Code session on the machine, including yours: it starts in Manual mode, refuses `--plugin-dir` / `--mcp-config`, and with `failIfUnavailable` refuses to start where no sandbox runs (native Windows). Test on a lab machine first, back up any existing file, and keep a rollback command ready.

Settings JSON accepts no comments, so the notes live here. Files: `managed-settings.template.json` (Windows, with the WSL line) · `managed-settings.template.linux-macos.json` (same, without `wslInheritsWindowsSettings`, launcher path for Linux/macOS only). Tests refer to `policy_test.py` lines; "not tested" means exactly that.

Docs: settings https://code.claude.com/docs/en/settings · reference https://code.claude.com/docs/en/settings-reference · managed https://code.claude.com/docs/en/managed-settings

---

### `wslInheritsWindowsSettings: true` (Windows file only)

- **Stops:** WSL sessions reading only the WSL policy folder, which is user-writable on WSL. With it, WSL follows the Windows policy chain (HKLM or `C:\Program Files\ClaudeCode\`).
- **Does NOT stop:** a local admin editing the Windows file.
- **Test:** **not tested** on the build (owner-pending). Until you test it, give WSL its own copy at `/etc/claude-code/managed-settings.json` and check it on every seat (`/status`).
- **Docs:** https://code.claude.com/docs/en/managed-settings

### `permissions.deny`: `Read(./.env)`, `Read(./.env.*)`, `Read(./secrets/**)`

- **Stops:** Claude's own file tools reading key files. Deny is checked first, then ask, then allow.
- **Does NOT stop:** a script that opens the file itself (that is the sandbox's job), or a mod (mods are not sandboxed; see `pluginConfigs`).
- **Test:** T2a (`File is in a directory that is denied by your permission settings.`).
- **Docs:** https://code.claude.com/docs/en/permissions

### `permissions.ask`: `Bash(git push *)`, `PowerShell(git push *)`

- **Stops:** code leaving the laptop without a person saying yes. Written once per shell: every shell rule has a Bash and a PowerShell twin.
- **Does NOT stop:** a push through a tool that is not Bash or PowerShell, or argument tricks (argument-matching patterns are fragile).
- **Test:** T1b.
- **Docs:** https://code.claude.com/docs/en/permissions

### `permissions.allow`: the four `mcp__plugin_kiran-noor_noor-bookings__<tool>` names

- **Stops:** nothing by itself; it lets the four approved connector tools run without a prompt. One line per tool, no wildcard for the whole connector.
- **Does NOT stop:** a fifth tool appearing in a new server version (it will ask, not run).
- **Test:** preflight (connector connected); tool names copied from `/mcp` with the plugin loaded.
- **Docs:** https://code.claude.com/docs/en/permissions · https://code.claude.com/docs/en/mcp

### `permissions.disableBypassPermissionsMode: "disable"`

- **Stops:** `--dangerously-skip-permissions` / `bypassPermissions`. In our runs these did not error: the session silently started in default mode.
- **Does NOT stop:** a local admin removing the line.
- **Test:** extra capture (bypass refusal), not a `policy_test.py` line.
- **Docs:** https://code.claude.com/docs/en/permission-modes

### `permissions.disableAutoMode: "disable"`

- **Stops:** auto mode, where an automatic reviewer approves actions instead of a person. Owner decision: on client work a person answers.
- **Does NOT stop:** nothing else; it only removes that mode. The session's init field may briefly report `auto` before the gate switches it back, so test behaviour, not the field.
- **Test:** T5.
- **Docs:** https://code.claude.com/docs/en/permission-modes

### `allowManagedPermissionRulesOnly: true` (lock 1)

- **Stops:** user, project, local and `--settings` rules, and `--allowedTools`, from adding permissions. A client repo's own `.claude/settings.json` allow lines do not count. Also hides "always allow" choices in prompts.
- **Does NOT stop:** prompts themselves (a person can still say yes once). It also breaks scripted runs that relied on `--allowedTools`: see `HEADLESS-NOTE.md`.
- **Test:** T1a, T1b (with the lock removed on purpose, both were let through).
- **Docs:** https://code.claude.com/docs/en/settings-reference

### `strictKnownMarketplaces: [{ "source": "github", "repo": "<org>/kiran-marketplace" }]`

- **Stops:** adding any other marketplace (`… is blocked by enterprise policy`).
- **Does NOT stop:** `--plugin-dir` (that is `disableSideloadFlags`).
- **Test:** T4a. Tested with a `directory` source on the lab; the `github` form is the documented shape.
- **Docs:** https://code.claude.com/docs/en/plugins/org

### `extraKnownMarketplaces` → `kiran-marketplace`

- **Stops:** nothing; it declares the approved catalogue so every seat knows it.
- **Does NOT stop:** —
- **Test:** preflight (both plugins loaded).
- **Docs:** https://code.claude.com/docs/en/plugins/org

### `enabledPlugins`: `kiran-core`, `kiran-noor`

- **Stops:** nothing; switches the approved plugins on for every seat.
- **Does NOT stop:** a missing install on a fresh seat (enabled is not installed; see module 07 `ONBOARDING.md`).
- **Test:** preflight.
- **Docs:** https://code.claude.com/docs/en/plugins/org

### `disableSideloadFlags: true`

- **Stops:** `--plugin-dir`, `--plugin-url`, `--agents`, `--mcp-config` (unless all servers are `type: "sdk"`), and Agent SDK `plugins`.
- **Does NOT stop:** plugins from the approved marketplace. It also stops your own scripted runners and plugin evals that use those flags: see `HEADLESS-NOTE.md`.
- **Test:** T4c (`--plugin-dir is disabled by your organization's managed settings (disableSideloadFlags)`).
- **Docs:** https://code.claude.com/docs/en/plugins/org

### `pluginConfigs` → `cc-plugin-sec-default@builtin` → `options.allowManagedModsOnly: true`

- **Stops:** mods (plugins that run code inside Claude Code) except the organisation's and the built-in ones. Mods are not sandboxed and can read a denied file.
- **Does NOT stop:** an approved mod doing something you did not review.
- **Test:** **not tested** by `policy_test.py` (docs only).
- **Docs:** https://code.claude.com/docs/en/plugins/mods/admin

### `allowedMcpServers` (connector rule) + `allowManagedMcpServersOnly: true`

- **Stops:** any MCP connector whose start command is not on the list (`Cannot add MCP server "<name>": not allowed by enterprise policy`). Matched by **command**, not name: anyone can give a connector any name (`serverName` is not a security control).
- **Does NOT stop:** a listed command doing more than you expect.
- **Must know:** only the full, exact, expanded command matched. A `${CLAUDE_PLUGIN_ROOT}` entry never matched, and no `serverName` form matched a plugin server. The tested design: the admin installs a fixed launcher (`C:\ProgramData\KiranStudio\bin\noor-bookings.cmd` on Windows, `/opt/kiran/bin/noor-bookings` on Linux/WSL), the plugin's `mcpServers` command calls that launcher, and the rule names that path. The `kiran-noor` plugin in module 07 starts `server.py` from its own folder; under this policy, ship a variant that calls the launcher (`scripts/setup-root.sh` builds one), or the connector silently disappears from `claude mcp list`.
- **Test:** T4b; connector-match probes in `scripts/v1_connector_match.sh`, `scripts/v1b_fixed_form.sh`. Windows launcher path **not tested**.
- **Docs:** https://code.claude.com/docs/en/managed-mcp

### `sandbox.enabled: true`

- **Stops:** shell commands (Bash, PowerShell, Monitor) and every program they start from writing outside the project folder or reaching hosts off the list.
- **Does NOT stop:** Claude's file tools, MCP servers and hooks (they run outside the sandbox), or anything on native Windows (no sandbox there at recording).
- **Test:** T2b, T2c.
- **Docs:** https://code.claude.com/docs/en/sandboxing

### `sandbox.autoAllowBashIfSandboxed: true`

- **Stops:** nothing; commands that stay inside the wall run without a prompt. Deny and ask rules still apply (`git push` still asks). Without it, every shell command asked a person, headless runs refused, and the wall was never reached.
- **Does NOT stop:** —
- **Test:** T2b/T2c reach the wall because of it.
- **Docs:** https://code.claude.com/docs/en/sandboxing

### `sandbox.network.allowedDomains` + `allowManagedDomainsOnly: true`

- **Stops:** shell traffic to any host not on the list, blocked without a prompt, in every permission mode. Only managed `allowedDomains` and managed `WebFetch(domain:…)` rules count.
- **Does NOT stop:** traffic to an allowed host (keep the list short; `github.com` is broad).
- **Test:** T2c (`deny network-outbound example.com:443`).
- **Docs:** https://code.claude.com/docs/en/sandboxing

### `sandbox.failIfUnavailable: true` (fix 1)

- **Stops:** Claude Code starting without a working sandbox (`Refusing to start without a working sandbox`). Fails closed.
- **Does NOT stop:** other tools, or an admin removing the line. On native Windows it means Claude Code does not start at all.
- **Test:** T3 (NOT BLOCKED before the fix, BLOCKED after). Native Windows: **owner-pending**, see `results/WINDOWS-RUN-PENDING.md`.
- **Docs:** https://code.claude.com/docs/en/sandboxing

### `sandbox.allowUnsandboxedCommands: false` (fix 1)

- **Stops:** a blocked command being retried outside the sandbox.
- **Does NOT stop:** —
- **Test:** part of the T3 fix; no separate line.
- **Docs:** https://code.claude.com/docs/en/sandboxing

### `env` (telemetry): `CLAUDE_CODE_ENABLE_TELEMETRY`, `OTEL_LOGS_EXPORTER`, `OTEL_METRICS_EXPORTER`, `OTEL_EXPORTER_OTLP_PROTOCOL`, `OTEL_EXPORTER_OTLP_ENDPOINT=http://<collector>:4318`, `OTEL_LOGS_EXPORT_INTERVAL`, `OTEL_RESOURCE_ATTRIBUTES=team.id=<org>,seat=…`

- **Stops:** nothing. Records tool activity to your collector.
- **Does NOT record:** every refusal (a Read deny wrote no event in our runs), command text, tool output, prompts. Those need extra switches and are a privacy decision: see `otel-console-setup.md`.
- **Test:** event samples captured on the lab (hook reject, config accept, mode change).
- **Docs:** https://code.claude.com/docs/en/monitoring-usage
