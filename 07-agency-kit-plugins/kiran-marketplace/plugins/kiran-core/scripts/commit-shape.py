#!/usr/bin/env python3
"""Reads the PreToolUse JSON on stdin. Prints how the Bash command uses `git commit`:
none | plain | all | paths | alias | unparseable.  Matches git invocations whose SUBCOMMAND is
commit, so `git -C . commit` and `git -c x=y commit` count. Text analysis only."""
import json, re, shlex, sys

ARG_LONG = {"--message", "--file", "--reuse-message", "--reedit-message", "--author", "--date",
            "--cleanup", "--template", "--fixup", "--squash", "--trailer", "--pathspec-from-file"}
ARG_SHORT = set("mFCct")
GIT_ARG = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path", "--super-prefix"}


def newlines_to_semicolons(s):
    """An unquoted newline ends a command, like ;  (a newline inside quotes is just text)."""
    out, q, esc = [], None, False
    for ch in s:
        if esc: esc = False
        elif ch == "\\" and q != "'": esc = True
        elif q: q = None if ch == q else q
        elif ch in "'\"": q = ch
        elif ch == "\n": ch = " ; "
        out.append(ch)
    return "".join(out)


def tokens(s):
    s = newlines_to_semicolons(s)
    lex = shlex.shlex(s, posix=True, punctuation_chars=True)
    lex.whitespace_split = True
    return list(lex)


def analyse(rest):
    kind, i, dashdash = "plain", 0, False
    while i < len(rest):
        t = rest[i]; i += 1
        if dashdash or not t.startswith("-"):
            return "paths"                        # a bare word after commit = a pathspec
        if t == "--":
            dashdash = True; continue
        if t.startswith("--"):
            name = t.split("=", 1)[0]
            if name in ("--all",): kind = "all"
            elif name in ("--include", "--only"): return "paths"
            elif name in ARG_LONG and "=" not in t: i += 1
            continue
        for n, ch in enumerate(t[1:]):             # short flag cluster, e.g. -am "msg"
            if ch == "a": kind = "all"
            elif ch in "io": return "paths"
            elif ch in ARG_SHORT:
                if n == len(t) - 2: i += 1         # arg is the next token
                break                              # else it is attached: rest of cluster
    return kind


def scan(s, depth=0):
    toks = tokens(s)
    found = []
    for idx, t in enumerate(toks):
        if re.search(r"\s", t) and "git" in t and "commit" in t and depth < 3:
            found += scan(t, depth + 1)            # bash -c "git commit ..."
        if re.split(r"[\/]", t)[-1] in ("git", "git.exe"):
            j, alias = idx + 1, False
            while j < len(toks) and toks[j].startswith("-"):
                if toks[j] in GIT_ARG:
                    if toks[j] == "-c" and j + 1 < len(toks) and toks[j + 1].startswith("alias."):
                        alias = True
                    j += 1
                j += 1
            if alias: found.append("alias")
            if j < len(toks) and toks[j] == "commit":
                end = j + 1
                while end < len(toks) and toks[end] not in ("&&", "||", ";", "|", "&", "(", ")"):
                    end += 1
                found.append(analyse(toks[j + 1:end]))
    return found


def main():
    try:
        cmd = json.load(sys.stdin).get("tool_input", {}).get("command", "")
    except Exception:
        print("unparseable"); return
    try:
        found = scan(cmd)
    except ValueError:
        found = ["unparseable"] if re.search(r"git.*commit", cmd) else []
    for k in ("unparseable", "alias", "all", "paths", "plain"):
        if k in found:
            print(k); return
    print("none")

main()
