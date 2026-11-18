# Site Watch morning report: <client or "all clients"> · run `<run name>`

> Template. `verify.py` writes the body of this report (`runs/<run>/report.md`) every night.
> A named person reads it, fills in the approval block at the bottom, and only then does any client see it.
> Example values come from the Episode 4 fixture (Kiran Studio, fictional clients, synthetic data).

Run: `<run>` · model `<model>` · `<turns>` turns · `<total_cost_usd>` (SDK estimate at list price, not an invoice) · `<seconds>` s · stop: `<completed | max_turns | budget_exhausted>`

If the stop reason is not `completed`, some sites may not have been reached. They show **NOT CHECKED**, never PASS.

## <Client name>: **PASS | FAIL | NOT CHECKED**

- <issue found by verify.py, e.g. "Lawn suit: page PKR 4500, data PKR 3600">
  seen at `<url>` · screenshot `runs/<run>/shots/NN.png`
- Needs a human look: agent saw "<quoted text>" (expected <value from data/<client>.json>) at `<url>`
- Pages opened: <n> · agent claims accepted: <n> · rejected/overridden: <n>

<one section per client>

---

Verdicts come from `verify.py` (deterministic). The AI agent is a sensor, not the judge.

## Approval (fill in before anything goes to a client)

| Field | Entry |
|---|---|
| Who approves | <named person and role: one person, not "the team"> |
| What they approve | This report as written: every FAIL is real, every NOT CHECKED is accepted or re-run, and the client may now see it. Approving the report does not approve any change to a client site; fixes go through the normal change process. |
| Decision | Approved to send / Approved with edits (listed below) / Not approved, re-run |
| Edits made by the approver | <none, or list> |
| Where it is recorded | <e.g. the client ticket or folder, plus this signed file kept next to `runs/<run>/run.json`> |
| Signed | <name> · <date and time> |

## What this report does not say

- A PASS covers only the pages the agent opened and the fields in `data/<client>.json` (hours, prices, phone). It is not a full site audit.
- A "Needs a human look" line passed the evidence checks, but nothing in it was machine-checkable. A person decides it.
- Run cost is the SDK's estimate at list price. It is not the client price. How to price this: Episode 6, full cost of delivery.

---

## Filled example (from the Episode 4 nightly run, fixture data)

```
# Site Watch report

Run: `nightly` · model `sonnet` · 33 turns · $0.2221 · 39.7 s · stop: completed

## Mehr Bakery: **PASS**
- Pages opened: 2 · agent claims accepted: 6

## Noor Dental: **PASS**
- Pages opened: 2 · agent claims accepted: 6

## Sufi Threads: **FAIL**
- Lawn suit: page PKR 4500, data PKR 3600
  seen at `http://localhost:8090/clean/sufi-threads/` · screenshot `runs/nightly/shots/03.png`
- Lawn suit: page PKR 4500, data PKR 3600
  seen at `http://localhost:8090/clean/sufi-threads/order.html?item=lawn-suit` · screenshot `runs/nightly/shots/04.png`
- Needs a human look: agent saw "Total to pay: PKR 4500" (expected Checkout total for Lawn suit 3600)
  at `http://localhost:8090/clean/sufi-threads/order.html?item=lawn-suit`
- Pages opened: 2 · agent claims accepted: 6

---
Verdicts come from verify.py (deterministic). The AI agent is a sensor, not the judge.
Reviewed and signed by: ____________________
```

The last line is what `verify.py` prints. Replace it with the approval block above when you send the report.
