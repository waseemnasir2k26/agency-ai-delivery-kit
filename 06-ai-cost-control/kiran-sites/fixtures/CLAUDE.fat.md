# Kiran Studio: client sites (fictional agency, demo data only)


## True for every task
- Pages live in `sites/<client>/index.html`. The truth for hours and prices is `data/<client>.json`.
- The only phone number on any page is the placeholder `+92 300 0000000`. No email addresses on pages.
- Run `python check-site.py <client>` after every page edit.
- Never commit `config/local.json`. Never push without a human review.
- Clients: Mehr Bakery (`mehr-bakery`), Sufi Threads (`sufi-threads`), Noor Dental Clinic (`noor-dental`). All fictional.

## Pull request checklist (added after the March footer incident)
Somebody merged a footer change that put a real email on all three sites. So, every PR:
- [ ] Title says which client and what changed, e.g. `mehr-bakery: winter hours`.
- [ ] One client per PR unless the change is in `shared/`.
- [ ] Run `python scripts/check-site.py <client>` for every touched client and paste the output in the PR.
- [ ] If `shared/footer.html` changed: one line, no email, no phone except the placeholder.
- [ ] Screenshots of the page before and after, desktop and phone width.
- [ ] Check the page title still matches the client name.
- [ ] Check every price line has the format `Item: PKR 1234` (no commas, no `Rs`).
- [ ] Check opening hours use 24h time `08:00-20:00`, plain hyphen only.
- [ ] No inline styles. No new external scripts. No tracking pixels without written client approval.
- [ ] No lorem ipsum, no TODO left on the page.
- [ ] Images: under 200 KB each, alt text on every image.
- [ ] Links: every link opens, no `http://` links.
- [ ] Request the review from the studio lead, not from yourself.
- [ ] Wait for the review workflow to post APPROVED before merging.
- [ ] Squash merge only. Delete the branch after merging.
- [ ] If the review workflow fails for a reason that is not your change, say so in the PR, do not re-run it five times.
- [ ] Link the client request file in the PR description.
- [ ] If a price changed, quote the data file line in the PR description.
- [ ] If hours changed, quote the data file line in the PR description.
- [ ] Never approve your own PR, even on a Sunday.

### Why we squash
In June we had 41 commits for one price change and nobody could find which one broke the footer. Squash.

### Review etiquette
- Comment on the line, not the person.
- One problem per comment.
- If you suggest a change, say what the data file says.
- Resolve your own comments only after the fix is pushed.
- A review older than 3 days is stale; ask again.

## Deploy steps (added after the Friday-evening outage)
We deployed Sufi Threads at 18:30 on a Friday and the sale prices were wrong all weekend. So:
1. Pull main. Make sure your working tree is clean.
2. Run `python scripts/build.py`. It writes `dist/<client>/index.html` with the shared footer injected.
3. Run `python scripts/check-site.py <client>` on every client you are deploying. All must PASS.
4. Create `config/local.json` from the template in the shared drive if you do not have it. Never commit it.
5. Run `python scripts/preview.py <client>` and open the preview link on your phone.
6. Send the preview link to the studio lead with the words: preview ready, <client>, <what changed>.
7. Wait for a written OK. A thumbs-up emoji is not an OK.
8. Upload `dist/<client>/` to the client's host folder. Keep the previous version as `previous/`.
9. Open the live page on a phone. Check hours and prices once by eye.
10. Post in the studio channel: deployed, <client>, <time>, <who approved>.
11. If anything looks wrong, roll back by restoring `previous/`, then tell the studio lead.
12. Nobody deploys on a Friday after 16:00 or on public holidays.
13. Nobody deploys two clients at the same time.
14. During Ramadan, Mehr Bakery hours change weekly: check the data file every Monday.
15. Keep the deploy log in the shared sheet: date, client, who, approved by, rollback needed yes/no.

### Rollback notes
- Restoring `previous/` takes under a minute. Do it first, investigate after.
- If `previous/` is missing, rebuild from the last tagged commit.
- Tell the client only after the studio lead agrees on the wording.

## Brand voice: Mehr Bakery (added after a client complained)
Mehr Bakery is a family bakery. They once rejected a whole page because it said 'artisanal'.
- Warm, short sentences. Read it aloud: if it sounds like an advert, rewrite it.
- Say 'fresh every morning', never 'freshly baked goods'.
- Prices always as `PKR 1234`.
- Never say 'cheap'; say 'everyday'.
- No exclamation marks except on Eid greetings.
- Product names exactly as on the price list: `Naan khatai (box)`, `Rusk (pack)`, `Fruit cake`.
- Opening hours in a list, one line per day group.
- Do not mention competitors or other bakeries.
- Do not promise delivery times.
- Seasonal lines allowed in winter: 'warm rusk with your chai'.
- No English slang. Simple Urdu words are fine in headings if the client asked.
- Photos: real products only, no stock images.
- Never mention ingredients or allergens unless the client sends the text.
- Sign-off line on campaigns: 'Mehr Bakery, since forever.'
- Avoid 'premium', 'luxury', 'gourmet'.
- Never use discount language without a written OK.

## Brand voice: Sufi Threads (added after a client complained)
Sufi Threads sells lawn suits and kurtas. They hate shouting.
- Calm, crafted, seasonal. Short paragraphs.
- Never 'SALE!!!'; say 'the winter edit' or 'sale prices this week'.
- Prices as `PKR 1234`, no strike-through old prices unless the client sends both.
- Fabric names lower case: lawn, khaddar, chiffon.
- No sizes promised unless they are in the data file.
- No model names or influencer names.
- Footer credit exactly as the client last requested.
- Colours: describe, never name a brand colour.
- Never write 'limited stock' unless true and confirmed.
- Eid collection copy needs the owner's OK.
- No emojis on the site.
- Avoid 'cheap', 'bargain', 'steal'.
- Use 'shop' as a verb only in buttons.
- No countdown timers.
- Hours: 'closed' in lower case for Sunday.
- Do not mention a returns policy unless the client sends the text.

## Brand voice: Noor Dental Clinic (added after a client complained)
Noor Dental Clinic is a clinic. Anything that sounds like a medical promise is a legal problem.
- Clear, reassuring, plain words.
- No medical claims. No 'painless', no 'guaranteed', no 'best dentist'.
- No before/after photos.
- Bookings only via the front desk; never promise a slot on the page.
- Dr Sana is the only named person on the site.
- Prices: only the consultation fee, only if the clinic sends it.
- Emergency line: placeholder only, `+92 300 0000000`.
- No patient stories or testimonials.
- Hours as in the data file; public holidays as a separate line.
- Avoid fear language like 'before it is too late' or 'do not wait'.
- Use 'appointment', not 'booking', in body copy.
- No discounts on treatments.
- No comparisons with other clinics.
- Never collect health information through a page form.
- Accessibility: font size at least 16px in body.
- Every change gets a second reader before it ships.

## Misc (things people asked to add)
- The studio lead prefers British spelling in internal docs.
- Meeting notes go in the shared drive, not in this repo.
- Use `py -3` on Windows if `python` opens the Store.
- If the preview script hangs, check `config/local.json` exists.
- Invoices are not handled in this repo.
- Ask before installing any new tool.
- Old client sites are archived outside this repo.
- The weekly client report is the `client-report` skill in the other repo.
- The holiday calendar is in the shared drive.
- Nobody edits `data/*.json` without the client's written request.
