#!/usr/bin/env python3
"""R77 scout — FRONTIER 1c (fixed): extent of the capture-sink override.

Witness = pw-link -l block walk: for each pw-record:input_* port, the
`|<-` producers are the nodes actually feeding the capture. Recorded raw so
the parse is auditable.
"""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r77_probe import (LINE, M_SPDIF, S_SPDIF, emit, mk, sh)  # noqa

TMP = mk()
HDMI = "alsa_output.pci-0000_01_00.1.hdmi-stereo"
SPK = "alsa_output.usb-Generic_USB_Audio-00.HiFi__Speaker__sink"


def producers(pwlink_text):
    """Blocks: a port line, then indented '|->'/'|<-' lines. For a
    pw-record:input_* port the '|<-' lines name the feeding ports."""
    lines = pwlink_text.splitlines()
    out = {}
    for i, ln in enumerate(lines):
        if ln.strip() == "pw-record:input_FL" or \
                ln.strip() == "pw-record:input_FR":
            srcs = []
            j = i + 1
            while j < len(lines) and lines[j].strip().startswith("|"):
                s = lines[j].strip()
                if s.startswith("|<-"):
                    srcs.append(s[3:].strip())
                j += 1
            out[ln.strip()] = srcs
    return out


def probe(argv):
    p = os.path.join(TMP, f"x{abs(hash(tuple(argv))) % 10**8}.wav")
    proc = subprocess.Popen(argv + [p], stdout=subprocess.DEVNULL,
                            stderr=subprocess.PIPE)
    time.sleep(1.5)
    _rc, so, _se, _w, _t = sh(["pw-link", "-l"], timeout=15)
    text = so.decode(errors="replace")
    prod = producers(text)
    nodes = sorted({s.rsplit(":", 1)[0] for v in prod.values() for s in v})
    # stream props: scan every object whose node.name is pw-record
    _rc2, so2, _se2, _w2, _t2 = sh(["pw-dump"], timeout=25)
    adv = []
    try:
        for o in json.loads(so2):
            pp = o.get("info", {}).get("props", {})
            if pp.get("node.name") == "pw-record" and \
                    pp.get("media.class") == "Stream/Input/Audio":
                adv.append({"target.object": pp.get("target.object"),
                            "stream.capture.sink": pp.get("stream.capture.sink"),
                            "object.serial": pp.get("object.serial")})
    except Exception as exc:                                   # noqa: BLE001
        adv = [f"parse:{exc}"]
    proc.send_signal(2)
    try:
        proc.wait(timeout=6)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=6)
    err = proc.stderr.read().decode(errors="replace")
    proc.stderr.close()
    n = os.path.getsize(p) if os.path.exists(p) else None
    return {"argv": argv, "feeding_nodes": nodes, "port_map": prod,
            "stream_objects": adv, "bytes": n, "rc": proc.returncode,
            "err_tail": err.strip().splitlines()[-1][:120] if err.strip()
            else ""}


def main():
    out = {"probe": "override-extent2-r77", "tmp": TMP,
           "default_sink": None, "default_source": None, "legs": {}}
    _rc, so, _se, _w, _t = sh(["pactl", "get-default-sink"])
    out["default_sink"] = so.decode().strip()
    _rc, so, _se, _w, _t = sh(["pactl", "get-default-source"])
    out["default_source"] = so.decode().strip()

    cases = [
        ("no_prop|SPDIF_sink", ["pw-record", "--target", S_SPDIF]),
        ("no_prop|HDMI_sink", ["pw-record", "--target", HDMI]),
        ("no_prop|SPDIF_monitor", ["pw-record", "--target", M_SPDIF]),
        ("no_prop|LINE_source", ["pw-record", "--target", LINE]),
        ("prop|SPDIF_sink", ["pw-record", "-P", "stream.capture.sink=true",
                             "--target", S_SPDIF]),
        ("prop|HDMI_sink", ["pw-record", "-P", "stream.capture.sink=true",
                            "--target", HDMI]),
        ("prop|SPEAKER_sink", ["pw-record", "-P", "stream.capture.sink=true",
                               "--target", SPK]),
        ("prop|HDMI_monitor", ["pw-record", "-P", "stream.capture.sink=true",
                               "--target", HDMI + ".monitor"]),
        ("prop|GARBAGE", ["pw-record", "-P", "stream.capture.sink=true",
                          "--target", "no_such_node_xyz"]),
        ("prop|LINE_source", ["pw-record", "-P", "stream.capture.sink=true",
                              "--target", LINE]),
        ("prop|MIC_source", ["pw-record", "-P", "stream.capture.sink=true",
                             "--target",
                             "alsa_input.usb-Generic_USB_Audio-00."
                             "HiFi__Mic__source"]),
    ]
    for label, argv in cases:
        out["legs"][label] = probe(argv + ["-n", "4800"])
    emit(out, "probe-override-extent2-r77.json")
    print(out["probe"])


if __name__ == "__main__":
    main()
