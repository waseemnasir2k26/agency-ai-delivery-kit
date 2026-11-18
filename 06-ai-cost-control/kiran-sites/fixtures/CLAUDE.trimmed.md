# Kiran Studio: client sites (fictional agency, demo data only)

Owner of this file: the studio lead. Change it only by pull request.

## True for every task
- Pages live in `sites/<client>/index.html`. The truth for hours and prices is `data/<client>.json`.
- The only phone number on any page is the placeholder `+92 300 0000000`. No email addresses on pages.
- Run `python check-site.py <client>` after every page edit.
- Never commit `config/local.json`. Never push without a human review.
- Clients: Mehr Bakery (`mehr-bakery`), Sufi Threads (`sufi-threads`), Noor Dental Clinic (`noor-dental`). All fictional.

## Everything else is a skill (loads only when needed)
- PR review: `.claude/skills/pr-review/`
- Deploy steps: `.claude/skills/deploy-steps/`
- Brand voice for all three clients: `.claude/skills/brand-voice/`
