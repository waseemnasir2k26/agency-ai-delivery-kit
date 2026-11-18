#!/usr/bin/env python3
"""kshell.py - the tiny shell shown on camera: prompt `kiran>`, real commands only.
  python monday.py [args]   -> runs the real monday.py in this terminal (live control room)
  type <path-to-digest.md>  -> prints the digest
  exit
"""
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
E = "\x1b["
CREAM, MUTE, RUST = "236;228;214", "150;142;130", "214;104;60"


def c(rgb, s, bold=False):
    return f"{E}{'1;' if bold else ''}38;2;{rgb}m{s}{E}0m"


def show_digest(path):
    for ln in path.read_text(encoding="utf-8").splitlines():
        if ln.startswith("# "):
            out = c(CREAM, ln[2:], True)
        elif ln.startswith("## "):
            out = "\n" + c(RUST, ln[3:].upper(), True)
        elif ln.startswith("_"):
            out = c(MUTE, ln.strip("_"))
        elif ln.split(". ", 1)[0].isdigit():
            out = c(CREAM, "  [ ] " + ln.split(". ", 1)[1])
        elif ln.startswith("- "):
            out = c(CREAM, "  · " + ln[2:])
        else:
            out = c(CREAM, ln)
        sys.stdout.write(out + "\n")
        sys.stdout.flush()
        time.sleep(0.05)


def main():
    sys.stdout.write(E + "2J" + E + "H")
    while True:
        sys.stdout.write(c(RUST, "kiran", True) + c(CREAM, "> "))
        sys.stdout.flush()
        try:
            line = input().strip()
        except EOFError:
            return
        if line.startswith("python monday.py"):
            subprocess.call([sys.executable, "-X", "utf8", "monday.py", *line.split()[2:]], cwd=str(HERE))
            sys.stdout.write("\n")
        elif line.startswith("type "):
            p = HERE / line[5:].strip().replace("\\", "/")
            sys.stdout.write("\n")
            show_digest(p) if p.exists() else sys.stdout.write(c(MUTE, "not found\n"))
            sys.stdout.write("\n")
        elif line == "clear":
            sys.stdout.write(E + "2J" + E + "H")
        elif line == "exit":
            return


if __name__ == "__main__":
    main()
