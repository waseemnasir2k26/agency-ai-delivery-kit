# Secret scanning, and what to do when a key leaks

## Leaked-key order of work (do it in this order)

1. **Revoke and rotate first.** At the system that issued the key: revoke it and issue a new one.
   Noor fixture: dashboard, Keys tab, "Revoke + issue new", or `python keys.py rotate read-only-connector`
   (run inside `noor-booking-app/`). The old key stops working at once (HTTP 401).
   Put the new value in the environment variable on each machine that runs the connector.
2. **Remove** the value from every file in the working tree, and put the label back:
   `"NOOR_API_TOKEN": "${NOOR_API_TOKEN}"`.
3. **History.** Git history still holds the old value. Rewrite history (everyone re-clones) or follow your Git
   host's leaked-secret process. Once the key is dead this is cleanup; it never replaces step 1.
4. **Scanner.** Add a scanner so the next one is caught before the commit, and in CI for anything that slips through.

Why rotate first: once a key has been pushed anywhere, assume it has been copied. Deleting the file does not un-copy it.

## What ships in this module

| File                                    | What it is                                                                                                                                                                                                                 |
| --------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `.gitleaks.toml`                        | gitleaks config: the default rules plus a custom rule `noor-api-token` for the fixture token shape `noor_test_...` / `noor_desk_...` / `noor_live_...`                                                                     |
| `.pre-commit-config.yaml`               | Runs `gitleaks-system` before every commit with `--config .gitleaks.toml` and **`pass_filenames: false`** (without it, the upstream hook passes file names, gitleaks errors and still exits 0, so the leak gets committed) |
| `ci-secrets.yml`                        | GitHub Actions job (copy to `.github/workflows/secrets.yml`): pinned gitleaks linux binary, checksum verified, full-history scan, fails on any finding                                                                     |
| `variants/mcp.WRONG-key-committed.json` | The planted test case: a FAKE fixture token written into `.mcp.json`                                                                                                                                                       |

## Commands

```
# once per clone (needs the gitleaks binary on PATH; Windows: winget install Gitleaks.Gitleaks)
pip install pre-commit
pre-commit install

# what the hook runs (staged changes only)
gitleaks git --pre-commit --staged --config .gitleaks.toml

# scan a folder (no git needed)
gitleaks dir . --config .gitleaks.toml
```

## Expected result when you scan this module

The scanner **reports findings on purpose**. The fixture tokens `noor_test_FAKE_0000` and `noor_desk_FAKE_1111` are
committed so the demo is reproducible. They appear in the booking app's seed script, the smoke test, these docs and
`variants/mcp.WRONG-key-committed.json`. Every finding should be rule `noor-api-token` on a value containing
`FAKE`. Any other finding is a real problem: stop and follow the order of work above.

For your own client project: copy `.gitleaks.toml`, change the custom rule's regex to your system's token shape,
and keep fixture tokens out of that repo.

A custom rule catches only the shape you describe; the default rules cover common providers. A scanner lowers the
risk of a committed key. It does not replace rotation.
