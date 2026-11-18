#!/bin/bash
# Run INSIDE WSL / Linux / macOS as the normal user (not root). Copies the lab + fixture to ~/ep08-lab, makes the fixture a git repo with a
# throwaway bare remote, marks the fixture folder trusted (WSL user's ~/.claude.json only), copies friends-plugin.
set -euo pipefail
EP8="$(cd "$(dirname "$0")/.." && pwd)"
LAB="$HOME/ep08-lab"
mkdir -p "$LAB"
cp "$EP8/lab/mock_api.py" "$EP8/lab/otel_sink.py" "$EP8/policy_test.py" "$LAB/"
rm -rf "$LAB/sufi-threads" "$LAB/remote.git" "$LAB/friends-plugin"
cp -r "$EP8/fixture/sufi-threads" "$EP8/fixture/friends-plugin" "$LAB/"
find "$LAB" -type f \( -name '*.py' -o -name '*.json' -o -name '*.md' -o -name '.env*' \) -exec sed -i 's/\r$//' {} +
git init -q --bare "$LAB/remote.git"
cd "$LAB/sufi-threads"
git init -q -b main
git -c user.name="Sufi Threads dev" -c user.email="dev@sufi-threads.example" add README.md leak.py .claude/settings.json .env.example
git -c user.name="Sufi Threads dev" -c user.email="dev@sufi-threads.example" commit -q -m "Add storefront setup + project settings"
git remote add origin "$LAB/remote.git"
printf '.env\n' > .git/info/exclude
python3 - "$LAB/sufi-threads" <<'EOF'
import json, os, sys
p = os.path.expanduser("~/.claude.json")
d = json.load(open(p)) if os.path.exists(p) else {}
d.setdefault("projects", {}).setdefault(sys.argv[1], {})["hasTrustDialogAccepted"] = True
d["hasCompletedOnboarding"] = True
json.dump(d, open(p, "w"), indent=2)
EOF
echo "OK: $LAB ready; fixture trusted; $(git log --oneline -1 -- .claude/settings.json)"
