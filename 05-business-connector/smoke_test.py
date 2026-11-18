"""Episode 5 smoke test. No model, no API key, no cost.

Runs against an ISOLATED copy (temp DB, port 8801), so a running demo on 8800 is untouched.
  1. booking app: auth, roles (read-only-connector refused on every change endpoint), front-desk can change
  2. noor-bookings (real): exactly 4 tools, one test per tool, no phone field, rows changed = 0
  3. noor-bookings-test (WRONG ON PURPOSE): 5 tools, phones leak, cancel works with the front-desk key,
     and the SAME cancel is refused by the booking system with the read-only key (box 3 holds alone)

Usage:  .venv\\Scripts\\python.exe smoke_test.py      (writes test-results/smoke_test.txt)
"""
from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

from mcp.client import Client
from mcp.client.stdio import StdioServerParameters

ROOT = Path(__file__).resolve().parent
APP = ROOT / "noor-booking-app"
PY = sys.executable
PORT = 8801
URL = f"http://127.0.0.1:{PORT}"
CONNECTOR, FRONT_DESK = "noor_test_FAKE_0000", "noor_desk_FAKE_1111"
EXPECTED = {"list_tomorrow_bookings", "find_available_slots", "get_booking_summary", "draft_reschedule"}
LINES: list[str] = []
FAILS = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global FAILS
    FAILS += 0 if ok else 1
    line = f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  ({detail})" if detail else "")
    print(line, flush=True)
    LINES.append(line)


