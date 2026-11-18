# Kiran Studio site checks

Every client page must pass all of these before it ships.

1. Opening hours on the page match data/<client>.json exactly.
2. Prices on the page match data/<client>.json exactly (item and PKR). This includes the winter page against the `winter` block.
3. A price on any page with no matching row in data/<client>.json is a failure. If the data has no price, the page shows no price.
4. The only phone number shown is the placeholder +92 300 0000000.
5. No email addresses anywhere on the page.
6. The page has a viewport meta tag.
7. The price section of each page shows "Prices checked: <updated date from data>" (in the page body, not the shared footer).
8. If `offer` in the data file is null, no page mentions an offer, discount or sale.

Run: python scripts/check-site.py <client>
