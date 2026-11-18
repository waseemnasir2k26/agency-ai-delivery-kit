# 07 · Agency kit plugins — Agency Kit Pack

**For the owner:** your agency's AI setup (skills, critic agent, guardrail hooks, client connectors) lives on one laptop and reaches new people as a zip and a long message. This pack turns it into two versioned plugins in a private marketplace, so a new freelancer gets the same setup with one install step, and a release can no longer leave a teammate on last week's hook.

**Shown in:** Episode 7, "What we are building, as Zara sees it", "The catalogue, the check, the team switch", "Test 1: the wrong name", "Test 2: the clean clone", "Test 3: the quiet one", "FIX: change the system, rerun the same tests".

**Prerequisites:** Claude Code installed, a Git host account (GitHub assumed), read access to a private repo, Git Bash on Windows, Python 3 on PATH. Kiran Studio, Mehr Bakery, Noor Dental Clinic and Zara are fictional; all data is synthetic.

## What's inside

| Path                                                               | What it is                                                                                                                                                                                                                                                      |
| :----------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `kiran-marketplace/`                                               | The marketplace repo. Push it as a **private** repo `<your-org>/kiran-marketplace`.                                                                                                                                                                             |
| `kiran-marketplace/.claude-plugin/marketplace.json`                | The catalogue: `kiran-marketplace`, two entries, relative sources, one name everywhere.                                                                                                                                                                         |
| `kiran-marketplace/plugins/kiran-core/`                            | Starter plugin: `.claude-plugin/plugin.json` · `skills/client-report/` · `skills/pr-review/` · `skills/proposal/` (added in 1.1.0, Episode 9) · `agents/critic.md` · `hooks/hooks.json` · `scripts/` (secret-firewall, commit-gate, run-review, record-review). |
| `kiran-marketplace/plugins/kiran-noor/`                            | Example client plugin: `.mcp.json` for the `noor-bookings` server (four read and draft tools), `server.py`, `requirements.txt`. Token by variable name `NOOR_API_TOKEN` only; no key and no permission rules inside.                                            |
| `kiran-marketplace/ci/check_kit.py`                                | Release rules: one name · files changed ⇒ version changed · newest `CHANGELOG.md` entry = `plugin.json` version. Stdlib only.                                                                                                                                   |
| `kiran-marketplace/.github/workflows/validate-kit.yml`             | CI: `claude plugin validate . --strict` + `claude plugin tag plugins/*/ --dry-run --force` + `check_kit.py --base origin/<base>`, on every pull request and push to `main`.                                                                                     |
| `kiran-marketplace/CHANGELOG.md`                                   | The live changelog (kiran-core 1.1.0, kiran-noor 1.0.0).                                                                                                                                                                                                        |
| `kiran-marketplace/ONBOARDING.md`                                  | The new-person checklist: shorter path first, install-order warning, update and pin-move lines, trust prompt note.                                                                                                                                              |
| `kiran-marketplace/.gitattributes`                                 | Keeps hook scripts LF on Windows clones.                                                                                                                                                                                                                        |
| `TEAM-SETTINGS-SNIPPET.md`                                         | The committed `.claude/settings.json` block, the two commands that write it, key order, pinned-tag form.                                                                                                                                                        |
| `team-settings.snippet.json` · `team-settings.pinned.snippet.json` | The same blocks as plain JSON.                                                                                                                                                                                                                                  |
| `HOOK-REVIEW-CHECKLIST.md`                                         | What to read in a plugin's `hooks.json` and scripts before you install it; the matchers in this kit.                                                                                                                                                            |
| `CHANGELOG-TEMPLATE.md`                                            | Changelog template + the release rule (no new version, no release).                                                                                                                                                                                             |
| `ADVANCED-CHECKS.md`                                               | One page: the twelve checks cut from the video.                                                                                                                                                                                                                 |

## Use it in 5 steps

