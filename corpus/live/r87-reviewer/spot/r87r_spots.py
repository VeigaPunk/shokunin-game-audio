#!/usr/bin/env python3
"""r87 reviewer — independent spots in the reviewer's own namespace.

Own code, own `r87r_*` objects; the fixture is never imported. Each spot
re-derives one encoded law from scratch:
  S1 routing precedence (flag vs node.target, garbage no-fallthrough,
     prop > flag, serial resolves / object.id never)
  S2 Props live-DSP exact ratio + spawn --volume 1.5 unclamped
  S3 `-s` sysex past-EOF survival (the labrat's UNTESTED half)
  S4 cold-registry artifact (piped pw-cli, t=0)
  S5 remote/RAOP surface census
  S6 create-node session-bound vs object.linger
Cleanup: own modules unloaded name-verified, own pids only, no
set-default-*, no foreign object touched.
"""
import json
import math
import os
import re
import shutil
import signal
import struct
import subprocess
import sys
import time
import wave
from pathlib import Path

PID = os.getpid()
PFX = f"r87r_{PID}"
NS = f"r87r_ns_{PID}"
NS2 = f"r87r_ns2_{PID}"
TAP = f"r87r_tap_{PID}"
BOGUS = "r87r_no_such_target"
DEAD = "99999999"
OUT = Path(__file__).resolve().parent / "spots.json"
TMP = Path(os.environ.get("TMPDIR", "/tmp")) / f"r87r-{PID}"
TMP.mkdir(parents=True, exist_ok=True)


def run(argv, timeout=12.0, env=None, stdin_data=None):
    try:
        p = subprocess.run(argv, capture_output=True, timeout=timeout,
                           env=env, input=stdin_data)
        return {"argv": " ".join(map(str, argv)), "rc": p.returncode,
                "stdout": p.stdout.decode(errors="replace")[:800],
                "stderr": p.stderr.decode(errors="replace")[:800]}
    except subprocess.TimeoutExpired:
        return {"argv": " ".join(map(str, argv)), "rc": None,
                "timeout": True, "stdout": "", "stderr": ""}


def spawn(argv, env=None):
    return subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            stdin=subprocess.DEVNULL, env=env,
                            start_new_session=True)


def kill(proc, sig=signal.SIGTERM):
    if proc is None:
        return
    try:
        os.killpg(proc.pid, sig)
    except (ProcessLookupError, PermissionError):
        pass
    try:
        proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            pass


def graph():
    p = subprocess.run(["pw-dump"], capture_output=True, timeout=25)
    objs = json.loads(p.stdout.decode())
    nodes, ports, links = {}, {}, []
    for o in objs:
        t = o.get("type")
        info = o.get("info") or {}
        if t == "PipeWire:Interface:Node":
            nodes[o["id"]] = {"id": o["id"],
                              "name": (info.get("props") or {}).get(
                                  "node.name"),
                              "class": (info.get("props") or {}).get(
                                  "media.class"),
                              "state": info.get("state")}
        elif t == "PipeWire:Interface:Port":
            ports[o["id"]] = {"node": info.get("node-id"),
                              "name": (info.get("props") or {}).get(
                                  "port.name"),
                              "dir": info.get("direction")}
        elif t == "PipeWire:Interface:Link":
            links.append({"out_node": info.get("output-node-id"),
                          "in_node": info.get("input-node-id"),
                          "out_port": info.get("output-port-id"),
                          "in_port": info.get("input-port-id"),
                          "state": info.get("state")})
    return nodes, ports, links


def edges_out(nodes, ports, links, node_name):
    out = []
    for l in links:
        on = nodes.get(l["out_node"]) or {}
        inn = nodes.get(l["in_node"]) or {}
        if on.get("name") == node_name:
            out.append({"in_node": inn.get("name"),
                        "in_port_name": (ports.get(l["in_port"]) or {}
                                         ).get("name")})
    return out


def load_ns(name):
    m = run(["pactl", "load-module", "module-null-sink",
             f"sink_name={name}", "sink_properties=device.description="
             f"{name}"], 15.0)
    idx = None
    if m["rc"] == 0 and m["stdout"].strip().isdigit():
        idx = int(m["stdout"].strip())
    return {"module_id": idx, "load": m}


