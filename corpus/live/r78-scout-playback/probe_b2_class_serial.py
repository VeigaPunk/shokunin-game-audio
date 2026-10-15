#!/usr/bin/env python3
"""Probe B2 — class-override crash + numeric target semantics.

B1: `-P media.class=Audio/Sink` on a playback stream exited rc=-11 (SIGSEGV)
with empty stderr and no node ever published; `--target <node id>` did not
resolve (fell back to the default sink).  Both need reproduction and the
numeric axis needs the correct key (object.serial, not the node id).
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r78p as H

CLASS_LEGS = [
    ("class_sink", ["-P", "media.class=Audio/Sink", "--target", H.NS]),
    ("class_source", ["-P", "media.class=Audio/Source", "--target", H.NS]),
    ("class_input", ["-P", "media.class=Stream/Input/Audio", "--target",
                     H.NS]),
    ("class_output", ["-P", "media.class=Stream/Output/Audio", "--target",
                      H.NS]),
    ("class_bogus", ["-P", "media.class=Audio/Bogus", "--target", H.NS]),
    ("class_duplex", ["-P", "media.class=Audio/Duplex", "--target", H.NS]),
]


def run(label, args, out, reps=1, timeout=9.0):
    for i in range(reps):
        tag = f"r78pB2_{label}_{i}"
        argv = ["pw-play", "-P", f"node.name={tag}", *args, H.TONE]
        mon = H.Monitors(tag=f"r78pmonB2_{label}_{i}")
        leg = H.one_leg(mon, argv, tag, probe_at=0.85, timeout=timeout)
        leg["label"], leg["requested"], leg["rep"] = label, args, i
        out["legs"].append(leg)
        print(f"{label:16s}#{i} rc={leg['rc']} wall={leg['wall_s']:5.2f} "
              f"mine={leg['carried']} "
              f"links={sorted({p for v in leg['mid'].get('links', {}).values() for p in v})} "
              f"tgt={leg['mid'].get('props', {}).get('target.object')} "
              f"err={leg['stderr'][:60]!r}", flush=True)


def main():
    out = {"probe": "playback-class-crash-and-serial-r78p", "legs": [],
           "toolchain": H.toolchain()}
    m1, _, _ = H.load_null(H.NS)
    time.sleep(0.5)
    H.make_tone(dur=1.6)
    nodes = H.pw_nodes()
    ns = nodes.get(H.NS, {})
    spdif = nodes.get(H.S_SPDIF, {})
    out["node_ids"] = {"ns_id": ns.get("_id"), "ns_serial": ns.get(
        "object.serial"), "spdif_id": spdif.get("_id"),
        "spdif_serial": spdif.get("object.serial")}
    for label, args in CLASS_LEGS:
        run(label, args, out, reps=3 if label in ("class_sink",) else 1)
    if ns.get("object.serial"):
        run("serial_ns", ["--target", str(ns["object.serial"])], out)
    if spdif.get("object.serial"):
        run("serial_spdif", ["--target", str(spdif["object.serial"])], out)
    run("serial_bogus", ["--target", "424242"], out)
    run("serial_prop_ns", ["-P", f"target.object={ns.get('object.serial')}"],
        out)
    run("id_prop_ns", ["-P", f"target.object={ns.get('_id')}"], out)
    H.unload(m1)
    for f in os.listdir(H.RAW):
        if f.startswith("r78pmonB2_"):
            os.unlink(os.path.join(H.RAW, f))
    H.save("probe-play-class-serial-r78p.json", out)


if __name__ == "__main__":
    main()
