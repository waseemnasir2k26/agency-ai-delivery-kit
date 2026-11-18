# Client report: b4

**ACCEPTED 5 · REJECTED 1 · NOT CHECKED 1**  
Checker verdict: **PASS** · verifier issues: 0 · findings filed: 7  
Source: `verify.json` from verify.py (plain Python, no model). NOT CHECKED never counts as a pass.

## Built

- http://localhost:8099/sufi-threads/ · screenshot `runs/b4/shots/01.png`
- http://localhost:8099/sufi-threads/winter.html · screenshot `runs/b4/shots/02.png`
- http://localhost:8099/sufi-threads/order.html?item=lawn-suit · screenshot `runs/b4/shots/03.png`
- http://localhost:8099/sufi-threads/fitting.html · screenshot `runs/b4/shots/04.png` · form POST → http://localhost:8099/enquiry

## Checked

| Check | Result | Page | Quoted text | Screenshot |
| --- | --- | --- | --- | --- |
| hours (model: PASS) | ACCEPTED | http://localhost:8099/sufi-threads/ | "Mon-Sat: 11:00-21:00" | runs/b4/shots/01.png |
| price (model: PASS) | ACCEPTED | http://localhost:8099/sufi-threads/ | "Lawn suit: PKR 3600" | runs/b4/shots/01.png |
| price (model: PASS) | ACCEPTED | http://localhost:8099/sufi-threads/winter.html | "Khaddar suit: PKR 6500" | runs/b4/shots/02.png |
| phone (model: PASS) | ACCEPTED | http://localhost:8099/sufi-threads/ | "Call us: +92 300 0000000" | runs/b4/shots/01.png |
| button (model: PASS) | NOT CHECKED | http://localhost:8099/sufi-threads/order.html?item=lawn-suit | "Total to pay: PKR 3600" | runs/b4/shots/03.png |
| form (model: PASS) | ACCEPTED | http://localhost:8099/sufi-threads/fitting.html | "Mon-Sat: 12:00-19:00 (by appointment)" | runs/b4/shots/04.png |
| price (model: PASS) | REJECTED | http://localhost:8099/sufi-threads/winter.html | "Velvet kurta: PKR 5400 (launch week PKR 4900)" | runs/b4/shots/02.png |

## Needs a human look

- NOT CHECKED: button: ACCEPTED (needs human: nothing machine-checkable) · quoted "Total to pay: PKR 3600" · page http://localhost:8099/sufi-threads/order.html?item=lawn-suit
- REJECTED: price: REJECTED: quoted text is not on that page · quoted "Velvet kurta: PKR 5400 (launch week PKR 4900)" · page http://localhost:8099/sufi-threads/winter.html

## Approval

Approved by (owner, not the builder): ____ · role: ____ · report version (commit): ____ · recorded: ____  
The approver opened the page themselves, every line above has evidence, and every human-look item is fixed or told to the client.
A recorded approval in `jobs/<job>/gates.md` row 4. Not a legal signature.
