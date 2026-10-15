#!/usr/bin/env python3
"""r83 REVIEWER live probe — narrow behavioral re-check of the four folded
boundary corrections plus the latency units, on THIS host, under the
fleet's live load.

Zero foreign-object contact: every PipeWire/Pulse object is seat-owned
(`r83r_*_<pid>`), unloads are name-verified, no set-default-*, every
spawn is a bounded process group killed with killpg. Taps are `-n`-bounded
pw-record runs. Writes receipts only under corpus/live/r83-reviewer/.
"""
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
import wave
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parent
PID = os.getpid()
NS_A = f"r83r_ns_a_{PID}"
NS_B = f"r83r_ns_b_{PID}"
NS_44 = f"r83r_ns44_{PID}"
PREFIX = f"r83r_{PID}"
GRP = f"r83r_grp_{PID}"
AMP = 8192
FL = 997.0 + (PID % 4) * 211.0
FR = FL + 503.0
RES = {"probe": "r83-reviewer-live", "pid": PID, "ns": [NS_A, NS_B, NS_44],
       "tone_pair": [FL, FR], "legs": {}, "host": {}}


def sh(argv, timeout=10, **kw):
    p = subprocess.run(argv, capture_output=True, timeout=timeout, **kw)
    return p.returncode, p.stdout.decode(errors="replace"), \
        p.stderr.decode(errors="replace")


def host_state():
    rc, out, _ = sh(["pactl", "info"])
    fields = dict(re.findall(r"^([A-Za-z ]+):\s*(.*)$", out, re.M))
    RES["host"] = {
        "loadavg": Path("/proc/loadavg").read_text().split()[:3],
        "nproc": os.cpu_count(),
        "pipewire": fields.get("Server Name"),
        "pactl_lib": fields.get("Library Protocol Version"),
        "default_sink": fields.get("Default Sink"),
        "default_source": fields.get("Default Source"),
        "modules_before": len([l for l in sh(["pactl", "list",
                                              "short", "modules"])[1]
                               .splitlines() if l.strip()]),
        "py": sys.version.split()[0], "numpy": np.__version__,
        "pw_cli": sh(["pw-cli", "--version"])[2].strip() or
        sh(["pw-cli", "--version"])[1].strip(),
    }


def sink_names():
    rc, out, _ = sh(["pactl", "list", "short", "sinks"])
    return [l.split("\t")[1] for l in out.splitlines() if l.strip()]


def ns_load(name, extra=()):
    rc, out, err = sh(["pactl", "load-module", "module-null-sink",
                       "sink_name=" + name, *extra])
    mid = out.strip()
    t0 = time.monotonic()
    while time.monotonic() - t0 < 6:
        if name in sink_names():
            return {"module_id": int(mid) if mid.isdigit() else None,
                    "rc": rc, "waited_s": round(time.monotonic() - t0, 3)}
        time.sleep(0.15)
    return {"module_id": int(mid) if mid.isdigit() else None, "rc": rc,
            "error": err[:120], "sink_seen": False}


def module_index_for_sink(name):
    """The module index whose args carry OUR sink_name (name-verified)."""
    rc, out, _ = sh(["pactl", "list", "modules"])
    idx = None
    for block in out.split("Module #"):
        if f"sink_name={name}" in block:
            m = re.match(r"(\d+)", block)
            if m:
                idx = int(m.group(1))
    return idx


def unload_own(name, captured):
    idx = module_index_for_sink(name)
    leaf = {"verified_index": idx, "captured": captured}
    if idx is None:
        leaf["skipped"] = "not_listed"
        return leaf
    leaf["recycled"] = (captured is not None and idx != captured)
    rc, _, err = sh(["pactl", "unload-module", str(idx)])
    leaf["exit_code"] = rc
    leaf["stderr_tail"] = err.strip()[:120] or None
    return leaf


def dump_nodes():
    rc, out, _ = sh(["pw-dump"], timeout=20)
    try:
        d = json.loads(out or "[]")
    except ValueError:
        return {}
    nodes = {}
    for o in d:
        if str(o.get("type", "")).endswith("Node"):
            props = ((o.get("info") or {}).get("props") or {})
            nodes[props.get("node.name")] = props
    return nodes


