"""CONTROLLED TEST for the Site Watch beat: make the public /site page advertise a slot that is already TAKEN.

    python plant_stale_slot.py          plant (tomorrow 10:00 with Dr Sana, which the fixture has booked)
    python plant_stale_slot.py --clear  page goes back to the live value from the booking system
"""
import sys
from datetime import datetime

import db

with db.connect() as conn:
    if "--clear" in sys.argv:
        conn.execute("DELETE FROM site_content WHERE key='next_free_slot'")
        print("cleared: /site shows the live next free slot again")
    else:
        d = db.day(1)
        text = f"{datetime.fromisoformat(d).strftime('%a %d %b')} 10:00 with Dr Sana"
        conn.execute("INSERT OR REPLACE INTO site_content(key, value) VALUES ('next_free_slot', ?)", (text,))
        taken = conn.execute("""SELECT b.id FROM bookings b JOIN dentists x ON x.id=b.dentist_id
                                WHERE b.start=? AND x.name='Dr Sana' AND b.status!='cancelled'""",
                             (d + " 10:00",)).fetchone()
        print(f"PLANTED stale slot on /site: '{text}' (booking system: taken by booking {taken[0] if taken else '?'})")
