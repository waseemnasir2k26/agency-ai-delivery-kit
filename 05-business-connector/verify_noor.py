"""verify.py for the Noor slot check: plain Python, no model. The agent is the sensor, this file is the judge.
Usage: NOOR_API_TOKEN=<read-only key> python verify_noor.py results/S1   -> prints + writes sw-slot.verify.txt"""
import json, os, re, sys, urllib.request
from datetime import datetime
from pathlib import Path

API = "http://127.0.0.1:8800"


def get(path, auth=True):
    h = {"Authorization": f"Bearer {os.environ['NOOR_API_TOKEN']}"} if auth else {}
    with urllib.request.urlopen(urllib.request.Request(API + path, headers=h), timeout=10) as r:
        return r.read().decode("utf-8")


out = Path(sys.argv[1])
run = json.loads((out / "sw-slot.run.json").read_text(encoding="utf-8"))
page = re.sub(r"<[^>]+>", " ", get("/site", auth=False))
m = re.search(r"Next free slot\s+(\w{3} \d{2} \w{3}) (\d{2}:\d{2}) with ([\w ]+?)\s{2,}", page)
lines = []
if not m:
    lines.append("verify.py: FAIL could not read 'Next free slot' on the page")
else:
    day, hhmm, dentist = m.group(1), m.group(2), m.group(3).strip()
    d = datetime.strptime(f"{day} {datetime.now().year}", "%a %d %b %Y").date().isoformat()
    sl = json.loads(get(f"/slots?date={d}&dentist={urllib.request.quote(dentist)}"))
    free = [s["time"] for s in sl["slots"]]
    ok = hhmm in free
    lines.append(f"page says : Next free slot {day} {hhmm} with {dentist}")
    lines.append(f"system says: {dentist} free on {d}: {', '.join(free) or 'none'}  ({hhmm} {'free' if ok else 'NOT free: already booked'})")
    lines.append(f"verify.py : {'PASS' if ok else 'FAIL'}  (deterministic, no model)")
agent = [f"{x.get('status')}" for x in run["findings"]] or ["no finding"]
lines.append(f"Site Watch (agent) said: {', '.join(agent)}")
(out / "sw-slot.verify.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
