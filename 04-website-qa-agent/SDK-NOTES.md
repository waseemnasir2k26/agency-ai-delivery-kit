# SDK notes: the developer asides from Episode 4

These were cut from the video to keep it short. They apply to `site_watch.py`. They describe the Claude Agent SDK
release used for the recording. Re-test after every SDK update: names and behaviour can change.

## 1. `query()` or `ClaudeSDKClient`

- `query()`: one prompt, a fresh session, stream the messages, done. Site Watch uses this: each nightly run is
  independent, and nothing should carry over from last night.
- `ClaudeSDKClient`: an open session you keep talking to (follow-up prompts, interrupts). Use it when a person or
  another program needs to steer the agent mid-run. Not needed for a scheduled check.

## 2. `can_use_tool` is never called for tools in `allowed_tools`

Tools listed in `allowed_tools` are auto-approved and skip the permission callback. That is why `visit` and
`click` are deliberately NOT in `allowed_tools` in `site_watch.py`: every visit goes through `guard()`.
Put `visit` in that list and the localhost guard silently stops running.

## 3. Redirects: check the final URL inside the tool

The permission callback sees tool calls, not what the browser does. `click` follows a link inside the browser,
so the `click` tool checks the link itself and refuses anything off-site (in the Episode 4 test, that tool-level
guard fired first). A redirect never asks anyone. If your clients' sites redirect, check `page.url` after
`page.goto()` inside the tool and refuse when it is off-site. The callback is the policy; the tool is the last line.

## 4. Both caps are fuses, not exact limits

- `max_budget_usd`: checked after a turn, so a run can overshoot a little. Recorded result: cap 0.01, run stopped at
  0.0101 (`error_max_budget_usd`).
- `max_turns`: `num_turns` can come back as the cap plus one. Recorded result: cap 12, run stopped at 13 turns
  (`error_max_turns`).
- Set caps with headroom, and alert on the stop reason, not on an exact number.

## 5. Catch the result error to keep cost and stop reason

When a cap is hit, the `ResultMessage` (with cost, turns and stop reason) arrives first, then the SDK raises
`ResultError`. `site_watch.py` keeps the last `ResultMessage` and catches the error:

```python
except ResultError as e:                        # a cap was hit: the ResultMessage already arrived
    print(f"STOPPED: {e.subtype} ({e.terminal_reason})")
```

Without the `except`, the script crashes and you lose the cost and the reason for that run.
Sites the agent never reached are then reported as NOT CHECKED by `verify.py`, never PASS.

## 6. The result message lists denied calls

`ResultMessage.permission_denials` lists every call the permission callback refused. `site_watch.py` saves it in
`run.json` next to its own `denials` list (which also holds the `click` tool's off-site blocks). Read both in
the morning: a denial is a page trying to send the agent somewhere it should not go.

## 7. The comma gotcha

A real page often writes a price with a thousands separator: `PKR 3,500`. The data file stores a plain number:
`3500`. A strict string compare fails a correct price. `verify.py` strips the commas and compares numbers
(`int(m.group(1).replace(",", ""))`). Get this wrong and the report cries wolf every night, and within a week
nobody reads it.

## Other settings worth knowing in `site_watch.py`

- `tools=[]`: no built-in tools at all (no Bash, no file edits, no web search). The only tools are the four you wrote.
- `setting_sources=[]`: load no user or project settings files, so nothing on the machine changes the agent's
  permissions or hooks.
- `PreToolUse` hook `audit()`: logs every tool call into `run.json` (`tool_log`), the client's receipt.
- `output_format=SUMMARY`: the agent's own summary comes back as structured JSON. It is still a draft; `verify.py`
  decides.
