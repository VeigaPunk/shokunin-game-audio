#!/usr/bin/env python3
"""r78 REVIEWER — independent raw re-derivation of the eight headline cells.

Written from scratch for this review: own tone (L 880 / R 1320 Hz, amp 10000),
own pw-link edge parser, own WAV/frequency witness, own timings. It does NOT
import or call corpus/fixtures/measure_audio.py; the only shared thing is the
host. Every check is bounded and restores host state (default.audio.sink
metadata + probe modules) in finally blocks.

Usage: python3 raw-checks.py [check ...]      (default: all)
Output: raw-checks.json + raw-checks.log in the same directory.
"""
import json
import os
import re
import signal
import subprocess
import sys
import threading
import time
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT_JSON = HERE / "raw-checks.json"
LOG = HERE / "raw-checks.log"

PID = os.getpid()
RATE = 48000
L_HZ, R_HZ, AMP = 880.0, 1320.0, 10000
TOL = 0.06
AMP_MIN = 3000

TMP = Path(f"/tmp/r78rev-{PID}")
TMP.mkdir(parents=True, exist_ok=True)

results = {}
logf = None


def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    logf.write(line + "\n")
    logf.flush()


def sh(argv, timeout=20, **kw):
    try:
        p = subprocess.run(argv, capture_output=True, timeout=timeout, **kw)
        return {"argv": " ".join(map(str, argv)), "rc": p.returncode,
                "out": p.stdout.decode(errors="replace"),
                "err": p.stderr.decode(errors="replace")}
    except subprocess.TimeoutExpired:
        return {"argv": " ".join(map(str, argv)), "rc": None,
                "out": "", "err": "", "timeout": True}


def spawn(argv, **kw):
    return subprocess.Popen([str(a) for a in argv], stdout=subprocess.DEVNULL,
                            stderr=subprocess.PIPE, start_new_session=True,
                            **kw)


def kill_wait(proc, timeout=8.0):
    try:
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        proc.wait()
    return proc.returncode


def tone(path, seconds, rate=RATE):
    n = int(rate * seconds)
    t = np.arange(n) / rate
    pcm = np.empty(n * 2, dtype="<i2")
    pcm[0::2] = (AMP * np.sin(2 * np.pi * L_HZ * t)).astype("<i2")
    pcm[1::2] = (AMP * np.sin(2 * np.pi * R_HZ * t)).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm.tobytes())


def wav_pcm16_stereo(path):
    """Read a wav's data chunk as an int16 Nx2 array (header-tolerant)."""
    try:
        raw = Path(path).read_bytes()
    except OSError:
        return None, None
    if len(raw) < 44 or raw[:4] != b"RIFF":
        return None, None
    # walk chunks
    pos, fmt, data_off, data_len = 12, None, None, 0
    while pos + 8 <= len(raw):
        cid, clen = raw[pos:pos + 4], int.from_bytes(raw[pos + 4:pos + 8], "little")
        if cid == b"fmt ":
            fmt = {"channels": int.from_bytes(raw[pos + 10:pos + 12], "little"),
                   "rate": int.from_bytes(raw[pos + 12:pos + 16], "little"),
                   "bits": int.from_bytes(raw[pos + 22:pos + 24], "little")}
        elif cid == b"data":
            data_off, data_len = pos + 8, clen
        pos += 8 + clen + (clen & 1)
    if fmt is None or data_off is None:
        return None, fmt
    if fmt["bits"] != 16 or fmt["channels"] != 2:
        return None, fmt
    payload = raw[data_off:min(len(raw), data_off + data_len)]
    payload = payload[:len(payload) - (len(payload) % 4)]
    arr = np.frombuffer(payload, dtype="<i2").reshape(-1, 2)
    return arr, fmt


