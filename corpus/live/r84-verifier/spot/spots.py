#!/usr/bin/env python3
"""r84 verifier — independent spot re-derivations (own r84v_* namespace).

Every spot re-executes a pinned argv/protocol shape from the r84 author
report with the verifier's OWN sink names and its OWN protocol code (no
fixture import), and records the measured value next to the pin.

Usage: spots.py [s1 s2 ... | all]
Writes spot/spots.jsonl (one record per spot, appended).
Never touches foreign sinks; never set-default-*; unloads own modules by
name-verified index; kills its own process groups only.
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

import numpy as np

PID = os.getpid()
NS = f"r84v_ns_{PID}"
NS2 = f"r84v_ns2_{PID}"
ROLE = f"r84vrole{PID}"
TMPROOT = Path(os.environ.get("TMPDIR", "/tmp"))
TMP = TMPROOT / f"r84v-spot-{PID}"
TMP.mkdir(parents=True, exist_ok=True)
TONE = TMP / "tone.wav"
TONE_B = TMP / "toneb.wav"
AMP = 8192
OUT = Path(__file__).resolve().parent / "spots.jsonl"
LOGS = []


def log(msg):
    LOGS.append(msg)
    print(msg, flush=True)


def write_tone(path, seconds=12.0, hz=1000.0, amp=AMP):
    n = int(48000 * seconds)
    t = np.arange(n) / 48000
    ch = (amp * np.sin(2 * np.pi * hz * t)).astype("<i2")
    pcm = np.empty(n * 2, dtype="<i2")
    pcm[0::2], pcm[1::2] = ch, ch
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(48000)
        w.writeframes(pcm.tobytes())


def run(argv, timeout=15.0, env=None):
    t0 = time.monotonic()
    try:
        p = subprocess.run(argv, capture_output=True, timeout=timeout,
                           env=env)
        return {"argv": " ".join(str(a) for a in argv),
                "rc": p.returncode, "signal": None,
                "out": p.stdout.decode(errors="replace"),
                "err": p.stderr.decode(errors="replace"),
                "wall_s": round(time.monotonic() - t0, 3)}
    except subprocess.TimeoutExpired:
        return {"argv": " ".join(str(a) for a in argv), "rc": None,
                "signal": "timeout", "out": "", "err": "",
                "wall_s": round(time.monotonic() - t0, 3)}


def pactl(*args, timeout=10.0):
    return run(["pactl", *[str(a) for a in args]], timeout)


def pactl_json(what):
    try:
        p = subprocess.run(["pactl", "-f", "json", "list", what],
                           capture_output=True, timeout=10)
        return json.loads(p.stdout or b"[]")
    except Exception:
        return []


def leaf_by_tag(tag, what="sink-inputs"):
    for leaf in pactl_json(what):
        pr = leaf.get("properties") or {}
        if pr.get("node.name") == tag or pr.get("application.name") == tag:
            return {"index": leaf.get("index"), "sink": leaf.get("sink"),
                    "source": leaf.get("source"),
                    "corked": leaf.get("corked"), "mute": leaf.get("mute"),
                    "volume": leaf.get("volume"), "properties": pr}
    return None


def leaf_by_pid(pid, what="source-outputs"):
    for leaf in pactl_json(what):
        pr = leaf.get("properties") or {}
        if str(pr.get("application.process.id")) == str(pid):
            return {"index": leaf.get("index"), "sink": leaf.get("sink"),
                    "source": leaf.get("source"),
                    "corked": leaf.get("corked"), "mute": leaf.get("mute"),
                    "volume": leaf.get("volume"), "properties": pr}
    return None


def sink_index(name):
    for leaf in pactl_json("sinks"):
        if leaf.get("name") == name:
            return leaf.get("index")
    return None


def wait_attached(tag, timeout=8.0):
    t0 = time.monotonic()
    leaf = None
    while time.monotonic() - t0 < timeout:
        leaf = leaf_by_tag(tag)
        if leaf is not None and leaf.get("sink") not in (None, 4294967295):
            return leaf, round(time.monotonic() - t0, 3)
        time.sleep(0.12)
    return leaf, round(time.monotonic() - t0, 3)


def si_percent(leaf):
    try:
        return int(str((leaf.get("volume") or {}).get("front-left", {})
                       .get("value_percent") or "").rstrip("%"))
    except ValueError:
        return None


def spawn(argv, env=None):
    return subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            stdin=subprocess.DEVNULL,
                            start_new_session=True, env=env)


def killpg(proc, sig=signal.SIGKILL):
    if proc is None:
        return
    try:
        os.killpg(proc.pid, sig)
    except ProcessLookupError:
        pass
    try:
        proc.wait(timeout=5.0)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        proc.wait()


def series(path, win_s=0.1):
    """[(t, peak)] per 0.1 s window of a s16 stereo wav."""
    try:
        with wave.open(str(path), "rb") as w:
            nch, sw, rate = w.getnchannels(), w.getsampwidth(), w.getframerate()
            raw = w.readframes(w.getnframes())
    except (wave.Error, EOFError, FileNotFoundError):
        return []
    if sw != 2 or nch != 2:
        return []
    pcm = np.frombuffer(raw, dtype="<i2").reshape(-1, 2)
    n = int(rate * win_s)
    return [(round(i / rate, 2),
             int(np.abs(pcm[i:i + n].astype(np.int32)).max()))
            for i in range(0, len(pcm) - n + 1, n)]


def med(ser, lo, hi):
    vals = [a for t, a in ser if lo <= t <= hi]
    return float(np.median(vals)) if vals else None


def play_tag(tag, target, tone, role=ROLE):
    return spawn(["pw-play", "-P", f"node.name={tag}",
                  "-P", f"application.name={tag}",
                  "-P", f"media.role={role}",
                  "--target", target, str(tone)])


def tap(ns, path, frames, tag):
    return spawn(["pw-record", "-P", "stream.capture.sink=true",
                  "-P", f"node.name={tag}", "--target", ns,
                  "-n", str(frames), "--rate", "48000", "--channels", "2",
                  "--format", "s16", str(path)])


def load_null(name):
    r = pactl("load-module", "module-null-sink", f"sink_name={name}",
              "rate=48000", "channels=2")
    if r["rc"] != 0:
        return None, r
    idx = r["out"].strip()
    if sink_index(name) is None:
        return None, {"load": r, "verify": "sink not enumerated"}
    return idx, r


def unload(idx, name):
    pre = sink_index(name)
    r = pactl("unload-module", idx)
    time.sleep(0.3)
    return {"module": idx, "name_at_unload": name if pre is not None else None,
            "rc": r["rc"], "gone": sink_index(name) is None}


def pre_reset(ns):
    return {"sink_vol": pactl("set-sink-volume", ns, "100%")["rc"],
            "sink_mute": pactl("set-sink-mute", ns, "0")["rc"],
            "src_vol": pactl("set-source-volume", ns + ".monitor",
                             "100%")["rc"],
            "src_mute": pactl("set-source-mute", ns + ".monitor", "0")["rc"]}


def vol_leaf(ns):
    for leaf in pactl_json("sinks"):
        if leaf.get("name") == ns:
            return {"volume": leaf.get("volume"), "mute": leaf.get("mute")}
    return None


def gain_spot(name, write_fn, expect, *, idx_addr=False, dur=6.0):
    """Generic cubic-gain spot: reset, play, tap, base window, write at
    t=2.4, post window, kill. write_fn(ns, idx) -> pactl receipt."""
    rec = {"spot": name, "ns": NS, "pin": expect, "protocol": "tap 6.0s"}
    rec["pre_reset"] = pre_reset(NS)
    tag = f"{NS}_{name}"
    pa = play_tag(tag, NS, TONE)
    si, w = wait_attached(tag)
    rec["stream_wait_s"] = w
    if si is None or si.get("sink") in (None, 4294967295):
        killpg(pa)
        rec["skipped"] = "stream never routed"
        return rec
    rec["stream_index"] = si["index"]
    tapf = TMP / f"{name}_tap.wav"
    tp = tap(NS, tapf, int(48000 * (dur + 1.5)), f"{tag}_tap")
    time.sleep(2.4)
    rec["write"] = write_fn(NS, si["index"]) if idx_addr else write_fn(NS, None)
    time.sleep(1.6)
    killpg(tp, signal.SIGTERM)
    killpg(pa)
    ser = series(tapf)
    base = med(ser, 0.6, 2.2)
    post = med(ser, 3.2, 5.6)
    rec.update({"base_amp": base, "post_amp": post,
                "ratio": round(post / base, 6) if base else None,
                "series_head": ser[:26], "sink_vol_after": vol_leaf(NS)})
    return rec


# ---------------------------------------------------------------- spots

def s1():
    return gain_spot("s1_sinkvol50", lambda ns, i: pactl(
        "set-sink-volume", ns, "50%"), "x0.125 (8192->1024)")


def s2():
    return gain_spot("s2_sinkvol150", lambda ns, i: pactl(
        "set-sink-volume", ns, "150%"), "x3.375 (8192->27648)")


def s3():
    return gain_spot("s3_sinkvol25_idx", lambda ns, i: pactl(
        "set-sink-volume", sink_index(ns), "25%"),
        "x0.015625 (8192->128) — index-addressed",
        idx_addr=True)


def s4():
    return gain_spot("s4_srcvol50", lambda ns, i: pactl(
        "set-source-volume", ns + ".monitor", "50%"),
        "x0.125 via monitor source")


def s9():
    """per-leg pre-reset refinement: a leftover 25% sink makes the next
    leg's base window read 128 unless the leg pre-resets."""
    rec = {"spot": "s9_prereset_cascade",
           "pin": "leftover 25% -> base 128; after reset -> base 8192"}
    pactl("set-sink-volume", NS, "25%")
    rec["leftover_sink_vol"] = vol_leaf(NS)
    tag = f"{NS}_s9a"
    pa = play_tag(tag, NS, TONE)
    si, _ = wait_attached(tag)
    tapf = TMP / "s9a_tap.wav"
    tp = tap(NS, tapf, int(48000 * 3.0), f"{tag}_tap")
    time.sleep(2.0)
    killpg(tp, signal.SIGTERM)
    killpg(pa)
    ser = series(tapf)
    rec["cascade_base_amp"] = med(ser, 0.3, 2.0)
    rec["cascade_ratio_vs_8192"] = round(
        (rec["cascade_base_amp"] or 0) / 8192.0, 6)
    rec["reset"] = pre_reset(NS)
    tag = f"{NS}_s9b"
    pa = play_tag(tag, NS, TONE)
    si, _ = wait_attached(tag)
    tapf = TMP / "s9b_tap.wav"
    tp = tap(NS, tapf, int(48000 * 3.0), f"{tag}_tap")
    time.sleep(2.0)
    killpg(tp, signal.SIGTERM)
    killpg(pa)
    ser = series(tapf)
    rec["reset_base_amp"] = med(ser, 0.3, 2.0)
    return rec


