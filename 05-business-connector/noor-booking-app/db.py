"""Shared database helpers for noor-booking-app.

FICTIONAL clinic. SYNTHETIC data only. Not medical or legal advice.
"""
from __future__ import annotations

import hashlib
import os
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("NOOR_DB_PATH", APP_DIR / "bookings.db"))

DENTISTS = ["Dr Sana", "Hygienist"]
OPEN_HOUR, CLOSE_HOUR = 9, 17          # last slot starts 16:30
SLOT_MINUTES = 30
LUNCH = {"Dr Sana": {"13:00", "13:30"}}  # Dr Sana does not book over lunch

ROLES = ("front-desk", "read-only-connector")

SCHEMA = """
CREATE TABLE IF NOT EXISTS dentists (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    dentist_id INTEGER NOT NULL REFERENCES dentists(id),
    start TEXT NOT NULL,              -- 'YYYY-MM-DD HH:MM', clinic local time
    duration_min INTEGER NOT NULL DEFAULT 30,
    treatment TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('confirmed','unconfirmed','cancelled','completed','no-show')),
    note TEXT NOT NULL DEFAULT '',     -- free text typed by the patient on the web form (UNTRUSTED)
    source TEXT NOT NULL DEFAULT 'front-desk',
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS api_keys (
    id INTEGER PRIMARY KEY,
    label TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('front-desk','read-only-connector')),
    token_sha256 TEXT NOT NULL UNIQUE,
    last4 TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('active','revoked')),
    created_at TEXT NOT NULL,
    revoked_at TEXT
);
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY,
    at TEXT NOT NULL,
    key_label TEXT,
    role TEXT,
    action TEXT NOT NULL,
    booking_id INTEGER,
    detail TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS site_content (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


def now_iso() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class _Conn(sqlite3.Connection):
    """`with connect() as conn:` commits (or rolls back) AND closes."""

    def __exit__(self, exc_type, exc, tb):
        try:
            return super().__exit__(exc_type, exc, tb)
        finally:
            self.close()


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=10, factory=_Conn)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def sha256(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def day(offset: int) -> str:
    return (date.today() + timedelta(days=offset)).isoformat()


def all_slot_times() -> list[str]:
    out = []
    t = datetime(2000, 1, 1, OPEN_HOUR, 0)
    end = datetime(2000, 1, 1, CLOSE_HOUR, 0)
    while t < end:
        out.append(t.strftime("%H:%M"))
        t += timedelta(minutes=SLOT_MINUTES)
    return out


def free_slots(conn: sqlite3.Connection, day_str: str, dentist: str | None = None) -> list[dict]:
    """Free 30-minute slots on a day, per dentist. Cancelled bookings free their slot."""
    dentists = [dentist] if dentist else DENTISTS
    taken = {
        (r["dentist"], r["start"][11:16])
        for r in conn.execute(
            """SELECT d.name AS dentist, b.start FROM bookings b JOIN dentists d ON d.id=b.dentist_id
               WHERE substr(b.start,1,10)=? AND b.status NOT IN ('cancelled')""",
            (day_str,),
        )
    }
    now = datetime.now()
    slots = []
    for name in dentists:
        for hhmm in all_slot_times():
            if hhmm in LUNCH.get(name, set()):
                continue
            if (name, hhmm) in taken:
                continue
            if datetime.fromisoformat(f"{day_str} {hhmm}") <= now:
                continue  # never offer a slot in the past
            slots.append({"date": day_str, "time": hhmm, "dentist": name})
    slots.sort(key=lambda s: (s["time"], s["dentist"]))
    return slots
