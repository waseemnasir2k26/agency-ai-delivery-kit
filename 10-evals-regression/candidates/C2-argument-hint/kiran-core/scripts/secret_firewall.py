"""kiran-core secret-firewall rules. Reads the PreToolUse JSON on stdin. Exit 2 = block.

Text guard only. A key format missing from KEY_PATTERNS goes straight through: that gap is the
Episode 7 drift test (fix the pattern, ship it under a NEW version, or teammates keep the old copy).
"""
import json
import re
import sys

# Key formats this release knows.
KEY_PATTERNS = {
    "Anthropic API key": r"sk-ant-[A-Za-z0-9_-]{20,}",
    "OpenAI API key": r"\bsk-(?:proj-)?[A-Za-z0-9_-]{32,}",
    "AWS access key id": r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b",
    "GitHub token": r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{50,})",
    "private key block": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    "Noor booking API key": r"\bnoor_(?:live|desk|test)_[A-Za-z0-9_]{4,}",
}

# Episode 2 rule: shell commands that touch .env-style files (incl. glob tricks). .env.example is allowed.
ENV_TOUCH = re.compile(r"\.env|\.e[a-z]{0,2}[*?[]|\.\[e\]|[*?]env|grep[ \t]+-[a-zA-Z]*r[a-zA-Z]*[^|;]*[ \t]\.([ \t\"]|$)", re.I)
# Write/Edit into a .env file (not .env.example).
ENV_FILE = re.compile(r"(^|[\\/])\.env(\.(?!example$)[^\\/]*)?$", re.I)


def block(msg):
    print(f"BLOCKED by secret-firewall: {msg}", file=sys.stderr)
    sys.exit(2)


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        block("could not read the tool call, so it was not checked.")
    tool = data.get("tool_name", "")
    ti = data.get("tool_input", {}) or {}
    if tool in ("Bash", "PowerShell"):
        text = ti.get("command", "") or ""
        if ENV_TOUCH.search(text.replace(".env.example", "")):
            block("this command touches a .env secrets file. Ask the human to share the specific value instead.")
    elif tool in ("Write", "Edit"):
        path = ti.get("file_path", "") or ""
        if ENV_FILE.search(path):
            block(f"{path} is a .env secrets file. Secrets stay out of files Claude writes.")
        text = (ti.get("content", "") or "") + "\n" + (ti.get("new_string", "") or "")
    else:
        sys.exit(0)
    for label, pat in KEY_PATTERNS.items():
        if re.search(pat, text):
            block(f"this {tool} call contains what looks like a {label}. Keys live in environment variables, never in files or commands.")
    sys.exit(0)


if __name__ == "__main__":
    main()
