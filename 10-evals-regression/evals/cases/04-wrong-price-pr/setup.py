#!/usr/bin/env python3
"""Build the pull request in the fresh workspace: base commit = the site as shipped (passes check-site.py),
PR commit = one wrong price (Fruit cake PKR 1200 -> 1500). Usage: setup.py <workspace>. Fictional git identity."""
import subprocess, sys, pathlib
w = pathlib.Path(sys.argv[1])
def git(*a):
    subprocess.run(["git", "-c", "user.name=Kiran Test", "-c", "user.email=test@kiran.invalid", *a], cwd=w, check=True, capture_output=True)
git("init", "-q", "-b", "main"); git("add", "-A"); git("commit", "-q", "-m", "Mehr Bakery site as shipped")
p = w / "sites" / "mehr-bakery" / "index.html"
t = p.read_text(encoding="utf-8"); assert "Fruit cake: PKR 1200" in t, "fixture changed"
p.write_text(t.replace("Fruit cake: PKR 1200", "Fruit cake: PKR 1500"), encoding="utf-8")
git("commit", "-q", "-am", "Mehr Bakery: refresh fruit cake listing")
