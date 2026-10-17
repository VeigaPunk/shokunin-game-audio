#!/usr/bin/env python3
"""R77 scout — FRONTIER 1e (serialized): content witness, single-threaded.

Runs strictly one leg at a time (no concurrent probe on this host) so a
tone played into sink A cannot appear in sink B's monitor by accident.

Witness: play the 1 kHz tone into a NAMED sink with `pw-cat -p --target S`,
then capture with `pw-record -P stream.capture.sink=true --target T`.
The capture carries the tone iff the node it actually consumed is S.
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
from r77_probe import (M_SPDIF, S_SPDIF, emit, mk, sh)  # noqa

TMP = mk()
SPK = "alsa_output.usb-Generic_USB_Audio-00.HiFi__Speaker__sink"
TONE = os.path.join(TMP, "tone.wav")


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
    if len(d) < 4:
        return None
    return max(abs(v) for v in struct.unpack("<%dh" % (len(d) // 2),
                                             d[:len(d) // 2 * 2]))


def nz(d):
    return round(sum(1 for b in d if b) / len(d), 4) if d else None


def one(label, play_argv, cap_argv, cap_path):
    pl = subprocess.Popen(play_argv, stdout=subprocess.DEVNULL,
                          stderr=subprocess.PIPE)
    time.sleep(0.25)
    cp = subprocess.Popen(cap_argv + [cap_path], stdout=subprocess.DEVNULL,
                          stderr=subprocess.PIPE)
    try:
        pl.wait(timeout=8)
    except subprocess.TimeoutExpired:
        pl.kill()
        pl.wait(timeout=4)
    time.sleep(0.35)
    if cp.poll() is None:
        cp.send_signal(signal.SIGTERM)
        try:
            cp.wait(timeout=8)
        except subprocess.TimeoutExpired:
            cp.kill()
            cp.wait(timeout=8)
    perr = pl.stderr.read().decode(errors="replace").strip()
    pl.stderr.close()
    cp.stderr.read()
    cp.stderr.close()
    d = open(cap_path, "rb").read() if os.path.exists(cap_path) else b""
    pay = d[44:] if d[:4] == b"RIFF" else d
    time.sleep(0.5)                      # settle before the next leg
    return {"leg": label, "play": play_argv, "cap": cap_argv,
            "play_rc": pl.returncode, "play_err": perr[-120:],
            "cap_rc": cp.returncode, "payload": len(pay),
            "nonzero_frac": nz(pay), "peak": peak(pay),
            "carries_tone": bool(peak(pay) and peak(pay) > 500)}


def main():
    out = {"probe": "override-content-serial-r77", "tmp": TMP, "legs": {}}
    make_tone()
    _rc, so, _se, _w, _t = sh(["pactl", "get-default-sink"])
    out["default_sink"] = so.decode().strip()

    cases = [
        ("A1 play->SPDIF   cap prop|SPDIF_sink",
         ["pw-cat", "-p", TONE, "--target", S_SPDIF],
         ["pw-record", "-P", "stream.capture.sink=true", "--target",
          S_SPDIF, "-n", "96000"]),
        ("A2 play->SPDIF   cap prop|SPEAKER_sink",
         ["pw-cat", "-p", TONE, "--target", S_SPDIF],
         ["pw-record", "-P", "stream.capture.sink=true", "--target",
          SPK, "-n", "96000"]),
        ("A3 play->SPDIF   cap prop|GARBAGE",
         ["pw-cat", "-p", TONE, "--target", S_SPDIF],
         ["pw-record", "-P", "stream.capture.sink=true", "--target",
          "no_such_node_xyz", "-n", "96000"]),
        ("B1 play->SPEAKER cap prop|SPDIF_sink",
         ["pw-cat", "-p", TONE, "--target", SPK],
         ["pw-record", "-P", "stream.capture.sink=true", "--target",
          S_SPDIF, "-n", "96000"]),
        ("B2 play->SPEAKER cap prop|SPEAKER_sink",
         ["pw-cat", "-p", TONE, "--target", SPK],
         ["pw-record", "-P", "stream.capture.sink=true", "--target",
          SPK, "-n", "96000"]),
        ("C1 play->SPEAKER cap parec SPDIF.monitor (no prop)",
         ["pw-cat", "-p", TONE, "--target", SPK],
         ["parec", "-d", M_SPDIF, "--raw"]),
        ("C2 play->SPDIF   cap parec SPDIF.monitor (no prop)",
         ["pw-cat", "-p", TONE, "--target", S_SPDIF],
         ["parec", "-d", M_SPDIF, "--raw"]),
        ("D1 play->SPEAKER cap pwrecord --target SPEAKER_sink (no prop)",
         ["pw-cat", "-p", TONE, "--target", SPK],
         ["pw-record", "--target", SPK, "-n", "96000"]),
        ("E0 no play       cap prop|SPDIF_sink (silence baseline)",
         ["pw-cat", "-p", os.path.join(TMP, "silence.wav"), "--target",
          S_SPDIF],
         ["pw-record", "-P", "stream.capture.sink=true", "--target",
          S_SPDIF, "-n", "96000"]),
    ]
    # silence member for E0
    with wave.open(os.path.join(TMP, "silence.wav"), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(48000)
        w.writeframes(b"\x00" * 384000)

    for label, play, cap in cases:
        p = os.path.join(TMP, f"s{abs(hash(label)) % 10**7}.wav")
        if os.path.exists(p):
            os.unlink(p)
        out["legs"][label] = one(label, play, cap, p)

    emit(out, "probe-override-content-serial-r77.json")
    print(out["probe"])


if __name__ == "__main__":
    main()
