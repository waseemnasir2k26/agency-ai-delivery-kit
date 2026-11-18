# Gates: <job>

Four human gates. The pipeline stops at each one and moves on only when `python pipeline.py approve <gate>` records a person here.
A recorded approval, not a legal signature. Leave `____` in a cell until the gate is approved: `pipeline.py` treats `____` as "not approved".
Keep the table exactly in this shape (one space each side of a cell, no extra padding): `pipeline.py approve` finds rows by `| <gate> |`.

| Gate | What is approved | Approved by (name, role) | Version (commit) | Recorded |
| ---- | ---------------- | ------------------------ | ---------------- | -------- |
| 1 SEND | proposal.md | ____ | ____ | ____ |
| 2 MERGE | pull request | ____ | ____ | ____ |
| 3 GO-LIVE | preview → live | ____ | ____ | ____ |
| 4 APPROVE REPORT | report.md | ____ | ____ | ____ |
