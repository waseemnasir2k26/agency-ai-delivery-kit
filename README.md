# Agency AI Delivery Kit

**The working files behind "Claude Code for Real Business", by SkynetLabs.**
Ten modules plus a bonus, one per episode. Each one is the real build from the video: copied, cleaned, and checked again for this kit.

---

## Who it is for

Owners, CEOs and agency operators who already deliver work for clients and want AI in that delivery without losing control of quality, cost or client data.

This is not a course in prompts. Each module is a system: files you install, a check that can fail, and a named person who approves before anything reaches a client.

## The ten modules

| #     | Module                                                   | The business outcome                                                                                                         |
| ----- | -------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| 01    | [Client site in a day](01-client-site-in-a-day/)         | A client-ready website preview in one session, with a written quality gate it has to pass first.                             |
| 02    | [Repeatable delivery](02-repeatable-delivery/)           | The weekly client report as a skill with a test, guarded by hooks, running unattended and leaving a receipt when it fails.   |
| 03    | [Parallel work](03-parallel-work/)                       | Three client jobs at once without workers overwriting each other, and a merge that waits for an approved review.             |
| 04    | [Website QA agent](04-website-qa-agent/)                 | A nightly agent that checks client sites against the client's own data, and a plain script that decides pass or fail.        |
| 05    | [Business connector](05-business-connector/)             | AI access to a client's booking system that can read and draft, never change. A person makes every change.                   |
| 06    | [AI cost control](06-ai-cost-control/)                   | A measured cost per client job, a cap on every unattended run, and a pricing worksheet built on full cost of delivery.       |
| 07    | [Agency kit plugins](07-agency-kit-plugins/)             | Your skills, hooks and agents as one versioned plugin a new freelancer installs in minutes.                                  |
| 08    | [Team policy](08-team-policy/)                           | A one-page AI policy you can send to a client's security questionnaire, enforced by managed settings and a test that reruns. |
| 09    | [Client delivery pipeline](09-client-delivery-pipeline/) | Brief to approved delivery with four recorded human decisions: send, merge, go-live, approve report.                         |
| 10    | [Evals and regression](10-evals-regression/)             | Know before the client does when an AI job quietly changes, and decide keep, investigate or roll back.                       |
| Bonus | [CEO control room](bonus-ceo-control-room/)              | One command runs a Monday of client maintenance under caps, and one page tells the owner what needs a decision.              |

Every module folder has its own README: the problem in three lines, what is inside, a five-step quickstart with exact commands, its limits, and the episode chapter that shows it.

## Before you start

- **Claude Code** installed, with a paid Claude plan or a Claude Console account. See https://code.claude.com/docs
- **Python 3.11 or newer.**
- **Git.** On Windows, install Git for Windows (hooks run in Git Bash, worktrees need git).
- **An API key in its own Console workspace with a small spend limit** for modules 04, 06, 09, 10 and the bonus, if you want cost per job from a bill instead of a list-price estimate.
- **WSL2 or Linux** for the sandboxed parts of modules 08 and 10.

Modules build on each other the way the season does. Module 09 and the bonus expect the plugin from 07, Site Watch from 04 and the runner from 06.

## Quickstart

```bash
# 1. Start with module 01: it needs nothing but Claude Code and a browser.
cd 01-client-site-in-a-day
#    read README.md, then open starter/index.html in a browser

# 2. Run the free offline checks for the module you care about
#    (each README lists them; VERIFY.md has the results for this release)

# 3. Move to the module that matches your biggest delivery problem.
#    Every module README has its own five steps.
```

## How to read the results in this kit

- All clients and data are fictional: Kiran Studio (the agency), Mehr Bakery, Noor Dental, Sufi Threads.
- Cost figures are Claude Code's own estimates at list price, not invoices. On a subscription login, the session dollar figure is not your bill.
- Guardrails here reduce risk from honest mistakes and injected instructions. None of them is a promise, and each README lists what it does not stop.
- `PROMISES.md` maps every item promised in the videos to its file. `VERIFY.md` lists what was run for this release and what needs your own Claude login.
- After every Claude Code update, rerun the checks before you trust old results.

---

## Want it built for your business?

SkynetLabs installs these systems in agencies and service businesses, adapted to your clients and your tools, or delivers the work white-label.
**https://skynetjoe.com**

## Free tool

**Lead Leak Audit** (MIT) finds where your website loses enquiries: broken forms, silent auto-replies, dead WhatsApp links.
https://github.com/waseemnasir2k26/lead-leak-audit

---

MIT licensed. See `LICENSE`. © SkynetLabs.
