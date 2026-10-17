#!/usr/bin/env python3
"""R77 scout — FRONTIER 1f (final): the exact `stream.capture.sink` lattice,
anchored on the tone, plus a clean raw-integrity and concurrency re-run.

The tone anchor makes "which node did this capture actually consume"
decidable without relying on byte counts (this host's Line/Mic sources are
digital silence, so byte identity alone is NOT evidence).

Play the tone into the DEFAULT sink (SPDIF). A capture that carries the tone
consumed the default sink's monitor; a capture that is silent consumed some
other node.
"""
import json
import math
import os
import signal
import struct
import subprocess
import sys
import time
import wave

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r77_probe import (CAP_BYTES, LINE, M_SPDIF, S_SPDIF, emit, mk,  # noqa
                       sh, sh_capped)

TMP = mk()
SPK = "alsa_output.usb-Generic_USB_Audio-00.HiFi__Speaker__sink"
HDMI = "alsa_output.pci-0000_01_00.1.hdmi-stereo"
TONE = os.path.join(TMP, "tone.wav")
N = "96000"


def make_tone():
    fr = bytearray()
    for i in range(96000):
        v = int(16384 * math.sin(2 * math.pi * 1000 * i / 48000))
        fr += struct.pack("<hh", v, v)
    with wave.open(TONE, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(48000)
        w.writeframes(bytes(fr))


def peak(d):
    return max(abs(v) for v in struct.unpack("<%dh" % (len(d) // 2),
                                             d[:len(d) // 2 * 2])) \
        if len(d) >= 4 else None


def tone_leg(label, cap_argv, cap_path):
    """Play the tone into the default sink, capture, report the tone anchor."""
    pl = subprocess.Popen(["pw-cat", "-p", TONE, "--target", S_SPDIF],
                          stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    time.sleep(0.25)
    cp = subprocess.Popen(cap_argv + [cap_path], stdout=subprocess.DEVNULL,
                          stderr=subprocess.PIPE)
    try:
        pl.wait(timeout=8)
    except subprocess.TimeoutExpired:
        pl.kill()
        pl.wait(timeout=4)
    time.sleep(0.3)
    if cp.poll() is None:
        cp.send_signal(signal.SIGTERM)
        try:
            cp.wait(timeout=8)
        except subprocess.TimeoutExpired:
            cp.kill()
            cp.wait(timeout=8)
    cp.stderr.read()
    cp.stderr.close()
    pl.stderr.close()
    d = open(cap_path, "rb").read() if os.path.exists(cap_path) else b""
    pay = d[44:] if d[:4] == b"RIFF" else d
    time.sleep(0.4)
    return {"leg": label, "cap_argv": cap_argv, "cap_rc": cp.returncode,
            "file_bytes": len(d), "payload": len(pay),
            "nonzero_frac": round(sum(1 for b in pay if b) / len(pay), 4)
            if pay else None,
            "peak": peak(pay),
            "consumed_default_sink_monitor": bool(peak(pay) and
                                                  peak(pay) > 500)}


def main():
    out = {"probe": "capture-sink-lattice-r77", "tmp": TMP, "lattice": {},
           "raw": {}, "concurrent": {}}
    make_tone()
    _rc, so, _se, _w, _t = sh(["pactl", "get-default-sink"])
    out["default_sink"] = so.decode().strip()

    # ---- the lattice: tone plays into the DEFAULT sink -----------------
    prop = ["-P", "stream.capture.sink=true"]
    cases = [
        ("prop|SPDIF_sink (default)", prop + ["--target", S_SPDIF]),
        ("prop|SPEAKER_sink", prop + ["--target", SPK]),
        ("prop|HDMI_sink", prop + ["--target", HDMI]),
        ("prop|SPDIF_sink.monitor", prop + ["--target", M_SPDIF]),
        ("prop|LINE_source", prop + ["--target", LINE]),
        ("prop|@DEFAULT_SOURCE@", prop + ["--target", "@DEFAULT_SOURCE@"]),
        ("prop|@DEFAULT_MONITOR@", prop + ["--target", "@DEFAULT_MONITOR@"]),
        ("prop|default", prop + ["--target", "default"]),
        ("prop|pulse", prop + ["--target", "pulse"]),
        ("prop|GARBAGE", prop + ["--target", "no_such_node_xyz"]),
        ("prop|NO_TARGET (auto)", prop),
        ("noprop|LINE_source", ["--target", LINE]),
        ("noprop|SPDIF_sink", ["--target", S_SPDIF]),
        ("noprop|SPDIF_sink.monitor", ["--target", M_SPDIF]),
        ("noprop|NO_TARGET (auto)", []),
    ]
    for label, extra in cases:
        p = os.path.join(TMP, f"l{abs(hash(label)) % 10**7}.wav")
        if os.path.exists(p):
            os.unlink(p)
        out["lattice"][label] = tone_leg(label, ["pw-record"] + extra +
                                         ["-n", N], p)

    # ---- F5 raw integrity, correct stdout forms ------------------------
    raw_cases = [
        ("parec --raw (pipe) TERM", ["parec", "-d", LINE, "--raw"], "TERM"),
        ("parec --raw (pipe) KILL", ["parec", "-d", LINE, "--raw"], "KILL"),
        ("pw-cat -r - (stdout) TERM", ["pw-cat", "-r", "-"], "TERM"),
        ("pw-cat -r - (stdout) KILL", ["pw-cat", "-r", "-"], "KILL"),
        ("pw-cat -r --raw - (stdout) TERM",
         ["pw-cat", "-r", "--raw", "-"], "TERM"),
        ("pw-cat -r --raw - (stdout) KILL",
         ["pw-cat", "-r", "--raw", "-"], "KILL"),
    ]
    for label, argv, sig in raw_cases:
        rc, n, se, wall, cap_hit, sigsent, raw = sh_capped(
            argv, cap=CAP_BYTES, timeout=8.0,
            kill_after=1.2 if sig == "KILL" else None,
            term_after=1.2 if sig == "TERM" else None)
        out["raw"][label] = {"rc": rc, "signal": sigsent, "nbytes": n,
                             "cap_hit": cap_hit,
                             "all_zero": raw.count(0) == len(raw)
                             if raw else None,
                             "err": se.strip().splitlines()[-1][:120]
                             if se.strip() else ""}
    # exact-count raw to a FILE (the only deterministic raw witness)
    for extra, exp in ((["--raw"], 48000 * 4), ([], 48000 * 4 + 44)):
        p = os.path.join(TMP, f"exact{len(extra)}.out")
        r = subprocess.run(["pw-record", "--target", LINE, "-n", "48000"] +
                           extra + [p], capture_output=True, timeout=20)
        out["raw"][f"pw-record -n 48000 {extra or '(container)'}"] = {
            "rc": r.returncode,
            "bytes": os.path.getsize(p) if os.path.exists(p) else None,
            "expected": exp,
            "err": r.stderr.decode(errors="replace").strip()
            .splitlines()[-1][:110] if r.stderr.strip() else ""}

    # ---- F6 concurrency, serialized, tone-anchored ---------------------
    def conc(label, cap_argv, cap_path, extra_play=None):
        pl = subprocess.Popen(["pw-cat", "-p", TONE, "--target", S_SPDIF],
                              stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        time.sleep(0.2)
        cp = subprocess.Popen(cap_argv + [cap_path],
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.PIPE)
        cp2 = None
        if extra_play:
            time.sleep(0.2)
            cp2 = subprocess.Popen(extra_play, stdout=subprocess.DEVNULL,
                                   stderr=subprocess.PIPE)
        try:
            pl.wait(timeout=8)
        except subprocess.TimeoutExpired:
            pl.kill()
        time.sleep(0.3)
        for pr in (cp, cp2):
            if pr and pr.poll() is None:
                pr.send_signal(signal.SIGTERM)
                try:
                    pr.wait(timeout=8)
                except subprocess.TimeoutExpired:
                    pr.kill()
                    pr.wait(timeout=8)
            if pr:
                pr.stderr.read()
                pr.stderr.close()
        pl.stderr.close()
        d = open(cap_path, "rb").read() if os.path.exists(cap_path) else b""
        pay = d[44:] if d[:4] == b"RIFF" else d
        time.sleep(0.4)
        return {"leg": label, "cap_argv": cap_argv, "second_rc":
                cp2.returncode if cp2 else None, "cap_rc": cp.returncode,
                "payload": len(pay), "peak": peak(pay),
                "carries_tone": bool(peak(pay) and peak(pay) > 500)}

    out["concurrent"]["play_tone + cap monitor (paired)"] = conc(
        "play_tone + cap monitor (paired)",
        ["pw-record", "-P", "stream.capture.sink=true", "--target", S_SPDIF,
         "-n", N], os.path.join(TMP, "c1.wav"))
    out["concurrent"]["play_tone + TWO concurrent monitor captures"] = conc(
        "play_tone + TWO concurrent monitor captures",
        ["pw-record", "-P", "stream.capture.sink=true", "--target", S_SPDIF,
         "-n", N], os.path.join(TMP, "c2.wav"),
        extra_play=["pw-record", "-P", "stream.capture.sink=true", "--target",
                    S_SPDIF, "-n", N, os.path.join(TMP, "c2b.wav")])
    out["concurrent"]["play_tone + parec monitor"] = conc(
        "play_tone + parec monitor",
        ["parec", "-d", M_SPDIF, "--raw"], os.path.join(TMP, "c3.raw"))
    out["concurrent"]["play_tone + ffmpeg monitor"] = conc(
        "play_tone + ffmpeg monitor",
        ["ffmpeg", "-nostdin", "-nostats", "-v", "error", "-f", "pulse",
         "-i", M_SPDIF, "-t", "2", "-y", os.path.join(TMP, "c4.wav")],
        os.path.join(TMP, "c4.wav"))
    # silence baseline: no playback at all
    p = os.path.join(TMP, "c0.wav")
    r = subprocess.run(["pw-record", "-P", "stream.capture.sink=true",
                        "--target", S_SPDIF, "-n", N, p],
                       capture_output=True, timeout=25)
    d = open(p, "rb").read() if os.path.exists(p) else b""
    out["concurrent"]["BASELINE no playback"] = {
        "rc": r.returncode, "payload": len(d) - 44 if d else 0,
        "peak": peak(d[44:]) if d else None}

    emit(out, "probe-capture-sink-lattice-r77.json")
    print(out["probe"])


if __name__ == "__main__":
    main()
