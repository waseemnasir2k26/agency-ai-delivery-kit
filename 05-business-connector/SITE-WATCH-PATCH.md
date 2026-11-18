# Site Watch patch: check the website against the booking system

Episode 5 reuses the Episode 4 agent (Module 4, `site_watch.py`) for one business check: does the clinic's public
site advertise a "Next free slot" that the booking system says is taken? The patched copy is `site_watch_noor.py`;
its judge is `verify_noor.py`. Both are in this folder.

## The three changes

**1. An `mcp_servers` entry for the connector**, next to Site Watch's own in-process server:

```python
mcp_servers={"sitewatch": server,
             "noor-bookings": {"command": VENV_PYTHON, "args": [str(NOOR_DIR / "server.py")],
                               "env": {"NOOR_API_TOKEN": os.environ["NOOR_API_TOKEN"]}}},
```

`VENV_PYTHON` is the project venv's interpreter (Windows: `<project>\.venv\Scripts\python.exe`;
macOS / Linux: `<project>/.venv/bin/python`). The key comes from the environment and must be the
**read-only-connector** key.

**2. A single connector tool name in `allowed_tools`** (never a wildcard):

```python
allowed_tools=["mcp__sitewatch__report", "mcp__noor-bookings__find_available_slots"],
```

Site Watch can read free slots and nothing else from the booking system. `visit` stays out of `allowed_tools`,
so the localhost guard (`can_use_tool`) still runs on every visit.

**3. The verifier re-checks the slot itself** (`verify_noor.py`, no model). It reads the "Next free slot" text from
the live `/site` page, asks the booking API (`GET /slots`) whether that time is free with that dentist, and prints
PASS or FAIL. The agent's own finding is printed next to it, but `verify_noor.py` decides.

## Run it (billed: Site Watch calls a model)

```
# terminal 1: the booking app
cd noor-booking-app
python reset.py
python plant_stale_slot.py        # CONTROLLED TEST: /site advertises tomorrow 10:00 Dr Sana, which is booked
python app.py

# terminal 2, from this folder (needs claude-agent-sdk + playwright, and your Claude login or API key)
$env:NOOR_API_TOKEN = "<read-only-connector key>"      # PowerShell; bash: export NOOR_API_TOKEN=...
python site_watch_noor.py --out results/S1
python verify_noor.py results/S1

# afterwards
cd noor-booking-app
python plant_stale_slot.py --clear
```

Recorded result (Episode 5, fixture data): the planted stale slot was caught. The page said 10:00, the system had
10:00 booked, and the first free slot was 12:30. Not re-run for the kit (needs a Claude login or API key).

`VENV_PYTHON` in `site_watch_noor.py` is written for Windows (`.venv/Scripts/python.exe`). On macOS / Linux,
change it to `.venv/bin/python`.
