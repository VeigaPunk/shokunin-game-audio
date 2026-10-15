#!/usr/bin/env python3
"""r80 scout harness — pactl module lattice / dynamic topology lifecycle.

READ-ONLY on corpus/fixtures (never imported). Every artefact lands under
corpus/live/r80-scout/. Own tone, own classifiers, own analysis.
"""
import json
import os
import shutil
import subprocess
import sys
import time
import wave
from array import array

ROOT = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(ROOT, "runs")
TMP = os.path.join(ROOT, "tmp")
os.makedirs(RUNS, exist_ok=True)
os.makedirs(TMP, exist_ok=True)

SEAT = "r80"          # every probe-owned name carries this prefix
TONE = os.path.join(TMP, "r80_tone.wav")
SR = 48000
SECS = 8


def gen_tone(path=TONE, sr=SR, secs=SECS, l=1000.0, r=1500.0, amp=16384):
    """Dual-tone stereo wav: L=l Hz, R=r Hz. Deterministic, seat-owned."""
    if os.path.exists(path) and os.path.getsize(path) > 44:
        return path
    import math
    n = sr * secs
    buf = array("h")
    for i in range(n):
        buf.append(int(amp * math.sin(2 * math.pi * l * i / sr)))
        buf.append(int(amp * math.sin(2 * math.pi * r * i / sr)))
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(buf.tobytes())
    return path


def run(cmd, timeout=20, env=None, stdin=None):
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=timeout, env=env,
                           input=stdin)
        rc, out, err = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        rc, out, err = "TIMEOUT", e.stdout or b"", e.stderr or b""
    dt = time.time() - t0
    return {
        "cmd": cmd,
        "rc": rc,
        "secs": round(dt, 3),
        "stdout": out.decode("utf-8", "replace"),
        "stderr": err.decode("utf-8", "replace"),
    }


# ---------------------------------------------------------------- pactl ---
def pactl(*args, timeout=20):
    return run(["pactl", *args], timeout=timeout)


def load(*args, timeout=20):
    """pactl load-module NAME [ARGS...] -> (index|None, receipt)"""
    r = pactl("load-module", *args, timeout=timeout)
    idx = None
    if r["rc"] == 0:
        try:
            idx = int(r["stdout"].strip().splitlines()[-1].strip())
        except Exception:
            idx = None
    return idx, r


def unload(idx, timeout=20):
    return pactl("unload-module", str(idx), timeout=timeout)


# -------------------------------------------------------------- pw-dump ---
def pw_dump():
    r = run(["pw-dump"], timeout=30)
    try:
        return json.loads(r["stdout"]), r
    except Exception:
        return [], r


def snap():
    """Full graph snapshot, compact."""
    d, r = pw_dump()
    if not d:
        return {"error": "pw-dump failed", "rc": r["rc"], "stderr": r["stderr"][:400]}
    nodes, links, clients, modules, objects = {}, [], {}, {}, {}
    for o in d:
        t = o.get("type")
        p = (o.get("info") or {}).get("props") or {}
        if t == "PipeWire:Interface:Node":
            nodes[o["id"]] = {
                "name": p.get("node.name"),
                "class": p.get("media.class"),
                "client.id": p.get("client.id"),
                "factory": p.get("factory.name"),
                "desc": p.get("node.description"),
                "pulse.module.id": p.get("pulse.module.id"),
                "serial": p.get("object.serial"),
                "state": (o.get("info") or {}).get("state"),
                "n_in": (o.get("info") or {}).get("n-input-ports"),
                "n_out": (o.get("info") or {}).get("n-output-ports"),
                "dont_move": p.get("node.dont-move"),
                "linger": p.get("node.linger"),
                "obj_linger": p.get("object.linger"),
                "virtual": p.get("node.virtual"),
                "autoconnect": p.get("node.autoconnect"),
                "link_group": p.get("node.link-group"),
                "audio.channels": p.get("audio.channels"),
                "audio.position": p.get("audio.position"),
                "node.group": p.get("node.group"),
            }
        elif t == "PipeWire:Interface:Link":
            links.append({"id": o["id"],
                          "out.node": p.get("link.output.node"),
                          "out.port": p.get("link.output.port"),
                          "in.node": p.get("link.input.node"),
                          "in.port": p.get("link.input.port"),
                          "state": (o.get("info") or {}).get("state"),
                          "passive": p.get("link.passive"),
                          "client.id": p.get("client.id")})
        elif t == "PipeWire:Interface:Client":
            clients[o["id"]] = {"name": p.get("application.name") or p.get("client.name"),
                                "pid": p.get("application.process.id")}
        elif t == "PipeWire:Interface:Module":
            modules[o["id"]] = p.get("module.name")
        else:
            objects[o["id"]] = t
    # annotate links with names
    for l in links:
        on = nodes.get(l["out.node"], {}).get("name")
        inn = nodes.get(l["in.node"], {}).get("name")
        l["out"] = f"{on}:{l['out.port']}"
        l["in"] = f"{inn}:{l['in.port']}"
    return {"nodes": nodes, "links": links, "clients": clients,
            "modules": modules, "objects": objects}


def named(s, prefix):
    return {k: v for k, v in s["nodes"].items()
            if (v.get("name") or "").startswith(prefix)}