def s5(sticky=True):
    """sticky restore: 30% write -> same-tag respawn 30% / tap ~221;
    different-tag respawn 100% (the name-scoped refinement); repair."""
    rec = {"spot": "s5_sticky30", "role": ROLE,
           "pin": "respawn 30% + tap med 150..340 (221=8192*0.3^3)"}
    pre_reset(NS)
    tag = f"{NS}_sticky"
    p1 = play_tag(tag, NS, TONE)
    si1, w1 = wait_attached(tag)
    rec["spawn1_wait_s"] = w1
    rec["spawn1_percent"] = si_percent(si1)
    if si1 is None or si1.get("sink") in (None, 4294967295):
        killpg(p1)
        rec["skipped"] = "s1 never routed"
        return rec
    time.sleep(0.3)
    rec["write30"] = pactl("set-sink-input-volume", si1["index"], "30%")["rc"]
    time.sleep(0.6)
    rec["after30_percent"] = si_percent(leaf_by_tag(tag))
    killpg(p1)
    time.sleep(0.5)
    tapf = TMP / "s5_tap.wav"
    tp = tap(NS, tapf, int(48000 * 4.5), f"{tag}_tap")
    p2 = play_tag(tag, NS, TONE)
    si2 = None
    t0 = time.monotonic()
    while time.monotonic() - t0 < 8.0:
        lf = leaf_by_tag(tag)
        if lf is not None and lf.get("index") != si1["index"] and \
                lf.get("sink") not in (None, 4294967295):
            si2 = lf
            break
        time.sleep(0.12)
    rec["respawn_percent"] = si_percent(si2)
    rec["respawn_wait_s"] = round(time.monotonic() - t0, 3)
    time.sleep(2.0)
    rec["repair"] = pactl("set-sink-input-volume",
                          (si2 or {}).get("index"), "100%")["rc"]
    time.sleep(0.6)
    killpg(tp, signal.SIGTERM)
    killpg(p2)
    ser = series(tapf)
    rec["respawn_tap_med"] = med(ser, 0.8, 3.2)
    rec["respawn_tap_series_tail"] = ser[-6:]
    # name-scoped refinement: different tag, same role -> expect 100%
    time.sleep(0.4)
    tag2 = f"{NS}_sticky_other"
    p3 = play_tag(tag2, NS, TONE)
    si3, w3 = wait_attached(tag2)
    rec["othertag_percent"] = si_percent(si3)
    rec["othertag_wait_s"] = w3
    killpg(p3)
    # repaired key verified on a fresh same-tag spawn
    time.sleep(0.4)
    p4 = play_tag(tag, NS, TONE)
    si4 = None
    t0 = time.monotonic()
    while time.monotonic() - t0 < 8.0:
        lf = leaf_by_tag(tag)
        if lf is not None and lf.get("index") not in (
                (si1 or {}).get("index"), (si2 or {}).get("index")) and \
                lf.get("sink") not in (None, 4294967295):
            si4 = lf
            break
        time.sleep(0.12)
    rec["repaired_percent"] = si_percent(si4)
    rec["repaired_mute"] = (si4 or {}).get("mute")
    killpg(p4)
    return rec


