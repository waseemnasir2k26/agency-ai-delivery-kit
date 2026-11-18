# Gate sheet: what the approver reads, and may not skip

One page for the person whose name goes into `gates.md`. The AI prepares and checks. A named person decides.
Each approval is recorded with `python pipeline.py approve <gate> --job <job> --by "<name>" --role <role>`:
who, what, which version, when. It is a recorded approval, not a legal signature, and it does not stop someone
typing a name they should not. Gates are approved in order; `pipeline.py` refuses a gate whose earlier gate is empty.

| Gate                                   | Who approves                                 | What they read                                                                               | What they may NOT skip                                                                                                                                                                                                                                        | Recorded as                                     |
| -------------------------------------- | -------------------------------------------- | -------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------- |
| **1 SEND** (proposal → client)         | The owner (or the named account lead)        | `proposal.md` · `unknowns.json` · the critic's verdict on the draft                          | Edit the draft themselves. Check every price and number was filled in by them, not by the model. Check no line promises rankings, sales, traffic or a result by a deadline. Send it **by hand**: the pipeline has no tool that can message a client.          | row 1: commit + `proposal.md` hash              |
| **2 MERGE** (build → main)             | The owner, not the builder                   | The pull request diff (all changed lines) · `check-site.py` result · the `pr-review` verdict | A green review means an agent approved, not that a person looked. Read the diff. Every price, hour and offer on the page must come from `data/<client>.json`. No merge while `pr-review` says REJECTED (the pipeline refuses).                                | row 2: merge commit + number of diff lines read |
| **3 GO-LIVE** (preview → live)         | The owner                                    | The preview page itself · `verify.json` verdict · the Site Watch findings                    | Open the preview yourself. Send **one test enquiry by hand** and confirm it arrives where the client asked. Read every NOT CHECKED and REJECTED line. On GitHub this is the required-reviewer approval of the `live` environment.                             | row 3: commit + verify verdict                  |
| **4 APPROVE REPORT** (report → client) | The owner, not the person who built the page | `report.md` from `build_report.py` · each evidence link                                      | Open the live page yourself. Every line has evidence (page, quoted text, screenshot). Every "needs a human look" item is fixed, or told to the client. NOT CHECKED is never PASS. The pipeline refuses if the report says "passed" where the counts disagree. | row 4: commit + `report.md` hash                |

## Rules for every gate

- The approver is a named person and a role. Never a shared inbox, never the build agent.
- The approval is for one exact version (commit, file hash). A change after approval needs a new approval.
- If anything on this sheet was skipped, do not record the gate. Write what is missing instead.
- Which gate must always stay human? All four. The machine prepares; a person decides.
