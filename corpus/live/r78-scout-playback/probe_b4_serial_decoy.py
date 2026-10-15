#!/usr/bin/env python3
"""Probe B4 — the serial-target decoy: where does the audio actually go?

B2/B3 + a manual repro: `pw-play --target <null-sink object.serial>` exits
rc=0, pw-link shows `r78p_ns:playback_FL/FR` consumers, the file is consumed at
real-time rate — and EVERY monitor is silent (not just ns: SPDIF is silent
too, so it is not a default-sink fallback either).  This probe reads the LINK
objects' own state/error out of pw-dump, which is the only witness left.
"""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r78p as H


def dump_links(tag):
    rc, out, err, _, _ = H.sh(["pw-dump"], timeout=10)
    try:
        d = json.loads(out.decode(errors="replace"))
    except Exception:
        return []
    ports = {}
    for o in d:
        if o.get("type") == "PipeWire:Interface:Port":
            p = o.get("info", {}).get("props", {})
            ports[o["id"]] = (p.get("node.name"), p.get("port.name"),
                              p.get("port.direction"))
    res = []
    for o in d:
        if o.get("type") != "PipeWire:Interface:Link":
            continue
        i = o.get("info", {})
        p = i.get("props", {})
        op, ip = ports.get(i.get("output-port-id")), ports.get(
            i.get("input-port-id"))
        names = f"{op}->{ip}"
        if tag in names or (op and "r78p_ns" in str(op[0])):
            res.append({"id": o["id"], "state": i.get("state"),
                        "error": i.get("error"), "output": op,
                        "input": ip, "props": {
                            k: p.get(k) for k in ("link.output.node",
                                                  "link.input.node",
                                                  "object.serial")}})
    return res


def pwtop_all(tag):
    rc, out, err, _, _ = H.sh(["pw-top", "-b", "-n", "1"], timeout=8)
    lines = out.decode(errors="replace").splitlines()
    keep = [l.rstrip() for l in lines
            if tag in l or "r78p_ns" in l or l.startswith("S   ID")]
    return keep[:10]


def main():
    out = {"probe": "playback-serial-decoy-r78p", "legs": [],
           "toolchain": H.toolchain()}
    m1, _, _ = H.load_null(H.NS)
    time.sleep(0.6)
    H.make_tone(dur=1.6)
    nodes = H.pw_nodes()
    serial = nodes.get(H.NS, {}).get("object.serial")
    out["ns"] = {"id": nodes.get(H.NS, {}).get("_id"), "serial": serial}

    for label, args in (("serial", ["--target", str(serial)]),
                        ("name", ["--target", H.NS]),
                        ("serial_spdif", ["--target", "59"]),
                        ("garbage", ["--target", "no_such_sink_xyz"])):
        tag = "r78pB4_" + label
        argv = ["pw-play", "-P", f"node.name={tag}", *args, H.TONE]
        mon = H.Monitors(tag="r78pmonB4_" + label, win=0.25)
        mon.start()
        t0 = time.monotonic()
        proc = subprocess.Popen(argv, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        time.sleep(1.0)
        mid = {"links": H.consumers_of(H.pwlink(), tag),
               "dump_links": dump_links(tag), "pw_top": pwtop_all(tag)}
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
        print(f"{label:12s} rc={rc} wall={wall:5.2f} carried={leg['carried']} "
              f"windows={leg['tone_windows']}")
        for L in mid["dump_links"]:
            print("    link", json.dumps(L))
        for l in mid["pw_top"]:
            print("    top ", l)
        for f in os.listdir(H.RAW):
            if f.startswith("r78pmonB4_") and label not in ("serial", "name"):
                os.unlink(os.path.join(H.RAW, f))
    H.unload(m1)
    H.save("probe-play-serial-decoy-r78p.json", out)


if __name__ == "__main__":
    main()
