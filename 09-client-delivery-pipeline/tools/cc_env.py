"""Environment for every Claude Code child process in the Episode 9 build.

- CLAUDE_CONFIG_DIR = BUILDS/ep09/.cfg (isolated; the owner's ~/.claude is never written).
- Auth: if ANTHROPIC_API_KEY is set, the child uses it (costs per call on your Console bill). If not, the
  signed-in subscription is passed to the child as CLAUDE_CODE_OAUTH_TOKEN, read fresh from your own
  credentials file at call time (read-only; the file is never copied or written, the token is never logged).
  Dollar figures are then a LOCAL ESTIMATE AT API LIST PRICE, NOT A BILL. EP9_NO_AUTH=1 skips the subscription token.
- Parent-session variables (CLAUDECODE*, CLAUDE_CODE_*) are stripped so the child is a fresh session.
"""
import json, os
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
CFG = HERE / ".cfg"


def owner_token():
    if os.environ.get("EP9_NO_AUTH"):
        return None
    f = Path.home() / ".claude" / ".credentials.json"
    try:
        return json.loads(f.read_text(encoding="utf-8"))["claudeAiOauth"]["accessToken"]
    except Exception:
        return None


def cc_env(extra=None):
    env = {k: v for k, v in os.environ.items()
           if not (k.startswith("CLAUDECODE") or k.startswith("CLAUDE_CODE_") or k in ("CLAUDE_PID", "CLAUDE_EFFORT", "AI_AGENT"))}
    env["CLAUDE_CONFIG_DIR"] = str(CFG)
    env["ENABLE_CLAUDEAI_MCP_SERVERS"] = "false"
    env["CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS"] = "0"
    tok = None if env.get("ANTHROPIC_API_KEY") else owner_token()
    if tok:
        env["CLAUDE_CODE_OAUTH_TOKEN"] = tok
    chrome = Path(os.environ.get("LOCALAPPDATA", "")) / "ms-playwright" / "chromium_headless_shell-1254" / "chrome-headless-shell-win64" / "chrome-headless-shell.exe"
    if chrome.exists():
        env.setdefault("SITEWATCH_CHROME", str(chrome))
    if extra:
        env.update(extra)
    return env
