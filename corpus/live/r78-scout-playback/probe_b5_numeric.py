#!/usr/bin/env python3
"""Probe B5 — numeric target axis, on a CLEAN single-instance sink.

B2–B4 read as "`--target <object.serial>` links but is silent".  That was a
self-inflicted artifact: an earlier crashed probe leaked a second null sink
with the SAME node.name, so the name-resolved monitor witness and the
serial-resolved stream landed on different nodes.  Here every probe-owned sink
is unloaded first, and the leg is judged by the FULL `pw-link -l` text plus the
witness, so name/serial/id resolution is unambiguous.
"""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r78p as H


def pwlink_text(tag):
    rc, out, err, _, _ = H.sh(["pw-link", "-l"], timeout=6)
    lines = out.decode(errors="replace").splitlines()
    return [l.rstrip() for l in lines if tag in l or "r78p_ns" in l]


def main():
    out = {"probe": "playback-numeric-target-clean-r78p", "legs": [],
           "toolchain": H.toolchain()}
    out["pre_cleanup"] = H.unload_all_mine()
    m1, rc1, e1 = H.load_null(H.NS)
    time.sleep(0.6)
    H.make_tone(dur=1.6)
    nodes = H.pw_nodes()
    ns = nodes.get(H.NS, {})
    serial, nid = ns.get("object.serial"), ns.get("_id")
    out["ns"] = {"module": m1, "id": nid, "serial": serial,
                 "sinks_short": H.pactl("list", "sinks", "short")[1].decode()}
    legs = [
        ("name", ["--target", H.NS]),
        ("serial", ["--target", str(serial)]),
        ("node_id", ["--target", str(nid)]),
        ("prop_serial_int", ["-P", f"target.object={serial}"]),
        ("prop_serial_str", ["-P", f"target.object={serial}"]),
        ("prop_id_int", ["-P", f"target.object={nid}"]),
        ("name_again", ["--target", H.NS]),
    ]
    try:
        for label, args in legs:
            tag = "r78pB5_" + label
            argv = ["pw-play", "-P", f"node.name={tag}", *args, H.TONE]
            mon = H.Monitors(tag="r78pmonB5_" + label, win=0.25)
            mon.start()
            t0 = time.monotonic()
            proc = subprocess.Popen(argv, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            time.sleep(1.0)
            mid = {"links": H.consumers_of(H.pwlink(), tag),
                   "pwlink_text": pwlink_text(tag)}
            try:
                so, se = proc.communicate(timeout=6)
                rc, err = proc.returncode, se.decode(errors="replace")
            except Exception:
                proc.kill()
                so, se = proc.communicate()
                rc, err = None, se.decode(errors="replace")
            wall = round(time.monotonic() - t0, 3)
            time.sleep(0.5)
            caps = mon.stop()
            leg = {"label": label, "args": args, "rc": rc, "wall_s": wall,
                   "stderr": err.strip()[:200], "mid": mid,
                   "tone_windows": {k: v["mine"] for k, v in caps.items()
                                    if v["mine"]},
                   "carried": [k for k, v in caps.items()
                               if v["verdict"] in ("mine", "mine_r_tag")]}
            out["legs"].append(leg)
            print(f"{label:16s} rc={rc} wall={wall:5.2f} carried={leg['carried']} "
                  f"windows={leg['tone_windows']}")
            for l in mid["pwlink_text"]:
                print("     ", l)
            for f in os.listdir(H.RAW):
                if f.startswith("r78pmonB5_") and label not in ("serial", "name"):
                    os.unlink(os.path.join(H.RAW, f))
    finally:
        out["post_cleanup"] = H.unload_all_mine()
        H.save("probe-play-numeric-target-r78p.json", out)


if __name__ == "__main__":
    main()
