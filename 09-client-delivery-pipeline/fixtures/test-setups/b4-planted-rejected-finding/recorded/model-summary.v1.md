# Sufi Threads: QA summary (run b4)

**Result: PASS.** We checked 4 pages of the site: home, winter collection, order page and fitting page. No problems were found. A few items still need a human to confirm them (see below).

## Confirmed on the live pages

| Check | What we confirmed | Page |
|---|---|---|
| Opening hours | Mon-Sat 11:00-21:00 | Home |
| Prices (core range) | Lawn suit PKR 3600 | Home |
| Prices (winter) | Khaddar suit PKR 6500 | Winter |
| Phone number | +92 300 0000000 | Home |
| Fitting hours | Mon-Sat 12:00-19:00, by appointment | Fitting |
| Fitting enquiry form | Present, and submits (POST) to /enquiry with name, phone, preferred day and item | Fitting |

## Not yet confirmed

- **Buy button total.** The order page shows "Total to pay: PKR 3600" for the lawn suit, which matches the expected price. Our automated check can't test this one, so someone should click through the order flow.
- **Other winter prices.** The winter page was only confirmed for the Khaddar suit (6500). The shawl (4200) and velvet kurta (5400) were not independently confirmed in this run. The other core-range prices (kurta 2200, dupatta 1100) were also not confirmed. We recommend checking these by eye before launch.
- **Launch-week price.** One of our checks reported a "launch week PKR 4900" price for the velvet kurta. Our verification found that text is not on the page, so we rejected that finding. If a launch-week price is planned, it has not been added to the site.
- **Sunday closure.** The expected hours include "Sun closed". The check confirmed the Mon-Sat hours, but the Sunday line was not separately confirmed.

## How we checked

An AI agent browsed the site and reported what it saw. A separate automated script then checked each claim against the actual page text. A claim only counts if the script finds the quoted text on that page. Of 7 claims, 5 were accepted, 1 was rejected as not on the page, and 1 needs a human check. The script found no problems with itself.

Screenshots of all four pages are in `runs/b4/shots/`.

**Sign-off:** pending human review.