1. **Prerequisites check.** `claude --version` · `git --version` · `python --version` (Windows: run the hooks' tests in Git Bash). Replace `<your-org>` in `ONBOARDING.md`, `TEAM-SETTINGS-SNIPPET.md` and the two plugin READMEs.
2. **Check the kit locally** (no sign-in, no API key needed):
   ```bash
   cd kiran-marketplace
   git init -b main && git add -A && git commit -m "kiran-marketplace"
   claude plugin validate . --strict
   for p in plugins/*/; do claude plugin tag "$p" --dry-run --force; done
   python ci/check_kit.py --base HEAD
   ```
   Then prove the firewall blocks both shells (Git Bash):
   ```bash
   printf '%s' '{"tool_name":"Bash","tool_input":{"command":"cat .env"}}' | bash plugins/kiran-core/scripts/secret-firewall.sh; echo "exit=$?"
   printf '%s' '{"tool_name":"PowerShell","tool_input":{"command":"Get-Content .env"}}' | bash plugins/kiran-core/scripts/secret-firewall.sh; echo "exit=$?"
   ```
   Both must print `BLOCKED by secret-firewall` and `exit=2`.
3. **Publish privately.** Create the private repo `<your-org>/kiran-marketplace`, push. CI runs on every pull request. Release: `python ci/check_kit.py --base kiran-core--v<last>` then `claude plugin tag plugins/kiran-core --push` (creates `kiran-core--v<version>`).
4. **Switch it on for a client repo.** In the client repo: `claude plugin marketplace add <your-org>/kiran-marketplace --scope project`, then `claude plugin install kiran-core@kiran-marketplace --scope project`. Commit `.claude/settings.json` in the key order in `TEAM-SETTINGS-SNIPPET.md`. Pin client repos to a tag if they must not follow your latest commit.
5. **Onboard a person.** Send them `kiran-marketplace/ONBOARDING.md` and `HOOK-REVIEW-CHECKLIST.md`. Ready when `claude plugin list` shows `kiran-core@kiran-marketplace`, `Scope: project`, enabled, at the newest `CHANGELOG.md` version.

## Why these choices

- **Hook matchers:** `secret-firewall` matches `Write|Edit|Bash|PowerShell`; `commit-gate` matches `Bash|PowerShell`. Series rule: every hook that guards the shell covers both shells. A Bash-only control let PowerShell read `.env` and commit (Episode 2 evidence).
- **Hook form:** shell form `bash "${CLAUDE_PLUGIN_ROOT}/scripts/<x>.sh"`, run by Git Bash on Windows. Exec form was not tested; on Windows it resolves `bash` from PATH, where WSL's `bash.exe` can win.
- **Names:** `claude plugin validate` (also `--strict`) and `claude plugin tag` both pass a name mismatch between catalogue entry and `plugin.json` (tag compares versions only). `check_kit.py` is the check that catches it.
- **CI tag step:** `--force` because a plain `tag --dry-run` fails once the current version is already tagged. Validate and tag need no sign-in or API key. A client repo whose CI must fetch a private marketplace needs a read token (`GH_TOKEN` + `gh auth setup-git`).

## Limits — what it does NOT do

- It does not force anyone to install or update. Trust and install stay each person's decision; updates are not pushed.
- Cloud sessions do not load local or repository-enabled plugins.
- `secret-firewall` is a text guard on tool calls, not a secret scanner. It cannot see what a script computes at runtime. Keep a real secret scanner in pre-commit and CI.
- `commit-gate` is a review workflow gate, not a security boundary. `run-review.sh` calls Claude headless (`claude -p … --agent kiran-core:critic`): that needs your Claude login and spends money (it carries a `--max-budget-usd` cap).
- The GitHub Actions runner itself was not run for the kit; the same three checks were run locally.
- The GitHub `owner/repo` settings shape follows the docs; the build tested the same entries with a local git URL standing in for a private GitHub repo.
- `kiran-noor` needs the Noor bookings API (fictional; the Episode 5 module ships a mock). It ships four read and draft tools and never changes a booking.
- Plugin commands change quickly. Re-check the official docs on the day you build, and re-run step 2 after every Claude Code update.

## Tested

On a temporary git copy of `kiran-marketplace`: `check_kit.py --base HEAD` passed; a catalogue name mismatch and an unbumped plugin change both FAILED as designed; `claude plugin validate . --strict` and `claude plugin tag --dry-run --force` passed with an empty, isolated config folder (validate also passed the name mismatch, as the episode says); secret-firewall blocked `cat .env` (Bash) and `Get-Content .env` (PowerShell) with exit 2.
