#!/usr/bin/env python3
"""R79 boundary follow-up — same-sink self-loop gain, and two more spawn-time
self-reference forms (`-P output.<self>`, `-C output.<self>`).

Leg A: `-C ns -i stream.capture.sink=true -P ns` on ONE probe-owned null sink,
fed a 0.25 s burst. A same-sink loop returns the monitor into the same sink,
where it sums with the direct signal -> measure the growth and the control
(kill the loopback -> silence). Probe-owned sinks only; bounded legs.

Writes r79b-selfsink.json next to this file.
"""
import json
import os
import signal
import subprocess
import time
import wave
from pathlib import Path

import numpy as np

SEAT = Path(__file__).resolve().parent
RAW = SEAT / "raw"
PID = os.getpid()
PREFIX = f"r79bs_{PID}"
RATE = 48000
PROCS, SINKS = [], {}


def sh(argv, timeout=20.0):
    p = subprocess.run(argv, capture_output=True, timeout=timeout)
    return {"rc": p.returncode, "out": p.stdout.decode(errors="replace"),
            "err": p.stderr.decode(errors="replace")}


def spawn(argv):
    p = subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                         stderr=subprocess.PIPE, start_new_session=True)
    PROCS.append(p)
    return p


def kill(p, sig=signal.SIGKILL):
    if p is None:
        return
    try:
        os.killpg(os.getpgid(p.pid), sig)
    except ProcessLookupError:
        pass
    try:
        p.wait(timeout=3)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except ProcessLookupError:
            pass
        p.wait(timeout=3)


def make_burst(path, burst_s=0.25, total_s=9.0, amp=1024):
    n = int(RATE * total_s)
    t = np.arange(n) / RATE
    x = (amp * np.sin(2 * np.pi * 1000 * t)).astype("<i2")
    x[t >= burst_s] = 0
    a = np.stack([x, x], 1)
    w = wave.open(str(path), "wb")
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(RATE)
    w.writeframes(a.astype("<i2").tobytes())
    w.close()


def timeline(path, step=0.25):
    w = wave.open(str(path))
    a = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(float)
    a = a.reshape(-1, 2)
    w.close()
    out = []
    for s in np.arange(0, len(a) / RATE - 0.2, step):
        seg = a[int(s * RATE):int((s + 0.15) * RATE)]
        out.append([round(float(s), 2), int(np.abs(seg[:, 0]).max()),
                    int(np.abs(seg[:, 1]).max())])
    return out


