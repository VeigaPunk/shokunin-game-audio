#!/usr/bin/env python3
"""Probe C2 — mid-playback target loss / re-link, one FRESH sink per leg.

C1 was invalidated by a cascade: leg 1 unloaded the shared probe sink, so every
later leg's `--target r78p_ns` (and its name-targeted monitor witness) fell
back to the default sink — the two witnesses then agreed on the wrong node.

Here each leg owns its sink (`r78pC_<label>`), so a leg's unload can only
affect that leg.  Witness set = own sink + a fixed sibling + SPDIF + Speaker.
"""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r78p as H

TONE6 = os.path.join(H.RAW, "tone_r78p_6s.wav")


def sink_input_index(tag):
    rc, out, err, _, _ = H.sh(["pactl", "-f", "json", "list", "sink-inputs"],
                              timeout=8)
    try:
        d = json.loads(out.decode(errors="replace"))
    except Exception:
        return None
    for si in d:
        p = si.get("properties", {})
        if p.get("node.name") == tag:
            return si.get("index")
    return None


def timed_leg(label, events, out, tone=TONE6, deadline=11.0):
    own = "r78pC_" + label
    mod, rc0, err0 = H.load_null(own)
    time.sleep(0.5)
    tag = "r78pC_" + label
    mon = H.Monitors(sinks=[("own", own), ("ns2", H.NS2),
                            ("spdif", H.S_SPDIF), ("spk", H.S_SPK)],
                     tag="r78pmonC2_" + label)
    mon.start()
    argv = ["pw-play", "-P", f"node.name={tag}", "--target", own, tone]
    t0 = time.monotonic()
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    fired, timeline = [], []
    pend = [(t, n, f) for t, n, f in events]
    while proc.poll() is None and time.monotonic() - t0 < deadline:
        t = time.monotonic() - t0
        while pend and pend[0][0] <= t:
            _, name, fn = pend.pop(0)
            try:
                fired.append({"t": round(time.monotonic() - t0, 2),
                              "event": name, "result": fn(tag, own)})
            except Exception as exc:
                fired.append({"t": round(time.monotonic() - t0, 2),
                              "event": name, "error": repr(exc)})
        timeline.append([round(time.monotonic() - t0, 2),
                         H.consumers_of(H.pwlink(), tag)])
        time.sleep(0.4)
    try:
        so, se = proc.communicate(timeout=4)
        rc, err, to = proc.returncode, se.decode(errors="replace"), False
    except subprocess.TimeoutExpired:
        proc.kill()
        so, se = proc.communicate()
        rc, err, to = None, se.decode(errors="replace"), True
    wall = round(time.monotonic() - t0, 3)
    time.sleep(0.6)
    caps = mon.stop()
    leg = {"label": label, "own_sink": own, "module": mod, "rc": rc,
           "stderr": err.strip()[:300], "wall_s": wall, "timed_out": to,
           "fired": fired, "timeline": timeline[-6:], "caps": caps,
           "tone_windows": {k: v["mine"] for k, v in caps.items()
                            if v["mine"]},
           "foreign_windows": {k: v["foreign"] for k, v in caps.items()
                               if v["foreign"]},
           "carried": [k for k, v in caps.items()
                       if v["verdict"] in ("mine", "mine_r_tag")],
           "final_consumers": H.consumers_of(H.pwlink(), tag)}
    out["legs"].append(leg)
    print(f"{label:20s} rc={rc} wall={wall:5.2f} "
          f"events={[f['event'] for f in fired]} "
          f"tone_windows={leg['tone_windows']} "
          f"foreign={leg['foreign_windows']} "
          f"final={sorted({p for v in leg['final_consumers'].values() for p in v})}",
          flush=True)
    # a leg must not leak: unload whatever is left of its own sink
    rc, o, e, _, _ = H.sh(["pactl", "list", "modules", "short"], timeout=8)
    for line in o.decode(errors="replace").splitlines():
        if f"sink_name={own}" in line:
            H.unload(line.split()[0])
    return leg


