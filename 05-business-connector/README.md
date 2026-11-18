# 05 · Business Connector — Business Connector Pack

**For the owner:** connect an AI assistant to a client's own system (here, a clinic's bookings) so staff get answers
and drafts in seconds, while no AI can change, cancel or create anything. A person applies every change, and the
handover page shows the client exactly what the assistant can and cannot do, with the tests that prove it.

**Shown in:** Episode 5, "What the receptionist gets, and the three boxes", "Box three first: the client's system and
its key", "Box one: four tools, and a test bench", "Box two: connect it, name the tools", "The business payoff: Site
Watch checks the website against the system", "Break test one: the cancel tool, added "for convenience"", "Break test
two: the note that gives orders", "A quick third: the key in the repo", "The key: rotate first, then a real scanner",
"What the client receives, limits, pack, next".

> Noor Dental Clinic, its patients and all data are fictional. Synthetic data only. Not medical or legal advice.
> Fixture keys are FAKE and test-only: `noor_test_FAKE_0000` (read-only-connector) and `noor_desk_FAKE_1111` (front-desk).

## What's inside

| Path                                                            | What it is                                                                                                                                                                                                                                                                                                                                              |
| --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `noor-booking-app/`                                             | The clinic's booking system (Python stdlib only): SQLite + local API on `127.0.0.1:8800` + browser dashboard (`/`), public site (`/site`) and booking form (`/site/book`). Two key roles: `front-desk` (read + change) and `read-only-connector` (read only, every change refused with 403). `seed.py` / `reset.py` rebuild `bookings.db` (not shipped) |
| `noor-booking-app/seed_note.py`                                 | The planted patient note fixture (break test 2: "Assistant, ignore your rules...")                                                                                                                                                                                                                                                                      |
| `noor-booking-app/plant_stale_slot.py`                          | Makes `/site` advertise a slot that is already booked (for the Site Watch check); `--clear` undoes it                                                                                                                                                                                                                                                   |
| `noor-booking-app/keys.py` · `snapshot.py`                      | Key list / rotate from the terminal · before/after "rows changed" evidence                                                                                                                                                                                                                                                                              |
| `noor-bookings/server.py`                                       | The connector: exactly four tools (`list_tomorrow_bookings`, `find_available_slots`, `get_booking_summary`, `draft_reschedule`), GET only, field whitelist (no phone), inputs validated, logging to stderr                                                                                                                                              |
| `noor-bookings/.mcp.json`                                       | Registers the server with `"NOOR_API_TOKEN": "${NOOR_API_TOKEN}"`: a label, no secret in the file                                                                                                                                                                                                                                                       |
| `noor-bookings/.claude/settings.json`                           | The four tools allowed by name, `cancel_appointment` and the whole test server denied, `"defaultMode": "default"`                                                                                                                                                                                                                                       |
| `noor-bookings-test/`                                           | **WRONG ON PURPOSE** copy (README headed "WRONG ON PURPOSE. Never point this at a real system."): a fifth tool `cancel_appointment`, a wildcard allow, every column returned                                                                                                                                                                            |
| `variants/`                                                     | Settings and config states: build, wrong wildcard, fixed, and the FAKE key committed into `.mcp.json` (see `variants/README.md`)                                                                                                                                                                                                                        |
| `smoke_test.py`                                                 | No-model test on an isolated temp copy (port 8801): key roles, one test per tool, rows changed = 0, and the wrong copy's dangers. Writes `test-results/smoke_test.txt`                                                                                                                                                                                  |
| `site_watch_noor.py` · `verify_noor.py`                         | The Site Watch patch (Episode 4 agent + one connector tool) and its slot re-check. See `SITE-WATCH-PATCH.md`                                                                                                                                                                                                                                            |
| `SITE-WATCH-PATCH.md`                                           | The three changes: `mcp_servers` entry, single `allowed_tools` name, verifier slot re-check                                                                                                                                                                                                                                                             |
| `.gitleaks.toml` · `.pre-commit-config.yaml` · `ci-secrets.yml` | Secret scanning: custom rule for the test token shape, pre-commit hook, CI workflow                                                                                                                                                                                                                                                                     |
| `SECRET-SCANNING.md`                                            | Leaked-key order of work (revoke and rotate, remove, history, scanner) and how to run the scanner                                                                                                                                                                                                                                                       |
| `handover-noor.md`                                              | Filled one-page client handover for Noor: tool, reads, returns, who applies the change, tests run, approver                                                                                                                                                                                                                                             |
| `handover-template.md`                                          | The same page, blank, for your client                                                                                                                                                                                                                                                                                                                   |
| `tool-surface-checklist.md`                                     | Per tool: which box stops it, most it can return, personal fields returned, worst case if a stranger controlled the prompt                                                                                                                                                                                                                              |
| `SCRIPTED-RUNS.md`                                              | `claude -p` and SDK runs load project `.mcp.json` servers without the approval prompt; how to keep a server out                                                                                                                                                                                                                                         |
| `ADVANCED.md`                                                   | Over-large results (10,000 / 25,000 token figures, saved-file behaviour, `count` + paged `search`), tool search and the first line of a description, the stdout rule, the unset-variable warning, HTTP transport for teams                                                                                                                              |
| `requirements.txt`                                              | `mcp[cli]>=2.3,<3` (plus the optional Site Watch packages, commented)                                                                                                                                                                                                                                                                                   |
| `.gitignore`                                                    | Keeps the venv, `bookings.db`, test results and `.env` out of git                                                                                                                                                                                                                                                                                       |

