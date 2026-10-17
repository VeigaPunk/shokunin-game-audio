#!/usr/bin/env python3
"""R77 scout — FRONTIER 1d: is `-P stream.capture.sink=true` target-blind?

Two witnesses that cannot be confused with silence:
  T1 link topology on an UNBOUNDED capture (raw pw-link text saved).
  T2 content: play a 1 kHz tone into the NON-default Speaker sink, then
     capture with `prop` aimed at (a) the default SPDIF sink, (b) the
     Speaker sink, (c) garbage. Whichever capture carries the tone names
     the node the prop actually honors.
"""
import hashlib
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
from r77_probe import (LINE, M_SPDIF, S_SPDIF, emit, mk, sh)  # noqa

TMP = mk()
SPK = "alsa_output.usb-Generic_USB_Audio-00.HiFi__Speaker__sink"
HDMI = "alsa_output.pci-0000_01_00.1.hdmi-stereo"
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


def nz(d):
    return round(sum(1 for b in d if b) / len(d), 4) if d else None


def peak(d):
    if len(d) < 4:
        return None
    return max(abs(v) for v in struct.unpack("<%dh" % (len(d) // 2),
                                             d[:len(d) // 2 * 2]))


def topology(argv):
    p = os.path.join(TMP, f"tp{abs(hash(tuple(argv))) % 10**7}.wav")
    proc = subprocess.Popen(argv + [p], stdout=subprocess.DEVNULL,
                            stderr=subprocess.PIPE)
    time.sleep(1.5)
    _rc, so, _se, _w, _t = sh(["pw-link", "-l"], timeout=15)
    text = so.decode(errors="replace")
    _rc2, so2, _se2, _w2, _t2 = sh(["pw-dump"], timeout=25)
    streams = []
    try:
        for o in json.loads(so2):
            pp = o.get("info", {}).get("props", {})
            if pp.get("media.class") == "Stream/Input/Audio":
                streams.append({"node.name": pp.get("node.name"),
                                "target.object": pp.get("target.object"),
                                "stream.capture.sink":
                                    pp.get("stream.capture.sink"),
                                "object.serial": pp.get("object.serial")})
    except Exception as exc:                                   # noqa: BLE001
        streams = [f"parse:{exc}"]
    proc.send_signal(2)
    try:
        proc.wait(timeout=6)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=6)
    proc.stderr.close()
    n = os.path.getsize(p) if os.path.exists(p) else None
    return {"argv": argv, "bytes": n, "rc": proc.returncode,
            "pwlink_text": text, "input_streams": streams}


def content_witness(label, play_sink, cap_argv, cap_path):
    pl = subprocess.Popen(["pw-cat", "-p", TONE, "--target", play_sink],
                          stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    time.sleep(0.2)
    cp = subprocess.Popen(cap_argv + [cap_path], stdout=subprocess.DEVNULL,
                          stderr=subprocess.PIPE)
    try:
        pl.wait(timeout=6)
    except subprocess.TimeoutExpired:
        pl.kill()
    time.sleep(0.3)
    if cp.poll() is None:
        cp.send_signal(signal.SIGTERM)
        try:
            cp.wait(timeout=6)
        except subprocess.TimeoutExpired:
            cp.kill()
            cp.wait(timeout=6)
    cp.stderr.close()
    pl.stderr.close()
    d = open(cap_path, "rb").read() if os.path.exists(cap_path) else b""
    pay = d[44:] if d[:4] == b"RIFF" else d
    return {"leg": label, "play_sink": play_sink, "cap_argv": cap_argv,
            "cap_rc": cp.returncode, "play_rc": pl.returncode,
            "bytes": len(d), "payload": len(pay), "nonzero_frac": nz(pay),
            "peak": peak(pay),
            "carries_tone": bool(peak(pay) and peak(pay) > 500)}


def main():
    out = {"probe": "override-content-r77", "tmp": TMP, "topology": {},
           "content": {}}
    make_tone()
    _rc, so, _se, _w, _t = sh(["pactl", "get-default-sink"])
    out["default_sink"] = so.decode().strip()

    for label, argv in [
        ("prop|SPDIF_sink", ["pw-record", "-P", "stream.capture.sink=true",
                             "--target", S_SPDIF]),
        ("prop|SPEAKER_sink", ["pw-record", "-P", "stream.capture.sink=true",
                               "--target", SPK]),
        ("prop|HDMI_sink", ["pw-record", "-P", "stream.capture.sink=true",
                            "--target", HDMI]),
        ("prop|GARBAGE", ["pw-record", "-P", "stream.capture.sink=true",
                          "--target", "no_such_node_xyz"]),
        ("prop|NO_TARGET", ["pw-record", "-P", "stream.capture.sink=true"]),
        ("noprop|SPEAKER_sink", ["pw-record", "--target", SPK]),
        ("noprop|SPDIF_monitor", ["pw-record", "--target", M_SPDIF]),
    ]:
        out["topology"][label] = topology(argv)

    # content: tone into the NON-default Speaker sink
    for label, cap in [
        ("tone->SPEAKER; cap prop|SPDIF_sink",
         ["pw-record", "-P", "stream.capture.sink=true", "--target",
          S_SPDIF, "-n", "96000"]),
        ("tone->SPEAKER; cap prop|SPEAKER_sink",
         ["pw-record", "-P", "stream.capture.sink=true", "--target",
          SPK, "-n", "96000"]),
        ("tone->SPEAKER; cap prop|GARBAGE",
         ["pw-record", "-P", "stream.capture.sink=true", "--target",
          "no_such_node_xyz", "-n", "96000"]),
        ("tone->SPDIF; cap prop|SPDIF_sink",
         ["pw-record", "-P", "stream.capture.sink=true", "--target",
          S_SPDIF, "-n", "96000"]),
        ("tone->SPDIF; cap prop|SPEAKER_sink",
         ["pw-record", "-P", "stream.capture.sink=true", "--target",
          SPK, "-n", "96000"]),
        ("tone->SPEAKER; cap parec SPDIF.monitor",
         ["parec", "-d", M_SPDIF, "--raw"]),
        ("tone->SPDIF; cap parec SPDIF.monitor",
         ["parec", "-d", M_SPDIF, "--raw"]),
    ]:
        sink = "spk" if "tone->SPEAKER" in label else S_SPDIF
        p = os.path.join(TMP, f"cw{abs(hash(label)) % 10**7}.wav")
        if os.path.exists(p):
            os.unlink(p)
        out["content"][label] = content_witness(label, sink, cap, p)

    emit(out, "probe-override-content-r77.json")
    print(out["probe"])


if __name__ == "__main__":
    main()
