# variants/ — settings and config states from Episode 5

| File | State | Use |
|---|---|---|
| `settings.build.json` | Build state: the 4 tools allowed one by one, no deny rules | Copy over `noor-bookings/.claude/settings.json` to re-run the "connect it, name the tools" step |
| `settings.WRONG-wildcard.json` | **WRONG ON PURPOSE**: `mcp__noor-bookings-test__*` allows every tool of the test server (a blank cheque) | Break test 1 only |
| `settings.fixed.json` | Fixed state: 4 named allows + deny `cancel_appointment` and the whole test server | Identical to the shipped `noor-bookings/.claude/settings.json` |
| `mcp.WRONG-key-committed.json` | **WRONG ON PURPOSE**: a key written straight into `.mcp.json`. The value `noor_test_FAKE_0000` is a FAKE fixture token | Quick test 3 (the key in the repo). The secret scanner rule `noor-api-token` must flag this file |

Never copy a WRONG file into a project that talks to a real system.
