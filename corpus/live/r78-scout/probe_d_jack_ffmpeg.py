#!/usr/bin/env python3
"""Probe D — JACK-ish surface without jackd + ffmpeg input-device parity.

Questions:
 1. Does `pw-jack` let a JACK client capture on this host (no jackd)? Which
    ports does the client get, and can jack-style target naming bind to a
    PipeWire node (r78_ns monitor)?
 2. ffmpeg input-device lattice: -f pulse / -f alsa (incl. `pipewire` PCM) /
    -f oss / -f jack, with and without the shim — parity and named classes.
"""
import json
import os
import signal
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r78_probe import (SEAT, SCRATCH, M_NS, NS, LINE, sh, load_ns, unload_ns,
                       gen_tone, inspect, audio_stats, payload_sha, out_kind,
                       errclass, norm_err, pwlink_map, mk, emit, du)


def ff_leg(name, argv, path, timeout=10, env=None, during=None):
    if os.path.exists(path):
        os.unlink(path)
    t0 = time.monotonic()
    p = subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                         stderr=subprocess.PIPE, env=env)
    time.sleep(0.9)
    dres = during() if during else None
    prc = p.poll()
    while prc is None and time.monotonic() - t0 < timeout:
        prc = p.poll()
        time.sleep(0.05)
    if prc is None:
        p.send_signal(signal.SIGTERM)
        try:
            prc = p.wait(timeout=4)
        except subprocess.TimeoutExpired:
            p.send_signal(signal.SIGKILL)
            prc = p.wait(timeout=4)
    se = p.stderr.read().decode(errors="replace")
    p.stderr.close()
    insp = inspect(path)
    st = audio_stats(path)
    return {"leg": name, "argv": argv, "rc": prc,
            "wall_s": round(time.monotonic() - t0, 3),
            "err_class": errclass(se)[0], "err_line": norm_err(se),
            "err_tail2": "\n".join(se.strip().splitlines()[-2:])[:220],
            "out_kind": out_kind(insp), "bytes": insp.get("bytes"),
            "fmt": insp.get("fmt"), "peak": st.get("peak"),
            "nz_frac": st.get("nz_frac"), "during": dres}


def main():
    tmp = mk()
    tone = gen_tone(os.path.join(tmp, "tone.wav"))
    idx, note = load_ns()
    res = {"ns_module": idx, "legs": []}
    if idx is None:
        emit(res, "probe-jack-ffmpeg-r78.json")
        return
    env = dict(os.environ)
    try:
        # ffmpeg jack demuxer options, once
        rc, so, se, _w, _t = sh(["ffmpeg", "-hide_banner", "-h",
                                 "demuxer=jack"], timeout=8)
        res["jack_demuxer_help"] = (so.decode(errors="replace") +
                                    se)[:600]

        # ---- pw-jack surface -------------------------------------------
        # A: ffmpeg -f jack WITHOUT shim -> expected failure class
        out = os.path.join(tmp, "jack_noshim.wav")
        res["legs"].append(ff_leg(
            "jack_noshim",
            ["ffmpeg", "-hide_banner", "-f", "jack", "-i", "ffmpeg",
             "-t", "1.0", "-y", out], out))

        # B: pw-jack ffmpeg -f jack (default connect): which ports feed it?
        out = os.path.join(tmp, "jack_shim.wav")
        res["legs"].append(ff_leg(
            "jack_shim_default",
            ["pw-jack", "ffmpeg", "-hide_banner", "-f", "jack", "-i",
             "ffmpeg", "-t", "1.2", "-y", out], out,
            during=lambda: pwlink_map(
                sh(["pw-link", "-l"])[1].decode(errors="replace"),
                "ffmpeg")))

        # C: pw-jack ffmpeg -f jack with tone playing into r78_ns —
        #    does the shim auto-connect to default source (Line)?
        out = os.path.join(tmp, "jack_shim_tone.wav")
        play = subprocess.Popen(["pw-cat", "-p", "--target", NS, tone],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        time.sleep(0.3)
        res["legs"].append(ff_leg(
            "jack_shim_tone",
            ["pw-jack", "ffmpeg", "-hide_banner", "-f", "jack", "-i",
             "ffmpeg", "-t", "1.2", "-y", out], out,
            during=lambda: pwlink_map(
                sh(["pw-link", "-l"])[1].decode(errors="replace"),
                "ffmpeg")))
        try:
            play.wait(timeout=5)
        except subprocess.TimeoutExpired:
            play.kill()

        # D: pw-jack ffmpeg, jack-style target "-i r78_ns" (client naming)
        out = os.path.join(tmp, "jack_named.wav")
        play = subprocess.Popen(["pw-cat", "-p", "--target", NS, tone],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        time.sleep(0.3)
        res["legs"].append(ff_leg(
            "jack_named_target",
            ["pw-jack", "ffmpeg", "-hide_banner", "-f", "jack", "-i",
             "r78_ns", "-t", "1.2", "-y", out], out,
            during=lambda: pwlink_map(
                sh(["pw-link", "-l"])[1].decode(errors="replace"),
                "r78_ns")))
        try:
            play.wait(timeout=5)
        except subprocess.TimeoutExpired:
            play.kill()

        # E: PIPEWIRE_PROPS env on a plain pw-record — env prop path
        out = os.path.join(tmp, "envprops.wav")
        play = subprocess.Popen(["pw-cat", "-p", "--target", NS, tone],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        time.sleep(0.3)
        e2 = dict(os.environ)
        e2["PIPEWIRE_PROPS"] = '{ stream.capture.sink=true node.name=r78env }'
        res["legs"].append(ff_leg(
            "env_pipwire_props",
            ["pw-record", "--target", NS, "-n", "48000", out], out,
            env=e2,
            during=lambda: pwlink_map(
                sh(["pw-link", "-l"])[1].decode(errors="replace"),
                "r78env")))
        try:
            play.wait(timeout=5)
        except subprocess.TimeoutExpired:
            play.kill()

        # ---- ffmpeg device parity ---------------------------------------
        play = subprocess.Popen(["pw-cat", "-p", "--target", NS, tone],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(0.3)
        out = os.path.join(tmp, "ff_pulse.wav")
        res["legs"].append(ff_leg(
            "ff_pulse_monitor",
            ["ffmpeg", "-hide_banner", "-f", "pulse", "-i", M_NS,
             "-t", "1.2", "-y", out], out))
        try:
            play.wait(timeout=5)
        except subprocess.TimeoutExpired:
            play.kill()

        for nm, dev in (("ff_alsa_pipewire", "pipewire"),
                        ("ff_alsa_default", "default"),
                        ("ff_alsa_sysdefault", "sysdefault"),
                        ("ff_alsa_plughw", "plughw:0,0"),
                        ("ff_alsa_hw", "hw:0,0")):
            out = os.path.join(tmp, nm + ".wav")
            res["legs"].append(ff_leg(
                nm,
                ["ffmpeg", "-hide_banner", "-f", "alsa", "-i", dev,
                 "-t", "1.0", "-y", out], out))

        out = os.path.join(tmp, "ff_oss.wav")
        res["legs"].append(ff_leg(
            "ff_oss",
            ["ffmpeg", "-hide_banner", "-f", "oss", "-i", "/dev/dsp",
             "-t", "1.0", "-y", out], out))
    finally:
        unload_ns(idx)
    res["scratch_bytes"] = du()
    emit(res, "probe-jack-ffmpeg-r78.json")


if __name__ == "__main__":
    main()
