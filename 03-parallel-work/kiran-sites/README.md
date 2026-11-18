# kiran-sites

Fictional client sites for Kiran Studio (demo data only).

- Pages: sites/<client>/index.html
- Truth: data/<client>.json
- Shared footer: shared/footer.html
- Build: python scripts/build.py
- Check: python scripts/check-site.py <client>
- Preview: python scripts/preview.py <client> (needs config/local.json, not in git)

Run the checker before every commit.

## Kit additions (Episode 3, Parallel Work Pack)

- `.worktreeinclude`: copies `config/local.json` into each NEW worktree
- `.claude/workflows/site-refresh.js`: the saved weekly workflow (`/site-refresh with date YYYY-MM-DD`)
- `.claude/agents/critic.md`: the read-only critic
- `.claude/skills/pr-review/SKILL.md`: the pull request review skill (name: `pr-review`)
- `.github/workflows/site-review.yml`: v2 review on every pull request; `.github/site-review.v1.yml` is the v1 for comparison (does not run)

The pages fail `check-site.py` on purpose until the three requests in `requests/` are done.