def s6():
    """parec --monitor-stream index refusals + source-output accept."""
    rec = {"spot": "s6_monitorstream_index",
           "pin": "0/999999 -> rc1 'Stream error: No such entity' + 44B; "
                  "source-output idx -> rc0 44B header-only"}
    pre_reset(NS)
    tag = f"{NS}_s6"
    pa = play_tag(tag, NS, TONE)
    si, _ = wait_attached(tag)
    rec["stream_index"] = (si or {}).get("index")
    outs = {}
    for key, idx in (("bad0", 0), ("dead", 999999)):
        f = TMP / f"s6_{key}.wav"
        r = run(["parec", "--latency-msec=50", "--rate=48000",
                 "--channels=2", "--format=s16le", "--file-format=wav",
                 "-d", NS, "--monitor-stream", str(idx), str(f)], timeout=12)
        outs[key] = {"rc": r["rc"], "err_tail": r["err"].strip().splitlines()[-2:],
                     "bytes": f.stat().st_size if f.exists() else None,
                     "data_bytes": _data_bytes(f)}
    # donor source-output: a second parec on the same sink's monitor
    donor_f = TMP / "s6_donor.wav"
    donor = spawn(["parec", "--latency-msec=50", "-d", NS + ".monitor",
                   "--rate", "48000", "--channels", "2", "--format", "s16le",
                   "--file-format=wav", str(donor_f)])
    so = None
    t0 = time.monotonic()
    while time.monotonic() - t0 < 8.0:
        so = leaf_by_pid(donor.pid, "source-outputs")
        if so is not None:
            break
        time.sleep(0.15)
    rec["donor_source_output"] = {"index": (so or {}).get("index"),
                                  "pid": donor.pid,
                                  "wait_s": round(time.monotonic() - t0, 3),
                                  "pid_attr_ok":
                                  str(((so or {}).get("properties") or {})
                                      .get("application.process.id"))
                                  == str(donor.pid)}
    f = TMP / "s6_soidx.wav"
    if so is not None:
        p = spawn(["parec", "--latency-msec=50", "--rate=48000",
                   "--channels=2", "--format=s16le", "--file-format=wav",
                   "-d", NS, "--monitor-stream", str(so["index"]), str(f)])
        time.sleep(4.0)
        alive_at_dur = p.poll() is None
        killpg(donor)          # end the pinned source-output
        t0 = time.monotonic()
        rc = None
        while time.monotonic() - t0 < 6.0:
            rc = p.poll()
            if rc is not None:
                break
            time.sleep(0.1)
        outs["soidx"] = {"alive_at_4s": alive_at_dur,
                         "rc_after_donor_end": rc,
                         "exit_wait_s": round(time.monotonic() - t0, 3),
                         "bytes": f.stat().st_size if f.exists() else None,
                         "data_bytes": _data_bytes(f)}
        killpg(p)
    else:
        killpg(donor)
    killpg(pa)
    rec["refusals"] = outs
    return rec


