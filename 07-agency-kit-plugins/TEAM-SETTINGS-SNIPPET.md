# Team settings snippet — the committed `.claude/settings.json` block

This is the "team switch". Committed in a client repo, it tells every person who clones that repo where the catalogue lives and which kit the repo wants. It is a **request**: it turns the kit on, it does not install it (see `kiran-marketplace/ONBOARDING.md`).

## The two commands that produce it

Run them inside the client repo, once, as the owner:

```bash
claude plugin marketplace add <your-org>/kiran-marketplace --scope project
claude plugin install kiran-core@kiran-marketplace --scope project
```

Then commit `.claude/settings.json`. Do not hand-type the block below into a repo: let the CLI write it, then check it against this page.

## The block (as the CLI writes it after install)

File: `team-settings.snippet.json`

```json
{
  "enabledPlugins": {
    "kiran-core@kiran-marketplace": true
  },
  "extraKnownMarketplaces": {
    "kiran-marketplace": {
      "source": {
        "source": "github",
        "repo": "<your-org>/kiran-marketplace"
      }
    }
  }
}
```

**Commit it in the CLI's key order, `enabledPlugins` first.** On the build, `marketplace add` wrote `extraKnownMarketplaces` first; the following `install` rewrote the file with `enabledPlugins` first. If you commit the first order, every teammate's install rewrites the file, dirties the clone, and the `commit-gate` hook then stops their commits with "unstaged edits".

Noor Dental Clinic repo: add `"kiran-noor@kiran-marketplace": true` under `enabledPlugins`, and keep the clinic's allow rules for the four `mcp__plugin_kiran-noor_noor-bookings__<tool>` names in the same file (the plugin carries no permission rules).

## Pinned-tag form (client repos that must not follow your latest commit)

File: `team-settings.pinned.snippet.json`. Same block plus `"ref": "kiran-core--v<version>"`:

```bash
claude plugin marketplace add <your-org>/kiran-marketplace#kiran-core--v<version> --scope project
```

```json
"source": {
  "source": "github",
  "repo": "<your-org>/kiran-marketplace",
  "ref": "kiran-core--v<version>"
}
```

Tags come from `claude plugin tag plugins/kiran-core --push`, which creates `kiran-core--v<version>`.

**Moving the pin:** run the same `marketplace add …#kiran-core--v<new> --scope project` in a reviewed commit, then `claude plugin update kiran-core@kiran-marketplace --scope project`. Editing `"ref"` by hand moved nothing in our test: `plugin update` and even `marketplace update` stayed on the old tag.

## What was tested, and what was not

- Tested: the key order rewrite, the pinned `"ref"` entry and the pin move, with the catalogue served from a local git URL standing in for a private GitHub repo (`"source": "git", "url": "<url>"`).
- The GitHub `owner/repo` shape above is the documented form the CLI writes for `owner/repo` input. Confirm it by running the two commands on your own repo and comparing.
