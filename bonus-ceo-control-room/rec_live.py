#!/usr/bin/env python3
"""rec_live.py - record the REAL Monday run with OBS, one clean terminal, real time, unedited.

Why a browser source and not a window capture: OBS window/display capture returns blank frames while the Windows session
is locked (seen during the recording: LogonUI running). An OBS browser source renders off-screen, so it records either way.
Chain: kshell.py (prompt `kiran>`) runs in a real pseudo-terminal (pywinpty/ConPTY) -> websocket -> xterm.js page
(tools/term/term.html) -> OBS browser source 1920x1080 -> NVENC (jim_nvenc, CQP 16) -> mkv -> mp4 (stream copy).
Typing is scripted at human pace; everything after Enter is the real program. Every output chunk is logged with its time
since record start (captures/obs/term-chunks.jsonl), so the take can be checked against the run's own logs.
OBS: own profile + scene collection "BonusCEO"; global.ini backed up and restored byte-for-byte after OBS exits.
Usage: python rec_live.py [monday args...]
"""
import asyncio
import functools
import http.server
import json
import os
import random
import re
import secrets
import shutil
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

from obs_rec import APPD, OBS, OBS_BIN, OUT, PROFILE, COLL, SCENE, write_profile

HERE = Path(__file__).resolve().parent
TERM_DIR = HERE / "tools" / "term"
ANSI = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]|\x1b\][^\x07\x1b]*(\x07|\x1b\\)|\x1b[()][0-9A-B]|\x1b[=>78DMEc]")
SRC = "kiran-term"
FS = 21


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def write_collection_browser(url):
    import uuid
    su, bu = str(uuid.uuid4()), str(uuid.uuid4())
    coll = {"name": COLL, "current_scene": SCENE, "current_program_scene": SCENE, "scene_order": [{"name": SCENE}],
            "current_transition": "Cut", "transition_duration": 0, "transitions": [], "groups": [], "quick_transitions": [],
            "modules": {}, "preview_locked": False, "scaling_enabled": False,
            "sources": [
                {"id": "scene", "versioned_id": "scene", "name": SCENE, "uuid": su, "enabled": True, "mixers": 0, "volume": 1.0,
                 "settings": {"id_counter": 1, "custom_size": False, "items": [
                     {"name": SRC, "source_uuid": bu, "visible": True, "locked": True, "rot": 0.0, "id": 1,
                      "pos": {"x": 0.0, "y": 0.0}, "scale": {"x": 1.0, "y": 1.0}, "align": 5, "bounds_type": 0,
                      "bounds_align": 0, "bounds": {"x": 0.0, "y": 0.0}, "crop_left": 0, "crop_top": 0, "crop_right": 0,
                      "crop_bottom": 0, "scale_filter": "disable", "blend_method": "default", "blend_type": "normal"}]}},
                {"id": "browser_source", "versioned_id": "browser_source", "name": SRC, "uuid": bu, "enabled": True, "mixers": 0,
                 "volume": 1.0, "settings": {"url": url, "width": 1920, "height": 1080, "fps_custom": True, "fps": 30,
                                             "reroute_audio": True, "shutdown": False, "restart_when_active": False, "css": ""}}]}
    (APPD / "basic" / "scenes" / f"{COLL}.json").write_text(json.dumps(coll, indent=1), encoding="utf-8")


class Term:
    def __init__(self):
        self.http_port, self.ws_port = free_port(), free_port()
        self.clients, self.size, self.loop, self.all, self.buf, self.t0 = set(), None, None, [], "", None

    def serve(self):
        import websockets
        h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(TERM_DIR))
        h.log_message = lambda *a: None
        srv = http.server.ThreadingHTTPServer(("127.0.0.1", self.http_port), h)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        self.loop = asyncio.new_event_loop()
        ready = threading.Event()

        async def handler(ws):
            self.clients.add(ws)
            async for m in ws:
                d = json.loads(m)
                if "size" in d:
                    self.size = d["size"]

        async def main():
            async with websockets.serve(handler, "127.0.0.1", self.ws_port, max_size=None):
                ready.set()
                await asyncio.Future()
        threading.Thread(target=lambda: self.loop.run_until_complete(main()), daemon=True).start()
        ready.wait(10)
        self.url = f"http://127.0.0.1:{self.http_port}/term.html?fs={FS}&ws={self.ws_port}&title=kiran"
        return self

    def spawn(self):
        from winpty import PtyProcess
        cols, rows = self.size
        env = {k: v for k, v in os.environ.items() if not (k.startswith("CLAUDECODE") or k.startswith("CLAUDE_CODE_"))}
        env["PYTHONIOENCODING"] = "utf-8"
        self.pty = PtyProcess.spawn([sys.executable, "-X", "utf8", str(HERE / "kshell.py")], cwd=str(HERE), env=env, dimensions=(rows, cols))
        threading.Thread(target=self._reader, daemon=True).start()

    def _send(self, obj):
        msg = json.dumps(obj)
        for c in list(self.clients):
            asyncio.run_coroutine_threadsafe(c.send(msg), self.loop)

    def _reader(self):
        while True:
            try:
                d = self.pty.read(65536)
            except EOFError:
                break
            except Exception:
                time.sleep(0.02)
                continue
            if not d:
                time.sleep(0.01)
                continue
            self.all.append((time.time(), d))
            self.buf += ANSI.sub("", d)
            self._send({"d": d})

    def type(self, text):
        for ch in text:
            self.pty.write(ch)
            time.sleep(random.uniform(0.05, 0.12) * (2.0 if ch == " " and random.random() < 0.2 else 1))
        time.sleep(0.45)
        self.pty.write("\r")

    def wait(self, rx, timeout):
        r, end = re.compile(rx, re.S | re.M), time.time() + timeout
        while time.time() < end:
            m = r.search(self.buf)
            if m:
                return m
            time.sleep(0.1)
        return None


