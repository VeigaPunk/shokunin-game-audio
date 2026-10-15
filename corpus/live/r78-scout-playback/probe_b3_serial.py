#!/usr/bin/env python3
"""Probe B3 — why does a SERIAL-targeted playback stream link but not sound?

B2: `--target <ns object.serial>` and `-P target.object=<serial>` both created
`r78p_ns:playback_FL/FR` links (pw-link confirms) yet the ns monitor carried
pure digital silence, while a NAME-targeted leg to the same sink carried the
tone in the same run.  This probe measures the stream's processing state.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r78p as H


def pwtop_full(tag):
    rc, out, err, _, _ = H.sh(["pw-top", "-b", "-n", "1"], timeout=8)
    return [l.rstrip() for l in out.decode(errors="replace").splitlines()
            if tag in l or "ERR" in l or l.startswith("S   ID")][:8]


def sink_input(tag):
    rc, out, err, _, _ = H.sh(["pactl", "-f", "json", "list", "sink-inputs"],
                              timeout=8)
    try:
        d = json.loads(out.decode(errors="replace"))
    except Exception:
        return None
    for si in d:
        p = si.get("properties", {})
        if p.get("node.name") == tag:
            return {"index": si.get("index"), "sink": si.get("sink"),
                    "corked": si.get("corked"), "volume": si.get("volume"),
                    "state": si.get("state")}
    return None


def stream_state(tag):
    for n, props in H.pw_nodes().items():
        if n == tag:
            return {"id": props.get("_id"), "state": props.get("_state"),
                    "media.class": props.get("media.class"),
                    "target.object": props.get("target.object")}
    return None


def main():
    out = {"probe": "playback-serial-vs-name-r78p", "legs": [],
           "toolchain": H.toolchain()}
    m1, _, _ = H.load_null(H.NS)
    time.sleep(0.6)
    H.make_tone(dur=1.6)
    nodes = H.pw_nodes()
    ns = nodes.get(H.NS, {})
    serial, nid = ns.get("object.serial"), ns.get("_id")
    out["ns"] = {"id": nid, "serial": serial}
    out["sink_volume"] = {
        "ns": H.pactl("get-sink-volume", H.NS)[1].decode().strip(),
        "ns_mute": H.pactl("get-sink-mute", H.NS)[1].decode().strip()}

    legs = [
        ("name", ["--target", H.NS]),
        ("serial", ["--target", str(serial)]),
        ("serial_str_prop", ["-P", f"target.object={serial}"]),
        ("serial_int_prop", ["-P", f"target.object={nid}"]),
        ("name_again", ["--target", H.NS]),
        ("name_sixs", ["--target", H.NS]),
    ]
    for label, args in legs:
        tag = "r78pB3_" + label
        argv = ["pw-play", "-P", f"node.name={tag}", *args, H.TONE]
        mon = H.Monitors(tag="r78pmonB3_" + label, win=0.25)
        mon.start()
        t0 = time.monotonic()
        import subprocess
        proc = subprocess.Popen(argv, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        time.sleep(1.0)
        mid = {"links": H.consumers_of(H.pwlink(), tag),
               "stream": stream_state(tag),
               "sink_input": sink_input(tag),
               "pw_top": pwtop_full(tag),
               "ns_sink_state": stream_state(H.NS)}
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
               "stderr": err.strip()[:200], "mid": mid, "caps": caps,
               "tone_windows": {k: v["mine"] for k, v in caps.items()
                                if v["mine"]},
               "carried": [k for k, v in caps.items()
                           if v["verdict"] in ("mine", "mine_r_tag")]}
        out["legs"].append(leg)
        print(f"{label:16s} rc={rc} wall={wall:5.2f} carried={leg['carried']} "
              f"windows={leg['tone_windows']} state={mid['stream']} "
              f"sink_input={mid['sink_input']} top={mid['pw_top']}",
              flush=True)
        for f in os.listdir(H.RAW):
            if f.startswith("r78pmonB3_") and label not in ("serial", "name"):
                os.unlink(os.path.join(H.RAW, f))
    H.unload(m1)
    H.save("probe-play-serial-vs-name-r78p.json", out)


if __name__ == "__main__":
    main()
