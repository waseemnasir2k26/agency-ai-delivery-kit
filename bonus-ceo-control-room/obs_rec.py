#!/usr/bin/env python3
"""obs_rec.py - KIT NOTE: shipped only because rec_live.py imports its OBS helpers (profile, websocket client).
Its own main() (window capture of stage.py) is the earlier recorder and needs stage.py, which is not in this pack.

record the stage window with OBS (own profile + scene collection, NVENC, window capture only).

Order: start stage.py first (it writes runs/_stage/ready.json with the window's client size), then:
  python obs_rec.py            -> captures/obs/control-room.mkv + .mp4 (stream copy remux)
What it touches outside this folder, and how it is put back:
  %APPDATA%/obs-studio/basic/profiles/BonusCEO/ and basic/scenes/BonusCEO.json   (new, ours; left in place)
  %APPDATA%/obs-studio/global.ini        backed up before launch, restored byte-for-byte after OBS exits
  obs-websocket: enabled for this launch only ([OBSWebSocket] in global.ini, own port + one-time password), restored after
"""
import json
import os
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path

import websocket  # websocket-client

HERE = Path(__file__).resolve().parent
STAGE = HERE / "runs" / "_stage"
OUT = HERE / "captures" / "obs"
APPD = Path(os.environ["APPDATA"]) / "obs-studio"
OBS_BIN = Path(os.environ.get("OBS_BIN", r"C:\Program Files\obs-studio\bin\64bit"))  # default Windows install folder
PROFILE, COLL, SCENE, SRC = "BonusCEO", "BonusCEO", "Control", "kiran-window"
WS_DIR = APPD / "plugin_config" / "obs-websocket"


def even(n):
    return n - (n % 2)


def write_profile(w, h):
    d = APPD / "basic" / "profiles" / PROFILE
    d.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    rec_path = str(OUT).replace("\\", "\\\\")
    (d / "basic.ini").write_text(f"""[General]
Name={PROFILE}

[Output]
Mode=Advanced
FilenameFormatting=control-room-%CCYY%MM%DD-%hh%mm%ss

[AdvOut]
RecType=Standard
RecFilePath={rec_path}
RecFormat2=mkv
RecEncoder=jim_nvenc
RecTracks=1
RecUseRescale=false
Encoder=jim_nvenc

[Video]
BaseCX={w}
BaseCY={h}
OutputCX={w}
OutputCY={h}
FPSType=0
FPSCommon=30
ScaleType=bicubic
ColorFormat=NV12
ColorSpace=709
ColorRange=Partial

[Audio]
SampleRate=48000
ChannelSetup=Stereo
""", encoding="utf-8-sig")
    (d / "recordEncoder.json").write_text(json.dumps({"rate_control": "CQP", "cqp": 16, "preset2": "p5", "profile": "high", "bf": 2}),
                                          encoding="utf-8")


def write_collection(w, h):
    su, wu = str(uuid.uuid4()), str(uuid.uuid4())
    coll = {"name": COLL, "current_scene": SCENE, "current_program_scene": SCENE, "scene_order": [{"name": SCENE}],
            "current_transition": "Cut", "transition_duration": 0, "transitions": [], "groups": [], "quick_transitions": [],
            "modules": {}, "preview_locked": False, "scaling_enabled": False,
            "sources": [
                {"id": "scene", "versioned_id": "scene", "name": SCENE, "uuid": su, "enabled": True, "mixers": 0, "volume": 1.0,
                 "settings": {"id_counter": 1, "custom_size": False, "items": [
                     {"name": SRC, "source_uuid": wu, "visible": True, "locked": True, "rot": 0.0, "id": 1,
                      "pos": {"x": 0.0, "y": 0.0}, "scale": {"x": 1.0, "y": 1.0}, "align": 5, "bounds_type": 2,
                      "bounds_align": 0, "bounds": {"x": float(w), "y": float(h)}, "crop_left": 0, "crop_top": 0, "crop_right": 0,
                      "crop_bottom": 0, "scale_filter": "disable", "blend_method": "default", "blend_type": "normal"}]}},
                {"id": "window_capture", "versioned_id": "window_capture", "name": SRC, "uuid": wu, "enabled": True, "mixers": 0,
                 "volume": 1.0, "settings": {"window": "kiran:ConsoleWindowClass:conhost.exe", "method": 1, "priority": 0,
                                             "cursor": False, "client_area": True, "compatibility": False}}]}
    d = APPD / "basic" / "scenes"
    (d / f"{COLL}.json").write_text(json.dumps(coll, indent=1), encoding="utf-8")


