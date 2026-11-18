"""Create bookings.db with deterministic SYNTHETIC data for the fictional Noor Dental Clinic.

All patients are "Test Patient NN". Phones follow the placeholder pattern +92 300 00000NN.
Dates are relative to the day you run this (yesterday, today, tomorrow, day after).

Fixture API keys (FAKE, test-only, committed on purpose so the demo is reproducible):
    front-desk           -> NOOR_FRONT_DESK_TOKEN  (default noor_desk_FAKE_1111)
    read-only-connector  -> NOOR_CONNECTOR_TOKEN   (default noor_test_FAKE_0000)
Only SHA-256 hashes are stored in the database.

Usage:  python seed.py            (refuses if bookings.db exists)
        python seed.py --force    (same as reset.py)
"""
from __future__ import annotations

import os
import random
import sys

import db

FRONT_DESK_TOKEN = os.environ.get("NOOR_FRONT_DESK_TOKEN", "noor_desk_FAKE_1111")
CONNECTOR_TOKEN = os.environ.get("NOOR_CONNECTOR_TOKEN", "noor_test_FAKE_0000")

TREATMENTS = ["Check-up", "Cleaning", "Filling", "Root canal review", "Whitening consult",
              "Crown fitting", "Child check-up", "Braces adjustment"]

# (day offset, time, dentist, status). C=confirmed U=unconfirmed D=completed N=no-show
PLAN = {
    -1: [("09:00", "Dr Sana", "D"), ("09:30", "Hygienist", "D"), ("10:30", "Dr Sana", "D"),
         ("11:00", "Hygienist", "N"), ("12:00", "Dr Sana", "D"), ("14:00", "Dr Sana", "D"),
         ("14:30", "Hygienist", "D"), ("15:30", "Dr Sana", "D"), ("16:00", "Hygienist", "D")],
    0: [("09:00", "Dr Sana", "C"), ("09:30", "Hygienist", "C"), ("10:00", "Dr Sana", "C"),
        ("11:00", "Dr Sana", "C"), ("11:30", "Hygienist", "C"), ("12:00", "Dr Sana", "C"),
        ("14:00", "Hygienist", "C"), ("14:30", "Dr Sana", "C"), ("15:30", "Dr Sana", "U"),
        ("16:30", "Hygienist", "C")],
    1: [("09:00", "Dr Sana", "C"), ("09:00", "Hygienist", "C"), ("09:30", "Dr Sana", "U"),
        ("10:00", "Dr Sana", "C"), ("10:00", "Hygienist", "U"), ("10:30", "Dr Sana", "C"),
        ("11:00", "Dr Sana", "U"), ("11:00", "Hygienist", "C"), ("11:30", "Dr Sana", "C"),
        ("12:00", "Dr Sana", "C"), ("14:00", "Dr Sana", "C"), ("14:00", "Hygienist", "C"),
        ("15:00", "Dr Sana", "U"), ("15:30", "Hygienist", "U"), ("16:30", "Dr Sana", "C")],
    2: [("09:30", "Dr Sana", "C"), ("10:30", "Hygienist", "U"), ("11:30", "Dr Sana", "C"),
        ("14:30", "Dr Sana", "C"), ("15:00", "Hygienist", "C"), ("16:00", "Dr Sana", "U")],
}
STATUS = {"C": "confirmed", "U": "unconfirmed", "D": "completed", "N": "no-show"}
HARMLESS_NOTES = ["Prefers a morning reminder.", "Nervous patient, please explain each step.",
                  "Asked about payment by card.", "First visit."]


def build(force: bool) -> None:
    if db.DB_PATH.exists():
        if not force:
            sys.exit(f"{db.DB_PATH.name} already exists. Use reset.py (or seed.py --force).")
    rng = random.Random(5)  # fixed seed -> same fixture every reset
    conn = db.connect()
    # Drop tables instead of deleting the file, so a reset works while the app is running (Windows file locks).
    conn.executescript("""PRAGMA foreign_keys=OFF;
        DROP TABLE IF EXISTS audit_log; DROP TABLE IF EXISTS api_keys; DROP TABLE IF EXISTS bookings;
        DROP TABLE IF EXISTS patients; DROP TABLE IF EXISTS dentists; DROP TABLE IF EXISTS site_content;
        PRAGMA foreign_keys=ON;""")
    conn.executescript(db.SCHEMA)
    for name in db.DENTISTS:
        conn.execute("INSERT INTO dentists(name) VALUES (?)", (name,))
    dentist_id = {r["name"]: r["id"] for r in conn.execute("SELECT id, name FROM dentists")}
    for i in range(1, 31):
        conn.execute("INSERT INTO patients(name, phone) VALUES (?, ?)",
                     (f"Test Patient {i:02d}", f"+92 300 00000{i:02d}"))
    patient_ids = list(range(1, 31))
    ts = db.now_iso()
    for offset in sorted(PLAN):
        d = db.day(offset)
        rng.shuffle(patient_ids)
        for (hhmm, dentist, st), pid in zip(PLAN[offset], patient_ids):
            note = rng.choice(HARMLESS_NOTES) if rng.random() < 0.25 else ""
            conn.execute(
                """INSERT INTO bookings(patient_id, dentist_id, start, duration_min, treatment, status, note, source, updated_at)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (pid, dentist_id[dentist], f"{d} {hhmm}", 30, rng.choice(TREATMENTS), STATUS[st], note,
                 rng.choice(["front-desk", "web-form", "phone"]), ts),
            )
    for label, role, token in (("front-desk", "front-desk", FRONT_DESK_TOKEN),
                               ("read-only-connector", "read-only-connector", CONNECTOR_TOKEN)):
        conn.execute(
            "INSERT INTO api_keys(label, role, token_sha256, last4, status, created_at) VALUES (?,?,?,?,?,?)",
            (label, role, db.sha256(token), token[-4:], "active", ts),
        )
    conn.execute("INSERT INTO audit_log(at, action, detail) VALUES (?, 'seed', 'fixture loaded')", (ts,))
    conn.commit()
    total = conn.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
    tom = conn.execute("SELECT COUNT(*) FROM bookings WHERE substr(start,1,10)=? AND status!='cancelled'",
                       (db.day(1),)).fetchone()[0]
    unc = conn.execute("SELECT COUNT(*) FROM bookings WHERE substr(start,1,10)=? AND status='unconfirmed'",
                       (db.day(1),)).fetchone()[0]
    conn.close()
    print(f"Seeded {db.DB_PATH.name}: {total} synthetic bookings | tomorrow ({db.day(1)}): {tom} bookings, "
          f"{unc} unconfirmed | keys: front-desk, read-only-connector (FAKE fixture tokens)")


if __name__ == "__main__":
    build(force="--force" in sys.argv)
