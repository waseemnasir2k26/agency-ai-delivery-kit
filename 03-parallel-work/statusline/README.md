# Status line: know which copy you are typing into

Cut from the episode for time. With three terminals open on three worktrees, the easiest mistake is
typing Mehr Bakery's request into Sufi Threads' session. This status line puts the worktree name at
the bottom of every Claude Code session:

```
[mehr] ctx 7% | $0.09
[sufi] ctx 8% | $0.09
[main] ctx 3% | $0.00       <- not in a worktree
```

`ctx` = how full the context window is. `$` = Claude Code's own cost estimate for the session, not a bill.

## Install (project level, so it travels with the repo)

1. Copy `statusline.py` to `kiran-sites/.claude/statusline.py`.
2. Merge `settings-snippet.json` into `kiran-sites/.claude/settings.json` (create the file if it does
   not exist). Use `python3` in the command if that is your Python's name.
3. Start `claude` in the repo. The line appears under the prompt.

## Test it without Claude (offline)

```bash
python statusline.py < sample-worktree.json     # [mehr] ctx 7% | $0.09
python statusline.py < sample-main.json         # [main] ctx 3% | $0.00
```

## Limits

- The status line is drawn in interactive sessions only; `claude -p` does not show it.
- It reads the fields Claude Code sends (`worktree.name`, `workspace.git_worktree`,
  `context_window.used_percentage`, `cost.total_cost_usd`). If a release renames a field, the script
  falls back to `main` / `0`. Re-test after every Claude Code update.
