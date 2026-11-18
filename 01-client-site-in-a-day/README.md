# 01 · Client Site in a Day — Business Website Starter

**For the owner:** Turn a one-paragraph client brief into a mobile-first website preview in one sitting, with a person approving the plan and the edits. A written six-line check catches what a good-looking page hides (thumb-sized buttons, a Call link that dials the wrong number) before a client sees it. Nothing goes live without the client's written yes.

**Shown in:** Episode 1, "The brief", "The permission prompt, and who decides", "Plan first", "The rule sheet: CLAUDE.md", "BREAK: five checks before a client sees it", "FIX: report it, add the rule, rerun the same check" and "Handover, limits, resource, next problem".

Kiran Studio and Mehr Bakery are fictional. Every menu item, price and review in the starter is SAMPLE content, and the phone number is the placeholder +92 300 0000000.

## What's inside

| Path                                           | What it is                                                                                                                                                                              |
| ---------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `BRIEF-TEMPLATE.md`                            | The one-paragraph client brief with five blanks (who, customer, must do, feel, still missing), plus the Mehr Bakery brief as the worked example.                                        |
| `starter/index.html`                           | The Mehr Bakery page as built in the episode after both fixes (tap targets, Call link): hero, SAMPLE menu, TEST MODE enquiry form, SAMPLE reviews.                                      |
| `starter/styles.css`                           | Mobile-first styles, including the 44px tap-target rule added in the fix.                                                                                                               |
| `starter/site.js`                              | Form validation and the TEST MODE inbox: enquiries are saved in the browser only, nothing is sent over the internet.                                                                    |
| `starter/inbox.html`                           | The TEST INBOX page that lists enquiries saved in this browser.                                                                                                                         |
| `starter/BRIEF.md`                             | The brief as saved by Claude before anything was built.                                                                                                                                 |
| `starter/CLAUDE.md`, `starter/QA-CHECKLIST.md` | The project's rule sheet and checklist, as they sit in the project folder.                                                                                                              |
| `starter/.claude/settings.json`                | Pins the project's starting permission mode to Manual: `{"permissions": {"defaultMode": "default"}}`.                                                                                   |
| `starter/.claude/SETTINGS-NOTE.md`             | The header note for `settings.json` (JSON cannot hold comments).                                                                                                                        |
| `CLAUDE.md`                                    | The project rule sheet: the 9 lines from the episode's rule-sheet chapter plus the 44px tap-target rule added in the fix (10 lines).                                                    |
| `CLAUDE-STARTER.md`                            | A blank rule-sheet template for your own project.                                                                                                                                       |
| `QA-CHECKLIST.md`                              | The mobile check: the five lines written by hand in the episode plus line 6 ("tap every button and link"), and how to open Chrome's device toolbar and measure a button.                |
| `CLIENT-CONTENT-CHECKLIST.md`                  | What to collect from the client before publishing: real menu, prices, photos, contact details, enquiry destination, written go-live approval.                                           |
| `PROMPTS.md`                                   | Every prompt typed in the episode, including the tap-target and Call-link bug reports as sent, three spare bug-report templates (overflow, phone, placeholder) and the settings prompt. |
| `PERMISSION-MODES.md`                          | One page: manual, accept edits, plan, auto; what each asks; the bottom line; Shift+Tab; `/plan`; `/auto-mode-setup`.                                                                    |
| `MEMORY-NOTES.md`                              | `CLAUDE.md` (you write it, you control it) vs auto memory (Claude writes it; `/memory`; `"autoMemoryEnabled": false`), `/init`, `AGENTS.md`, `/clear`.                                  |
| `WINDOWS-NOTES.md`                             | PowerShell vs CMD, "claude is not recognised", Git for Windows (needed from Episode 2), Bash and PowerShell side by side.                                                               |

## Use it in 5 steps

1. **Check the prerequisites.** Claude Code needs a paid Claude plan or a Claude Console account; the free plan does not include it. Install it from https://code.claude.com/docs/en/setup, then in a new terminal:

   ```bash
   claude --version
   ```

   Windows: use PowerShell and read `WINDOWS-NOTES.md`. The starter itself needs no install: it opens in any browser.

2. **Look at the finished example.** Double-click `starter/index.html`. Run `QA-CHECKLIST.md` against it at 375px wide (instructions in that file). In the recorded episode this copy passed all six lines.

3. **Start your own project.** Make a new empty folder for your client, open a terminal in it, and copy in the settings pin and the rule-sheet template:

   ```bash
   # macOS / Linux / WSL, from inside your new project folder
   mkdir -p .claude
   cp <path-to-kit>/01-client-site-in-a-day/starter/.claude/settings.json .claude/
   cp <path-to-kit>/01-client-site-in-a-day/CLAUDE-STARTER.md CLAUDE.md
   ```

   ```powershell
   # Windows PowerShell
   New-Item -ItemType Directory -Force .claude
   Copy-Item <path-to-kit>\01-client-site-in-a-day\starter\.claude\settings.json .claude\
   Copy-Item <path-to-kit>\01-client-site-in-a-day\CLAUDE-STARTER.md CLAUDE.md
   ```

   Edit `CLAUDE.md` (replace every `[...]`). Then type `claude` and check the bottom line says manual mode.

4. **Brief, plan, build.** Fill `BRIEF-TEMPLATE.md`, paste the paragraph and ask Claude to save it as `BRIEF.md`. Switch to plan mode (Shift+Tab, or `/plan`) and send the plan prompt from `PROMPTS.md`. Read the plan, approve it, read the first edit. Give feedback in three parts: what is wrong, where, what good looks like.

5. **Check, fix, hand over.** Copy `QA-CHECKLIST.md` into the project and run all six lines yourself. For each failure, send a bug report (templates in `PROMPTS.md`), add one rule to `CLAUDE.md`, and rerun the same line, then all six. Hand the client the preview, what you checked, and `CLIENT-CONTENT-CHECKLIST.md`. Publish only after their written yes.

## Limits — what it does NOT do

- It does not put anything online. No hosting, no deploy, no domain. Going live is a separate step after the client's written yes.
- The enquiry form is TEST MODE: enquiries are saved in this browser only and reach nobody. A real destination needs the client's details and a separate build.
- All content is SAMPLE. Menu, prices, reviews and phone number must be replaced with the client's real ones.
- The checklist was run by hand in one browser (Chrome) at one phone width. It is not a test on real devices, other browsers, slow connections or screen readers.
- A written checklist only catches what is written on it. A person still taps every button before a client sees the page.
- `CLAUDE.md` is guidance Claude reads, not a lock. The check you run is the proof.
- Claude Code output varies between runs: your build will not match the starter line for line.
- Permission-mode names, the starting mode and prompt wording can change between Claude Code releases. Re-check `PERMISSION-MODES.md` against https://code.claude.com/docs after each update.

## Tested

Offline for the kit: `starter/.claude/settings.json` parses; a Python open-check of `starter/` passed 14/14 (all local links resolve, no template text, the Call `tel:` link dials the number shown, every item and review carries SAMPLE, the 44px tap-target rule is in `styles.css`, `site.js` passes `node --check` and has no network calls). The six-line checklist itself was run by hand in the episode's recording.
