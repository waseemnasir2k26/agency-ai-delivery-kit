# QA-CHECKLIST.md: run by hand at 375px wide (Chrome, F12, device toolbar)
1. Scroll the whole page. Nothing scrolls sideways, nothing is cut off.
2. Every button and link is easy to tap with a thumb (about 44px tall or more).
3. Phone field: empty → refused. "abc" → refused. +92 300 0000000 → accepted.
4. Send one correct enquiry. It appears in inbox.html, labelled TEST INBOX.
5. Read every price, review and contact detail. Each sample item shows a SAMPLE label. No lorem ipsum, no "your text here".
6. Tap every button and link. Each one goes where its label says (Call dials the number shown).

---

## How to see the page at phone width (Chrome)

1. Open `index.html` with a double click, so it opens in Chrome.
2. Press **F12** (on a Mac: **Cmd + Option + I**). The developer tools open.
3. Click the small **phone and tablet icon** at the top left of the developer tools ("Toggle device toolbar"). Shortcut: **Ctrl + Shift + M** (Mac: **Cmd + Shift + M**).
4. In the bar above the page, pick a phone from the **Dimensions** list, or choose **Responsive** and type `375` as the width.
5. Reload the page (F5) and run the six lines above, top to bottom. Write PASS or FAIL next to each line.

## How to measure a button (line 2)

Right-click the button or link → **Inspect**. Hover the highlighted line in the Elements panel: Chrome shows the element's size, for example `a 312 × 22`. The second number is the height. Under 44 means it fails line 2.

## Rules for using this checklist

- Write the lines before you look at the page. Once a page looks good, people stop looking for problems.
- The person who approves the page runs the check, not Claude.
- After a fix, rerun the exact line that failed, then all six again: a fix can break something else.
- Scope of this check: one browser (Chrome), one phone width, by hand. It is not a test on real devices, other browsers or slow connections.
