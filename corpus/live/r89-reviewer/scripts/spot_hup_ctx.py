#!/usr/bin/env python3
"""Context probe: does SIGHUP still kill `pw-profiler -J -n 0` when the
seat's own null sinks + pw-play followers are cycling (the fixture's g_hup
context) and a co-tenant probe is live?

Everything this script creates is r89r_ctx_<pid>-tagged; unload is verified
against the module's own `sink_name=` argument immediately before the call.

usage: spot_hup_ctx.py [n] [sig_at] [hold_s]
"""
import json
import os
import re
import signal
import subprocess
import sys
import time
import wave
from pathlib import Path

N = int(sys.argv[1]) if len(sys.argv) > 1 else 3
SIG_AT = float(sys.argv[2]) if len(sys.argv) > 2 else 0.8
HOLD = float(sys.argv[3]) if len(sys.argv) > 3 else 4.0
PID = os.getpid()
NS = f"r89r_ctx_ns_{PID}"
NS2 = f"r89r_ctx_ns2_{PID}"
OUT = Path(__file__).resolve().parent.parent / "receipts" / \
    "spot-hup-ctx.json"
TONE = Path(os.environ.get("TMPDIR", "/tmp")) / f"r89r_ctx_{PID}.wav"
MASKS = ("SigBlk", "SigIgn", "SigCgt")
log = {"pid": PID, "ns": NS, "ns2": NS2, "loadavg0": None, "loadavg1": None,
       "modules": {}, "rows": []}


def sh(argv, timeout=15):
    return subprocess.run(argv, capture_output=True, timeout=timeout)


def masks(pid):
    try:
        txt = Path(f"/proc/{pid}/status").read_text()
    except OSError as exc:
        return {"error": str(exc)[:60]}
    out = {"state": None}
    for ln in txt.splitlines():
        for m in MASKS:
            if ln.startswith(m + ":"):
                out[m] = ln.split(":", 1)[1].strip()
        if ln.startswith("State:"):
            out["state"] = ln.split(":", 1)[1].strip()
    return out


def write_tone(path, seconds=30.0, rate=48000):
    import math
    import struct
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        frames = bytearray()
        for i in range(int(seconds * rate)):
            frames += struct.pack("<h", int(12000 * math.sin(
                2 * math.pi * 440 * i / rate)))
        w.writeframes(bytes(frames))


def load_sink(name):
    r = sh(["pactl", "load-module", "module-null-sink",
            f"sink_name={name}",
            f"sink_properties=device.description={name}"])
    idx = (r.stdout.decode().strip() or None)
    return idx, r.returncode


def unload_verified(idx, name):
    if idx is None:
        return None
    lines = sh(["pactl", "list", "modules", "short"]).stdout.decode()
    ok = any(f"{idx}\t" in ln and f"sink_name={name}" in ln
             for ln in lines.splitlines())
    if not ok:
        return {"skipped": "index/name not verified", "idx": idx}
    r = sh(["pactl", "unload-module", str(idx)])
    return {"rc": r.returncode, "verified": True}


def one(i):
    proc = subprocess.Popen(["pw-profiler", "-J", "-n", "0"],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            stdin=subprocess.DEVNULL,
                            start_new_session=True)
    os.set_blocking(proc.stdout.fileno(), False)
    t0 = time.monotonic()
    buf = bytearray()
    fired = False
    rec = {"i": i, "pid": proc.pid}
    while True:
        now = time.monotonic() - t0
        if not fired and now >= SIG_AT:
            rec["masks_before_hup"] = masks(proc.pid)
            rec["alive_at_sig"] = proc.poll() is None
            if rec["alive_at_sig"]:
                try:
                    proc.send_signal(signal.SIGHUP)
                except ProcessLookupError:
                    rec["alive_at_sig"] = False
            fired = True
            time.sleep(0.05)
            rec["masks_after_hup_50ms"] = masks(proc.pid)
        if proc.poll() is not None:
            while True:
                try:
                    chunk = os.read(proc.stdout.fileno(), 65536)
                except (BlockingIOError, OSError):
                    chunk = b""
                if not chunk:
                    break
                buf += chunk
            break
        if now >= HOLD:
            rec["masks_at_bound"] = masks(proc.pid)
            rec["killed_at_bound"] = True
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.wait()
            continue
        try:
            chunk = os.read(proc.stdout.fileno(), 65536)
            if chunk:
                buf += chunk
        except (BlockingIOError, OSError):
            pass
        time.sleep(0.01)
    rec.update({"exit_code": proc.returncode,
                "signal": (signal.Signals(-proc.returncode).name
                           if (proc.returncode or 0) < 0 else None),
                "wall_s": round(time.monotonic() - t0, 3),
                "stdout_bytes": len(buf)})
    return rec


players, idxs = [], []
try:
    write_tone(TONE)
    log["loadavg0"] = Path("/proc/loadavg").read_text().strip()
    for name in (NS, NS2):
        idx, rc = load_sink(name)
        idxs.append((idx, name))
        log["modules"][name] = {"idx": idx, "rc": rc}
    time.sleep(0.6)
    for name in (NS, NS2):
        players.append(subprocess.Popen(
            ["pw-play", "-P", f"node.name=r89r_ctx_pl_{PID}",
             "-P", f"media.role=r89rrole{PID}", "--target", name,
             str(TONE)],
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL, start_new_session=True))
    time.sleep(2.0)
    g = sh(["pw-link", "-l"]).stdout.decode()
    log["linked"] = {name: (name in g) for name in (NS, NS2)}
    log["rows"] = [one(i) for i in range(N)]
finally:
    for p in players:
        try:
            os.killpg(p.pid, signal.SIGTERM)
            p.wait(timeout=3)
        except Exception:
            try:
                os.killpg(p.pid, signal.SIGKILL)
            except Exception:
                pass
    log["unloads"] = {name: unload_verified(idx, name)
                      for idx, name in idxs}
    time.sleep(0.4)
    dump = sh(["pw-dump"], timeout=20).stdout.decode(errors="replace")
    log["residue_nodes"] = sorted(set(re.findall(
        r'"name":\s*"(r89r_ctx[^"]*)"', dump)))
    log["loadavg1"] = Path("/proc/loadavg").read_text().strip()
    try:
        TONE.unlink()
    except OSError:
        pass

log["hup_deaths"] = sum(1 for r in log["rows"] if r["exit_code"] == -1)
log["survived_to_bound"] = sum(1 for r in log["rows"]
                               if r.get("killed_at_bound"))
OUT.write_text(json.dumps(log, indent=2) + "\n")
print(json.dumps({k: v for k, v in log.items() if k != "rows"},
                 indent=2))
for r in log["rows"]:
    print(json.dumps(r, indent=2))