def http(method: str, path: str, token: str | None = None, body: dict | None = None):
    data = json.dumps(body).encode() if body is not None else (b"{}" if method == "POST" else None)
    h = {"Content-Type": "application/json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(URL + path, method=method, data=data, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


def snapshot(env) -> dict:
    out = subprocess.run([PY, "-c", "import db,json;c=db.connect();print(json.dumps([list(r) for r in c.execute("
                          "'SELECT id,start,status,note FROM bookings ORDER BY id')]))"],
                         cwd=APP, env=env, capture_output=True, text=True, check=True)
    return {r[0]: r for r in json.loads(out.stdout)}


def rows_changed(a: dict, b: dict) -> int:
    return sum(1 for k in set(a) | set(b) if a.get(k) != b.get(k))


def tool_json(result) -> dict:
    if getattr(result, "structured_content", None):
        sc = result.structured_content
        return sc.get("result", sc) if isinstance(sc, dict) and set(sc) == {"result"} else sc
    return json.loads(result.content[0].text)


def server(folder: str, token: str, env) -> StdioServerParameters:
    e = dict(env, NOOR_API_TOKEN=token, NOOR_API_URL=URL)
    return StdioServerParameters(command=PY, args=[str(ROOT / folder / "server.py")], env=e, cwd=str(ROOT / folder))


async def mcp_checks(env) -> None:
    # ---- real connector ----
    before = snapshot(env)
    async with Client(server("noor-bookings", CONNECTOR, env)) as c:
        tools = (await c.list_tools()).tools
        names = {t.name for t in tools}
        check("noor-bookings lists exactly the 4 frozen tools", names == EXPECTED, f"{len(names)}: {sorted(names)}")
        check("every tool annotated read-only", all(t.annotations and t.annotations.read_only_hint for t in tools))

        r = tool_json(await c.call_tool("list_tomorrow_bookings", {}))
        keys = set().union(*(b.keys() for b in r["bookings"]))
        check("test_list_tomorrow_bookings", r["active_count"] > 0 and keys == {"id", "patient_name", "time", "dentist", "status"},
              f"active={r['active_count']} unconfirmed={r['unconfirmed_count']} fields={sorted(keys)}")
        tomorrow = r["date"]

        r = tool_json(await c.call_tool("find_available_slots", {"date": "tomorrow", "dentist": "Dr Sana", "part_of_day": "afternoon"}))
        check("test_find_available_slots", r["count"] > 0 and all(s["time"] >= "13:00" for s in r["slots"]),
              f"Dr Sana tomorrow afternoon: {[s['time'] for s in r['slots']]}")
        slot = f"{r['slots'][0]['date']} {r['slots'][0]['time']}"
        bad = await c.call_tool("find_available_slots", {"date": "2026-02-31"})
        check("find_available_slots rejects a bad date, message reaches the model", bad.is_error
              and "not a real date" in bad.content[0].text, bad.content[0].text)

        bid = next(b["id"] for b in tool_json(await c.call_tool("list_tomorrow_bookings", {}))["bookings"]
                   if b["status"] == "unconfirmed")
        r = tool_json(await c.call_tool("get_booking_summary", {"booking_id": bid}))
        check("test_get_booking_summary (no phone field)", "patient_phone" not in r and "phone" not in json.dumps(r).lower()
              and "patient_note_untrusted" in r, f"fields={sorted(r)}")

        r = tool_json(await c.call_tool("draft_reschedule", {"booking_id": bid, "new_slot": slot}))
        check("test_draft_reschedule returns DRAFT, changed=False", r["status"] == "DRAFT" and r["changed"] is False
              and r["new_slot_free"] is True, f"#{bid} {r['old_time']} -> {r['new_time']}")
    after = snapshot(env)
    n = rows_changed(before, after)
    check("rows changed after all noor-bookings calls == 0", n == 0, f"rows changed: {n}")
    src = (ROOT / "noor-bookings" / "server.py").read_text(encoding="utf-8")
    check("server.py has no change method", not any(m in src for m in ('"POST"', "'POST'", '"PUT"', '"DELETE"', '"PATCH"')))

    # ---- WRONG ON PURPOSE test copy ----
    async with Client(server("noor-bookings-test", FRONT_DESK, env)) as c:
        names = {t.name for t in (await c.list_tools()).tools}
        check("noor-bookings-test has 5 tools incl. cancel_appointment", names == EXPECTED | {"cancel_appointment"}, f"{sorted(names)}")
        r = tool_json(await c.call_tool("get_booking_summary", {"booking_id": bid}))
        check("test copy leaks phone (mistake 4, expected)", "patient_phone" in r, f"phone={r.get('patient_phone')}")
        b4 = snapshot(env)
        res = await c.call_tool("cancel_appointment", {"booking_id": bid})
        n = rows_changed(b4, snapshot(env))
        check("test copy + front-desk key CAN cancel (the danger, expected)", not res.is_error and n == 1, f"rows changed: {n}")
    async with Client(server("noor-bookings-test", CONNECTOR, env)) as c:
        other = next(b for b in http("GET", f"/bookings?date={tomorrow}", CONNECTOR)[1]["bookings"] if b["status"] == "confirmed")["id"]
        b4 = snapshot(env)
        res = await c.call_tool("cancel_appointment", {"booking_id": other})
        n = rows_changed(b4, snapshot(env))
        msg = res.content[0].text if res.content else ""
        check("test copy + read-only key: booking system refuses cancel", res.is_error and n == 0 and "403" in msg, msg[:220])


def main() -> int:
    tmp = tempfile.mkdtemp(prefix="noor-smoke-")
    env = dict(os.environ, NOOR_DB_PATH=str(Path(tmp) / "bookings.db"), NOOR_PORT=str(PORT), PYTHONIOENCODING="utf-8")
    env.pop("NOOR_API_TOKEN", None)
    subprocess.run([PY, "seed.py"], cwd=APP, env=env, check=True)
    app = subprocess.Popen([PY, "app.py"], cwd=APP, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(50):
            try:
                if http("GET", "/health")[0] == 200:
                    break
            except Exception:
                time.sleep(0.2)
        check("app /health", http("GET", "/health")[0] == 200)
        check("no token -> 401", http("GET", "/bookings")[0] == 401)
        check("bad token -> 401", http("GET", "/bookings", "nope")[0] == 401)
        s, r = http("GET", "/whoami", CONNECTOR)
        check("connector key role = read-only-connector", r.get("role") == "read-only-connector")
        s, r = http("POST", "/bookings/22/cancel", CONNECTOR)
        check("read-only-connector cancel -> 403", s == 403, r.get("message", ""))
        s, r = http("POST", "/bookings/22/reschedule", CONNECTOR, {"start": "2030-01-01 10:00"})
        check("read-only-connector reschedule -> 403", s == 403)
        s, r = http("POST", "/keys/rotate", CONNECTOR, {"label": "read-only-connector"})
        check("read-only-connector key rotate -> 403", s == 403)
        asyncio.run(mcp_checks(env))
        s, r = http("POST", "/bookings/20/cancel", FRONT_DESK)
        check("front-desk cancel -> 200", s == 200 and r["booking"]["status"] == "cancelled")
        s, r = http("POST", "/keys/rotate", FRONT_DESK, {"label": "read-only-connector"})
        check("front-desk rotates connector key", s == 200)
        check("old connector key now refused (401)", http("GET", "/bookings", CONNECTOR)[0] == 401)
    finally:
        app.terminate()
        app.wait(timeout=10)
    summary = f"\n{len(LINES) - FAILS}/{len(LINES)} PASS"
    print(summary)
    out = ROOT / "test-results" / "smoke_test.txt"
    out.parent.mkdir(exist_ok=True)
    out.write_text(f"smoke_test.py  {time.strftime('%Y-%m-%d %H:%M')}  python {sys.version.split()[0]}\n"
                   + "\n".join(LINES) + summary + "\n", encoding="utf-8")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
