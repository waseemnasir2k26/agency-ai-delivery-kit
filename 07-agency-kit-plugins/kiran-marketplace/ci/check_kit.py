#!/usr/bin/env python3
"""check_kit.py: Kiran Studio release rules for kiran-marketplace. Stdlib only. Exit 1 on any FAIL.

  1. ONE NAME: folder name == marketplace entry name == plugin.json name. This rule is check_kit's job:
     `claude plugin validate` (also with --strict) and `claude plugin tag` both pass a name mismatch
     (tag compares the plugin.json version with the catalogue entry's version, never names).
  2. VERSION BUMP: if a plugin's files changed since --base, its plugin.json version must have changed too.
  3. CHANGELOG: the newest CHANGELOG.md entry for each plugin ("## <plugin> <version> ...") == plugin.json version.

Usage:  python ci/check_kit.py                 # rule 2 compares the working tree with HEAD (pre-commit use)
        python ci/check_kit.py --base origin/main   # CI on a pull request
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
fails = []


def ok(msg):
    print(f"PASS  {msg}")


def fail(msg):
    print(f"FAIL  {msg}")
    fails.append(msg)


def git(*args):
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    return r.returncode, r.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="HEAD", help="git ref to compare against for the version rule (default HEAD)")
    base = ap.parse_args().base

    market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8") if (ROOT / "CHANGELOG.md").exists() else ""

    for entry in market.get("plugins", []):
        ename, src = entry.get("name"), entry.get("source")
        if not isinstance(src, str) or not src.startswith("./"):
            fail(f"{ename}: source must be a relative path inside this repo, got {src!r}")
            continue
        pdir = (ROOT / src).resolve()
        rel = pdir.relative_to(ROOT).as_posix()
        mpath = pdir / ".claude-plugin" / "plugin.json"
        if not mpath.exists():
            fail(f"{ename}: {rel}/.claude-plugin/plugin.json is missing")
            continue
        manifest = json.loads(mpath.read_text(encoding="utf-8"))
        mname, version = manifest.get("name"), manifest.get("version")

        # Rule 1
        if ename == mname == pdir.name:
            ok(f"{ename}: one name (folder = catalogue entry = label)")
        else:
            fail(f"{ename}: names disagree: folder={pdir.name!r} entry={ename!r} plugin.json={mname!r}")

        if not version:
            fail(f"{ename}: plugin.json has no version (updates would be detected by commit, not by release)")
            continue

        # Rule 2
        code, _ = git("rev-parse", "--verify", "--quiet", base)
        if code != 0:
            print(f"SKIP  {ename}: version rule (base ref {base!r} not found)")
        else:
            if base == "HEAD":
                _, changed = git("diff", "--name-only", "HEAD", "--", rel)
                _, untracked = git("ls-files", "--others", "--exclude-standard", "--", rel)
                changed += untracked
            else:
                _, changed = git("diff", "--name-only", f"{base}...HEAD", "--", rel)
            changed = [c for c in changed.split() if c]
            code, old = git("show", f"{base}:{rel}/.claude-plugin/plugin.json")
            old_version = json.loads(old).get("version") if code == 0 else None
            if not changed:
                ok(f"{ename}: no plugin files changed since {base}")
            elif old_version is None:
                ok(f"{ename}: new plugin since {base} (version {version})")
            elif old_version == version:
                fail(f"{ename}: {len(changed)} plugin file(s) changed since {base} but version is still {version}. Bump plugin.json version and add a CHANGELOG.md line.")
            else:
                ok(f"{ename}: files changed and version moved {old_version} -> {version}")

        # Rule 3
        m = re.search(rf"^##\s+{re.escape(ename)}\s+v?(\S+)", changelog, re.M)
        if not m:
            fail(f"{ename}: no '## {ename} <version>' entry in CHANGELOG.md")
        elif m.group(1) != version:
            fail(f"{ename}: newest CHANGELOG.md entry is {m.group(1)}, plugin.json says {version}")
        else:
            ok(f"{ename}: CHANGELOG.md top entry = plugin.json version {version}")

    print(f"\ncheck_kit: {'FAILED, ' + str(len(fails)) + ' problem(s)' if fails else 'all rules passed'}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
