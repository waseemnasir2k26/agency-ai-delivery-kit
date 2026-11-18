#!/usr/bin/env python3
"""Scripted stand-in for the Anthropic Messages API (FORCED TEST driver, zero model spend).

Claude Code runs for real (permission rules, managed settings, sandbox, hooks, MCP policy).
Only the model is replaced: each main-loop request gets the next tool call from a PLAN file,
so every attack is a deterministic, labelled forced test. Nothing here decides a result:
Claude Code's own tool_result is what policy_test.py reads.

Plan file (JSON): {"steps": [{"name": "Read", "input": {...}}, ...], "final": "text"}
Step index = number of assistant tool_use turns already in the request (stateless).
Env: MOCK_PLAN=/path/plan.json  MOCK_PORT=8787  MOCK_LOG=/path/requests.log
"""
import json
import os
import sys
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(os.environ.get("MOCK_PORT", "8787"))
LOG = os.environ.get("MOCK_LOG", "/tmp/mock_api.log")


def load_plan():
    path = os.environ.get("MOCK_PLAN", "")
    # plan can be swapped per run by rewriting the file the env var points to
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {"steps": [], "final": "no plan"}


def log(obj):
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(obj) + "\n")


def count_tool_turns(messages):
    n = 0
    for m in messages:
        if m.get("role") == "assistant" and isinstance(m.get("content"), list):
            if any(b.get("type") == "tool_use" for b in m["content"]):
                n += 1
    return n


def last_tool_results(messages):
    out = []
    if messages and messages[-1].get("role") == "user" and isinstance(messages[-1].get("content"), list):
        for b in messages[-1]["content"]:
            if b.get("type") == "tool_result":
                c = b.get("content")
                if isinstance(c, list):
                    c = " ".join(x.get("text", "") for x in c if isinstance(x, dict))
                out.append({"is_error": b.get("is_error", False), "content": str(c)[:2000]})
    return out


def sse(handler, event, data):
    handler.wfile.write(f"event: {event}\ndata: {json.dumps(data)}\n\n".encode())


class H(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    def _json(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self._json(200, {"data": [], "has_more": False})

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("content-length", "0")
        self.end_headers()

    def do_POST(self):
        n = int(self.headers.get("content-length", "0") or 0)
        raw = self.rfile.read(n) if n else b"{}"
        try:
            req = json.loads(raw or b"{}")
        except Exception:
            req = {}
        path = self.path.split("?")[0]
        if path.endswith("/count_tokens"):
            return self._json(200, {"input_tokens": 10})
        if not path.endswith("/v1/messages"):
            return self._json(200, {})
        messages = req.get("messages", [])
        has_tools = bool(req.get("tools"))
        plan = load_plan()
        idx = count_tool_turns(messages)
        results = last_tool_results(messages)
        log({"path": path, "tools": has_tools, "idx": idx, "tool_results": results, "model": req.get("model")})
        block = None
        if has_tools and idx < len(plan.get("steps", [])):
            step = plan["steps"][idx]
            block = {"type": "tool_use", "id": "toolu_" + uuid.uuid4().hex[:20], "name": step["name"], "input": step["input"]}
        text = plan.get("final", "done") if has_tools else "ok"
        if not req.get("stream"):
            content = [block] if block else [{"type": "text", "text": text}]
            return self._json(200, {
                "id": "msg_" + uuid.uuid4().hex[:20], "type": "message", "role": "assistant",
                "model": req.get("model", "mock"), "content": content,
                "stop_reason": "tool_use" if block else "end_turn", "stop_sequence": None,
                "usage": {"input_tokens": 1, "output_tokens": 1}})
        self.send_response(200)
        self.send_header("content-type", "text/event-stream")
        self.send_header("cache-control", "no-cache")
        self.send_header("connection", "close")
        self.end_headers()
        mid = "msg_" + uuid.uuid4().hex[:20]
        sse(self, "message_start", {"type": "message_start", "message": {
            "id": mid, "type": "message", "role": "assistant", "model": req.get("model", "mock"),
            "content": [], "stop_reason": None, "stop_sequence": None,
            "usage": {"input_tokens": 1, "output_tokens": 1}}})
        if block:
            start = dict(block, input={})
            sse(self, "content_block_start", {"type": "content_block_start", "index": 0, "content_block": start})
            sse(self, "content_block_delta", {"type": "content_block_delta", "index": 0,
                "delta": {"type": "input_json_delta", "partial_json": json.dumps(block["input"])}})
        else:
            sse(self, "content_block_start", {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}})
            sse(self, "content_block_delta", {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": text}})
        sse(self, "content_block_stop", {"type": "content_block_stop", "index": 0})
        sse(self, "message_delta", {"type": "message_delta", "delta": {
            "stop_reason": "tool_use" if block else "end_turn", "stop_sequence": None}, "usage": {"output_tokens": 1}})
        sse(self, "message_stop", {"type": "message_stop"})
        self.wfile.flush()
        self.close_connection = True


if __name__ == "__main__":
    print(f"mock api on 127.0.0.1:{PORT}", file=sys.stderr)
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
