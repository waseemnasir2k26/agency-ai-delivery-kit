---
name: proposal
description: Turn a client brief into an unknowns list and a draft proposal for Kiran Studio. Use when a new client brief arrives.
argument-hint: [path to brief.md]
allowed-tools: Read, Glob, Write, Edit
---

# Kiran Studio proposal draft

The brief is at `$ARGUMENTS`. Write both output files into the SAME folder as the brief. Read the brief and the client's data file (`data/<client>.json`, if the brief names a client that has one). Nothing else.

## 1. `unknowns.json` first

Every fact the job needs that the brief does NOT state. Prices, dates, offers and their terms, opening or fitting hours, where enquiries go, who approves, content and photos the client must send. One item per question. A JSON array, each item exactly:

```json
{ "id": "kebab-case-id", "question": "One plain question for the client", "status": "open", "answer": null }
```

Every item starts `"status": "open"`. Never answer a question yourself. Never guess a value.

## 2. `proposal.md`

Exactly these sections, in this order:

- `# Proposal: <client> <job>`
- `## Scope`: what Kiran Studio will build, in plain bullets. Only what the brief asks for.
- `## Unknowns`: the questions from `unknowns.json`, one bullet each. Say the build starts only when every one is answered.
- `## Client provides`: what the client must send (answers, content, approvals).
- `## Price`: the single line `Price: from pricing sheet (filled in by the owner)`. NEVER write a number, a range or a currency amount here or anywhere in the proposal.

## Hard rules

1. No number for money anywhere. A person fills in the price.
2. No promise of results: no search rankings, traffic, sales figures, conversion rates, or any result with a deadline.
3. No email address, no phone number.
4. Under 300 words for `proposal.md`.

Finish with one line: `WROTE <n> unknowns · proposal.md`.