def main():
    out = {"probe": "playback-loss-relink-c2-r78p", "legs": [],
           "toolchain": H.toolchain()}
    out["pre_cleanup"] = H.unload_all_mine()
    m2, _, _ = H.load_null(H.NS2)
    H.make_tone(TONE6, dur=6.0)
    try:
        # 1. destroy the target node mid-run
        def unload_own(tag, own):
            r = []
            rc, o, e, _, _ = H.sh(["pactl", "list", "modules", "short"],
                                  timeout=8)
            for line in o.decode(errors="replace").splitlines():
                if f"sink_name={own}" in line:
                    r.append([line.split()[0], H.unload(line.split()[0])[0]])
            return {"unloaded": r}
        timed_leg("unload_own", [(2.0, "unload_own", unload_own)], out)

        # 2. drop the link mid-run
        def unlink(tag, own):
            res = []
            for port, peers in H.consumers_of(H.pwlink(), tag).items():
                for peer in peers:
                    res.append([f"{port}->{peer}",
                                H.sh(["pw-link", "-d", port, peer],
                                     timeout=5)[0]])
            return res
        timed_leg("unlink_own", [(2.0, "unlink", unlink)], out)

        # 3. move the ACTIVE stream to another sink
        def move_spk(tag, own):
            idx = sink_input_index(tag)
            if idx is None:
                return {"index": None}
            rc, o, e, _, _ = H.pactl("move-sink-input", str(idx), H.S_SPK)
            return {"index": idx, "rc": rc, "err": e.strip()[:120]}
        timed_leg("move_spk", [(2.0, "move_spk", move_spk)], out)

        # 4. move the ACTIVE stream to a nonexistent sink
        def move_garbage(tag, own):
            idx = sink_input_index(tag)
            if idx is None:
                return {"index": None}
            rc, o, e, _, _ = H.pactl("move-sink-input", str(idx),
                                     "no_such_sink")
            return {"index": idx, "rc": rc, "err": e.strip()[:160]}
        timed_leg("move_garbage", [(2.0, "move_garbage", move_garbage)], out)

        # 5. change the DEFAULT sink under an ACTIVE stream (native metadata)
        def set_default(tag, own):
            rc, o, e, _, _ = H.sh(["pw-metadata", "-n", "default", "0",
                                   "default.audio.sink",
                                   json.dumps({"name": H.S_SPK})], timeout=6)
            return {"rc": rc, "err": e.strip()[:80]}
        timed_leg("set_default_midrun", [(2.0, "set_default", set_default)],
                  out)
        H.sh(["pw-metadata", "-n", "default", "0", "default.audio.sink",
              json.dumps({"name": H.S_SPDIF})], timeout=6)

        # 6. suspend the target sink mid-run
        def suspend(tag, own):
            return {"rc": H.pactl("suspend-sink", own, "1")[0]}
        timed_leg("suspend_own", [(2.0, "suspend", suspend)], out)

        # 7. mute the target sink mid-run (does the monitor tap follow?)
        def mute(tag, own):
            return {"rc": H.pactl("set-sink-mute", own, "1")[0]}
        timed_leg("mute_own", [(2.0, "mute", mute)], out)

        # 8. unload the target, then re-create a sink with the SAME name
        def recreate(tag, own):
            rc, o, e, _, _ = H.sh(["pactl", "list", "modules", "short"],
                                  timeout=8)
            gone = []
            for line in o.decode(errors="replace").splitlines():
                if f"sink_name={own}" in line:
                    gone.append([line.split()[0],
                                 H.unload(line.split()[0])[0]])
            time.sleep(0.5)
            mid, rc2, err2 = H.load_null(own)
            return {"unloaded": gone, "reload_module": mid, "rc": rc2}
        timed_leg("unload_recreate", [(2.0, "recreate", recreate)], out)
    finally:
        out["post_cleanup"] = H.unload_all_mine()
        H.sh(["pw-metadata", "-n", "default", "0", "default.audio.sink",
              json.dumps({"name": H.S_SPDIF})], timeout=6)
        H.unload(m2)
        H.save("probe-play-loss-c2-r78p.json", out)


if __name__ == "__main__":
    main()
