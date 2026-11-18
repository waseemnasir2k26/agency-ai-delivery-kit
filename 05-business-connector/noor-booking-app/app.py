"""noor-booking-app: small local booking API + browser dashboard for the FICTIONAL Noor Dental Clinic.

SYNTHETIC data only. Not medical or legal advice. Python stdlib only (no installs).

Run:   python app.py            -> http://127.0.0.1:8800   (NOOR_PORT to change)

Every /api-style endpoint needs:  Authorization: Bearer <token>
Roles (set on the key, checked by the server):
    front-desk           read + change (cancel, reschedule, rotate keys)
    read-only-connector  read only. Every change endpoint refuses it with 403.

Endpoints
    GET  /health                              no auth
    GET  /  /dashboard                        front-desk dashboard (HTML, asks for a key)
    GET  /site                                public clinic home page ("Next free slot")
    GET  /site/book  POST /site/book          public booking-request form (notes box = untrusted text)
    GET  /whoami
    GET  /dentists
    GET  /bookings?date=YYYY-MM-DD[&status=]
    GET  /bookings/{id}
    GET  /slots?date=YYYY-MM-DD[&dentist=Dr Sana]
    POST /bookings/{id}/cancel                front-desk only
    POST /bookings/{id}/reschedule            front-desk only, JSON {"start": "YYYY-MM-DD HH:MM"}
    GET  /keys                                front-desk only (labels, roles, last 4 chars, status)
    POST /keys/rotate                         front-desk only, JSON {"label": "read-only-connector"}
    GET  /audit                               front-desk only (last 50 change events)
"""
from __future__ import annotations

import html
import json
import os
import re
import secrets
import sys
from datetime import date, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import db

PORT = int(os.environ.get("NOOR_PORT", "8800"))
HOST = "127.0.0.1"  # local only, never bind to 0.0.0.0 for this demo
STATIC = Path(__file__).resolve().parent / "static"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
START_RE = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$")

CHANGE_ROLE = "front-desk"
REFUSAL = ("This key has role read-only-connector. Changing bookings needs the front-desk role. "
           "Nothing was changed.")


def booking_row(r) -> dict:
    return {
        "id": r["id"], "date": r["start"][:10], "time": r["start"][11:16], "start": r["start"],
        "duration_min": r["duration_min"], "patient_name": r["patient_name"], "patient_phone": r["phone"],
        "dentist": r["dentist"], "treatment": r["treatment"], "status": r["status"], "note": r["note"],
        "source": r["source"], "updated_at": r["updated_at"],
    }


BOOKING_SQL = """SELECT b.*, p.name AS patient_name, p.phone, d.name AS dentist
                 FROM bookings b JOIN patients p ON p.id=b.patient_id JOIN dentists d ON d.id=b.dentist_id"""


