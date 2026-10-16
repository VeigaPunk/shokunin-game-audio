#!/usr/bin/env python3
"""r87 reviewer — S1b/S2b fixups: serial leg (regex fixed) and the
live-DSP tap (capture-side `stream.capture.sink=true`, per r78's law).
Own `r87r_*` namespace; own modules unloaded name-verified.
"""
import json
import math
import os
import re
import signal
import struct
import subprocess
import time
import wave
from pathlib import Path

PID = os.getpid()
PFX = f"r87r_{PID}"
NS = f"r87r_ns_{PID}"
TAP = f"r87r_tap_{PID}"
TMP = Path(os.environ.get("TMPDIR", "/tmp")) / f"r87r-fix-{PID}"
TMP.mkdir(parents=True, exist_ok=True)
OUT = Path(__file__).resolve().parent / "fixups.json"


def run(argv, timeout=15.0, stdin_data=None):
    try:
        p = subprocess.run(argv, capture_output=True, timeout=timeout,
                           input=stdin_data)
        return {"rc": p.returncode,
                "stdout": p.stdout.decode(errors="replace")[:900],
                "stderr": p.stderr.decode(errors="replace")[:400]}
    except subprocess.TimeoutExpired:
        return {"rc": None, "timeout": True, "stdout": "", "stderr": ""}


def spawn(argv):
    return subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            stdin=subprocess.DEVNULL,
                            start_new_session=True)


def kill(proc):
    if proc is None:
        return
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        proc.wait(timeout=4)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        proc.wait(timeout=3)


def graph():
    p = subprocess.run(["pw-dump"], capture_output=True, timeout=25)
    objs = json.loads(p.stdout.decode())
    nodes, ports, links = {}, {}, []
    for o in objs:
        t, info = o.get("type"), o.get("info") or {}
        props = info.get("props") or {}
        if t == "PipeWire:Interface:Node":
            nodes[o["id"]] = {"name": props.get("node.name"),
                              "class": props.get("media.class")}
        elif t == "PipeWire:Interface:Port":
            ports[o["id"]] = {"node": info.get("node-id"),
                              "name": props.get("port.name")}
        elif t == "PipeWire:Interface:Link":
            links.append({"out_node": info.get("output-node-id"),
                          "in_node": info.get("input-node-id")})
    return nodes, ports, links


def consumers(nodes, links, name):
    return sorted({(nodes.get(l["in_node"]) or {}).get("name")
                   for l in links
                   if (nodes.get(l["out_node"]) or {}).get("name") == name})


def write_tone(path, seconds=14.0, amp=12000, rate=48000):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(rate)
        frames = bytearray()
        for i in range(int(seconds * rate)):
            v = int(amp * math.sin(2 * math.pi * 1000.0 * i / rate))
            frames += struct.pack("<hh", v, v)
        w.writeframes(bytes(frames))


def rms_series(path, win=0.1):
    import numpy as np
    with wave.open(str(path), "rb") as w:
        rate, ch = w.getframerate(), w.getnchannels()
        data = w.readframes(w.getnframes())
    a = np.frombuffer(data, dtype="<i2").astype("float64")
    if not len(a):
        return []
    a = a.reshape(-1, ch).mean(axis=1)
    step = int(rate * win)
    return [(i / rate, float(np.sqrt((a[i:i + step] ** 2).mean())))
            for i in range(0, len(a) - step, step)]


def med(series, lo, hi):
    v = sorted(x for t, x in series if lo <= t <= hi)
    return v[len(v) // 2] if v else None


def main():
    out = {}
    tone = TMP / "tone.wav"
    write_tone(tone)
    m = run(["pactl", "load-module", "module-null-sink",
             f"sink_name={NS}"])
    idx = int(m["stdout"].strip()) if m["rc"] == 0 else None
    time.sleep(0.6)
    try:
        nodes, ports, links = graph()
        nid = next((i for i, n in nodes.items() if n["name"] == NS), None)
        info = run(["pw-cli", "info", str(nid)])
        ser = re.search(r'object\.serial = "?(\d+)', info["stdout"])
        serial = ser.group(1) if ser else None
        # ---- serial leg (--target <object.serial>) ----
        leg = f"{PFX}_serial"
        p = spawn(["pw-play", "-P", f"node.name={leg}", "--target",
                   serial or "0", str(tone)])
        time.sleep(1.4)
        n2, p2, l2 = graph()
        cons_serial = consumers(n2, l2, leg)
        kill(p)
        # ---- live DSP with a correct capture-side tap ----
        tapfile = TMP / "tap.wav"
        tap = spawn(["pw-record", "-P", f"node.name={TAP}",
                     "-P", "stream.capture.sink=true",
                     "--target", NS, str(tapfile)])
        time.sleep(1.0)
        n2, p2, l2 = graph()
        tap_edges = [{"in": (n2.get(l["in_node"]) or {}).get("name")}
                     for l in l2
                     if (n2.get(l["out_node"]) or {}).get("name") == TAP]
        player = spawn(["pw-play", "-P", f"node.name={PFX}_dsp",
                        "--target", NS, str(tone)])
        time.sleep(1.6)
        n3, _, _ = graph()
        dsp = next((i for i, n in n3.items()
                    if n["name"] == f"{PFX}_dsp"), None)
        w = run(["pw-cli", "set-param", str(dsp), "Props",
                 "{ volume: 0.25 }"])
        t_write = time.monotonic()
        time.sleep(1.4)
        kill(player)
        time.sleep(0.2)
        kill(tap)
        series = rms_series(tapfile)
        solo = med(series, 0.4, 1.3)
        v25 = med(series, 0.0, 0.0)
        # windows are relative to the tap start: the write happened at
        # t_write; recompute against the tap's own clock
        out["S2b"] = {"tap_edges": tap_edges, "write_rc": w["rc"],
                      "series_len": len(series),
                      "solo_rms": solo,
                      "max_rms": max((x for _, x in series), default=None),
                      "min_after_write_rms": min(
                          (x for t, x in series
                           if t >= series[-1][0] - 1.2), default=None),
                      "tail": [round(x, 1) for _, x in series[-14:]],
                      "head": [round(x, 1) for _, x in series[:14]]}
        out["S1b"] = {"ns": NS, "ns_id": nid, "ns_serial": serial,
                      "serial_leg_consumers": cons_serial,
                      "verdict": {"serial_resolves":
                                  cons_serial == [NS]}}
    finally:
        n4, _, _ = graph()
        resid = [i for i, n in n4.items()
                 if n["name"] and PFX in n["name"]]
        out["_residual"] = [{"id": i, **run(["pw-cli", "destroy", str(i)])}
                            for i in resid]
        short = run(["pactl", "list", "modules", "short"])
        ver = None
        for ln in short["stdout"].splitlines():
            parts = ln.split("\t")
            if len(parts) >= 3 and parts[0].strip() == str(idx) and \
                    f"sink_name={NS}" in parts[2]:
                ver = {"verified_index": idx,
                       "unload": run(["pactl", "unload-module",
                                      str(idx)])}
        out["_unload"] = ver
        time.sleep(0.4)
        sinks = run(["pactl", "list", "sinks", "short"])["stdout"]
        n5, _, _ = graph()
        out["_residue"] = {"sinks": [ln for ln in sinks.splitlines()
                                     if PFX in ln],
                           "nodes": [n["name"] for n in n5.values()
                                     if n["name"] and PFX in n["name"]]}
        OUT.write_text(json.dumps(out, indent=1) + "\n")
        print(json.dumps(out, indent=1))
        print("receipt:", OUT)


if __name__ == "__main__":
    main()
