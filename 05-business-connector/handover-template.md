# Handover: `<connector name>` assistant connector for <client>

> One page. The client keeps this with its system records. Fill every <placeholder>; delete nothing.
> If a row cannot be filled, the connector is not ready to hand over.

## In one sentence

The assistant can **read** <what> and can **draft** <what>. It cannot <change / cancel / create / delete ...>.
A person at <client> applies every change in <client's own system screen>.

## What the connector can do

| Tool | What it reads (client system) | What it returns | Who applies the change |
|---|---|---|---|
| `<tool_1>` | <endpoint or table, read only> | <fields, one by one> | <Nothing to apply (read only) / role of the person> |
| `<tool_2>` | | | |
| `<tool_3>` | | | |
| `<tool_4>` | | | |

Tools: **<n>**. Tools that can write: **<n>** (checked against the code, not only the tool labels).

## What it cannot do

- <Change / cancel / create / delete ...>. There is no such tool, and its key could not do it anyway.
- Return <personal fields never returned, e.g. phone numbers> or any field not listed above.
- Follow instructions typed into <free-text fields from the public, e.g. notes>. They reach the assistant labelled
  untrusted. That label is a warning, not a lock; the locks are the missing tools, the missing fields and the key's role.
- Act without being asked. It runs only inside a session someone opened in the `<project>` folder.

## The three controls, and who owns each

| Control | Where it lives | Owner |
|---|---|---|
| 1. Tools that exist | `<project>/server.py` (<n> tools) | <agency>; any new tool needs the client's written OK |
| 2. Claude Code permission rule | `<project>/.claude/settings.json`: tools named one by one, <denied tools> denied, `"defaultMode": "default"` | <agency>; reviewed with the client |
| 3. The system's own key | `<ENV_VAR_NAME>` environment variable on each machine. Never in a project file. | **<client>** (it issues and revokes keys) |

## Keys and roles

| Key label | Role | Can read | Can change | Who holds it |
|---|---|---|---|---|
| `<staff key>` | <role> | yes | yes | <staff only. Never given to the assistant.> |
| `<connector key>` | <read-only role> | yes | **no** (<how the system refuses, e.g. HTTP 403>) | The assistant connector |

Only the last 4 characters of a key are ever shown on screen or in logs.

## Key rotation (routine and after a leak)

1. Revoke and issue a new key at the client system first: <where / command>.
2. Put the new value in `<ENV_VAR_NAME>` on each machine that runs the connector.
3. Only then remove a leaked value from any file. Git history still holds it; follow the Git host's process.
4. The secret scanner (<tool>, rule `<rule id>`) runs before every commit and in CI.

Routine rotation: <every N days>, when someone with access leaves, and at once on any suspicion of a leak.
Who may revoke a key: <name> (client) · backup: <name> (agency, on the client's request)

## Tests run before handover (<data used: synthetic / anonymised>, reset before each run)

| Test | Result |
|---|---|
| Each tool called by hand, no AI (Inspector or smoke test) | <tools listed, rows changed> |
| Draft a change | <draft returned, rows changed = 0> |
| Break test: a change tool added "for convenience" (test copy only) | <result> |
| Break test: an order planted in a free-text field | <result> |
| Same request on the fixed connector | <result> |
| Direct change with the connector key, no AI | <refused how> |
| Fake key committed to a config file | <scanner result> |

Model results are from the model available on the test day. Rerun the tests when the model, the connector or the settings change.

## Approvals

- Changes in <system> are approved and applied by: <name> (named person at the client)
- Adding or changing any connector tool, permission rule or key role needs written approval from: <name>
- Before any real personal data is connected: privacy and legal review done by: <name> on <date>

Approved for the client: <name> · for the agency: <name>