def _data_bytes(path):
    try:
        with wave.open(str(path), "rb") as w:
            return w.getnframes() * w.getnchannels() * w.getsampwidth()
    except Exception:
        return None


def s7():
    """routed-leaf gating: pre-route leaf has sink=0xFFFFFFFF and an
    all-zero volume block; a si-volume write fired pre-route does not
    show up on the routed leaf."""
    rec = {"spot": "s7_preroute_leaf",
           "pin": "pre-route sink=0xFFFFFFFF + zero volume; pre-route "
                  "write not registered"}
    pre_reset(NS2)
    tag = f"{NS2}_s7"
    pa = play_tag(tag, NS2, TONE)
    first, t_first = None, None
    t0 = time.monotonic()
    while time.monotonic() - t0 < 8.0:
        lf = leaf_by_tag(tag)
        if lf is not None:
            if first is None:
                first = lf
                t_first = round(time.monotonic() - t0, 3)
            if lf.get("sink") not in (None, 4294967295):
                rec["routed_leaf"] = {"sink": lf.get("sink"),
                                      "sink_is_ns2": lf.get("sink")
                                      == sink_index(NS2),
                                      "percent": si_percent(lf),
                                      "at_s": round(time.monotonic() - t0, 3)}
                break
        time.sleep(0.05)
    if first is not None:
        rec["preroute_leaf"] = {
            "sink": first.get("sink"),
            "sink_sentinel": first.get("sink") in (None, 4294967295),
            "volume_all_zero": all(
                (d or {}).get("value") in (0, None)
                for d in (first.get("volume") or {}).values()),
            "percent_read": si_percent(first),
            "at_s": t_first}
        # fire a write in the pre-route window and see if it sticks
        if first.get("sink") in (None, 4294967295) and first.get("index"):
            rec["preroute_write"] = pactl(
                "set-sink-input-volume", first["index"], "25%")["rc"]
            time.sleep(1.2)
            rec["after_route_percent"] = si_percent(leaf_by_tag(tag))
    killpg(pa)
    return rec


