# PROMPTS.md: every prompt typed in Episode 1

All prompts as sent in the recorded session, in order. Mehr Bakery and Kiran Studio are fictional. Replace the bakery details with your client's; keep the structure.

## 1. Install and start (terminal, not Claude)

```
# Windows PowerShell
irm https://claude.ai/install.ps1 | iex

# macOS, Linux, WSL
curl -fsSL https://claude.ai/install.sh | bash

# then, in a NEW terminal
claude --version

# Windows: also install Git for Windows (needed from Episode 2)
# https://git-scm.com/downloads/win

# project folder
mkdir mehr-bakery
cd mehr-bakery
claude

# bottom line shows the mode. If it says "auto mode on":
# press Shift+Tab until it says "manual mode on"
```

Copy the install command from the official setup page (https://code.claude.com/docs/en/setup), not from this file: it can change.

## 2. The brief

```
Client brief: Mehr Bakery (fictional), a family bakery in Lahore. Customers find them on a phone, but the current page is hard to read on a small screen and gives no clear way to ask about an order. The typical visitor is planning a birthday or family event, on her phone, and wants to see what the bakery makes and ask one question. In the first screen she must see who Mehr Bakery is and what it sells; below that, a short menu readable with one thumb; then an enquiry form with name, phone and message. Feel: warm and handmade, not corporate: cream background, deep brown text, one warm accent colour, a serif font for headings, generous spacing, CSS-only decoration because we have no photos yet. Content rules: every menu item, price and review is SAMPLE and must carry a visible SAMPLE label; the phone number is the placeholder +92 300 0000000; no invented address, opening hours or awards. Enquiry form: TEST MODE only. On send, save the enquiry in the browser and list it on a separate page, inbox.html, labelled TEST INBOX. Send nothing over the internet. Build: one page, mobile first, plain HTML, CSS and a little JavaScript, no frameworks, no build step, must open with a double click.
```

```
Save the brief above as BRIEF.md in this folder. Do not build anything yet.
```

Template with blanks: `BRIEF-TEMPLATE.md`.

## 3. The settings prompt (pin the project to manual)

```
Create .claude/settings.json in this folder that sets this project's default permission mode to manual ("default"). Change nothing else.
```

Result: `starter/.claude/settings.json`. Why: `PERMISSION-MODES.md`.

## 4. Plan first

Press Shift+Tab until the bottom line says plan mode (or start the message with `/plan`), then:

```
Read BRIEF.md and plan the site. List the files you will create, the sections in order, how the form validates each field, and how test mode and inbox.html work. Plan only.
```

Check three things before you approve: does it match the brief, is it building anything you did not ask for, did it understand test mode. In the episode the plan added a Call button with the placeholder number; it was kept. Approval option used: "Yes, manually approve edits".

## 5. Open the preview (optional)

```
Open index.html in my browser.
```

This raises a command prompt. In the episode it was cancelled and the page was opened with a double click instead. Be slower to answer "don't ask again" on commands: that answer is remembered for the project, not just the session.

## 6. One round of precise feedback

Weak (not run): `Make it look better.`

Specific (run). Three parts: what is wrong, where it is, what good looks like. Then "change nothing else".

```
The top section looks flat: the bakery name sits on plain cream with two pale circles, one of them half hidden behind the Call button like a smudge, and nothing says "bakery". In the hero only, replace those circles with a CSS-only decoration (no photos), for example a soft arched shape behind the heading with a thin hand-drawn style border in the accent colour, and make the "Ask about an order" button the most visible thing on the first screen. Keep it tidy at 375px wide and change nothing else on the page.
```

## 7. The rule sheet

```
Create CLAUDE.md in this folder with exactly these rules.

# Mehr Bakery site: project rules
- Read BRIEF.md before any change. The brief is the source of truth.
- Mobile first. Check every change at 375px wide. Nothing may scroll sideways.
- Menu items, prices and reviews are SAMPLE until the client sends real ones. Keep the SAMPLE label visible.
- The phone number stays +92 300 0000000 until the client confirms the real one.
- The enquiry form is TEST MODE. Never send form data over the internet without my written OK.
- Change only what I ask about. Tell me which files you changed.
- Never deploy or publish. Putting this online needs my explicit yes.
- After any change, tell me which lines of QA-CHECKLIST.md to rerun.
```

`QA-CHECKLIST.md` was then written by hand, not by Claude. The person who approves the page writes the check.

## 8. Bug report: tap targets (QA line 2 failed), as sent

Three parts: WHAT I DID · WHAT I SAW · WHAT I EXPECTED.

```
Bug: two links are too small to tap with a thumb. Steps: open index.html, set the width to 375px, scroll to the form and then to the footer. I saw: "View the test inbox" under the form is 22px tall, and "Test inbox" in the footer is 20px tall. Every other button is 55px or more. I expected: every button and link at least 44px tall, as QA-CHECKLIST.md line 2 says. Fix these links, change nothing else, and tell me which file and lines you changed.
```

Then the rule that lasts:

```
Add this line to CLAUDE.md, change nothing else: - Every button and link must be at least 44px tall at 375px wide, including small text links.
```

Then rerun the exact line that failed, then all five.

## 9. Handover list

```
List every file in this folder with one line on what it does. Then list every piece of content that is still SAMPLE or placeholder, with the file and the line.
```

## 10. Bug report: the Call link (found by a person tapping every button), as sent

```
Bug: the Call button at the top of the page dials the wrong number. Steps: open index.html on a phone and tap Call. I saw: the button text says +92 300 0000000, but the link behind it is tel:+920300000000, with an extra 0 after 92. I expected: the link dials the same number the button shows, tel:+923000000000. Fix only that link, change nothing else, and tell me which file and line you changed.
```

The fix was one line in `index.html`. Claude said it had not tested it on a phone; that is the person's job. It became `QA-CHECKLIST.md` line 6.

## 11. Three spare bug-report templates

For the other checks, in case they fail on your page. Fill the `[...]` from what you measured.

**Overflow (QA line 1):**

```
Bug: at 375px wide the page scrolls sideways. Steps: open index.html, set the width to 375px, scroll down. I saw: [WHICH ELEMENT, AND HOW WIDE IT MEASURES COMPARED WITH 375]. I expected: no sideways scroll anywhere. Find the element that is wider than the screen, fix it, change nothing else, and tell me which file and lines you changed.
```

Rule for CLAUDE.md: `- No element may be wider than the screen at 375px. Long words, tables, images and decorations must wrap or shrink.`

**Phone validation (QA line 3):**

```
Bug: the enquiry form accepts a bad phone number. Steps: name "Test Customer", phone [THE BAD INPUT YOU USED], any message, Send. I saw: the enquiry was saved to the test inbox. I expected: the form refuses, and a short message next to the phone field says what is wrong. Accept digits, spaces and a leading +, at least 10 digits. Change nothing else, and tell me which file and lines you changed.
```

Rule for CLAUDE.md: `- The form must refuse a phone number that is empty or has fewer than 10 digits, and say why next to the field.`

**Unlabelled placeholder (QA line 5):**

```
Bug: sample content without a label. I saw: [THE ITEM, AND WHERE ON THE PAGE]. BRIEF.md says every sample item must show a visible SAMPLE label, and nothing invented may appear. Fix this item, then search the whole page for any other unlabelled sample or template text and list what you found. Change nothing else, and tell me which file and lines you changed.
```

Rule for CLAUDE.md: `- Before you say a task is done, search the page for unlabelled sample or template text and list what you found.`

## Two habits

- Plan before you build (plan mode, or start the message with `/plan`).
- Type `/clear` when you switch tasks, so old instructions do not leak into new work.