class Handler(BaseHTTPRequestHandler):
    server_version = "noor-booking-app/1.0"

    # ---------- plumbing ----------
    def log_message(self, fmt, *args):  # quieter console, still useful on screen
        sys.stderr.write(f"[noor-booking-app] {self.command} {self.path} -> {args[1] if len(args) > 1 else ''}\n")

    def send_json(self, code: int, body) -> None:
        data = json.dumps(body, indent=2).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def send_html(self, code: int, text: str) -> None:
        data = text.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def read_body(self) -> bytes:
        n = int(self.headers.get("Content-Length") or 0)
        if n > 64_000:
            raise ValueError("body too large")
        return self.rfile.read(n) if n else b""

    def read_json(self) -> dict:
        raw = self.read_body()
        if not raw:
            return {}
        body = json.loads(raw)
        if not isinstance(body, dict):
            raise ValueError("JSON body must be an object")
        return body

    def auth(self):
        """Return the api_keys row for the bearer token, or None (and send 401)."""
        h = self.headers.get("Authorization", "")
        token = h[7:].strip() if h.lower().startswith("bearer ") else ""
        if not token:
            self.send_json(401, {"error": "unauthorized", "message": "Missing Authorization: Bearer <token>."})
            return None
        with db.connect() as conn:
            key = conn.execute("SELECT * FROM api_keys WHERE token_sha256=?", (db.sha256(token),)).fetchone()
        if key is None:
            self.send_json(401, {"error": "unauthorized", "message": "Unknown key."})
            return None
        if key["status"] != "active":
            self.send_json(401, {"error": "unauthorized", "message": f"Key '{key['label']}' was revoked."})
            return None
        return key

    def require_change_role(self, key, action: str, booking_id=None) -> bool:
        if key["role"] != CHANGE_ROLE:  # <-- the role check that box three is about
            with db.connect() as conn:
                conn.execute("INSERT INTO audit_log(at,key_label,role,action,booking_id,detail) VALUES (?,?,?,?,?,?)",
                             (db.now_iso(), key["label"], key["role"], f"REFUSED {action}", booking_id, "role check"))
            self.send_json(403, {"error": "forbidden", "role": key["role"], "message": REFUSAL})
            return False
        return True

    # ---------- GET ----------
    def do_GET(self):  # noqa: N802
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        path = u.path.rstrip("/") or "/"
        try:
            if path == "/health":
                return self.send_json(200, {"ok": True, "app": "noor-booking-app", "data": "synthetic"})
            if path in ("/", "/dashboard"):
                return self.send_html(200, (STATIC / "index.html").read_text(encoding="utf-8"))
            if path == "/site":
                return self.public_site()
            if path == "/site/book":
                return self.public_form()
            key = self.auth()
            if key is None:
                return
            if path == "/whoami":
                return self.send_json(200, {"label": key["label"], "role": key["role"],
                                            "can_change_bookings": key["role"] == CHANGE_ROLE})
            if path == "/dentists":
                return self.send_json(200, {"dentists": db.DENTISTS})
            if path == "/bookings":
                d = q.get("date", date.today().isoformat())
                if not DATE_RE.match(d):
                    return self.send_json(400, {"error": "bad_request", "message": "date must be YYYY-MM-DD"})
                sql, args = BOOKING_SQL + " WHERE substr(b.start,1,10)=?", [d]
                if q.get("status"):
                    sql += " AND b.status=?"
                    args.append(q["status"])
                with db.connect() as conn:
                    rows = [booking_row(r) for r in conn.execute(sql + " ORDER BY b.start, d.name", args)]
                return self.send_json(200, {"date": d, "count": len(rows), "bookings": rows})
            m = re.fullmatch(r"/bookings/(\d+)", path)
            if m:
                with db.connect() as conn:
                    r = conn.execute(BOOKING_SQL + " WHERE b.id=?", (int(m.group(1)),)).fetchone()
                if r is None:
                    return self.send_json(404, {"error": "not_found", "message": "No booking with that id."})
                return self.send_json(200, booking_row(r))
            if path == "/slots":
                d = q.get("date", "")
                dentist = q.get("dentist") or None
                if not DATE_RE.match(d):
                    return self.send_json(400, {"error": "bad_request", "message": "date must be YYYY-MM-DD"})
                if dentist and dentist not in db.DENTISTS:
                    return self.send_json(400, {"error": "bad_request", "message": f"dentist must be one of {db.DENTISTS}"})
                with db.connect() as conn:
                    slots = db.free_slots(conn, d, dentist)
                return self.send_json(200, {"date": d, "dentist": dentist, "count": len(slots), "slots": slots})
            if path == "/keys":
                if not self.require_change_role(key, "list keys"):
                    return
                with db.connect() as conn:
                    rows = [{"label": r["label"], "role": r["role"], "ends_with": r["last4"], "status": r["status"],
                             "created_at": r["created_at"], "revoked_at": r["revoked_at"]}
                            for r in conn.execute("SELECT * FROM api_keys ORDER BY id")]
                return self.send_json(200, {"keys": rows})
            if path == "/audit":
                if not self.require_change_role(key, "read audit"):
                    return
                with db.connect() as conn:
                    rows = [dict(r) for r in conn.execute("SELECT * FROM audit_log ORDER BY id DESC LIMIT 50")]
                return self.send_json(200, {"events": rows})
            return self.send_json(404, {"error": "not_found", "message": "No such endpoint."})
        except Exception as e:  # keep the demo server alive
            return self.send_json(500, {"error": "server_error", "message": str(e)})

    # ---------- POST ----------
    def do_POST(self):  # noqa: N802
        u = urlparse(self.path)
        path = u.path.rstrip("/")
        try:
            if path == "/site/book":
                return self.public_form_submit()
            key = self.auth()
            if key is None:
                return
            m = re.fullmatch(r"/bookings/(\d+)/(cancel|reschedule)", path)
            if m:
                bid, action = int(m.group(1)), m.group(2)
                if not self.require_change_role(key, action, bid):
                    return
                return self.change_booking(key, bid, action)
            if path == "/keys/rotate":
                if not self.require_change_role(key, "rotate key"):
                    return
                return self.rotate_key(key)
            return self.send_json(404, {"error": "not_found", "message": "No such endpoint."})
        except (ValueError, json.JSONDecodeError) as e:
            return self.send_json(400, {"error": "bad_request", "message": str(e)})
        except Exception as e:
            return self.send_json(500, {"error": "server_error", "message": str(e)})

    def change_booking(self, key, bid: int, action: str):
        body = self.read_json()
        with db.connect() as conn:
            r = conn.execute(BOOKING_SQL + " WHERE b.id=?", (bid,)).fetchone()
            if r is None:
                return self.send_json(404, {"error": "not_found", "message": "No booking with that id."})
            if r["status"] in ("cancelled", "completed", "no-show"):
                return self.send_json(409, {"error": "conflict", "message": f"Booking is already {r['status']}."})
            if action == "cancel":
                conn.execute("UPDATE bookings SET status='cancelled', updated_at=? WHERE id=?", (db.now_iso(), bid))
                detail = f"cancelled {r['start']} {r['dentist']}"
            else:
                start = str(body.get("start", ""))
                if not START_RE.match(start):
                    return self.send_json(400, {"error": "bad_request", "message": "start must be 'YYYY-MM-DD HH:MM'"})
                free = {(s["date"] + " " + s["time"]) for s in db.free_slots(conn, start[:10], r["dentist"])}
                if start not in free:
                    return self.send_json(409, {"error": "conflict", "message": f"{start} is not free for {r['dentist']}."})
                conn.execute("UPDATE bookings SET start=?, updated_at=? WHERE id=?", (start, db.now_iso(), bid))
                detail = f"moved {r['start']} -> {start} {r['dentist']}"
            conn.execute("INSERT INTO audit_log(at,key_label,role,action,booking_id,detail) VALUES (?,?,?,?,?,?)",
                         (db.now_iso(), key["label"], key["role"], action, bid, detail))
            r2 = conn.execute(BOOKING_SQL + " WHERE b.id=?", (bid,)).fetchone()
        return self.send_json(200, {"ok": True, "action": action, "booking": booking_row(r2)})

    def rotate_key(self, key):
        label = str(self.read_json().get("label", ""))
        with db.connect() as conn:
            old = conn.execute("SELECT * FROM api_keys WHERE label=? AND status='active'", (label,)).fetchone()
            if old is None:
                return self.send_json(404, {"error": "not_found", "message": "No active key with that label."})
            new_token = "noor_test_" + secrets.token_hex(12)
            ts = db.now_iso()
            conn.execute("UPDATE api_keys SET status='revoked', revoked_at=? WHERE id=?", (ts, old["id"]))
            conn.execute("INSERT INTO api_keys(label,role,token_sha256,last4,status,created_at) VALUES (?,?,?,?,?,?)",
                         (label, old["role"], db.sha256(new_token), new_token[-4:], "active", ts))
            conn.execute("INSERT INTO audit_log(at,key_label,role,action,detail) VALUES (?,?,?,?,?)",
                         (ts, key["label"], key["role"], "rotate key", f"{label}: ...{old['last4']} revoked"))
        return self.send_json(200, {"ok": True, "label": label, "revoked_ends_with": old["last4"],
                                    "new_token_shown_once": new_token})

    # ---------- public fixture website (for Site Watch + the notes-box story) ----------
    def public_site(self):
        with db.connect() as conn:
            planted = conn.execute("SELECT value FROM site_content WHERE key='next_free_slot'").fetchone()
            if planted:
                text = planted["value"]
            else:
                nxt = None
                for off in range(0, 7):
                    s = db.free_slots(conn, db.day(off), "Dr Sana")
                    if s:
                        nxt = s[0]
                        break
                text = (f"{datetime.fromisoformat(nxt['date']).strftime('%a %d %b')} {nxt['time']} with {nxt['dentist']}"
                        if nxt else "none this week")
        page = (STATIC / "site.html").read_text(encoding="utf-8")
        return self.send_html(200, page.replace("{{NEXT_FREE_SLOT}}", html.escape(text)))

    def public_form(self, msg: str = ""):
        page = (STATIC / "book.html").read_text(encoding="utf-8")
        return self.send_html(200, page.replace("{{MESSAGE}}", msg))

    def public_form_submit(self):
        form = {k: v[0] for k, v in parse_qs(self.read_body().decode("utf-8")).items()}
        name = form.get("name", "").strip()[:60] or "Test Patient (web)"
        when = form.get("start", "").strip()
        notes = form.get("notes", "").strip()[:500]
        if not START_RE.match(when):
            return self.public_form("<p class='err'>Pick a time as YYYY-MM-DD HH:MM.</p>")
        with db.connect() as conn:
            free = {(s["date"] + " " + s["time"]) for s in db.free_slots(conn, when[:10], "Dr Sana")}
            if when not in free:
                return self.public_form("<p class='err'>That time is not free with Dr Sana.</p>")
            pid = conn.execute("INSERT INTO patients(name, phone) VALUES (?, '+92 300 0000000')", (name,)).lastrowid
            did = conn.execute("SELECT id FROM dentists WHERE name='Dr Sana'").fetchone()[0]
            bid = conn.execute(
                "INSERT INTO bookings(patient_id,dentist_id,start,duration_min,treatment,status,note,source,updated_at)"
                " VALUES (?,?,?,?,?,?,?,?,?)",
                (pid, did, when, 30, "Check-up", "unconfirmed", notes, "web-form", db.now_iso())).lastrowid
            conn.execute("INSERT INTO audit_log(at,action,booking_id,detail) VALUES (?, 'web booking request', ?, 'public form')",
                         (db.now_iso(), bid))
        return self.public_form(f"<p class='ok'>Request received (booking #{bid}, unconfirmed). The front desk will call you.</p>")


def main():
    if not db.DB_PATH.exists():
        sys.exit("bookings.db not found. Run: python seed.py")
    srv = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"noor-booking-app on http://{HOST}:{PORT}  (FICTIONAL clinic, SYNTHETIC data)  Ctrl+C to stop", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()


if __name__ == "__main__":
    main()