def s8():
    """donor must be a parec: pw-record --target <sink> and
    --target <sink>.monitor refuse; parec -d <sink>.monitor registers."""
    rec = {"spot": "s8_parec_only_donor",
           "pin": "pw-record refuses both targets; parec registers SO"}
    for key, tgt in (("sink", NS), ("monitor", NS + ".monitor")):
        f = TMP / f"s8_{key}.wav"
        r = run(["pw-record", "--target", tgt, "-n", "48000",
                 "--rate", "48000", "--channels", "2", "--format", "s16",
                 str(f)], timeout=12)
        rec[f"pwrecord_{key}"] = {
            "rc": r["rc"], "err_tail": r["err"].strip().splitlines()[-2:]}
    return rec


def s7b():
    """pre-route si-volume write vs the stream-restore key (author
    refinement 2's actual claim), with a post-route control."""
    rec = {"spot": "s7b_preroute_restore_key",
           "pin": "pre-route write not registered in the restore key; "
                  "post-route write registered"}
    for mode in ("preroute", "postroute"):
        pre_reset(NS2)
        tag = f"{NS2}_s7b_{mode}"
        p1 = play_tag(tag, NS2, TONE)
        first, wrote = None, None
        t0 = time.monotonic()
        while time.monotonic() - t0 < 8.0:
            lf = leaf_by_tag(tag)
            if lf is not None:
                if first is None:
                    first = lf
                unrouted = lf.get("sink") in (None, 4294967295)
                if mode == "preroute" and unrouted and wrote is None:
                    wrote = pactl("set-sink-input-volume", lf["index"],
                                  "25%")["rc"]
                if not unrouted:
                    rec[f"{mode}_routed_percent"] = si_percent(lf)
                    break
            time.sleep(0.05)
        if mode == "postroute" and first is not None:
            lf = leaf_by_tag(tag)
            if lf:
                wrote = pactl("set-sink-input-volume", lf["index"],
                              "25%")["rc"]
        rec[f"{mode}_write_rc"] = wrote
        rec[f"{mode}_preroute_sentinel"] = bool(
            first and first.get("sink") in (None, 4294967295))
        killpg(p1)
        time.sleep(0.8)
        p2 = play_tag(tag, NS2, TONE)
        si2, _ = wait_attached(tag)
        rec[f"{mode}_respawn_percent"] = si_percent(si2)
        killpg(p2)
        time.sleep(0.3)
    return rec


