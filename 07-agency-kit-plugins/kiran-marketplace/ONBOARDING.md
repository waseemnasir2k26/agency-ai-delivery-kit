# ONBOARDING — Kiran Studio kit (fictional agency, synthetic data)

Counted on a clean Claude Code profile (empty config folder) and a fresh clone of the Mehr Bakery repo, from the run, not from this list. Plugin commands change quickly: re-check this list after every Claude Code update.

**Shorter path: 4 commands · 1 prompt (the trust prompt).** Long path, also counted: 6 commands · 1 prompt.

Replace `<your-org>` with the GitHub organisation that holds your private `kiran-marketplace` repo.

## Shorter path (use this one)

0. Owner: give read access to the client repo and to `<your-org>/kiran-marketplace`.
1. Sign in to git once so it never has to ask. Claude Code clones the catalogue with prompts turned off, so a credential must already be stored. GitHub: `gh auth login`, then `gh auth setup-git`. No GitHub SSH key on this machine? Set `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` first (PowerShell: `$env:CLAUDE_CODE_PLUGIN_PREFER_HTTPS = "1"`).
2. `git clone <client repo>` and `cd` into it.
3. Read `hooks/hooks.json` and the scripts in `scripts/` of `kiran-core` in `<your-org>/kiran-marketplace` (see `HOOK-REVIEW-CHECKLIST.md`). Hooks run as you, on your machine.
4. `claude plugin install kiran-core --marketplace <your-org>/kiran-marketplace --scope project`. The `--marketplace` flag adds the catalogue to your **user** settings and installs in one step, before the first session.
5. `claude`. Read the trust prompt, then answer it.
6. Ready when: `claude plugin list` shows `kiran-core@kiran-marketplace`, `Scope: project`, `Status: ✔ enabled`, version = the newest `kiran-core` line in `CHANGELOG.md`; typing `/kiran` lists the `/kiran-core:` commands (`client-report`, `pr-review`, `proposal`).
7. When `CHANGELOG.md` moves (a new release): `claude plugin marketplace update kiran-marketplace`, then `claude plugin update kiran-core@kiran-marketplace`, then restart. `plugin update` alone does NOT re-read the catalogue and answers "already at the latest version".
8. When the client repo's pinned tag moves (in a reviewed commit): `claude plugin marketplace add <your-org>/kiran-marketplace#kiran-core--v<new> --scope project`, then `claude plugin update kiran-core@kiran-marketplace --scope project`. Editing `"ref"` in `.claude/settings.json` by hand does not re-point a catalogue that is already registered.

## Install-order warning

Never run a plain `claude plugin install kiran-core@kiran-marketplace` before your first trusted session in that clone. Until you answer the trust prompt, your machine does not know the catalogue exists, and install says `Plugin "kiran-core" not found in marketplace "kiran-marketplace"`. Nothing is misspelled. Use the shorter path (it names the marketplace), or start `claude` and answer the trust prompt first.

## Long path (6 commands · 1 prompt)

1. `git clone <client repo>` · 2. `cd` into it · 3. `claude`, answer the trust prompt (trust registers the catalogue and loads the kit **for this session only**) · 4. in the session: `! claude plugin install kiran-core@kiran-marketplace --scope project` · 5. `/reload-plugins` · 6. `! claude plugin list` (ready when step 6 of the shorter path holds).

## Noor Dental Clinic repo

Also `claude plugin install kiran-noor@kiran-marketplace --scope project`, a Python 3.11+ with `pip install -r requirements.txt` from the plugin folder (set `NOOR_PYTHON` if plain `python` lacks the `mcp` package), and `NOOR_API_TOKEN` set in the shell (read-only key), never in a file. Expect one extra approval for the `noor-bookings` server in an interactive session (from the docs; not captured on the build). So the count is per repo.

## What the trust prompt means

The repo's `.claude/settings.json` is somebody else's file until you trust the folder. Before you answer, its deny and ask rules already apply, but its allow rules and the declared catalogue (`extraKnownMarketplaces`) wait. After "Yes", Claude Code registers `kiran-marketplace` and can load `kiran-core` for that one session. `enabledPlugins` in the committed file is a request: it turns the kit on, it does not download it for good. The install command does that, once per person, per clone. Trusting a parent folder is not the same as trusting this one.