def unload_verified(name, idx):
    """Re-read the module table; fire only the index whose arg carries
    our own sink_name=."""
    short = run(["pactl", "list", "modules", "short"], 15.0)
    for ln in short["stdout"].splitlines():
        parts = ln.split("\t")
        if len(parts) >= 3 and parts[0].strip() == str(idx) and \
                f"sink_name={name}" in parts[2]:
            return {"verified_index": idx, "unload": run(
                ["pactl", "unload-module", str(idx)], 15.0)}
    return {"verified_index": None, "unload": None,
            "reason": "own sink_name= line not found at captured index"}


def write_tone(path, seconds=16.0, amp=12000, rate=48000):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(rate)
        frames = bytearray()
        n = int(seconds * rate)
        for i in range(n):
            v = int(amp * math.sin(2 * math.pi * 1000.0 * i / rate))
            frames += struct.pack("<hh", v, v)
        w.writeframes(bytes(frames))
    return path


def rms_windows(path, win=0.1):
    with wave.open(str(path), "rb") as w:
        rate = w.getframerate()
        ch = w.getnchannels()
        data = w.readframes(w.getnframes())
    import numpy as np
    a = np.frombuffer(data, dtype="<i2").astype("float64")
    a = a.reshape(-1, ch).mean(axis=1)
    step = int(rate * win)
    out = []
    for i in range(0, len(a) - step, step):
        seg = a[i:i + step]
        out.append((i / rate, float(np.sqrt((seg ** 2).mean()))))
    return out


