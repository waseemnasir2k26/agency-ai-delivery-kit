# Unknowns checklist

The first thing the pipeline produces is not a proposal. It is a list of questions: every fact the job needs that
the brief did not give. Every item starts `open`. The build stage reads `jobs/<job>/unknowns.json` first and, if one
item is still open, stops before any agent starts (0 model calls).

## Ask about every one of these before a build

- [ ] **Prices:** every price that will appear on the page, item by item. If the client gives no price, the page shows no price.
- [ ] **Hours:** opening hours, booking or fitting hours, holiday changes.
- [ ] **Offer terms:** is there an offer at all? If yes: exact terms, which items, start and end dates. "We are thinking of an offer" is not an answer.
- [ ] **Enquiry destination:** where form enquiries go (which inbox or system), and who reads them. No personal email address on the page.
- [ ] **Photos:** which photos, and does the client have the right to use them?
- [ ] **Who approves:** one named person at the client who can approve the page.
- [ ] **Legal lines:** terms, returns, privacy, registration or licence numbers that must appear.
- [ ] **Deadline:** the date the page must be live.
- [ ] **Descriptions:** product or service details (sizes, materials, inclusions) that the page states as facts.

## How it runs in `pipeline.py`

1. `python pipeline.py proposal --job <job>`: the `kiran-core:proposal` skill writes `unknowns.json` (all `open`) and a draft `proposal.md` with an Unknowns section.
2. Gate 1 SEND: the owner sends the proposal and the questions by hand.
3. `python pipeline.py answers --job <job> --reply <client-reply.json>`: answers are recorded and the client data file is updated from `data_patch`. Items without an answer stay `open`.
4. `python pipeline.py build --job <job>`: pre-flight prints `unknowns open = n`. If n > 0:
   `BLOCKED: 1 unknown(s) still open: price-velvet-kurta. Ask the client first. 0 agents started, 0 model calls.` (recorded result, `fixtures/test-setups/b1-skipped-unknowns/recorded/fixed-blocked.txt`).

## Files

- Blank example: `jobs/_new-job-template/unknowns.json`
- Filled example (fictional Sufi Threads job, all answered): `jobs/sufi-winter/unknowns.json`
- Client answers format: `jobs/sufi-winter/client-reply-1.json` (one price forgotten) and `client-reply-2.json`

```json
{
  "id": "prices",
  "question": "What is the price of each item?",
  "status": "open",
  "answer": null
}
```
