# Advanced checks — everything cut from the video

One page. Run through it before the second person joins, and again after every Claude Code update (plugin commands change quickly; re-check the official docs on the day you build).

1. **Source paths.** Every plugin `source` in `marketplace.json` stays inside the marketplace repo (`./plugins/<name>`). A `..` in a `source` fails `claude plugin validate`. A `source` that points at a missing directory **passes** validate and fails only at install, so `check_kit.py` also checks that `plugin.json` exists there.

2. **Trust.** Until a person answers the trust prompt, a repo's `.claude/settings.json` can restrict but not add: deny and ask rules apply at once; allow rules and declared marketplaces (`extraKnownMarketplaces`) wait for the answer. Trusting a parent folder is not enough: each clone is trusted on its own.

3. **Context trimming.** Every installed skill and agent puts its description into each session. Read `claude plugin details <plugin>@<marketplace>` for the size, shorten long descriptions, mark human-only skills so Claude does not load their label (`disable-model-invocation: true` in the skill's front matter), and move rarely used skills into a second plugin.

4. **Namespaced commands.** After the move into a plugin, `/client-report` becomes `/kiran-core:client-report`. Search and replace the old names in docs, scripts, scheduled jobs and checklists. Re-check permission rules against the tool names shown with the plugin loaded (connectors become `mcp__plugin_<plugin>_<server>__<tool>`).

5. **Double-firing hooks.** If a hook used to live in a project's `.claude/settings.json` and now ships in the plugin, delete the project copy. Otherwise the same hook runs twice on every call.

6. **Private repo access.** Claude Code never prompts for Git credentials when it clones a catalogue; a credential must already be stored (`gh auth login` + `gh auth setup-git`, or an SSH key; no SSH key → `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1`). `file://` and `git://` marketplace sources are rejected. A "dumb" HTTP git server fails, because the clone is shallow. In CI, a private marketplace needs a read token (`GH_TOKEN` + `gh auth setup-git`).

7. **Auto-update.** Auto-update is off by default for your own marketplace. Decide who may switch it on, and write it down. Client work often prefers a pinned tag (`"ref": "kiran-core--v<version>"`), moved only in a reviewed commit, so a release never lands in a client repo by surprise.

8. **Plugin evals.** `claude plugin eval` tests a plugin's skills (Episode 10). It makes model calls, so it spends money: set a cap first.

9. **Client plugins with an MCP server.** Expect one extra approval prompt per server in each clone (from the docs; not captured on the build). Count it in the onboarding numbers for that repo.

10. **Cloud sessions.** Local and repository-enabled plugins do not load in cloud sessions. Cloud work needs its own setup.

11. **Headless runs.** After trust, `claude -p` registers the catalogue but never loads a kit that is not installed. An **installed** project-scope plugin did load in a headless run in a folder that was never trusted (interactive sessions still ask for trust first). Do not rely on trust to keep an installed plugin out of scripted runs.

12. **Session-only load.** After trust, a kit from a relative-path catalogue loads for that one interactive session; `/reload-plugins` brings it back for one session only. Only `claude plugin install` makes it stay.
