---
name: deploy-steps
description: Kiran Studio deploy steps for a client site (build, preview, go-live checklist). Use only when deploying a site.
---

# Deploy steps (fictional agency, demo only)

1. `python scripts/build.py` (injects the shared footer into `dist/<client>/index.html`).
2. `python scripts/check-site.py <client>` must print PASS.
3. Preview with `python scripts/preview.py <client>` (needs `config/local.json`, never committed).
4. A human approves the preview before go-live. Nobody deploys on a Friday after 16:00.
5. After go-live, open the live page on a phone and check hours and prices once by eye.