def write_tone(path, seconds, rate=48000):
    n = int(rate * seconds)
    t = np.arange(n) / rate
    left = (AMP * np.sin(2 * np.pi * FL * t)).astype("<i2")
    right = (AMP * np.sin(2 * np.pi * FR * t)).astype("<i2")
    pcm = np.empty(n * 2, dtype="<i2")
    pcm[0::2], pcm[1::2] = left, right
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm.tobytes())


SPAWNED = []


def spawn(argv):
    p = subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                         stderr=subprocess.PIPE, start_new_session=True)
    SPAWNED.append(p.pid)          # only ever killpg our own group leaders
    return p


def shot(sid, argv, timeout=3.0, kill=True):
    """One bounded spawn: rc/signal/stderr + post-exit tagged-node witness."""
    rec = {"argv": " ".join(argv), "leg": sid}
    p = spawn(argv)
    t0 = time.monotonic()
    killed = False
    try:
        p.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        killed = True
        if kill:
            os.killpg(p.pid, signal.SIGKILL)
            p.wait()
    err = p.stderr.read().decode(errors="replace")
    rec.update({
        "wall_s": round(time.monotonic() - t0, 3),
        "exit_code": p.returncode,
        "signal": (signal.Signals(-p.returncode).name
                   if (p.returncode or 0) < 0 else None),
        "killed_at_bound": killed,
        "stderr_head": err.strip().splitlines()[:3],
        "stderr_full": err[:600],
    })
    nodes = dump_nodes()
    rec["nodes_after"] = sorted(n for n in nodes
                                if n and sid in n)
    return rec


def read_wav(path):
    insp = {}
    try:
        with wave.open(str(path), "rb") as w:
            insp["rate"] = w.getframerate()
            insp["channels"] = w.getnchannels()
            insp["frames"] = w.getnframes()
            raw = w.readframes(w.getnframes())
    except Exception as exc:  # noqa: BLE001
        return None, {"error": type(exc).__name__}
    a = np.frombuffer(raw, dtype="<i2")
    if insp["channels"] > 1:
        a = a.reshape(-1, insp["channels"])
    else:
        a = a.reshape(-1, 1)
    return a, insp


def amp_at(seg, rate, freq):
    n = len(seg)
    if n < 256:
        return 0.0
    x = seg.astype(np.float64) * np.hanning(n)
    k = np.exp(-2j * np.pi * freq * np.arange(n) / rate)
    return float(4.0 * abs(np.dot(x, k)) / n)


def first_nonsilent(a, rate, thresh=400):
    nz = np.nonzero(np.max(np.abs(a), axis=1) > thresh)[0]
    return round(float(nz[0]) / rate, 5) if len(nz) else None


