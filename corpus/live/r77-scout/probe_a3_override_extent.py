#!/usr/bin/env python3
"""R77 scout — FRONTIER 1c: extent of the capture-sink override.

Does `-P stream.capture.sink=true` force the DEFAULT SINK's monitor
regardless of `--target`, or does it honor a sink name and only fall back
for unusable names? Resolve by link topology (pw-link) on six targets that
are all *distinct* sinks/sources.
"""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r77_probe import (LINE, M_SPDIF, M_SPK, S_SPDIF, emit, mk, sh)  # noqa

TMP = mk()
HDMI = "alsa_output.pci-0000_01_00.1.hdmi-stereo"
SPK = "alsa_output.usb-Generic_USB_Audio-00.HiFi__Speaker__sink"


def links_of(argv):
    p = os.path.join(TMP, f"t_{abs(hash(tuple(argv))) % 10**8}.wav")
    proc = subprocess.Popen(argv + [p], stdout=subprocess.DEVNULL,
                            stderr=subprocess.PIPE)
    time.sleep(1.0)
    _rc, so, _se, _w, _t = sh(["pw-link", "-l"], timeout=10)
    consumed = set()
    for ln in so.decode(errors="replace").splitlines():
        if "pw-record:input" in ln and ln.strip().startswith("|<-"):
            src = ln.split("|<-", 1)[1].strip()
            consumed.add(src.rsplit(":", 1)[0])
    _rc2, so2, _se2, _w2, _t2 = sh(["pw-dump"], timeout=20)
    tgt = None
    try:
        for o in json.loads(so2):
            pp = o.get("info", {}).get("props", {})
            if pp.get("application.name") == "pw-record":
                tgt = pp.get("target.object")
                break
    except Exception:                                          # noqa: BLE001
        pass
    proc.send_signal(2)
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)
    n = os.path.getsize(p) if os.path.exists(p) else None
    return {"argv": [a for a in argv], "advertised_target_object": tgt,
            "actually_consumed_nodes": sorted(consumed), "bytes": n,
            "rc": proc.returncode}


def main():
    out = {"probe": "capture-sink-override-extent-r77", "tmp": TMP,
           "default_sink": None, "legs": {}}
    _rc, so, _se, _w, _t = sh(["pactl", "get-default-sink"])
    out["default_sink"] = so.decode().strip()

    cases = [
        ("no_prop|target_SPDIF_sink", ["pw-record", "--target", S_SPDIF]),
        ("no_prop|target_HDMI_sink", ["pw-record", "--target", HDMI]),
        ("no_prop|target_SPDIF_monitor", ["pw-record", "--target", M_SPDIF]),
        ("prop|target_SPDIF_sink", ["pw-record", "-P",
                                    "stream.capture.sink=true",
                                    "--target", S_SPDIF]),
        ("prop|target_HDMI_sink", ["pw-record", "-P",
                                   "stream.capture.sink=true",
                                   "--target", HDMI]),
        ("prop|target_SPEAKER_sink", ["pw-record", "-P",
                                      "stream.capture.sink=true",
                                      "--target", SPK]),
        ("prop|target_HDMI_monitor", ["pw-record", "-P",
                                      "stream.capture.sink=true",
                                      "--target",
                                      HDMI + ".monitor"]),
        ("prop|target_GARBAGE", ["pw-record", "-P",
                                 "stream.capture.sink=true",
                                 "--target", "no_such_node_xyz"]),
        ("prop|target_LINE_source", ["pw-record", "-P",
                                     "stream.capture.sink=true",
                                     "--target", LINE]),
        ("prop|target_0", ["pw-record", "-P", "stream.capture.sink=true",
                           "--target", "0"]),
    ]
    for label, argv in cases:
        out["legs"][label] = links_of(argv + ["-n", "4800"])
    emit(out, "probe-override-extent-r77.json")
    print(out["probe"])


if __name__ == "__main__":
    main()
