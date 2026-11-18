# source me inside WSL before running the suite. Isolated config: never the owner's ~/.claude config.
export PATH="$HOME/.local/bin:$PATH"
# Settings, plugins, hooks, history and memory all live in ~/ep10-cfg (log in once there, or use an API key).
# Optional (WSL): read only the credential from your Windows Claude profile instead of logging in again:
#   export CLAUDE_SECURESTORAGE_CONFIG_DIR="<WSL path to your Windows profile>/.claude"
export CLAUDE_CONFIG_DIR="$HOME/ep10-cfg"
export CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0
mkdir -p "$CLAUDE_CONFIG_DIR"