def s13():
    """pw_server isolation measurement: aplay -D pipewire:SERVER=bogus
    (run1 saw an 8 s hang/kill instead of 'Host is down')."""
    rec = {"spot": "s13_pw_server_isolation",
           "pin": "rc=1 'audio open error: Host is down', wall ~0.00 s"}
    for key, srv in (("bogus", "no_such_r84v"), ("bogus2", "no_such_r84v2")):
        r = run(["aplay", "-D", f"pipewire:SERVER={srv}", str(TONE)],
                timeout=14)
        rec[key] = {"rc": r["rc"], "signal": r["signal"],
                    "wall_s": r["wall_s"],
                    "stderr": r["err"].strip()[:200]}
    return rec


def s10():
    """-D '' argv-eating: real empty element -> 'Unknown PCM ' (empty);
    absent element (getopt eats -d) -> 'Unknown PCM -d'."""
    rec = {"spot": "s10_argv_eating",
           "pin": "empty element -> 'Unknown PCM '; absent -> '-d'"}
    r = run(["aplay", "-D", "", str(TONE)], timeout=10)
    rec["aplay_D_empty"] = {"rc": r["rc"], "err": r["err"].strip()[:400]}
    r = run(["aplay", "-D", "-d", "1", str(TONE)], timeout=10)
    rec["aplay_D_dashd"] = {"rc": r["rc"], "err": r["err"].strip()[:400]}
    r = run(["arecord", "-D", "", "-d", "1", "-f", "cd",
             str(TMP / "s10_empty.wav")], timeout=10)
    rec["arecord_D_empty"] = {"rc": r["rc"], "err": r["err"].strip()[:400]}
    return rec


def s11():
    """ONE capture-refusal class + NODE=<source> revival."""
    rec = {"spot": "s11_capture_refusal",
           "pin": "bare pipewire/default -> one class (Unable to install "
                  "hw params + TICK_TIME: [0 0]); NODE=<source> revives"}
    for key, dev in (("bare", "pipewire"), ("default", "default")):
        f = TMP / f"s11_{key}.wav"
        r = run(["arecord", "-D", dev, "-d", "1", "-f", "cd", str(f)],
                timeout=12)
        rec[f"cap_{key}"] = {
            "rc": r["rc"], "exists": f.exists(),
            "bytes": f.stat().st_size if f.exists() else None,
            "has_hw_params": "Unable to install hw params:" in r["err"],
            "has_tick": "TICK_TIME: [0 0]" in r["err"]}
    f = TMP / "s11_node.wav"
    r = run(["arecord", "-D", f"pipewire:NODE={NS}.monitor", "-d", "2",
             "-f", "cd", str(f)], timeout=15)
    rec["cap_node_revive"] = {"rc": r["rc"], "exists": f.exists(),
                              "bytes": f.stat().st_size if f.exists() else None,
                              "err_tail": r["err"].strip().splitlines()[-2:]}
    return rec