def med(series, lo, hi):
    vals = [v for t, v in series if lo <= t <= hi]
    if not vals:
        return None
    vals.sort()
    return vals[len(vals) // 2]


def smf(path, seconds=4.0):
    """480 tpq, 120 bpm — the same shape as the r87 fixture."""
    def vlq(n):
        b = [n & 0x7f]
        n >>= 7
        while n:
            b.append((n & 0x7f) | 0x80)
            n >>= 7
        return bytes(reversed(b))
    trk = b""
    trk += vlq(0) + b"\xff\x51\x03" + struct.pack(">I", 500000)[1:]
    trk += vlq(0) + bytes([0x90, 60, 96])
    trk += vlq(1920) + bytes([0x80, 60, 0])
    trk += vlq(960) + bytes([0x90, 64, 96])
    trk += vlq(960) + bytes([0x80, 64, 0])
    trk += vlq(0) + b"\xff\x2f\x00"
    Path(path).write_bytes(b"MThd" + struct.pack(">IHHH", 6, 0, 1, 480)
                           + b"MTrk" + struct.pack(">I", len(trk)) + trk)
    return path


def main():
    spots = {}
    tone = write_tone(TMP / "tone.wav")
    smf(TMP / "r87r.mid")
    loads = {}
    try:
        # ---------------- S1 routing precedence ----------------
        for nm in (NS, NS2):
            loads[nm] = load_ns(nm)
        time.sleep(0.6)
        nodes, ports, links = graph()
        ns_id = next((n["id"] for n in nodes.values()
                      if n["name"] == NS), None)
        ns_serial = None
        if ns_id:
            p = subprocess.run(["pw-cli", "info", str(ns_id)],
                               capture_output=True, timeout=15)
            m = re.search(r"object.serial = (\d+)",
                          p.stdout.decode(errors="replace"))
            ns_serial = m.group(1) if m else None
        legs = {}

        def watch(name, tail):
            tag = f"{PFX}_{name}"
            proc = spawn(["pw-play", "-P", f"node.name={tag}", *tail,
                          str(tone)])
            time.sleep(1.3)
            nodes2, ports2, links2 = graph()
            cons = sorted({e["in_node"] for e in
                           edges_out(nodes2, ports2, links2, tag)})
            kill(proc)
            legs[name] = {"argv": " ".join(map(str, tail)),
                          "consumers": cons}

        watch("own", ["--target", NS])
        watch("nt_vs_flag", ["-P", f"node.target={NS2}",
                             "--target", NS])
        watch("nt_rev", ["-P", f"node.target={NS}", "--target", NS2])
        watch("nt_garbage", ["-P", f"node.target={NS2}",
                             "--target", BOGUS])
        watch("pb1", ["--target", NS, "-P", f"target.object={BOGUS}"])
        watch("pb2", ["--target", BOGUS, "-P", f"target.object={NS}"])
        watch("serial", ["--target", ns_serial] if ns_serial else
              ["--target", "0"])
        watch("objid", ["--target", str(ns_id)] if ns_id else
              ["--target", "0"])
        spots["S1_routing"] = {"ns": NS, "ns2": NS2, "ns_id": ns_id,
                               "ns_serial": ns_serial, "legs": legs,
                               "verdict": {
                                   "flag_beats_node_target":
                                       legs["nt_vs_flag"]["consumers"] == [NS]
                                       and legs["nt_rev"]["consumers"] == [NS2],
                                   "garbage_flag_no_fallthrough":
                                       legs["nt_garbage"]["consumers"] != [NS2],
                                   "prop_beats_flag":
                                       legs["pb1"]["consumers"] != [NS]
                                       and legs["pb2"]["consumers"] == [NS],
                                   "serial_resolves": ns_serial is not None
                                   and legs["serial"]["consumers"] == [NS],
                                   "objid_never": ns_id is not None
                                   and legs["objid"]["consumers"] != [NS]}}
        # ---------------- S2 live DSP + spawn volume ----------------
        tapfile = TMP / "tap.wav"
        tap = subprocess.Popen(
            ["pw-record", "-P", f"node.name={TAP}", "--target", NS,
             str(tapfile)], stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL,
            start_new_session=True)
        time.sleep(1.2)
        player = spawn(["pw-play", "-P", f"node.name={PFX}_dsp",
                        "--target", NS, str(tone)])
        time.sleep(1.4)
        nodes2, ports2, links2 = graph()
        dsp_id = next((n["id"] for n in nodes2.values()
                       if n["name"] == f"{PFX}_dsp"), None)
        t0 = time.monotonic()
        w = run(["pw-cli", "set-param", str(dsp_id), "Props",
                 "{ volume: 0.25 }"], 12.0)
        time.sleep(1.2)
        kill(player)
        kill(tap)
        series = rms_windows(tapfile)
        solo = med(series, 0.4, 1.2)
        v25 = med(series, t0 + 0.4, t0 + 1.0)
        # spawn-time --volume 1.5 through the same sink, fresh tap
        tapfile2 = TMP / "tap2.wav"
        tap2 = subprocess.Popen(
            ["pw-record", "-P", f"node.name={TAP}2", "--target", NS,
             str(tapfile2)], stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL,
            start_new_session=True)
        time.sleep(1.0)
        t1 = time.monotonic()
        vp = spawn(["pw-play", "-P", f"node.name={PFX}_v150",
                    "--volume", "1.5", "--target", NS, str(tone)])
        time.sleep(2.0)
        kill(vp)
        kill(tap2)
        s2 = rms_windows(tapfile2)
        v150 = med(s2, t1 + 0.6, t1 + 1.6)
        spots["S2_live_dsp"] = {
            "dsp_node": dsp_id, "write_rc": w["rc"],
            "solo_rms": solo, "vol25_rms": v25,
            "vol25_ratio": (round(v25 / solo, 4)
                            if (v25 and solo) else None),
            "v150_rms": v150, "solo2_rms": med(s2, 0.2, 0.8),
            "verdict": {
                "props_live_ratio_025":
                    bool(solo and v25 and abs(v25 / solo - 0.25) <= 0.02),
                "spawn_volume_15_unclamped":
                    bool(v150 and abs(v150 / med(s2, 0.2, 0.8) - 1.5)
                         <= 0.06)}}
        # ---------------- S3 sysex past EOF ----------------
        sx = spawn(["pw-cat", "-s", "-p", "--target", "0", "-P",
                    f"node.name={PFX}_sx", str(TMP / "r87r.mid")])
        samples = []
        t0 = time.monotonic()
        for at in (0.9, 1.7, 3.0, 5.0, 9.0):
            left = at - (time.monotonic() - t0)
            if left > 0:
                time.sleep(left)
            n2, p2, l2 = graph()
            present = any(n["name"] == f"{PFX}_sx" for n in n2.values())
            samples.append({"at_s": at, "present": present,
                            "proc_alive": sx.poll() is None})
            if not present and sx.poll() is not None:
                break
        kill(sx)
        spots["S3_sysex_past_eof"] = {
            "fixture_seconds": 4.0, "samples": samples,
            "rc_after_kill": sx.returncode,
            "verdict": {"alive_past_eof":
                        any(s["present"] for s in samples
                            if s["at_s"] >= 5.0)}}
        # ---------------- S4 cold registry ----------------
        nodes2, _, _ = graph()
        live = next((n["id"] for n in nodes2.values()
                     if n["name"] == NS), None)
        cold = run(["pw-cli"], 10.0,
                   stdin_data=f"info {live}\nquit\n".encode())
        warm = run(["pw-cli", "info", str(live)], 12.0)
        spots["S4_cold_registry"] = {
            "live_id": live,
            "cold_unknown_global":
                f"unknown global '{live}'" in
                (cold["stdout"] + cold["stderr"]),
            "cold_class": re.search(r"unknown global '[^']*'",
                                    cold["stdout"] + cold["stderr"]).group(0)
            if "unknown global" in cold["stdout"] + cold["stderr"] else None,
            "warm_rc": warm["rc"],
            "warm_has_id": "id:" in warm["stdout"]}
        # ---------------- S5 remote census ----------------
        nodes2, _, _ = graph()
        named = [n["name"] for n in nodes2.values()
                 if n["name"] and re.search(r"raop|zeroconf|airplay|remote",
                                            n["name"], re.I)]
        mods = sorted(p.name for p in
                      Path("/usr/lib/pipewire-0.3").iterdir())
        spots["S5_remote_census"] = {
            "remote_named_nodes": named,
            "module_dir_count": len(mods),
            "net_modules": [m for m in mods
                            if re.search(r"raop|zeroconf|airplay", m)],
            "verdict": {"absent": not named and not [m for m in mods
                         if re.search(r"raop|zeroconf|airplay", m)]}}
        # ---------------- S6 create-node session vs linger ------------
        def create(linger):
            cname = f"{PFX}_" + ("ling" if linger else "adp")
            p = subprocess.Popen(["pw-cli"], stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 start_new_session=True)
            time.sleep(1.2)
            cmd = ('create-node adapter { factory.name='
                   '"support.null-audio-sink" node.name="%s" '
                   'media.class="Audio/Sink"%s }'
                   % (cname, " object.linger=true" if linger else ""))
            p.stdin.write(cmd.encode() + b"\n")
            p.stdin.flush()
            time.sleep(2.0)
            n2, _, _ = graph()
            in_session = any(n["name"] == cname for n in n2.values())
            p.stdin.write(b"quit\n")
            p.stdin.flush()
            try:
                p.stdin.close()
            except OSError:
                pass
            try:
                p.wait(timeout=6)
            except subprocess.TimeoutExpired:
                kill(p)
            time.sleep(0.7)
            n3, _, _ = graph()
            after = next((n["id"] for n in n3.values()
                          if n["name"] == cname), None)
            rec = {"in_session": in_session, "after_quit_id": after}
            if after is not None:
                rec["destroy"] = run(["pw-cli", "destroy", str(after)],
                                     12.0)
                time.sleep(0.6)
                n4, _, _ = graph()
                rec["after_destroy"] = any(n["name"] == cname
                                           for n in n4.values())
            return rec

        spots["S6_create_node"] = {
            "session_bound": create(False), "linger": create(True)}
        spots["S6_create_node"]["verdict"] = {
            "session_dies_with_client":
                spots["S6_create_node"]["session_bound"]["in_session"]
                and spots["S6_create_node"]["session_bound"]
                ["after_quit_id"] is None,
            "linger_survives_until_destroy":
                spots["S6_create_node"]["linger"]["after_quit_id"] is not None
                and spots["S6_create_node"]["linger"].get("after_destroy")
                is False}
    finally:
        # ---------------- cleanup ----------------
        nodes2, _, _ = graph()
        residual = [n["id"] for n in nodes2.values()
                    if n["name"] and PFX in n["name"]]
        spots["_residual_destroy"] = [
            {"id": i, **run(["pw-cli", "destroy", str(i)], 12.0)}
            for i in residual]
        spots["_unloads"] = {nm: unload_verified(nm, lf.get("module_id"))
                             for nm, lf in loads.items()}
        time.sleep(0.5)
        sinks = run(["pactl", "list", "sinks", "short"], 15.0)["stdout"]
        nodes3, _, _ = graph()
        spots["_residue"] = {
            "sinks_left": [ln for ln in sinks.splitlines()
                           if PFX in ln],
            "nodes_left": [n["name"] for n in nodes3.values()
                           if n["name"] and PFX in n["name"]],
            "own_procs_left": [p for p in
                               (run(["pgrep", "-f", PFX], 10.0)["stdout"]
                                or "").split()]}
        OUT.write_text(json.dumps(spots, indent=1) + "\n")
        print(json.dumps({k: v for k, v in spots.items()
                          if k in ("S1_routing", "S2_live_dsp",
                                   "S3_sysex_past_eof", "S4_cold_registry",
                                   "S5_remote_census", "S6_create_node")},
                         indent=1))
        print("receipt:", OUT)


if __name__ == "__main__":
    main()
