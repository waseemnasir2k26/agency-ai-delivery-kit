---
name: client-report
description: Weekly client report.
argument-hint: [client-slug]
allowed-tools: Read
---

## Data for this client

!`cat data/$ARGUMENTS.json`

## Task

Write the weekly report for this client using ONLY the data above. Output the report text and nothing else.

Hard rules (each one is checked by an automated test):

1. Start with one line: `Weekly report: <client> (<week>)`.
2. Then a heading line `Wins` followed by EXACTLY 3 bullet lines starting with `- `. Pick the 3 strongest items from `events`. Never more, never fewer.
3. Then one line `Numbers:` with site visits, leads and revenue copied exactly from `metrics`. Do not calculate, average, round or invent any other figure.
4. Then one line `Next:` naming the first item of `next`.
5. NEVER write any email address. Do not use the contact email, not even to sign off.
6. Total length 150 words or fewer. No greeting paragraph, no sign-off.
