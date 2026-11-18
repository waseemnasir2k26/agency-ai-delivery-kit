# Client brief template: one paragraph, five blanks

A client would never brief your team in six words, so do not brief Claude that way. Write one paragraph, the way you would write it up after a first call. Fill the five blanks, then paste the paragraph into Claude Code and ask it to save the brief as `BRIEF.md` before anything is built.

## The five blanks

| Blank | Ask yourself | Write |
| --- | --- | --- |
| 1. WHO | Who is the business, where, and what is wrong with what they have today? | |
| 2. CUSTOMER | Who visits, on what device, and what are they trying to get done? | |
| 3. MUST DO | What must the visitor be able to do, in what order on the page? | |
| 4. FEEL | How should it feel? Colours, fonts, spacing, what to avoid. | |
| 5. STILL MISSING | What has the client not sent yet, and how is it marked until they do? (sample labels, placeholder phone number, test-mode form) | |

Add one build line at the end: what kind of files, what is not allowed (frameworks, build steps, anything sent over the internet), and how you will open it.

## Fill-in version

```
Client brief: [BUSINESS NAME] (fictional or real), [WHAT THEY ARE] in [CITY]. [WHAT IS WRONG TODAY].
The typical visitor is [WHO], on [DEVICE], and wants to [GOAL].
In the first screen she must see [FIRST SCREEN]; below that, [SECTION 2]; then [SECTION 3, e.g. an enquiry form with name, phone and message].
Feel: [FEEL: colours, fonts, spacing, decoration].
Content rules: every [MENU ITEM / PRICE / REVIEW] is SAMPLE and must carry a visible SAMPLE label; the phone number is the placeholder +92 300 0000000; no invented address, opening hours or awards.
Enquiry form: TEST MODE only. On send, save the enquiry in the browser and list it on a separate page, inbox.html, labelled TEST INBOX. Send nothing over the internet.
Build: [one page, mobile first, plain HTML, CSS and a little JavaScript, no frameworks, no build step, must open with a double click].
```

Then send:

```
Save the brief above as BRIEF.md in this folder. Do not build anything yet.
```

## Worked example: Mehr Bakery (fictional), as sent in Episode 1

```
Client brief: Mehr Bakery (fictional), a family bakery in Lahore. Customers find them on a phone, but the current page is hard to read on a small screen and gives no clear way to ask about an order. The typical visitor is planning a birthday or family event, on her phone, and wants to see what the bakery makes and ask one question. In the first screen she must see who Mehr Bakery is and what it sells; below that, a short menu readable with one thumb; then an enquiry form with name, phone and message. Feel: warm and handmade, not corporate: cream background, deep brown text, one warm accent colour, a serif font for headings, generous spacing, CSS-only decoration because we have no photos yet. Content rules: every menu item, price and review is SAMPLE and must carry a visible SAMPLE label; the phone number is the placeholder +92 300 0000000; no invented address, opening hours or awards. Enquiry form: TEST MODE only. On send, save the enquiry in the browser and list it on a separate page, inbox.html, labelled TEST INBOX. Send nothing over the internet. Build: one page, mobile first, plain HTML, CSS and a little JavaScript, no frameworks, no build step, must open with a double click.
```

How the five blanks map onto it:

| Blank | Mehr Bakery |
| --- | --- |
| WHO | A family bakery in Lahore; the current page is hard to read on a phone and has no clear way to ask about an order. |
| CUSTOMER | Someone planning a birthday or family event, on her phone, who wants to see what the bakery makes and ask one question. |
| MUST DO | First screen: who Mehr Bakery is and what it sells. Then a short menu readable with one thumb. Then an enquiry form: name, phone, message. |
| FEEL | Warm and handmade, not corporate. Cream background, deep brown text, one warm accent, serif headings, generous spacing, CSS-only decoration. |
| STILL MISSING | Real menu, prices, reviews, photos and contact details. Until then: SAMPLE labels, the placeholder number, and a TEST MODE form that sends nothing. |

The saved result is `starter/BRIEF.md`.

## Three lines that matter most

- **SAMPLE labels, visible on the page.** Nothing fake may look real, because the client's name is on it.
- **TEST MODE form.** A real site needs somewhere for enquiries to go, and that needs the client's real details. Until then, enquiries stay in the browser.
- **Opens with a double click.** Nothing extra to install, so anyone on the team can check it.
