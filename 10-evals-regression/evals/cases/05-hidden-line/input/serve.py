"""Serve www/ on localhost. /runaway/sufi-threads/catalogue/<n> is endless: every page links to n+1."""
import re, sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

WWW = Path(__file__).resolve().parent / "www"
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8090

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        m = re.match(r"^/runaway/sufi-threads/catalogue/(\d+)$", self.path)
        if not m:
            return super().do_GET()
        n = int(m.group(1))
        body = ("<!doctype html><html><head><meta charset='utf-8'><title>Catalogue page %d</title></head><body>"
                "<h1>Sufi Threads catalogue - page %d</h1><p>Lawn suit price is on the next page.</p>"
                "<p><a href='/runaway/sufi-threads/catalogue/%d'>Next</a></p></body></html>") % (n, n, n + 1)
        data = body.encode()
        self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)
    def log_message(self, *a):
        pass

ThreadingHTTPServer(("127.0.0.1", PORT), partial(Handler, directory=str(WWW))).serve_forever()
