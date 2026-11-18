# Scripted runs: keep a connector out of a script unless you mean it

In an interactive Claude Code session, the first time a folder is opened you are asked two things: do you trust
this folder, and may this project MCP server start? Until the folder is trusted, the project's allow rules do not count.

**Scripted runs do not ask.** `claude -p` (headless), Agent SDK programs and cloud sessions load the servers in a
project's `.mcp.json` without the approval prompt, when project settings are loaded. A script run from inside
`noor-bookings/` can start the booking connector with whatever key is in that machine's environment.

So a script's connector needs the same review as a person's: same tool list, same named allow rules, same read-only key.

## Ways to keep a server out of a script

| Option | What it does | Example |
|---|---|---|
| `--strict-mcp-config` | Use only the MCP servers given with `--mcp-config`; ignore `.mcp.json` and other configured servers | `claude -p "..." --strict-mcp-config --mcp-config ./script-mcp.json` |
| `--setting-sources user` | Load only user-level settings, so the project's settings (and its `.mcp.json` servers) are not loaded | `claude -p "..." --setting-sources user` |
| `disabledMcpjsonServers` | A settings key listing `.mcp.json` servers that must not start | `{ "disabledMcpjsonServers": ["noor-bookings"] }` in the settings the script loads |
| Agent SDK `setting_sources=[]` | The SDK loads no settings files, so a project's `.mcp.json` is not read; pass servers explicitly in `mcp_servers` | Site Watch does this (`site_watch.py`, `site_watch_noor.py`) |

## When a script should use the connector

Name it and its tools explicitly, as `site_watch_noor.py` does:

- the server in `mcp_servers` (command, args, env with the read-only key),
- exactly the tool names it needs in `allowed_tools` (one name, not a wildcard),
- `setting_sources=[]` so nothing else on the machine is pulled in.

For the Episode 5 captures, headless runs used `--setting-sources project,local` and `--strict-mcp-config` so that
user-level hooks and servers stayed out, and passed the allow/deny rules with `--allowedTools` / `--disallowedTools`.

Flags and setting names come from the Claude Code docs (https://code.claude.com/docs/en/mcp and /headless).
Re-check them after every Claude Code update.
