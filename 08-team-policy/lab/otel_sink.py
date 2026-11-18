#!/usr/bin/env python3
"""Tiny local OpenTelemetry log server (OTLP over HTTP/JSON), stdlib only. The 'small log server on my own machine'.
Writes each received log record as one flat JSON line to OTEL_SINK_OUT (default /tmp/otel_events.jsonl).
Run: python3 otel_sink.py   (listens on 127.0.0.1:4318; Claude Code env OTEL_EXPORTER_OTLP_PROTOCOL=http/json)
"""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

OUT = os.environ.get("OTEL_SINK_OUT", "/tmp/otel_events.jsonl")


def val(v):
    for k in ("stringValue", "intValue", "doubleValue", "boolValue"):
        if k in v:
            return v[k]
    return v


def attrs(lst):
    return {a["key"]: val(a.get("value", {})) for a in lst or []}


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_POST(self):
        body = self.rfile.read(int(self.headers.get("content-length", "0") or 0))
        try:
            doc = json.loads(body or b"{}")
        except Exception:
            doc = {}
        if self.path.startswith("/v1/logs"):
            with open(OUT, "a", encoding="utf-8") as fh:
                for rl in doc.get("resourceLogs", []):
                    res = attrs(rl.get("resource", {}).get("attributes"))
                    for sl in rl.get("scopeLogs", []):
                        for rec in sl.get("logRecords", []):
                            a = attrs(rec.get("attributes"))
                            fh.write(json.dumps({"event": val(rec.get("body", {})), "attributes": a,
                                                 "resource": {k: res[k] for k in res if k in ("team.id", "seat", "service.name", "service.version")}}) + "\n")
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", "2")
        self.end_headers()
        self.wfile.write(b"{}")


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 4318), H).serve_forever()