def mine_windows(path, window_s=0.1):
    """Frequency-strict classifier over the wav; returns dict."""
    arr, fmt = wav_pcm16_stereo(path)
    out = {"fmt": fmt, "windows": [], "mine_spans": []}
    if arr is None or len(arr) == 0:
        out["unreadable"] = True
        return out
    rate = (fmt or {}).get("rate") or RATE
    win = max(64, int(rate * window_s))
    han = np.hanning(win)
    fax = np.fft.rfftfreq(win, 1.0 / rate)
    spans, cur = [], None
    for i in range(len(arr) // win):
        seg = arr[i * win:(i + 1) * win].astype(np.float64) * han[:, None]
        row = {}
        for ch, want in (("L", L_HZ), ("R", R_HZ)):
            mag = np.abs(np.fft.rfft(seg[:, 0 if ch == "L" else 1]))
            k = int(np.argmax(mag))
            row[ch] = (float(fax[k]), float(4.0 * mag[k] / len(seg)))
        at = round(i * window_s, 2)
        mine = (abs(row["L"][0] - L_HZ) <= TOL * L_HZ and
                abs(row["R"][0] - R_HZ) <= TOL * R_HZ and
                row["L"][1] >= AMP_MIN and row["R"][1] >= AMP_MIN)
        peak = max(row["L"][1], row["R"][1])
        out["windows"].append({"at_s": at, "f_l": int(row["L"][0]),
                               "f_r": int(row["R"][0]),
                               "a_l": int(row["L"][1]), "a_r": int(row["R"][1]),
                               "peak": int(peak), "mine": bool(mine),
                               "silent": bool(peak < 50)})
        if mine:
            cur = [at, at + window_s] if cur is None else [cur[0], at + window_s]
        elif cur is not None:
            spans.append([round(x, 2) for x in cur])
            cur = None
    if cur is not None:
        spans.append([round(x, 2) for x in cur])
    out["mine_spans"] = spans
    out["mine_windows"] = sum(1 for w in out["windows"] if w["mine"])
    out["silent_windows"] = sum(1 for w in out["windows"] if w["silent"])
    out["peak_max"] = max((w["peak"] for w in out["windows"]), default=0)
    return out


def link_edges():
    r = sh(["pw-link", "-l"], timeout=10)
    port, edges = None, []
    for ln in r["out"].splitlines():
        if not ln or not ln[0].isspace():
            port = ln.strip() or None
            continue
        if port is None:
            continue
        if "|->" in ln:
            edges.append((port, ln.split("|->", 1)[1].strip()))
        elif "|<-" in ln:
            edges.append((ln.split("|<-", 1)[1].strip(), port))
    return sorted(set(edges)), r["rc"]


def consumers(tag):
    edges, rc = link_edges()
    fl = {d for s, d in edges if s == f"{tag}:output_FL"}
    fr = {d for s, d in edges if s == f"{tag}:output_FR"}
    both = fl & fr
    nodes = sorted({p.rsplit(":", 1)[0] for p in (both or (fl | fr))})
    return {"consumer_ports": sorted(fl | fr), "nodes": nodes, "link_rc": rc}


def producers(tag):
    edges, rc = link_edges()
    fl = {s for s, d in edges if d == f"{tag}:input_FL"}
    fr = {s for s, d in edges if d == f"{tag}:input_FR"}
    both = fl & fr
    nodes = sorted({p.rsplit(":", 1)[0] for p in (both or (fl | fr))})
    return {"producer_ports": sorted(fl | fr), "nodes": nodes, "link_rc": rc}


def output_ports(tag):
    r = sh(["pw-link", "-o"], timeout=10)
    return sorted(l.strip() for l in r["out"].splitlines()
                  if l.strip().startswith(f"{tag}:"))


def default_sink_name():
    r = sh(["pactl", "get-default-sink"], timeout=10)
    return r["out"].strip() or None


def metadata_default():
    r = sh(["pw-metadata", "-n", "default", "0", "default.audio.sink"], timeout=10)
    m = re.search(r"value:'(.*?)'(?:\s*type|\s*$)", r["out"])
    raw = m.group(1) if m else None
    name = None
    if raw:
        mm = re.search(r'"?name"?\s*[:=]\s*"?([^",}\s]+)"?', raw)
        name = mm.group(1) if mm else None
    return {"name": name, "raw": raw, "rc": r["rc"]}


def metadata_set(raw):
    return sh(["pw-metadata", "-n", "default", "0", "default.audio.sink", raw], timeout=10)


# The host's real session default (recorded pre-state). A sibling lane's probe
# sink can be the *current* default while it runs — restoring "whatever we saw
# at startup" would then write a foreign probe sink back; pin the real one.
HOST_DEFAULT_SINK = "alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink"


def restore_host_default(fallback_raw=None):
    sinks = sh(["pactl", "list", "short", "sinks"], timeout=10)["out"]
    if HOST_DEFAULT_SINK in sinks:
        return metadata_set(json.dumps({"name": HOST_DEFAULT_SINK}))
    if fallback_raw:
        return metadata_set(fallback_raw)
    return None


def null_sink_load(name):
    r = sh(["pactl", "load-module", "module-null-sink", f"sink_name={name}"], timeout=15)
    mid = r["out"].strip()
    return (int(mid) if mid.isdigit() else None), r["rc"], r["err"][:200] or None


def unload(mid):
    if mid is None:
        return None
    return sh(["pactl", "unload-module", str(mid)], timeout=15)["rc"]


def tap(target, path, seconds, tag):
    return spawn(["pw-record", "-P", "stream.capture.sink=true", "-P",
                  f"node.name={tag}", "--target", target, "-n",
                  int(RATE * seconds), "--rate", RATE, "--channels", "2",
                  "--format", "s16", path])


# ---------------------------------------------------------------- checks ---
def check_lattice():
    """Cell 1 — fallback lattice: garbage/absent/default-token/source-name
    all land the CURRENT default sink at rc=0/empty stderr/real-time wall,
    witnessed by pw-link consumers + a frequency-strict monitor tap."""
    d0 = default_sink_name()
    res = {"default_sink": d0, "legs": {}}
    tonef = TMP / "tone_lat.wav"
    tone(tonef, 2.6)
    sink_load, lrc, lerr = null_sink_load(f"r78rev_play_{PID}")
    res["probe_sink_load"] = {"module_id": sink_load, "rc": lrc, "error": lerr}
    legs = [
        ("garbage", ["--target", "no_such_sink_rev"], "fallback"),
        ("absent_after_unload", None, "fallback"),
        ("default_token", ["--target", "default"], "fallback"),
        ("at_default_sink", ["--target", "@DEFAULT_SINK@"], "fallback"),
        ("source_name", ["--target", _default_source()], "fallback"),
        ("monitor_of_probe", ["--target", f"r78rev_play_{PID}.monitor"], "monitor"),
        ("target_0", ["--target", "0"], "stall"),
        ("honored_probe_sink", ["--target", f"r78rev_play_{PID}"], "honored"),
    ]
    # absent_after_unload: load then unload a sink, then target its name
    tmp_mid, _, _ = null_sink_load(f"r78rev_absent_{PID}")
    unload(tmp_mid)
    legs[1] = ("absent_after_unload", ["--target", f"r78rev_absent_{PID}"], "fallback")

    try:
        for name, tail, kind in legs:
            tag = f"r78rev_lat_{name}"
            d0_leg = default_sink_name() or d0
            tapf = TMP / f"tap_{name}.wav"
            want_tap = d0_leg if kind != "honored" else f"r78rev_play_{PID}"
            tapf_s = 3.6
            tp = tap(want_tap, tapf, tapf_s, f"{tag}_tap")
            time.sleep(0.4)
            bound = 6.0 if kind == "stall" else 2.6 + 6.0
            argv = ["pw-play", "-P", f"node.name={tag}", *(tail or []), str(tonef)]
            t0 = time.monotonic()
            proc = spawn(argv)
            samples = []
            for at in ((1.0, 2.5, 4.5) if kind == "stall" else (0.8, 1.8)):
                left = at - (time.monotonic() - t0)
                if left > 0:
                    time.sleep(left)
                samples.append({"at_s": at, "live": proc.poll() is None,
                                "output_ports": output_ports(tag),
                                **consumers(tag)})
            killed = False
            try:
                proc.wait(timeout=max(0.05, bound - (time.monotonic() - t0)))
            except subprocess.TimeoutExpired:
                killed = True
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
            wall = round(time.monotonic() - t0, 2)
            err = proc.stderr.read().decode(errors="replace")
            kill_wait(tp, 8)
            leg = {"tail": tail, "kind": kind, "rc": proc.returncode,
                   "killed_at_bound": killed, "wall_s": wall,
                   "default_sink_at_leg": d0_leg,
                   "stderr_tail": err.strip().splitlines()[-1][-120:] if err.strip() else "",
                   "samples": samples,
                   "consumers_union": sorted({n for s in samples for n in s["nodes"]}),
                   "tap": {"target": want_tap, **mine_windows(tapf)}}
            res["legs"][name] = leg
            log(f"lattice {name}: rc={leg['rc']} killed={killed} wall={wall} "
                f"consumers={leg['consumers_union']} "
                f"tap_mine={leg['tap'].get('mine_windows')}/{len(leg['tap'].get('windows', []))}")
            time.sleep(0.5)
    finally:
        unload(sink_load)
    res["probe_sink_gone"] = f"r78rev_play_{PID}" not in sh(
        ["pactl", "list", "short", "sinks"], timeout=10)["out"]
    return res


def _default_source():
    r = sh(["pactl", "get-default-source"], timeout=10)
    return r["out"].strip() or None


def check_follow():
    """Cell 2 — followed_move: an ACTIVE fallback stream re-links when the
    live default moves (pw-metadata), and pactl set-default-sink is a
    rc=0 no-op (stale default). A background sampler records the metadata
    every 0.25 s so any FOREIGN writer is visible in the trace."""
    meta0 = metadata_default()
    d0 = meta0["name"]
    res = {"metadata_initial": meta0, "pactl_default_initial": default_sink_name()}
    s_new = f"r78rev_def_{PID}"
    mid, lrc, lerr = null_sink_load(s_new)
    res["def_sink_load"] = {"module_id": mid, "rc": lrc, "error": lerr}
    tonef = TMP / "tone_follow.wav"
    tone(tonef, 6.0)
    trace, stop = [], threading.Event()

    def sampler():
        t0 = time.monotonic()
        while not stop.is_set():
            trace.append({"t": round(time.monotonic() - t0, 2),
                          "metadata": metadata_default()["name"]})
            stop.wait(0.25)

    th = threading.Thread(target=sampler, daemon=True)
    th.start()
    try:
        tag = "r78rev_fol"
        proc = spawn(["pw-play", "-P", f"node.name={tag}", "--target",
                      "no_such_sink_rev", str(tonef)])
        t0 = time.monotonic()
        samples = []
        for at, ev in ((1.0, None), (1.6, "move"), (2.6, None), (4.0, None),
                       (4.6, "restore"), (5.4, None)):
            left = at - (time.monotonic() - t0)
            if left > 0:
                time.sleep(left)
            if ev == "move":
                res["move_write"] = metadata_set(json.dumps({"name": s_new}))
            if ev == "restore":
                res["restore_write"] = metadata_set(
                    meta0["raw"] or json.dumps({"name": d0}))
            samples.append({"at_s": at, "live": proc.poll() is None,
                            **consumers(tag)})
        rc = kill_wait(proc, 10)
        res["stream"] = {"rc": rc, "samples": samples}
        res["followed_move"] = all(s["nodes"] == [s_new] for s in samples[2:4])
        res["spawn_consumer"] = samples[0]["nodes"]
        res["restored_consumer"] = samples[5]["nodes"]
        log(f"follow: spawn={samples[0]['nodes']} after_move="
            f"{[s['nodes'] for s in samples[2:4]]} after_restore="
            f"{samples[5]['nodes']} rc={rc}")

        # pactl stale-default: put the metadata on the probe sink, then write
        # the REAL default through pactl and poll both views for 5.5 s.
        time.sleep(0.5)
        metadata_set(json.dumps({"name": s_new}))
        time.sleep(0.5)
        pre = metadata_default()
        pa = sh(["pactl", "set-default-sink", d0], timeout=10)
        t1 = time.monotonic()
        ptrace, moved = [], None
        while time.monotonic() - t1 < 5.5:
            time.sleep(0.5)
            mn = metadata_default()
            pn = default_sink_name()
            ptrace.append({"at_s": round(time.monotonic() - t1, 1),
                           "metadata": mn["name"], "pactl": pn})
            if mn["name"] == d0:
                moved = round(time.monotonic() - t1, 1)
                break
        res["pactl_stale"] = {"rc": pa["rc"], "moved_at_s": moved,
                              "poll_trace": ptrace,
                              "pre_metadata": pre["name"],
                              "stderr": pa["err"][:120]}
        log(f"pactl set-default-sink: rc={pa['rc']} moved_at={moved} "
            f"trace_tail={ptrace[-1]}")

        # durability probe: write the probe default and watch with NO stream
        # running — separates a WirePlumber re-assert from a stream-driven
        # re-link (the harness's pactl test has no such guard).
        time.sleep(0.5)
        metadata_set(json.dumps({"name": s_new}))
        t2 = time.monotonic()
        dur = []
        while time.monotonic() - t2 < 6.0:
            time.sleep(0.25)
            dur.append({"at_s": round(time.monotonic() - t2, 2),
                        "metadata": metadata_default()["name"]})
        res["durability_no_stream"] = {
            "held_s": next((d["at_s"] for d in dur
                            if d["metadata"] != s_new), None),
            "trace": dur}
        log(f"durability (no stream): first non-probe at "
            f"{res['durability_no_stream']['held_s']} s "
            f"of {len(dur)} samples")
    finally:
        stop.set()
        th.join(timeout=2)
        restore_host_default(meta0["raw"] or json.dumps({"name": d0}))
        unload(mid)
    res["metadata_trace"] = trace
    res["metadata_final"] = metadata_default()
    res["def_sink_gone"] = s_new not in sh(["pactl", "list", "short", "sinks"], timeout=10)["out"]
    return res


def check_loss():
    """Cell 3 — unload mid-play re-links to default (rc=0, to EOF);
    manual pw-link -d leaves it unlinked but consumed at real-time rate."""
    d0 = default_sink_name()
    res = {"default_sink": d0, "legs": {}}
    loss = f"r78rev_loss_{PID}"
    mid, lrc, lerr = null_sink_load(loss)
    res["sink_load"] = {"module_id": mid, "rc": lrc, "error": lerr}
    tonef = TMP / "tone_loss.wav"
    tone(tonef, 6.0)
    try:
        # leg A: unload mid-play
        tag = "r78rev_loss_unload"
        proc = spawn(["pw-play", "-P", f"node.name={tag}", "--target", loss, str(tonef)])
        t0 = time.monotonic()
        samples = []
        for at, ev in ((1.0, None), (2.0, "unload"), (3.0, None), (5.0, None)):
            left = at - (time.monotonic() - t0)
            if left > 0:
                time.sleep(left)
            if ev == "unload":
                res["unload_rc"] = unload(mid)
            samples.append({"at_s": at, "live": proc.poll() is None,
                            **consumers(tag)})
        rc = kill_wait(proc, 10)
        res["legs"]["unload_relink"] = {
            "rc": rc, "wall_s": round(time.monotonic() - t0, 2),
            "stderr_tail": proc.stderr.read().decode(errors="replace").strip()[-100:],
            "samples": samples}
        log(f"loss unload: samples={[s['nodes'] for s in samples]} rc={rc}")
        time.sleep(0.6)
        # leg B: manual unlink
        mid2, rc2, err2 = null_sink_load(loss)
        res["sink_load_2"] = {"module_id": mid2, "rc": rc2, "error": err2}
        tag2 = "r78rev_loss_unlink"
        proc2 = spawn(["pw-play", "-P", f"node.name={tag2}", "--target", loss, str(tonef)])
        t0 = time.monotonic()
        samples2, unlink_rcs = [], None
        for at, ev in ((1.0, None), (2.0, "cut"), (3.0, None), (5.0, None)):
            left = at - (time.monotonic() - t0)
            if left > 0:
                time.sleep(left)
            if ev == "cut":
                unlink_rcs = [sh(["pw-link", "-d", f"{tag2}:output_{ch}",
                                  f"{loss}:playback_{ch}"], timeout=10)["rc"]
                              for ch in ("FL", "FR")]
            samples2.append({"at_s": at, "live": proc2.poll() is None,
                             **consumers(tag2)})
        rc2x = kill_wait(proc2, 10)
        res["legs"]["manual_unlink"] = {
            "rc": rc2x, "wall_s": round(time.monotonic() - t0, 2),
            "unlink_rcs": unlink_rcs,
            "stderr_tail": proc2.stderr.read().decode(errors="replace").strip()[-100:],
            "samples": samples2}
        log(f"loss unlink: samples={[s['nodes'] for s in samples2]} "
            f"unlink_rcs={unlink_rcs} rc={rc2x}")
    finally:
        unload(mid)
        unload(mid2)
    res["sink_gone"] = loss not in sh(["pactl", "list", "short", "sinks"], timeout=10)["out"]
    return res


def check_segv():
    """Cell 4 — class_override_segv: -P media.class=<non-output> SIGSEGVs
    pw-play (rc=-11, empty stderr, no node) while Stream/Output/Audio plays."""
    d0 = default_sink_name()
    res = {"default_sink": d0, "legs": {}}
    sink = f"r78rev_segv_{PID}"
    mid, lrc, lerr = null_sink_load(sink)
    res["sink_load"] = {"module_id": mid, "rc": lrc, "error": lerr}
    tonef = TMP / "tone_segv.wav"
    tone(tonef, 1.6)
    try:
        for cls in ("Audio/Sink", "Stream/Input/Audio", "Audio/Duplex",
                    "Audio/Bogus", "Stream/Output/Audio", "Audio/Source"):
            tag = "r78rev_segv_" + cls.split("/")[-1].lower()
            t0 = time.monotonic()
            proc = spawn(["pw-play", "-P", f"node.name={tag}", "--target", sink,
                          "-P", f"media.class={cls}", str(tonef)])
            mid_cons = None
            if cls == "Stream/Output/Audio":
                time.sleep(0.6)          # mid-play sample for the control
                mid_cons = consumers(tag)["nodes"]
            bound = 6.0 if cls == "Audio/Source" else 4.0
            try:
                proc.wait(timeout=bound)
                killed = False
            except subprocess.TimeoutExpired:
                killed = True
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
            wall = round(time.monotonic() - t0, 2)
            err = proc.stderr.read().decode(errors="replace")
            cons = consumers(tag)
            res["legs"][cls] = {"rc": proc.returncode, "wall_s": wall,
                                "killed_at_bound": killed,
                                "stderr_len": len(err),
                                "stderr_tail": err.strip()[-100:],
                                "consumers": cons["nodes"],
                                "mid_play_consumers": mid_cons,
                                "output_ports": output_ports(tag)}
            log(f"segv {cls}: rc={proc.returncode} wall={wall} "
                f"stderr_len={len(err)} killed={killed} cons={cons['nodes']}")
            time.sleep(0.3)
    finally:
        unload(mid)
    return res


def check_aplay():
    """Cell 5 — aplay EBUSY under a monitor witness + lock-retention bracket
    (+1 s busy / +7 s free) + aplay converts vs arecord constrains."""
    d0 = default_sink_name()
    res = {"default_sink": d0}
    # subject device = hw:0,0 (Speaker sink on card 0)
    dev = "hw:0,0"
    sink = "alsa_output.usb-Generic_USB_Audio-00.HiFi__Speaker__sink"
    res["subject"] = {"device": dev, "sink": sink}
    tiny = TMP / "tiny.wav"
    tone(tiny, 0.3)
    t1s = TMP / "one_s.wav"
    tone(t1s, 1.2)
    try:
        res["params_play"] = {k: v for k, v in sh(
            ["aplay", "-D", dev, "--dump-hw-params", str(tiny)], timeout=10).items()
            if k in ("rc", "err", "out")}
        res["params_play"]["FORMAT"] = re.search(r"^FORMAT:\s*(.*)$", res["params_play"]["out"] + res["params_play"]["err"], re.M).group(1) if re.search(r"^FORMAT:\s*(.*)$", res["params_play"]["out"] + res["params_play"]["err"], re.M) else None
        res["params_cap"] = {k: v for k, v in sh(
            ["arecord", "-D", dev, "--dump-hw-params", "-d", "1", "/dev/null"], timeout=10).items()
            if k in ("rc", "err", "out")}
        # baseline on a free device
        res["hw_baseline"] = sh(["aplay", "-D", dev, str(t1s)], timeout=10)
        res["hw_baseline"] = {k: res["hw_baseline"][k] for k in ("rc", "err")}
        # witness: monitor tap of the Speaker sink holds the PCM
        tapf = TMP / "tap_witness.wav"
        tp = tap(sink, tapf, 5.0, "r78rev_wit_tap")
        time.sleep(0.8)
        busy = sh(["aplay", "-D", dev, str(tiny)], timeout=10)
        res["busy_under_witness"] = {"rc": busy["rc"],
                                     "err_tail": busy["err"].strip().splitlines()[-1][-120:] if busy["err"].strip() else ""}
        t_end = time.monotonic()
        tp.terminate()
        kill_wait(tp, 8)
        # lock retention after the witness dies: poll aplay until rc=0
        released = None
        t0 = time.monotonic()
        while time.monotonic() - t0 < 14:
            time.sleep(0.6)
            p = sh(["aplay", "-D", dev, str(tiny)], timeout=8)
            if p["rc"] == 0:
                released = round(time.monotonic() - t_end, 1)
                break
        res["witness_lock_release_s"] = released
        log(f"aplay witness: busy_rc={busy['rc']} release_in={released}s")
        # retention bracket: a fresh PipeWire playback on the same sink
        tag = "r78rev_aplay_hold"
        proc = spawn(["pw-play", "-P", f"node.name={tag}", "--target", sink, str(t1s)])
        time.sleep(0.6)
        res["pipewire_hold"] = {"consumers": consumers(tag)["nodes"],
                                "rc_poll": proc.poll()}
        t_h = time.monotonic()
        time.sleep(max(0.0, 1.0 - (time.monotonic() - t_h)))
        r1 = sh(["aplay", "-D", dev, str(tiny)], timeout=8)
        left = 7.0 - (time.monotonic() - t_h)
        if left > 0:
            time.sleep(left)
        r7 = sh(["aplay", "-D", dev, str(tiny)], timeout=8)
        kill_wait(proc, 8)
        res["retention"] = {
            "plus_1s_rc": r1["rc"],
            "plus_1s_err": r1["err"].strip().splitlines()[-1][-100:] if r1["err"].strip() else "",
            "plus_7s_rc": r7["rc"],
            "plus_7s_err": r7["err"].strip().splitlines()[-1][-100:] if r7["err"].strip() else ""}
        log(f"retention: +1s rc={r1['rc']} +7s rc={r7['rc']}")
        # convert vs constrain
        conv = sh(["aplay", "-D", dev, "-f", "FLOAT_LE", str(t1s)], timeout=10)
        m = re.search(r"format is changed to (\S+)", conv["err"] + conv["out"])
        res["convert_float"] = {"rc": conv["rc"],
                                "converted_to": m.group(1) if m else None}
        rec = sh(["arecord", "-D", dev, "-d", "1", "/dev/null"], timeout=10)
        res["arecord_constrain"] = {
            "rc": rec["rc"],
            "err_tail": rec["err"].strip().splitlines()[-1][-120:] if rec["err"].strip() else "",
            "format_line": next((l for l in rec["err"].splitlines()
                                 if "Sample format" in l), None)}
        log(f"convert rc={conv['rc']} -> {res['convert_float']['converted_to']}; "
            f"arecord rc={rec['rc']}")
    finally:
        pass
    return res


def check_zeros():
    """Cell 6 — capture link loss: cutting the producer links leaves the
    capture running filled with zeros (unlinked_sustained_zeros); cutting the
    capture's own input links freezes the file (unlinked_stall)."""
    res = {"legs": {}}
    sink = f"r78rev_cap_{PID}"
    mid, lrc, lerr = null_sink_load(sink)
    res["sink_load"] = {"module_id": mid, "rc": lrc, "error": lerr}
    feed_tone = TMP / "tone_cap.wav"
    tone(feed_tone, 12.0)
    try:
        # producer-side unlink (the headline cell)
        out = TMP / "cap_prod.wav"
        feed = spawn(["pw-cat", "-p", "-P", "node.name=r78rev_feed",
                      "--target", sink, str(feed_tone)])
        time.sleep(0.5)
        frames = int(5.0 * RATE)
        cap = spawn(["pw-record", "-P", "stream.capture.sink=true", "-P",
                     "node.name=r78rev_cap", "--target", sink, "-n", str(frames),
                     "--rate", RATE, "--channels", "2", "--format", "s16", str(out)])
        t0 = time.monotonic()
        sizes, rcs = [], None
        for at, ev in ((0.8, "size"), (1.6, "cut"), (2.1, "size"), (2.6, "size"),
                       (3.1, "size"), (4.1, "size"), (4.6, "size")):
            left = at - (time.monotonic() - t0)
            if left > 0:
                time.sleep(left)
            if ev == "cut":
                rcs = [sh(["pw-link", "-d", f"r78rev_feed:output_{ch}",
                           f"{sink}:playback_{ch}"], timeout=10)["rc"]
                       for ch in ("FL", "FR")]
            else:
                sizes.append({"at_s": at,
                              "bytes": out.stat().st_size if out.exists() else 0})
        rc = kill_wait(cap, 15)
        err = cap.stderr.read().decode(errors="replace")
        if feed.poll() is None:
            os.killpg(feed.pid, signal.SIGKILL)
        feed.wait()
        w = mine_windows(out)
        pre = [x for x in w["windows"] if x["at_s"] < 1.4]
        post = [x for x in w["windows"] if x["at_s"] > 2.2]
        res["legs"]["producer_unlink"] = {
            "rc": rc, "unlink_rcs": rcs, "size_trace": sizes,
            "bytes": out.stat().st_size if out.exists() else 0,
            "expected_bytes": 44 + frames * 4,
            "stderr_tail": err.strip()[-100:],
            "pre_mine": sum(1 for x in pre if x["mine"]),
            "pre_windows": len(pre),
            "post_windows": len(post),
            "post_silent": sum(1 for x in post if x["silent"]),
            "post_peak_max": max((x["peak"] for x in post), default=0)}
        log(f"zeros producer: sizes={[s['bytes'] for s in sizes]} "
            f"pre_mine={res['legs']['producer_unlink']['pre_mine']}/{len(pre)} "
            f"post_silent={res['legs']['producer_unlink']['post_silent']}/{len(post)} "
            f"peak_post={res['legs']['producer_unlink']['post_peak_max']}")
        time.sleep(0.6)
        # consumer-side unlink: freeze + resume
        out2 = TMP / "cap_cons.wav"
        feed2 = spawn(["pw-cat", "-p", "-P", "node.name=r78rev_feed2",
                       "--target", sink, str(feed_tone)])
        time.sleep(0.5)
        frames2 = int(7.0 * RATE)
        cap2 = spawn(["pw-record", "-P", "stream.capture.sink=true", "-P",
                      "node.name=r78rev_cap2", "--target", sink, "-n", str(frames2),
                      "--rate", RATE, "--channels", "2", "--format", "s16", str(out2)])
        t0 = time.monotonic()
        sizes2, cut_rc, relink_rc = [], None, None
        for at, ev in ((0.8, "size"), (1.3, "size"), (1.6, "cut"), (2.1, "size"),
                       (2.6, "size"), (3.4, "size"), (3.9, "relink"),
                       (4.4, "size"), (4.9, "size")):
            left = at - (time.monotonic() - t0)
            if left > 0:
                time.sleep(left)
            if ev == "cut":
                cut_rc = [sh(["pw-link", "-d", f"{sink}:monitor_{ch}",
                              f"r78rev_cap2:input_{ch}"], timeout=10)["rc"]
                          for ch in ("FL", "FR")]
            elif ev == "relink":
                relink_rc = [sh(["pw-link", f"{sink}:monitor_{ch}",
                                 f"r78rev_cap2:input_{ch}"], timeout=10)["rc"]
                             for ch in ("FL", "FR")]
            else:
                sizes2.append({"at_s": at,
                               "bytes": out2.stat().st_size if out2.exists() else 0})
        rc2 = kill_wait(cap2, 15)
        if feed2.poll() is None:
            os.killpg(feed2.pid, signal.SIGKILL)
        feed2.wait()
        res["legs"]["consumer_unlink"] = {
            "rc": rc2, "cut_rc": cut_rc, "relink_rc": relink_rc,
            "size_trace": sizes2,
            "bytes": out2.stat().st_size if out2.exists() else 0,
            "expected_bytes": 44 + frames2 * 4}
        log(f"zeros consumer: sizes={[s['bytes'] for s in sizes2]}")
    finally:
        unload(mid)
    return res


def check_parec():
    """Cell 7 — parec --fix-*: payload adopts the source spec while the wav
    header keeps the request (header_prefix_mismatch); no-fix control honest."""
    res = {"legs": {}}
    sink = f"r78rev_fix_{PID}"
    mon = sink + ".monitor"
    mid, lrc, lerr = null_sink_load(sink)
    res["sink_load"] = {"module_id": mid, "rc": lrc, "error": lerr}
    feed_tone = TMP / "tone_fix.wav"
    tone(feed_tone, 70.0)
    feed = None
    try:
        feed = spawn(["pw-cat", "-p", "-P", "node.name=r78rev_fixfeed",
                      "--target", sink, str(feed_tone)])
        time.sleep(0.5)
        for name, args, seekable in (
                ("hdr_rate_fix", ["--file-format=wav", "--rate=22050",
                                  "--channels=2", "--format=s16le", "--fix-rate"], True),
                ("hdr_rate_plain", ["--file-format=wav", "--rate=22050",
                                    "--channels=2", "--format=s16le"], True),
                ("rate_fix_raw", ["--raw", "--rate=22050", "--fix-rate"], False),
                ("rate_req_raw", ["--raw", "--rate=22050"], False)):
            op = TMP / f"{name}.out"
            fh = open(op, "wb") if seekable else None
            src = subprocess.Popen(["parec", "-d", mon, *args],
                                   stdout=fh or subprocess.PIPE,
                                   stderr=subprocess.PIPE, start_new_session=True)
            dd = None
            if not seekable:
                dd = subprocess.Popen(["dd", f"of={op}", "bs=8192", "status=none"],
                                      stdin=src.stdout, stderr=subprocess.DEVNULL,
                                      start_new_session=True)
                src.stdout.close()
            sizes, t0 = [], time.monotonic()
            for _ in range(10):
                time.sleep(0.55)
                sizes.append({"at_s": round(time.monotonic() - t0, 2),
                              "bytes": op.stat().st_size if op.exists() else 0})
            if src.poll() is None:
                os.killpg(src.pid, signal.SIGKILL)
            src.wait()
            if fh:
                fh.close()
            if dd is not None:
                try:
                    dd.wait(timeout=6)
                except subprocess.TimeoutExpired:
                    os.killpg(dd.pid, signal.SIGKILL)
                    dd.wait()
            nz = [s for s in sizes if s["bytes"] > 1024]
            bps = 0
            if len(nz) >= 3:
                n = len(nz)
                mt = sum(s["at_s"] for s in nz) / n
                mb = sum(s["bytes"] for s in nz) / n
                cov = sum((s["at_s"] - mt) * (s["bytes"] - mb) for s in nz)
                var = sum((s["at_s"] - mt) ** 2 for s in nz)
                bps = cov / var if var else 0
            arr, fmt = (wav_pcm16_stereo(op) if seekable else (None, None))
            raw = op.read_bytes() if op.exists() else b""
            hdr = None
            if raw[:4] == b"RIFF":
                hdr = {"channels": int.from_bytes(raw[22:24], "little"),
                       "rate": int.from_bytes(raw[24:28], "little"),
                       "bits": int.from_bytes(raw[34:36], "little")}
            res["legs"][name] = {
                "args": args, "rc": src.returncode, "bytes": len(raw),
                "size_trace": sizes, "bytes_per_s": int(bps),
                "implied_rate_16bit_stereo": round(bps / 4, 1) if bps else None,
                "wav_header": hdr}
            log(f"parec {name}: bps={int(bps)} implied_rate={res['legs'][name]['implied_rate_16bit_stereo']} hdr={hdr}")
    finally:
        if feed is not None:
            if feed.poll() is None:
                os.killpg(feed.pid, signal.SIGKILL)
            feed.wait()
        unload(mid)
    return res


CHECKS = {"lattice": check_lattice, "follow": check_follow, "loss": check_loss,
          "segv": check_segv, "aplay": check_aplay, "zeros": check_zeros,
          "parec": check_parec}


def main():
    global logf
    logf = open(LOG, "a")
    want = sys.argv[1:] or list(CHECKS)
    meta0 = metadata_default()
    log(f"=== raw-checks start pid={PID} default_sink={meta0['name']} ===")
    try:
        for name in want:
            log(f"--- check {name} ---")
            try:
                results[name] = CHECKS[name]()
            except Exception as exc:  # noqa: BLE001
                results[name] = {"EXCEPTION": f"{type(exc).__name__}: {exc}"}
                log(f"!!! {name} raised {type(exc).__name__}: {exc}")
            OUT_JSON.write_text(json.dumps(results, indent=1, default=str) + "\n")
    finally:
        cur = metadata_default()
        if cur["name"] != HOST_DEFAULT_SINK:
            restore_host_default(meta0["raw"])
            log(f"RESTORED metadata {cur['name']} -> {HOST_DEFAULT_SINK}")
        log("=== raw-checks end ===")
        logf.close()


if __name__ == "__main__":
    main()
