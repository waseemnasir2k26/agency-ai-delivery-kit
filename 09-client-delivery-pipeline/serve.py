"""Preview server for the Episode 9 job: serves dist/ on localhost (private, this machine only).
POST /enquiry = the fitting form's target in this build: appends the enquiry to runs/enquiries.jsonl (TEST)."""
import json, sys, time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

HERE = Path(__file__).resolve().parent
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8099


class Handler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path.split("?")[0] != "/enquiry":
            self.send_error(404); return
        body = self.rfile.read(int(self.headers.get("Content-Length") or 0)).decode("utf-8", "replace")
        rec = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "fields": {k: v[0] for k, v in parse_qs(body).items()}}
        (HERE / "runs").mkdir(exist_ok=True)
        with (HERE / "runs" / "enquiries.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
        out = b"<!doctype html><p>Thank you. Your fitting enquiry was received (TEST ENQUIRY).</p>"
        self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(out))); self.end_headers(); self.wfile.write(out)

    def log_message(self, *a):
        pass


ThreadingHTTPServer(("127.0.0.1", PORT), partial(Handler, directory=str(HERE / "dist"))).serve_forever()
