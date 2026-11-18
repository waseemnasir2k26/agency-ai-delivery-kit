# Critic addition: "Claims a proposal may never make"

**Ships in `kiran-core`** (module 07: `07-agency-kit-plugins/kiran-marketplace/plugins/kiran-core/agents/critic.md`,
version 1.1.0). This file is an excerpt for reading; install the plugin to use it. `pipeline.py proposal` runs the
critic as `kiran-core:critic` on the draft before any person reads it.

Excerpt:

```markdown
5. If you are reviewing a proposal (a `proposal.md`), it makes none of the claims below.

## Claims a proposal may never make

A proposal is a promise in the client's hands. REJECT any line that promises:

- search rankings or positions (Google, "page one", "top 3");
- sales, revenue or order figures;
- traffic, visitors, leads or conversion rates;
- any result tied to a deadline ("within 30 days", "by Eid");
- a price or number the owner did not fill in from the pricing sheet.

Quote the exact line and name which claim it makes. A list only catches the wording on the list: say so if you are unsure.
```

## How it was tested

`python pipeline.py proposal --job sufi-winter --plant` inserts one labelled promise into a copy of the draft
(CONTROLLED TEST · PLANTED PROMISE: page one of Google for a search phrase within 30 days of launch) and asks the
critic to review it. The critic must quote that line and end `VERDICT: REJECTED`. This calls Claude: needs your
Claude login / API key.

Limit: a list only catches the wording on the list. The owner still reads every line at Gate 1 SEND.
