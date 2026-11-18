# Advanced insert (moved out of Episode 5)

For developers. These topics were cut from the video to keep it short. Product figures below come from the
Claude Code and MCP Python SDK docs, not from a measurement in this kit. Re-check them after every update.

## 1. The over-large result, and the fix

**The problem.** A tool like `list_all_patients` (return every patient, every column) looks harmless on a
30-row fixture. On a real clinic it returns thousands of rows. Claude Code's docs give these MCP output limits:

- a warning when a tool result passes **10,000 tokens**;
- a default maximum of **25,000 tokens** (`MAX_MCP_OUTPUT_TOKENS` raises or lowers it);
- an over-limit result is saved to a file and replaced by a message naming the path; text over 50,000 characters
  is saved to a file whatever its token count.

So the model may never see the rows you thought it saw, and the full list (with every personal field) now sits
in a file on disk. Raising the limit is the wrong fix.

**The fix.** Never offer "all". Offer a count, and a search that pages:

```python
@mcp.tool(annotations=READ_ONLY)
def count_patients(seen_since: str | None = None) -> dict:
    """Count patients (optionally seen since YYYY-MM-DD). Returns a number only, no names."""
    ...

@mcp.tool(annotations=READ_ONLY)
def search_patients(name_prefix: str, page: int = 1) -> dict:
    """Find patients whose name starts with name_prefix. 20 per page, fields: id, name. Needs 2+ characters."""
    if len(name_prefix.strip()) < 2:
        raise ToolError("name_prefix needs at least 2 characters")
    ...  # LIMIT 20 OFFSET (page-1)*20, whitelisted fields only, return {"page", "has_more", "results"}
```

The `list_all_patients` demo and this fix are a pattern sketch. They are not in this kit's test copy and were not
run for the kit. `noor-bookings` itself needs neither: its four tools are bounded to one day or one booking.

## 2. Tool search, and why the first line of a description matters

When many MCP tools are connected, Claude Code can keep their full definitions out of context and load them on
demand through a tool search (the MCP docs say when this switches on). The model then finds a tool by its name and
description. Put the job and the limit in the **first line** of the docstring, because that line is what gets
matched and read first:

- good: `"""Returns a DRAFT reschedule. Does NOT change the booking. A person applies it in the clinic dashboard."""`
- weak: `"""Helper for the reschedule flow."""`

In the MCP Python SDK, the function name, docstring and type hints become the tool definition.

## 3. stdio servers: stdout is the wire

A stdio MCP server talks to Claude Code over stdout. One stray `print()` corrupts the protocol and the server
appears broken. Log to stderr only. `noor-bookings/server.py` does:

```python
logging.basicConfig(stream=sys.stderr, level=logging.INFO, format="[noor-bookings] %(message)s")
```

Also: in MCP Python SDK v2 only a `ToolError`'s message reaches the model; any other exception reaches it only as
`Error executing tool <name>`. Raise `ToolError` with a sentence the model can act on.

## 4. The unset-variable warning in `claude mcp list`

`.mcp.json` stores `"NOOR_API_TOKEN": "${NOOR_API_TOKEN}"`: a label, not the key. If the variable is not set on a
machine, the server still loads; `claude mcp list` shows a missing-variable warning, and the raw text
`${NOOR_API_TOKEN}` is passed through. `server.py` checks for that and refuses with
"NOOR_API_TOKEN is not set on this machine". Read the warning before you suspect the code.
(`${VAR:-default}` also works, but never put a real key as the default.)

## 5. HTTP transport for teams

stdio means every person runs their own copy of the server, with their own key, on their own machine. For a team,
run one server over HTTP and register it with `claude mcp add --transport http <name> <url>` (plus an auth header).
The key then lives on the server, not on each laptop, and there is one place to log and revoke. That server is
now a network service: it needs authentication, TLS, and the same tool list, field whitelist and read-only key.
Not built or tested in this kit.