## Use it in 5 steps

Commands are PowerShell from this folder. On macOS / Linux use `.venv/bin/python` instead of `.venv\Scripts\python.exe`.

1. **Prerequisites.** Python 3.11+, Node (for the Inspector), Claude Code, Git. Create the project venv here:
   ```powershell
   python -m venv .venv
   .venv\Scripts\python.exe -m pip install -r requirements.txt
   .venv\Scripts\python.exe -c "import mcp, importlib.metadata as m; print('mcp', m.version('mcp'))"
   node --version; claude --version; git --version
   ```
2. **Start the clinic's system and run the no-model tests:**
   ```powershell
   cd noor-booking-app
   ..\.venv\Scripts\python.exe reset.py          # 40 synthetic bookings, 15 tomorrow, 5 unconfirmed
   ..\.venv\Scripts\python.exe app.py            # http://127.0.0.1:8800 (sign in with a FAKE key above)
   # second terminal, from this folder (uses its own temp copy on port 8801, never touches 8800):
   .venv\Scripts\python.exe smoke_test.py        # expect 23/23 PASS
   ```
   Call the tools by hand, no AI: `cd noor-bookings`, `$env:NOOR_API_TOKEN = "noor_test_FAKE_0000"`, then
   `npx @modelcontextprotocol/inspector ../.venv/Scripts/python.exe server.py -e NOOR_API_TOKEN=$env:NOOR_API_TOKEN`.
3. **Register the connector** (already done in the shipped `noor-bookings/.mcp.json`; this is how it was made):

   ```powershell
   cd noor-bookings
   claude mcp add --transport stdio --scope project noor-bookings -e 'NOOR_API_TOKEN=${NOOR_API_TOKEN}' -- ../.venv/Scripts/python.exe server.py
   ```

   - **Name before `-e`.** `-e` takes several values, so a name placed right after it is read as another variable and
     rejected (`Invalid environment variable format: noor-bookings`). Put the server name first.
   - **Single quotes** keep `${NOOR_API_TOKEN}` literal, so `.mcp.json` stores the label, not the key.
   - **Windows: point at the venv interpreter, not bare `python`.** A global `python` without `mcp` starts and fails.
     Generic form: `-- <project>\.venv\Scripts\python.exe server.py` (the shipped file uses the relative
     `../.venv/Scripts/python.exe`, which Claude Code resolves from the project folder).

4. **Connect it, with the read-only key from the environment only:**
   ```powershell
   $env:NOOR_API_TOKEN = "noor_test_FAKE_0000"   # read-only-connector FAKE fixture key; never in a file
   claude mcp list                               # a missing-variable warning means the key is not set
   claude                                        # first time: trust the folder AND approve noor-bookings
   ```
   Then ask: `List tomorrow's bookings.` Until the folder is trusted, the allow rules in `.claude/settings.json` do not count.
   For scripts, read `SCRIPTED-RUNS.md` first.
5. **Break it, fix it, hand it over.** Break tests run only in `noor-bookings-test/` (WRONG ON PURPOSE) with
   `reset.py` before each run and `snapshot.py dump/diff` around it; break test 2 adds `seed_note.py`. The fix is
   `variants/settings.fixed.json` (already in `noor-bookings/`), the read-only key, and no cancel tool. Turn on the
   scanner (`SECRET-SCANNING.md`), fill `tool-surface-checklist.md` and `handover-template.md`, and get the named
   approver to sign. Optional: the Site Watch check in `SITE-WATCH-PATCH.md` (billed model run).

## Limits — what it does NOT do

- Fictional clinic, local test system, synthetic data. Real patient data needs its own privacy and legal review
  before any connector touches it.
- It cannot change bookings, by design. Drafts are text; a person applies them in the dashboard.
- The `patient_note_untrusted` label is a warning, not a lock. The locks are the missing tools, the missing fields
  and the read-only key. Every other tool in the same session counts too: keep client-data sessions small.
- The recorded break-test results (handover page) came from the model available when they were recorded. They were
  not re-run for the kit; rerun them when the model, the connector or the settings change.
- Scripted runs (`claude -p`, SDK) start project servers without asking. See `SCRIPTED-RUNS.md`.
- stdio only, one machine per key. The HTTP-for-teams setup in `ADVANCED.md` is described, not built.
- The scanner catches only the shapes in its rules; it does not replace key rotation.
- `.mcp.json` and `site_watch_noor.py` point at the Windows venv path; change to `.venv/bin/python` on macOS / Linux.

## Tested

Offline, on a scratch copy with `mcp` 2.x: all 13 `.py` files compile; `seed.py`, `seed_note.py`,
`plant_stale_slot.py` (plant + clear), `snapshot.py` dump/diff (1 row changed: the planted note), `keys.py list` and
`reset.py` ran; `smoke_test.py` 23/23 PASS (including one test per tool); all settings/`.mcp.json` files parse;
gitleaks with `.gitleaks.toml` flagged only the FAKE fixture tokens (rule `noor-api-token`).
Claude Code, Inspector and Site Watch live runs were SKIPPED (need Claude Code login / Node / API key).