def main():
    args = " ".join(sys.argv[1:])
    OUT.mkdir(parents=True, exist_ok=True)
    term = Term().serve()
    write_profile(1920, 1080)
    write_collection_browser(term.url)
    gbak = OUT / "global.ini.bak"
    shutil.copyfile(APPD / "global.ini", gbak)
    port, pw = 4466, secrets.token_hex(12)
    sect = ("[OBSWebSocket]\nFirstLoad=false\nServerEnabled=true\nServerPort=%d\nAlertsEnabled=false\n"
            "AuthRequired=true\nServerPassword=%s\n\n" % (port, pw))
    txt = gbak.read_text(encoding="utf-8-sig")
    txt = re.sub(r"\[OBSWebSocket\][^\[]*", lambda m: sect, txt) if "[OBSWebSocket]" in txt else txt + "\n" + sect
    (APPD / "global.ini").write_text(txt, encoding="utf-8-sig")
    p = subprocess.Popen([str(OBS_BIN / "obs64.exe"), "--profile", PROFILE, "--collection", COLL, "--scene", SCENE,
                          "--minimize-to-tray", "--multi", "--disable-shutdown-check", "--disable-updater",
                          "--websocket_port", str(port), "--websocket_password", pw], cwd=str(OBS_BIN))
    log = {"canvas": [1920, 1080], "source": "browser_source (xterm.js) fed by a real ConPTY", "args": args}
    t_rec = None
    try:
        o = OBS(port, pw)
        for _ in range(60):
            r = o.req("GetVideoSettings")
            if r["requestStatus"]["result"]:
                break
            time.sleep(0.5)
        log["video"] = r.get("responseData")
        for _ in range(200):
            if term.size:
                break
            time.sleep(0.1)
        if not term.size:
            raise RuntimeError("terminal page never connected (browser source)")
        log["term_size"] = term.size
        term.spawn()
        term.wait(r"kiran", 15)
        time.sleep(1.5)
        import base64
        shot = o.req("GetSourceScreenshot", {"sourceName": SRC, "imageFormat": "png", "imageWidth": 960})
        if shot["requestStatus"]["result"]:
            (OUT / "precheck.png").write_bytes(base64.b64decode(shot["responseData"]["imageData"].split(",", 1)[1]))
        log["start"] = o.req("StartRecord")["requestStatus"]
        t_rec = time.time()
        time.sleep(2.5)
        term.type("python monday.py" + (" " + args if args else ""))
        m = term.wait(r"Done in \d\d:\d\d|PREFLIGHT FAILED", 20 * 60)
        log["end_line"] = m.group(0) if m else None
        time.sleep(5.0)
        rid = re.search(r"digest: runs/(\S+?)/digest\.md", term.buf)
        if rid:
            term.type(f"type runs\\{rid.group(1)}\\digest.md")
            term.wait(r"## |COST", 10)
            time.sleep(12.0)
            log["run"] = rid.group(1)
        else:
            time.sleep(4.0)
        r = o.req("StopRecord")
        log["output"] = (r.get("responseData") or {}).get("outputPath")
        time.sleep(2.0)
    finally:
        subprocess.run(["taskkill", "/PID", str(p.pid)], capture_output=True)
        try:
            p.wait(30)
        except Exception:
            subprocess.run(["taskkill", "/F", "/PID", str(p.pid)], capture_output=True)
            p.wait(10)
        shutil.copyfile(gbak, APPD / "global.ini")
        log["restored_global_ini"] = (APPD / "global.ini").read_bytes() == gbak.read_bytes()
        try:
            term.pty.terminate(force=True)
        except Exception:
            pass
        t0 = t_rec or time.time()
        with (OUT / "term-chunks.jsonl").open("w", encoding="utf-8") as f:
            for t, d in term.all:
                f.write(json.dumps({"t": round(t - t0, 3), "d": d}) + "\n")
        plain = ANSI.sub("", "".join(d for _, d in term.all))
        home = str(Path.home())
        log["privacy_hits"] = [h for h in (home, home.replace("\\", "/"), "@gmail", "sk-ant-oat") if h.lower() in plain.lower()]
        (OUT / "rec_live.log.json").write_text(json.dumps(log, indent=1, default=str), encoding="utf-8")
    src = log.get("output")
    if src and Path(src).exists():
        mp4 = OUT / "control-room.mp4"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-c", "copy", "-movflags", "+faststart", str(mp4)])
        print("RECORDED", mp4, json.dumps({k: log.get(k) for k in ("end_line", "run", "privacy_hits", "restored_global_ini")}))
        return 0
    print("NO RECORDING", json.dumps(log, default=str)[:600])
    return 1


if __name__ == "__main__":
    sys.exit(main())
