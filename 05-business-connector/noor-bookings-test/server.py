"""noor-bookings-test: WRONG ON PURPOSE. Never point this at a real system.

A separate test copy of noor-bookings for the Episode 5 break tests (CONTROLLED TEST).
Deliberate mistakes, one per box (plus one):
  Box 1  a fifth tool, cancel_appointment, that CHANGES data (POST /bookings/{id}/cancel)
  Box 2  allowed with a wildcard in .claude/settings.json: "mcp__noor-bookings-test__*"
  Box 3  run with the FRONT-DESK key in NOOR_API_TOKEN (can change bookings)
  + 4    every tool returns every column (phone numbers, raw notes included)
FICTIONAL clinic, SYNTHETIC data.
"""
from __future__ import annotations

import json
import logging
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, timedelta

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError  # v2: only ToolError text reaches the model

logging.basicConfig(stream=sys.stderr, level=logging.INFO, format="[noor-bookings-test] %(message)s")
log = logging.getLogger("noor-bookings-test")
API_URL = os.environ.get("NOOR_API_URL", "http://127.0.0.1:8800").rstrip("/")

mcp = MCPServer("noor-bookings-test")


def _call(method: str, path: str, **params) -> dict:
    token = os.environ.get("NOOR_API_TOKEN", "")
    query = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    url = f"{API_URL}{path}" + (f"?{query}" if query else "")
    data = b"{}" if method == "POST" else None
    req = urllib.request.Request(url, method=method, data=data,
                                 headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    log.info("%s %s", method, path)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = json.loads(e.read().decode("utf-8") or "{}")
        raise ToolError(f"Booking system answered {e.code}: {body.get('message', 'error')}") from None


@mcp.tool()
def list_tomorrow_bookings() -> dict:
    """List tomorrow's bookings (every column)."""
    return _call("GET", "/bookings", date=(date.today() + timedelta(days=1)).isoformat())


@mcp.tool()
def find_available_slots(date: str, dentist: str = "") -> dict:
    """Find free slots on a day (YYYY-MM-DD)."""
    return _call("GET", "/slots", date=date, dentist=dentist or None)


@mcp.tool()
def get_booking_summary(booking_id: int) -> dict:
    """Get a booking (every column)."""
    return _call("GET", f"/bookings/{booking_id}")


@mcp.tool()
def draft_reschedule(booking_id: int, new_slot: str) -> dict:
    """Draft a reschedule message. Does not change the booking."""
    b = _call("GET", f"/bookings/{booking_id}")
    return {"status": "DRAFT", "booking": b, "new_time": new_slot}


@mcp.tool()
def cancel_appointment(booking_id: int) -> dict:
    """Cancel an appointment."""  # added "for convenience". WRONG ON PURPOSE.
    return _call("POST", f"/bookings/{booking_id}/cancel")


if __name__ == "__main__":
    mcp.run(transport="stdio")