class OBS:
    def __init__(self, port, password):
        import base64, hashlib
        for _ in range(90):
            try:
                self.ws = websocket.create_connection(f"ws://127.0.0.1:{port}", timeout=2)
                break
            except Exception:
                time.sleep(0.5)
        else:
            raise RuntimeError("obs-websocket did not answer")
        self.ws.settimeout(30)
        hello = json.loads(self.ws.recv())["d"]
        ident = {"rpcVersion": 1, "eventSubscriptions": 0}
        if hello.get("authentication"):
            a = hello["authentication"]
            sec = base64.b64encode(hashlib.sha256((password + a["salt"]).encode()).digest()).decode()
            ident["authentication"] = base64.b64encode(hashlib.sha256((sec + a["challenge"]).encode()).digest()).decode()
        self.ws.send(json.dumps({"op": 1, "d": ident}))
        json.loads(self.ws.recv())                       # Identified
        self.n = 0

    def req(self, t, data=None):
        self.n += 1
        self.ws.send(json.dumps({"op": 6, "d": {"requestType": t, "requestId": str(self.n), "requestData": data or {}}}))
        while True:
            m = json.loads(self.ws.recv())
            if m.get("op") == 7 and m["d"]["requestId"] == str(self.n):
                return m["d"]


def main():
    info = json.loads((STAGE / "ready.json").read_text(encoding="utf-8"))
    w, h = even(info["w"]), even(info["h"])
    write_profile(w, h)
    write_collection(w, h)
    gbak = OUT / "global.ini.bak"
    shutil.copyfile(APPD / "global.ini", gbak)
    import re, secrets
    port, pw = 4466, secrets.token_hex(12)
    g = APPD / "global.ini"   # websocket on for this launch only; file restored after exit
    sect = ("[OBSWebSocket]\nFirstLoad=false\nServerEnabled=true\nServerPort=%d\nAlertsEnabled=false\n"
            "AuthRequired=true\nServerPassword=%s\n\n" % (port, pw))
    txt = gbak.read_text(encoding="utf-8-sig")
    txt = re.sub(r"\[OBSWebSocket\][^\[]*", lambda m: sect, txt) if "[OBSWebSocket]" in txt else txt + "\n" + sect
    g.write_text(txt, encoding="utf-8-sig")
    p = subprocess.Popen([str(OBS_BIN / "obs64.exe"), "--profile", PROFILE, "--collection", COLL, "--scene", SCENE,
                          "--minimize-to-tray", "--multi", "--disable-shutdown-check", "--disable-updater",
                          "--websocket_port", str(port), "--websocket_password", pw], cwd=str(OBS_BIN))
    log = {"canvas": [w, h]}
    try:
        o = OBS(port, pw)
        for _ in range(60):   # OBS answers "not ready" while it is still starting
            r = o.req("GetVideoSettings")
            if r["requestStatus"]["result"]:
                break
            time.sleep(0.5)
        log["video"] = r.get("responseData") or r["requestStatus"]
        log["items"] = o.req("GetSceneItemList", {"sceneName": SCENE}).get("responseData")
        wins = (o.req("GetInputPropertiesListPropertyItems", {"inputName": SRC, "propertyName": "window"}).get("responseData") or {}).get("propertyItems", [])
        log["windows"] = [x.get("itemName") for x in wins]
        pick = [x for x in wins if x.get("itemName", "").startswith("[conhost.exe]: kiran")]
        if not pick:
            raise RuntimeError("stage window 'kiran' not in OBS window list: %s" % log["windows"])
        log["window"] = pick[0]["itemValue"]
        o.req("SetInputSettings", {"inputName": SRC, "inputSettings": {"window": pick[0]["itemValue"], "method": int(os.environ.get("OBS_METHOD", "1")), "priority": 0,
                                                                      "client_area": True, "cursor": False}})
        time.sleep(2.0)
        shot = o.req("GetSourceScreenshot", {"sourceName": SRC, "imageFormat": "png", "imageWidth": 960})
        log["screenshot_ok"] = shot["requestStatus"]["result"]
        if shot["requestStatus"]["result"]:
            import base64
            (OUT / "precheck.png").write_bytes(base64.b64decode(shot["responseData"]["imageData"].split(",", 1)[1]))
        log["start"] = o.req("StartRecord")["requestStatus"]
        t0 = time.time()
        time.sleep(1.5)
        (STAGE / "go").write_text("go", encoding="utf-8")
        while not (STAGE / "done").exists() and time.time() - t0 < 25 * 60:
            time.sleep(0.5)
        time.sleep(1.0)
        r = o.req("StopRecord")
        log["stop"] = r
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
        (OUT / "obs_rec.log.json").write_text(json.dumps(log, indent=1, default=str), encoding="utf-8")
    src = log.get("output")
    if src and Path(src).exists():
        mp4 = OUT / "control-room.mp4"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-c", "copy", "-movflags", "+faststart", str(mp4)])
        print("RECORDED", src, "->", mp4)
    else:
        print("NO RECORDING", json.dumps(log, default=str)[:800])
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