def s12():
    """PERIOD_BYTES=4096 -> node.latency 1024/48000; NODE= miss silent
    fallback to the default sink; RATE=44100 warning."""
    rec = {"spot": "s12_period_fallback",
           "pin": "PERIOD_BYTES 4096 -> node.latency 1024/48000; NODE=miss "
                  "-> default sink; RATE=44100 warns"}
    default = run(["pactl", "get-default-sink"])["out"].strip()
    p = spawn(["aplay", "-D", "pipewire:PERIOD_BYTES=4096", str(TONE)])
    lat = None
    t0 = time.monotonic()
    while time.monotonic() - t0 < 6.0:
        dump = run(["pw-dump"], timeout=20)["out"]
        try:
            nodes = json.loads(dump)
        except ValueError:
            nodes = []
        for n in nodes:
            pr = (n.get("info") or {}).get("props") or {}
            if pr.get("node.name") == "alsa_playback.aplay" or \
                    pr.get("application.name", "").startswith(
                        "PipeWire ALSA"):
                lat = pr.get("node.latency")
        if lat:
            break
        time.sleep(0.2)
    rec["period_latency"] = lat
    killpg(p)
    p = spawn(["aplay", "-D", "pipewire:NODE=no_such_r84v", str(TONE)])
    landed = None
    t0 = time.monotonic()
    while time.monotonic() - t0 < 6.0:
        for leaf in pactl_json("sink-inputs"):
            pr = leaf.get("properties") or {}
            if pr.get("application.name", "").startswith("PipeWire ALSA") or \
                    pr.get("node.name") == "alsa_playback.aplay":
                landed = {"sink": leaf.get("sink"),
                          "default_index": sink_index(default),
                          "landed_on_default": leaf.get("sink")
                          == sink_index(default)}
        if landed:
            break
        time.sleep(0.2)
    rec["node_miss_fallback"] = landed
    killpg(p)
    f = TMP / "s12_rate.wav"
    r = run(["arecord", "-D", "pipewire:RATE=44100", "-d", "1", "-f", "cd",
             str(f)], timeout=12)
    rec["rate44"] = {"rc": r["rc"],
                     "warn": "rate is not accurate" in r["err"],
                     "err_tail": r["err"].strip().splitlines()[-2:]}
    return rec


def s11b():
    """capture revival: NODE=<hardware source> revives; NODE=<sink>.monitor
    refuses with the SAME single class (the one-sided law)."""
    rec = {"spot": "s11b_capture_node_arms",
           "pin": "hw-source NODE= revives rc0 real wav; monitor NODE= "
                  "refuses in the same single class"}
    line = "alsa_input.usb-Generic_USB_Audio-00.HiFi__Line__source.29"
    f = TMP / "s11b_hw.wav"
    r = run(["arecord", "-D", f"pipewire:NODE={line}", "-d", "2", "-f",
             "cd", str(f)], timeout=15)
    rec["hw_source_node"] = {"rc": r["rc"], "exists": f.exists(),
                             "bytes": f.stat().st_size if f.exists() else None,
                             "has_hw_params":
                             "Unable to install hw params:" in r["err"],
                             "err_tail": r["err"].strip().splitlines()[-2:]}
    f2 = TMP / "s11b_mon.wav"
    r2 = run(["arecord", "-D", f"pipewire:NODE={NS}.monitor", "-d", "2",
              "-f", "cd", str(f2)], timeout=15)
    rec["monitor_node"] = {"rc": r2["rc"], "exists": f2.exists(),
                           "has_hw_params":
                           "Unable to install hw params:" in r2["err"],
                           "has_tick": "TICK_TIME: [0 0]" in r2["err"]}
    return rec


