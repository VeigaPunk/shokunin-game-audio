#!/usr/bin/env python3
"""R77 scout — FRONTIER 1: source-selection lattice.

Enumerate the live record surface, then attempt a bounded capture on EACH
named source per consumer. Classify every cell as
  real_audio | silent_empty | hard_fail | blocked | rc0_silent
so "which names work" is a measured cell, never an inference.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r77_probe import (CAP_BYTES, LINE, MIC, M_SPDIF, M_SPK, S_SPDIF,
                       errclass, emit, inspect, leg_file, leg_stdout, mk,
                       norm_err, out_kind, sh, wav_header)   # noqa: E402

TMP = mk()
N = "4800"


def cell(leg, kind=None):
    """Reduce a leg to the lattice verdict."""
    if leg.get("timed_out") or leg.get("rc") is None:
        return "blocked_timeout"
    b = leg.get("bytes") or 0
    da = leg.get("data_actual")
    if leg["out_kind"] == "missing" and b is None:
        return "no_file"
    if b == 0:
        return "empty_file"
    if leg["out_kind"] == "riff_wav_empty" or da == 0:
        return "silent_empty"            # header, zero audio frames
    if leg["out_kind"] == "raw_stream" and b > 0:
        return "raw_bytes"
    if da and da > 0:
        return "real_audio"
    return f"other:{leg['out_kind']}"


def pulse_names():
    return [
        ("LINE_literal", LINE),
        ("MIC_literal", MIC),
        ("MONITOR_defaultsink", M_SPDIF),
        ("MONITOR_speaker", M_SPK),
        ("SINK_not_monitor", S_SPDIF),
        ("DEFAULT_SOURCE_at", "@DEFAULT_SOURCE@"),
        ("DEFAULT_MONITOR_at", "@DEFAULT_MONITOR@"),
        ("default_word", "default"),
        ("pulse_word", "pulse"),
        ("zero_serial", "0"),
    ]


def main():
    out = {"probe": "source-lattice-r77", "tmp": TMP, "cells": {}}

    # ---- enumeration snapshot -------------------------------------------
    rc, so, se, _w, _t = sh(["pactl", "list", "sources", "short"])
    out["pactl_sources_short"] = so.decode(errors="replace").splitlines()
    rc, so, se, _w, _t = sh(["pactl", "info"])
    out["pactl_info"] = [ln for ln in so.decode(errors="replace").splitlines()
                         if ln.startswith(("Default ", "Server Name"))]
    rc, so, se, _w, _t = sh(["arecord", "-L"])
    out["arecord_L"] = [ln for ln in so.decode(errors="replace").splitlines()
                        if not ln.startswith(" ")][:20]

    for label, name in pulse_names():
        # 1. pw-record direct
        p = os.path.join(TMP, f"pwr_{label}.wav")
        leg = leg_file(f"pwrecord:{label}",
                       ["pw-record", "--target", name, "-n", N, p], p)
        out["cells"][f"pwrecord_direct|{label}"] = {
            "verdict": cell(leg), "name": name, **leg}
        # 2. pw-record with capture-sink prop
        p = os.path.join(TMP, f"pwrm_{label}.wav")
        leg = leg_file(f"pwrecord_mon:{label}",
                       ["pw-record", "-P", "stream.capture.sink=true",
                        "--target", name, "-n", N, p], p)
        out["cells"][f"pwrecord_monprop|{label}"] = {
            "verdict": cell(leg), "name": name, **leg}
        # 3. parec wav (stdout, TERM-bounded)
        p = os.path.join(TMP, f"parec_{label}.wav")
        leg = leg_stdout(f"parec:{label}",
                         ["parec", "-d", name, "--file-format=wav"],
                         p, timeout=6.0, term_after=1.2, kill_after=4.0)
        out["cells"][f"parec_wav|{label}"] = {
            "verdict": cell(leg), "name": name, **leg}
        # 4. parec raw (stdout, capped)
        p = os.path.join(TMP, f"parecr_{label}.raw")
        leg = leg_stdout(f"parec_raw:{label}",
                         ["parec", "-d", name, "--raw"],
                         p, timeout=6.0, term_after=1.2, kill_after=4.0)
        out["cells"][f"parec_raw|{label}"] = {
            "verdict": cell(leg), "name": name, **leg}
        # 5. ffmpeg -f pulse
        p = os.path.join(TMP, f"ffp_{label}.wav")
        leg = leg_file(f"ffmpeg_pulse:{label}",
                       ["ffmpeg", "-nostdin", "-nostats", "-v", "error",
                        "-f", "pulse", "-i", name, "-t", "0.6", "-y", p], p)
        out["cells"][f"ffmpeg_pulse|{label}"] = {
            "verdict": cell(leg), "name": name, **leg}
        # 6. ffmpeg -f alsa
        p = os.path.join(TMP, f"ffa_{label}.wav")
        leg = leg_file(f"ffmpeg_alsa:{label}",
                       ["ffmpeg", "-nostdin", "-nostats", "-v", "error",
                        "-f", "alsa", "-i", name, "-t", "0.6", "-y", p], p)
        out["cells"][f"ffmpeg_alsa|{label}"] = {
            "verdict": cell(leg), "name": name, **leg}

    # ---- arecord device axis (ALSA namespace, not pulse) ----------------
    for label, dev in [("default", "default"), ("pipewire", "pipewire"),
                       ("sysdefault", "sysdefault"), ("hw00", "hw:0,0"),
                       ("plughw00", "plughw:0,0"), ("null", "null"),
                       ("pulse_plugin", "pulse"),
                       ("LINE_as_dev", LINE),
                       ("MON_as_dev", M_SPDIF)]:
        p = os.path.join(TMP, f"arec_{label}.wav")
        leg = leg_file(f"arecord:{label}",
                       ["arecord", "-D", dev, "-d", "1", "-f", "cd", p], p)
        out["cells"][f"arecord_dev|{label}"] = {
            "verdict": cell(leg), "device": dev, **leg}

    emit(out, "probe-source-lattice-r77.json")
    print(out["probe"])


if __name__ == "__main__":
    main()