def links_of(s, node_id):
    return [l for l in s["links"] if l["out.node"] == node_id or l["in.node"] == node_id]


def ports(node_id):
    d, _ = pw_dump()
    for o in d:
        if o.get("id") == node_id and o.get("type") == "PipeWire:Interface:Node":
            return o.get("info", {}).get("ports", [])
    return []


def pactl_sinks():
    r = pactl("list", "short", "sinks")
    out = {}
    for ln in r["stdout"].splitlines():
        f = ln.split("\t")
        if len(f) >= 2:
            out[f[1]] = {"index": f[0], "state": f[-1]}
    return out


def pactl_sources():
    r = pactl("list", "short", "sources")
    out = {}
    for ln in r["stdout"].splitlines():
        f = ln.split("\t")
        if len(f) >= 2:
            out[f[1]] = {"index": f[0], "state": f[-1]}
    return out


# --------------------------------------------------------------- writers ---
class Receipt:
    def __init__(self, name):
        self.name = name
        self.dir = os.path.join(RUNS, name)
        os.makedirs(self.dir, exist_ok=True)
        self.legs = []
        self.notes = []
        self.t0 = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    def leg(self, label, data):
        rec = {"label": label, "at": time.strftime("%H:%M:%S"), **data}
        self.legs.append(rec)
        ld = os.path.join(self.dir, label)
        os.makedirs(ld, exist_ok=True)
        for k, v in data.items():
            if isinstance(v, dict) and "cmd" in v:      # a run() receipt
                with open(os.path.join(ld, f"{k}.cmd"), "w") as f:
                    f.write(" ".join(map(str, v["cmd"])) + f"\nrc={v['rc']}\nsecs={v['secs']}\n")
                with open(os.path.join(ld, f"{k}.stdout"), "w") as f:
                    f.write(v["stdout"])
                with open(os.path.join(ld, f"{k}.stderr"), "w") as f:
                    f.write(v["stderr"])
        self.flush()          # incremental: a killed run still leaves receipts
        return rec

    def flush(self):
        with open(os.path.join(ROOT, f"{self.name}.json"), "w") as f:
            json.dump({"name": self.name, "started": self.t0, "legs": self.legs,
                       "notes": self.notes}, f, indent=1)

    def note(self, s):
        self.notes.append(s)
        print(f"  [{self.name}] {s}", flush=True)

    def close(self):
        with open(os.path.join(ROOT, f"{self.name}.json"), "w") as f:
            json.dump({"name": self.name, "started": self.t0, "legs": self.legs,
                       "notes": self.notes}, f, indent=1)
        with open(os.path.join(self.dir, "SUMMARY.md"), "w") as f:
            f.write(f"# {self.name}\n\n" + "\n".join("- " + n for n in self.notes) + "\n")


# ------------------------------------------------------------- analysis ---
def wav_stats(path):
    try:
        with wave.open(path, "rb") as w:
            n = w.getnframes()
            ch = w.getnchannels()
            sw = w.getsampwidth()
            raw = w.readframes(n)
    except Exception as e:
        return {"error": str(e), "size": os.path.getsize(path) if os.path.exists(path) else None}
    a = array("h")
    a.frombytes(raw[: len(raw) - (len(raw) % 2)])
    peak = max((abs(x) for x in a), default=0)
    return {"size": os.path.getsize(path), "frames": n, "channels": ch,
            "sampwidth": sw, "peak": peak, "rms": (sum(x * x for x in a) / max(1, len(a))) ** 0.5}


def fft_peaks(path, topk=3):
    """Cheap Goertzel-free: report amplitude at the two tone bins + dc."""
    import cmath
    import math
    try:
        with wave.open(path, "rb") as w:
            n = w.getnframes()
            ch = w.getnchannels()
            raw = w.readframes(min(n, SR))
    except Exception:
        return None
    a = array("h")
    a.frombytes(raw[: len(raw) - (len(raw) % 2)])
    left = [a[i] for i in range(0, len(a), ch)]
    right = [a[i + 1] for i in range(0, len(a), ch)] if ch > 1 else left
    def amp(sig, f):
        if not sig:
            return 0.0
        N = len(sig)
        acc = sum(sig[i] * cmath.exp(-2j * math.pi * f * i / SR) for i in range(N))
        return round(2 * abs(acc) / N, 1)
    return {"L@1000": amp(left, 1000), "L@1500": amp(left, 1500),
            "R@1000": amp(right, 1000), "R@1500": amp(right, 1500),
            "n": len(left)}


def client_snapshot():
    """Contention ledger: foreign pactl clients + pw nodes not ours."""
    s = snap()
    if "error" in s:
        return s
    foreign_nodes = {k: v["name"] for k, v in s["nodes"].items()
                     if not (v.get("name") or "").startswith(SEAT)}
    foreign_clients = {k: v for k, v in s["clients"].items()
                       if not (v.get("name") or "").startswith(SEAT)}
    return {"n_nodes": len(s["nodes"]), "n_links": len(s["links"]),
            "foreign_nodes": foreign_nodes, "foreign_clients": foreign_clients,
            "modules": sorted(s["modules"].values())}


if __name__ == "__main__":
    gen_tone()
    print(json.dumps(client_snapshot(), indent=1)[:2000])
