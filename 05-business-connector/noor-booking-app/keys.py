"""Key admin from the terminal (same effect as the dashboard Keys tab).

    python keys.py list
    python keys.py rotate read-only-connector    revoke the active key, print a NEW token once
"""
import secrets
import sys

import db

if len(sys.argv) >= 2 and sys.argv[1] == "list":
    with db.connect() as conn:
        for r in conn.execute("SELECT label, role, last4, status, created_at, revoked_at FROM api_keys ORDER BY id"):
            print(f"{r['label']:22} {r['role']:20} ...{r['last4']}  {r['status']:8} {r['created_at']} {r['revoked_at'] or ''}")
elif len(sys.argv) == 3 and sys.argv[1] == "rotate":
    label = sys.argv[2]
    with db.connect() as conn:
        old = conn.execute("SELECT * FROM api_keys WHERE label=? AND status='active'", (label,)).fetchone()
        if not old:
            sys.exit("no active key with that label")
        tok, ts = "noor_test_" + secrets.token_hex(12), db.now_iso()
        conn.execute("UPDATE api_keys SET status='revoked', revoked_at=? WHERE id=?", (ts, old["id"]))
        conn.execute("INSERT INTO api_keys(label,role,token_sha256,last4,status,created_at) VALUES (?,?,?,?,?,?)",
                     (label, old["role"], db.sha256(tok), tok[-4:], "active", ts))
    print(f"revoked ...{old['last4']}; new {label} token (shown once, put it in the machine's NOOR_API_TOKEN): {tok}")
else:
    sys.exit(__doc__)