def main():
    for tool in ("pw-loopback", "pw-cat", "pw-record", "pactl", "pw-dump"):
        if shutil.which(tool) is None:
            print("MISSING", tool)
            return 2
    host_state()
    loads = {}
    for nm, extra in ((NS_A, ()), (NS_B, ()), (NS_44, ("rate=44100",))):
        loads[nm] = ns_load(nm, extra)
        if loads[nm].get("waited_s") is None:
            print("SINK LOAD FAILED", nm, loads[nm])
            for n2, leaf in loads.items():
                unload_own(n2, leaf.get("module_id"))
            return 2
    RES["sink_loads"] = loads
    tmp = OUT / "tmp"
    tmp.mkdir(exist_ok=True)
    tone = tmp / "tag48.wav"
    tone44 = tmp / "tag44.wav"
    write_tone(tone, 6.0, 48000)
    write_tone(tone44, 6.0, 44100)
    try:
        legs = RES["legs"]
        # ---- (A) malformed-prop two classes ---------------------------
        legs["drop_silent"] = shot(
            f"{PREFIX}_drop_silent",
            ["pw-loopback", "-n", f"{PREFIX}_drop_silent", "-C", NS_A,
             "-i", "}{ garbage", "-P", NS_B], timeout=2.2)
        nd = dump_nodes()
        p = nd.get(f"input.{PREFIX}_drop_silent") or {}
        legs["drop_silent"]["input_props"] = {
            k: p.get(k) for k in ("media.name", "bogus.prop")}
        for sid, argv in (
                (f"{PREFIX}_err_i", ["pw-loopback", "-n",
                                     f"{PREFIX}_err_i", "-C", NS_A,
                                     "-i", "a=b }{ c=d", "-P", NS_B]),
                (f"{PREFIX}_err_o", ["pw-loopback", "-n",
                                     f"{PREFIX}_err_o", "-C", NS_A,
                                     "-i", "stream.capture.sink=true",
                                     "-o", "media.name=", "-P", NS_B]),
                (f"{PREFIX}_pc_err", ["pw-cat", "-p", "-P",
                                      "a=b }{ c=d", "-P",
                                      f"node.name={PREFIX}_pc_err",
                                      "--target", NS_B, str(tone)]),
                (f"{PREFIX}_pr_err", ["pw-record", "-P", "a=b }{ c=d",
                                      "-P",
                                      f"node.name={PREFIX}_pr_err",
                                      "--target", NS_A,
                                      str(tmp / "pr_err.wav")])):
            legs[sid.split("_", 2)[2] + "_hard"] = shot(sid, argv,
                                                        timeout=3.0)
        # ---- (B) empty/whitespace props SIGSEGV -----------------------
        for tag, argv in (
                ("lb_i_empty", ["pw-loopback", "-n", f"{PREFIX}_ie",
                                "-C", NS_A, "-i", "", "-P", NS_B]),
                ("lb_i_space", ["pw-loopback", "-n", f"{PREFIX}_is",
                                "-C", NS_A, "-i", " ", "-P", NS_B]),
                ("lb_o_empty", ["pw-loopback", "-n", f"{PREFIX}_oe",
                                "-C", NS_A, "-i",
                                "stream.capture.sink=true", "-o", "",
                                "-P", NS_B]),
                ("pc_empty", ["pw-cat", "-p", "-P", "", "-P",
                              f"node.name={PREFIX}_pe", "--target", NS_B,
                              str(tone)]),
                ("pr_empty", ["pw-record", "-P", "", "-P",
                              f"node.name={PREFIX}_re", "--target", NS_A,
                              str(tmp / "re.wav")])):
            legs["segv_" + tag] = shot(f"{PREFIX}_{tag}", argv,
                                       timeout=4.0)
        # ---- (C) latency units + uint32 wrap --------------------------
        for sid, tail in (("lat_l5", ["-l", "5"]),
                          ("lat_lneg5", ["-l", "-5"]),
                          ("lat_d025", ["-d", "0.25"]),
                          ("lat_group", ["-g", GRP]),
                          ("lat_none", [])):
            rec = shot(f"{PREFIX}_{sid}",
                       ["pw-loopback", "-n", f"{PREFIX}_{sid}",
                        "-C", NS_A, "-i", "stream.capture.sink=true",
                        "-P", NS_B, *tail], timeout=2.0)
            nd = dump_nodes()
            inp = nd.get(f"input.{PREFIX}_{sid}") or {}
            outp = nd.get(f"output.{PREFIX}_{sid}") or {}
            rec["input_props"] = {k: inp.get(k) for k in
                                  ("node.latency", "node.group")}
            rec["output_props"] = {k: outp.get(k) for k in
                                   ("node.latency", "node.group")}
            legs[sid] = rec
        # ---- (D) -d real transport delay (ctl vs -d 1.0) --------------
        for sid, extra in (("onset_ctl", []), ("onset_d10", ["-d", "1.0"])):
            tag = f"{PREFIX}_{sid}"
            tapf = tmp / f"tap_{sid}.wav"
            rec = {"leg": sid, "extra": extra}
            proc = spawn(["pw-loopback", "-n", tag, "-C", NS_A,
                          "-i", "stream.capture.sink=true", "-P", NS_B,
                          *extra])
            t0 = time.monotonic()
            linked = False
            while time.monotonic() - t0 < 9:
                nd = dump_nodes()
                ports = sh(["pw-link", "-l"])[1]
                if f"input.{tag}" in ports and f"output.{tag}" in ports:
                    linked = True
                    break
                if proc.poll() is not None:
                    break
                time.sleep(0.1)
            rec["linked"] = linked
            if not linked:
                if proc.poll() is None:
                    os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
                rec["blocked"] = "never linked"
                legs[sid] = rec
                continue
            t_tap = time.monotonic()
            tap = spawn(["pw-record", "-P", "stream.capture.sink=true",
                         "-P", f"node.name={tag}_tap", "--target", NS_B,
                         "-n", str(48000 * 3), "--rate", "48000",
                         "--channels", "2", "--format", "s16", str(tapf)])
            time.sleep(0.15)
            t_feed = time.monotonic()
            feed = spawn(["pw-cat", "-p", "-P", f"node.name={tag}_feed",
                          "--target", NS_A, str(tone)])
            try:
                tap.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(tap.pid, signal.SIGKILL)
                tap.wait()
            for p2 in (feed, proc):
                if p2.poll() is None:
                    os.killpg(p2.pid, signal.SIGKILL)
                p2.wait()
            a, insp = read_wav(tapf)
            rec["feed_lead_s"] = round(t_feed - t_tap, 4)
            if a is None:
                rec["tap_error"] = insp
            else:
                onset = first_nonsilent(a, insp["rate"])
                rec["onset_s"] = onset
                rec["transport_s"] = (round(onset - rec["feed_lead_s"], 4)
                                      if onset is not None else None)
            legs[sid] = rec
        ctl = legs["onset_ctl"].get("transport_s")
        d10 = legs["onset_d10"].get("transport_s")
        RES["onset_delta_s"] = (round(d10 - ctl, 4)
                                if ctl is not None and d10 is not None
                                else None)
        # ---- (E) resample.peaks |x| artifact (upsample only) ----------
        for sid, tonef, sink, prop in (
                ("peaks_up", tone44, NS_B, "resample.peaks=true"),
                ("peaks_matched", tone, NS_B, "resample.peaks=true")):
            tag = f"{PREFIX}_{sid}"
            tapf = tmp / f"tap_{sid}.wav"
            tap = spawn(["pw-record", "-P", "stream.capture.sink=true",
                         "-P", f"node.name={tag}_tap", "--target", sink,
                         "-n", str(48000 * 3), "--rate", "48000",
                         "--channels", "2", "--format", "s16", str(tapf)])
            time.sleep(0.4)
            rec = shot(tag, ["pw-cat", "-p", "-P", prop, "-P",
                             f"node.name={tag}", "--target", sink,
                             str(tonef)], timeout=3.0)
            try:
                tap.wait(timeout=8)
            except subprocess.TimeoutExpired:
                os.killpg(tap.pid, signal.SIGKILL)
                tap.wait()
            a, insp = read_wav(tapf)
            if a is None:
                rec["tap_error"] = insp
            else:
                seg = a[int(insp["rate"] * 0.3):]
                c0, c1 = seg[:, 0].astype(np.int64), seg[:, 1].astype(
                    np.int64)
                rec["tap_stats"] = []
                for c, f0 in ((c0, FL), (c1, FR)):
                    rec["tap_stats"].append({
                        "min": int(c.min()), "max": int(c.max()),
                        "mean": round(float(c.mean()), 2),
                        "neg_frac": round(float(np.mean(c < 0)), 4),
                        "zero_frac": round(float(np.mean(c == 0)), 4),
                        f"amp_at_{int(f0)}": round(
                            amp_at(c, insp["rate"], f0), 1),
                        f"amp_at_{int(2 * f0)}": round(
                            amp_at(c, insp["rate"], 2 * f0), 1),
                    })
            legs[sid] = rec
        # ---- (F) CLI wiring: mutex + dispatch -------------------------
        rcm, outm, errm = sh([sys.executable,
                              str(OUT / "measure_audio_a151a226.py"),
                              "--probe-pwcat-r83", "--probe-gst-r81"])
        RES["cli_mutex"] = {"rc": rcm,
                            "stderr_head": errm.strip().splitlines()[:2]}
    finally:
        # kill only OUR spawned process groups, then name-verified unloads
        RES["leftover_procs"] = []
        for pid in SPAWNED:
            if Path(f"/proc/{pid}").exists():
                RES["leftover_procs"].append(pid)
                try:
                    os.killpg(pid, signal.SIGKILL)
                except (ProcessLookupError, PermissionError):
                    pass
        RES["unloads"] = {nm: unload_own(nm, leaf.get("module_id"))
                          for nm, leaf in loads.items()}
        after = sink_names()
        RES["sinks_gone"] = {nm: nm not in after for nm in loads}
        nd = dump_nodes()
        RES["own_nodes_after"] = sorted(n for n in nd
                                        if PREFIX in (n or ""))
        RES["modules_after"] = len([l for l in sh(
            ["pactl", "list", "short", "modules"])[1].splitlines()
            if l.strip()])
        RES["default_sink_after"] = sh(
            ["pactl", "get-default-sink"])[1].strip()
    (OUT / "probe_live.json").write_text(json.dumps(RES, indent=1) + "\n")
    print(json.dumps({k: v for k, v in RES.items()
                      if k not in ("legs",)}, indent=1)[:4000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
