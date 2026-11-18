"""Before/after evidence for "rows changed".

    python snapshot.py dump  <file.json>          write every booking row (canonical, sorted)
    python snapshot.py diff  <before.json> <after.json>   print rows changed + what changed
"""
import json
import sys

import db


def dump(path):
    with db.connect() as conn:
        rows = [dict(r) for r in conn.execute(
            "SELECT id, patient_id, dentist_id, start, status, note FROM bookings ORDER BY id")]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=1)
    print(f"dumped {len(rows)} booking rows -> {path}")


def diff(a, b):
    with open(a, encoding="utf-8") as f:
        before = {r["id"]: r for r in json.load(f)}
    with open(b, encoding="utf-8") as f:
        after = {r["id"]: r for r in json.load(f)}
    changed = []
    for bid in sorted(set(before) | set(after)):
        x, y = before.get(bid), after.get(bid)
        if x != y:
            if x is None:
                changed.append(f"  #{bid}: NEW row {y['start']} status={y['status']}")
            elif y is None:
                changed.append(f"  #{bid}: DELETED")
            else:
                fields = [f"{k}: {x[k]!r} -> {y[k]!r}" for k in x if x[k] != y[k]]
                changed.append(f"  #{bid}: " + "; ".join(fields))
    print(f"rows changed: {len(changed)}")
    print("\n".join(changed))
    return len(changed)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "dump":
        dump(sys.argv[2])
    elif len(sys.argv) == 4 and sys.argv[1] == "diff":
        diff(sys.argv[2], sys.argv[3])
    else:
        sys.exit(__doc__)
