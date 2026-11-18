"""Environment for every Claude Code child process in the CEO Monday pack. Same pattern as Episode 9.

- CLAUDE_CONFIG_DIR = <this pack>/.cfg (isolated; your own ~/.claude is never written).
- Auth (real runs): the child gets your signed-in subscription as CLAUDE_CODE_OAUTH_TOKEN, read fresh at call time from
  ~/.claude/.credentials.json (read-only; the file is never copied or written, the token is never logged). If that file
  does not exist (for example macOS keeps the login in the Keychain), no token is passed and the child uses whatever login
  is stored in .cfg. Dollar figures are a LOCAL ESTIMATE AT API LIST PRICE, NOT A BILL.
- mock_port set: no token at all; ANTHROPIC_BASE_URL points at tools/mock_api.py (FORCED TEST, zero model spend).
- Parent-session variables (CLAUDECODE*, CLAUDE_CODE_*) are stripped so every child is a fresh session.
"""
import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
CFG = HERE / ".cfg"


def owner_token():
    f = Path.home() / ".claude" / ".credentials.json"
    try:
        return json.loads(f.read_text(encoding="utf-8"))["claudeAiOauth"]["accessToken"]
    except Exception:
        return None


def cc_env(extra=None, mock_port=None):
    env = {k: v for k, v in os.environ.items()
           if not (k.startswith("CLAUDECODE") or k.startswith("CLAUDE_CODE_") or k in ("CLAUDE_PID", "CLAUDE_EFFORT", "AI_AGENT"))}
    env["CLAUDE_CONFIG_DIR"] = str(CFG)
    env["ENABLE_CLAUDEAI_MCP_SERVERS"] = "false"
    env["CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS"] = "0"
    env["PYTHONIOENCODING"] = "utf-8"
    env.pop("ANTHROPIC_API_KEY", None)
    env.pop("ANTHROPIC_BASE_URL", None)
    if mock_port:
        env["ANTHROPIC_BASE_URL"] = f"http://127.0.0.1:{mock_port}"
        env["ANTHROPIC_API_KEY"] = "sk-ant-mock-not-a-real-key"
    else:
        tok = owner_token()
        if tok:
            env["CLAUDE_CODE_OAUTH_TOKEN"] = tok
    chrome = Path(os.environ.get("LOCALAPPDATA", "")) / "ms-playwright" / "chromium_headless_shell-1254" / "chrome-headless-shell-win64" / "chrome-headless-shell.exe"
    if chrome.exists():
        env.setdefault("SITEWATCH_CHROME", str(chrome))
    if extra:
        env.update(extra)
    return env
