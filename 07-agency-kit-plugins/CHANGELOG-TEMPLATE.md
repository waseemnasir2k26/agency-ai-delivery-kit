# CHANGELOG template + release rule

## The rule

**No new version, no release.** Every change to a plugin's files:

1. bumps `version` in that plugin's `.claude-plugin/plugin.json`, and
2. adds one entry at the top of that plugin's section in `CHANGELOG.md`, newest first.

`ci/check_kit.py` enforces it: plugin files changed since `--base` with the same version = FAIL; newest `## <plugin> <version>` entry ≠ `plugin.json` version = FAIL. Without a version bump, teammates who run `plugin update` keep the old copy (the drift test in the episode).

## Release steps

```bash
python ci/check_kit.py --base kiran-core--v<last>     # must pass
claude plugin validate . --strict
claude plugin tag plugins/kiran-core --push           # creates and pushes kiran-core--v<version>
```

Then tell the team: `claude plugin marketplace update kiran-marketplace` + `claude plugin update kiran-core@kiran-marketplace` + restart. Pinned client repos move only in a reviewed commit (see `TEAM-SETTINGS-SNIPPET.md`).

## Template (copy into `CHANGELOG.md` at the marketplace root)

```markdown
# CHANGELOG — <marketplace-name>

Rule: no new version, no release. Every change to a plugin's files bumps its `plugin.json` version and adds one line here, newest first. `ci/check_kit.py` enforces it.

## <plugin-name> <x.y.z>

- <What changed, in one line a teammate understands. Name the skill / agent / hook.>
- <Why it matters to them: what they must do after updating, if anything.>

## <plugin-name> <previous x.y.z>

- <...>
```

## Format notes

- The heading must start `## <plugin-name> <version>`; `check_kit.py` reads the first such line per plugin. A `v` before the number is allowed. Text after the version (a date, a ticket number) is ignored.
- Versions: `MAJOR.MINOR.PATCH`. Patch = fix (e.g. a firewall pattern). Minor = new skill or agent rule. Major = a renamed command or removed skill (teammates must change docs and scripts).
- One plugin per heading. A release that touches two plugins gets two headings.