def s12b():
    """RATE=44100 on playback: rc=0 + the 'rate is not accurate' warning.
    (first attempt used the 14 s spot tone and was killed at the 15 s
    bound while still playing — protocol artifact, not a hang)."""
    rec = {"spot": "s12b_rate_warning",
           "pin": "aplay -D pipewire:NODE=<ns>,RATE=44100 -> rc0 + warning"}
    short = TMP / "tone_short.wav"
    write_tone(short, 1.4)
    r = run(["aplay", "-D", f"pipewire:NODE={NS},RATE=44100", str(short)],
            timeout=20)
    rec["rate44_playback"] = {
        "rc": r["rc"], "warn": "rate is not accurate" in r["err"],
        "err_tail": r["err"].strip().splitlines()[-3:]}
    rec["control_plain"] = {
        "rc": run(["aplay", "-D", "pipewire", str(short)],
                  timeout=20)["rc"]}
    return rec


def s14():
    """boundary correction: arecord -D null is NOT zeros (period-locked
    nonzero bursts); the arm asserts nonzero CONTENT only."""
    rec = {"spot": "s14_null_capture_content",
           "pin": "nonzero content (bursts), not the falsified 5512 spacing"}
    f = TMP / "s14_null.wav"
    r = run(["arecord", "-D", "null", "-d", "1", "-f", "cd", str(f)],
            timeout=12)
    rec["rc"] = r["rc"]
    if f.exists():
        ser = series(f)
        try:
            with wave.open(str(f), "rb") as w:
                nch, sw, rate, nfr = (w.getnchannels(), w.getsampwidth(),
                                      w.getframerate(), w.getnframes())
                raw = w.readframes(nfr)
            pcm = np.frombuffer(raw, dtype="<i2").reshape(-1, 2)
            nz = np.any(pcm != 0, axis=1)
            idx = np.flatnonzero(nz)
            starts = (idx[np.r_[True, np.diff(idx) > 1]] if len(idx)
                      else np.array([], dtype=np.int64))
            rec.update({"rate": rate, "frames": int(nfr),
                        "nz_rows": int(nz.sum()),
                        "bursts": int(len(starts)),
                        "first_starts": [int(s) for s in starts[:8]],
                        "peak": int(np.abs(pcm.astype(np.int32)).max())})
        except Exception as exc:
            rec["wav_error"] = f"{type(exc).__name__}: {exc}"
    return rec


SPOTS = {"s1": s1, "s2": s2, "s3": s3, "s4": s4, "s5": s5, "s6": s6,
         "s7": s7, "s7b": s7b, "s8": s8, "s9": s9, "s10": s10,
         "s11": s11, "s11b": s11b, "s12": s12, "s12b": s12b, "s13": s13,
         "s14": s14}


def main():
    which = sys.argv[1:] or ["all"]
    if which == ["all"]:
        which = list(SPOTS)
    write_tone(TONE, 14.0)
    write_tone(TONE_B, 14.0, hz=2700.0)
    ns_idx, r = load_null(NS)
    ns2_idx, r2 = load_null(NS2)
    meta = {"spot": "setup", "pid": PID, "ns": NS, "ns2": NS2,
            "role": ROLE, "ns_module": ns_idx, "ns2_module": ns2_idx,
            "load_rc": [r["rc"], r2["rc"]], "tmp": str(TMP),
            "default_sink": run(["pactl", "get-default-sink"])["out"].strip(),
            "default_source": run(["pactl", "get-default-source"])["out"].strip()}
    with OUT.open("a") as fh:
        fh.write(json.dumps(meta) + "\n")
    log(f"setup: {meta}")
    try:
        for key in which:
            fn = SPOTS.get(key)
            if fn is None:
                log(f"unknown spot {key}")
                continue
            t0 = time.monotonic()
            try:
                rec = fn()
            except Exception as exc:
                rec = {"spot": key, "error": f"{type(exc).__name__}: {exc}"}
            rec["wall_s"] = round(time.monotonic() - t0, 3)
            with OUT.open("a") as fh:
                fh.write(json.dumps(rec) + "\n")
            log(f"{key}: {json.dumps(rec)[:600]}")
    finally:
        teardown = {"spot": "teardown",
                    "unload_ns": unload(ns_idx, NS) if ns_idx else None,
                    "unload_ns2": unload(ns2_idx, NS2) if ns2_idx else None}
        with OUT.open("a") as fh:
            fh.write(json.dumps(teardown) + "\n")
        log(f"teardown: {teardown}")


if __name__ == "__main__":
    main()