def null_sink(name):
    r = sh(["pactl", "load-module", "module-null-sink", f"sink_name={name}"])
    SINKS[name] = int(r["out"].strip()) if r["out"].strip().isdigit() else None


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    out = {"pid": PID, "legs": []}
    burst = f"/tmp/{PREFIX}_burst.wav"
    make_burst(burst)
    ns = f"{PREFIX}_ns"
    ns_b = f"{PREFIX}_ns_b"
    null_sink(ns)
    null_sink(ns_b)
    time.sleep(0.8)
    try:
        # ---- leg A: same sink on both sides, burst + growth + control
        name = f"{PREFIX}_selfsink"
        lb = spawn(["timeout", "-s", "KILL", "25", "pw-loopback", "-n", name,
                    "-C", ns, "-i", "stream.capture.sink=true", "-P", ns])
        time.sleep(1.5)
        tap = spawn(["pw-record", "-P", f"node.name={PREFIX}_tapA",
                     "-P", "stream.capture.sink=true", "--target", ns,
                     "-n", str(RATE * 8), str(RAW / "selfsink_tap.wav")])
        time.sleep(0.7)
        b = spawn(["pw-cat", "-p", "-P", f"node.name={PREFIX}_burst",
                   "--target", ns, burst])
        time.sleep(3.5)
        # control: kill the loopback -> the loop must stop
        kill(lb)
        time.sleep(1.2)
        try:
            tap.wait(timeout=10)
        except subprocess.TimeoutExpired:
            kill(tap)
        b.wait(timeout=5)
        leg = {"leg": "A-same-sink-both-sides", "name": name,
               "burst_amp": 1024, "burst_s": 0.25}
        leg["links_pre"] = sh(["pw-link", "-l"])["out"]
        leg["tap_rc"] = tap.returncode
        leg["timeline"] = timeline(str(RAW / "selfsink_tap.wav"))
        peaks = [row[2] for row in leg["timeline"]]
        leg["peak_max"] = max(peaks) if peaks else 0
        leg["peak_series_ch1"] = peaks
        leg["grew"] = bool(peaks and max(peaks) > 4 * 1024)
        out["legs"].append(leg)

        # ---- leg A2: same sink, CONTINUOUS stereo tone, growth + stop-the-source
        name = f"{PREFIX}_selfsink_cont"
        lb = spawn(["timeout", "-s", "KILL", "25", "pw-loopback", "-n", name,
                    "-C", ns, "-i", "stream.capture.sink=true", "-P", ns])
        time.sleep(1.5)
        tap = spawn(["pw-record", "-P", f"node.name={PREFIX}_tapA2",
                     "-P", "stream.capture.sink=true", "--target", ns,
                     "-n", str(RATE * 8), str(RAW / "selfsink_cont_tap.wav")])
        tone = spawn(["pw-cat", "-p", "-P", f"node.name={PREFIX}_toneA2",
                      "--target", ns, "/tmp/r79bchk10_tone_a.wav"]) if False else None
        # stereo two-tone (L 1k, R 1.5k) from the harness scratch
        two = SEAT / "scratch" / f"tone_{PID}.wav"
        if not two.exists():
            n2 = int(RATE * 20)
            t2 = np.arange(n2) / RATE
            L = (8192 * np.sin(2 * np.pi * 1000 * t2)).astype("<i2")
            R = (8192 * np.sin(2 * np.pi * 1500 * t2)).astype("<i2")
            w = wave.open(str(two), "wb")
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(RATE)
            w.writeframes(np.stack([L, R], 1).astype("<i2").tobytes())
            w.close()
        tone = spawn(["pw-cat", "-p", "-P", f"node.name={PREFIX}_toneA2",
                      "--target", ns, str(two)])
        time.sleep(3.0)
        kill(tone)                      # stop the source: does it decay or persist?
        time.sleep(2.5)
        kill(lb)                        # control: kill the loop
        time.sleep(1.0)
        try:
            tap.wait(timeout=10)
        except subprocess.TimeoutExpired:
            kill(tap)
        leg = {"leg": "A2-same-sink-continuous", "name": name,
               "source_stopped_at_s": 3.0, "loop_killed_at_s": 5.5}
        leg["tap_rc"] = tap.returncode
        leg["timeline"] = timeline(str(RAW / "selfsink_cont_tap.wav"))
        leg["peak_max_ch1"] = max((r[2] for r in leg["timeline"]), default=0)
        leg["peak_max_ch0"] = max((r[1] for r in leg["timeline"]), default=0)
        out["legs"].append(leg)

        # ---- leg B: playback target = own output node (no tone)
        name = f"{PREFIX}_b"
        lb = spawn(["timeout", "-s", "KILL", "12", "pw-loopback", "-n", name,
                    "-C", ns, "-i", "stream.capture.sink=true",
                    "-P", f"output.{name}"])
        time.sleep(2.0)
        g = json.loads(sh(["pw-dump"])["out"])
        byid, ports = {}, {}
        for o in g:
            if o.get("type", "").endswith("Node"):
                p = (o.get("info") or {}).get("props") or {}
                byid[o["id"]] = p.get("node.name")
            if o.get("type", "").endswith("Port"):
                p = (o.get("info") or {}).get("props") or {}
                ports[o["id"]] = p.get("port.name")
        links = []
        for o in g:
            if o.get("type", "").endswith("Link"):
                i = o.get("info") or {}
                on, inn = byid.get(i.get("output-node-id")), byid.get(i.get("input-node-id"))
                if PREFIX in str(on) or PREFIX in str(inn):
                    links.append(f"{on}:{ports.get(i.get('output-port-id'))} -> "
                                 f"{inn}:{ports.get(i.get('input-port-id'))}")
        out["legs"].append({"leg": "B-playback-own-output", "name": name,
                            "links": sorted(links)})
        kill(lb)

        # ---- leg C: capture target = own output node (no prop, no tone)
        name = f"{PREFIX}_c"
        lb = spawn(["timeout", "-s", "KILL", "12", "pw-loopback", "-n", name,
                    "-C", f"output.{name}", "-P", ns_b])
        time.sleep(2.0)
        g = json.loads(sh(["pw-dump"])["out"])
        byid, ports = {}, {}
        for o in g:
            if o.get("type", "").endswith("Node"):
                p = (o.get("info") or {}).get("props") or {}
                byid[o["id"]] = p.get("node.name")
            if o.get("type", "").endswith("Port"):
                p = (o.get("info") or {}).get("props") or {}
                ports[o["id"]] = p.get("port.name")
        links = []
        states = {}
        for o in g:
            if o.get("type", "").endswith("Node"):
                p = (o.get("info") or {}).get("props") or {}
                if p.get("node.name", "").startswith(("input.", "output.")) and name in p.get("node.name", ""):
                    states[p["node.name"]] = (o.get("info") or {}).get("state")
            if o.get("type", "").endswith("Link"):
                i = o.get("info") or {}
                on, inn = byid.get(i.get("output-node-id")), byid.get(i.get("input-node-id"))
                if PREFIX in str(on) or PREFIX in str(inn):
                    links.append(f"{on}:{ports.get(i.get('output-port-id'))} -> "
                                 f"{inn}:{ports.get(i.get('input-port-id'))}")
        out["legs"].append({"leg": "C-capture-own-output", "name": name,
                            "links": sorted(links), "node_states": states})
        kill(lb)
    finally:
        for p in PROCS:
            if p.poll() is None:
                kill(p)
        for n, mid in SINKS.items():
            if mid:
                sh(["pactl", "unload-module", str(mid)])
    (SEAT / "r79b-selfsink.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({"written": str(SEAT / 'r79b-selfsink.json'),
                      "peak_max": out["legs"][0]["peak_max"],
                      "grew": out["legs"][0]["grew"],
                      "series": out["legs"][0]["peak_series_ch1"][:24]}, indent=1))


if __name__ == "__main__":
    main()
