#!/usr/bin/env python3
"""Probe C — mid-playback target loss / re-link (playback-side loss law).

r77/r78 pinned the CAPTURE side: destroying the captured node or dropping the
link changes nothing in the artifact (`sustained_after_target_loss`,
`unlinked_sustained_zeros`).  Playback has no artifact, so the questions are
different and sharper:
  * does a playback stream RE-LINK to the default sink when its target sink
    is destroyed mid-run?
  * does it stall, or keep consuming the file into nowhere?
  * do the session-manager verbs (`move-sink-input`, `set-default-sink`,
    `suspend-sink`) move an ACTIVE playback stream?

Each leg plays a 6 s tagged tone and records a dense topology timeline; the
witness captures are classified per 0.5 s window, so the exact second the tone
stops/restarts is measured, not inferred.
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
        if p.get("node.name") == tag or tag in str(p.get("application.name")):
            return si.get("index")
    return None


def timed_leg(label, args, events, out, tone=TONE6, deadline=11.0):
    """events: [(t_offset, name, fn)] fired against the running consumer."""
    tag = "r78pC_" + label
    mon = H.Monitors(tag="r78pmonC_" + label)
    mon.start()
    argv = ["pw-play", "-P", f"node.name={tag}", *args, tone]
    t0 = time.monotonic()
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    fired = []
    timeline = []
    pend = list(events)
    while proc.poll() is None and time.monotonic() - t0 < deadline:
        t = time.monotonic() - t0
        while pend and pend[0][0] <= t:
            _, name, fn = pend.pop(0)
            try:
                fired.append({"t": round(time.monotonic() - t0, 2),
                              "event": name, "result": fn(tag)})
            except Exception as exc:
                fired.append({"t": round(time.monotonic() - t0, 2),
                              "event": name, "error": repr(exc)})
        timeline.append([round(time.monotonic() - t0, 2),
                         H.consumers_of(H.pwlink(), tag)])
        time.sleep(0.4)
    for _, name, fn in pend:                # fire leftovers after exit
        try:
            fired.append({"t": round(time.monotonic() - t0, 2),
                          "event": name + ":post", "result": fn(tag)})
        except Exception as exc:
            fired.append({"t": round(time.monotonic() - t0, 2),
                          "event": name + ":post", "error": repr(exc)})
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
    leg = {"label": label, "argv": argv, "rc": rc,
           "stderr": err.strip()[:300], "wall_s": wall, "timed_out": to,
           "fired": fired, "timeline": timeline, "caps": caps,
           "carried": [k for k, v in caps.items()
                       if v["verdict"] in ("mine", "mine_r_tag")],
           "foreign": [k for k, v in caps.items() if v["foreign"]],
           "tone_windows": {k: v["mine"] for k, v in caps.items()
                            if v["mine"]},
           "final_consumers": H.consumers_of(H.pwlink(), tag)}
    out["legs"].append(leg)
    print(f"{label:22s} rc={rc} wall={wall:5.2f} fired={[f['event'] for f in fired]} "
          f"mine={leg['carried']} tone_windows={leg['tone_windows']} "
          f"final={sorted({p for v in leg['final_consumers'].values() for p in v})}",
          flush=True)
    return leg


def main():
    out = {"probe": "playback-loss-relink-r78p", "toolchain": H.toolchain(),
           "legs": []}
    out["pre_cleanup"] = H.unload_all_mine()
    m1, _, _ = H.load_null(H.NS)
    m2, _, _ = H.load_null(H.NS2)
    time.sleep(0.5)
    H.make_tone(TONE6, dur=6.0)

    # 1. destroy the target node mid-run
    def unload_ns(tag):
        return {"unload": H.unload(m1)[0],
                "sinks": H.pactl("list", "sinks", "short")[1].decode()
                .count("r78p_ns")}
    timed_leg("unload_ns", ["--target", H.NS], [(2.0, "unload_ns", unload_ns)],
              out)

    # 2. drop the link mid-run
    def unlink_ns(tag):
        res = []
        for port in (f"{tag}:output_FL", f"{tag}:output_FR"):
            for peer in H.consumers_of(H.pwlink(), tag).get(port, []):
                res.append([f"pw-link -d {port} {peer}",
                            H.sh(["pw-link", "-d", port, peer],
                                 timeout=5)[0]])
        return res
    timed_leg("unlink_ns", ["--target", H.NS], [(2.0, "unlink_ns", unlink_ns)],
              out)

    # 3. move the ACTIVE stream to another sink
    def move_to_spk(tag):
        idx = sink_input_index(tag)
        if idx is None:
            return {"index": None}
        rc, o, e, _, _ = H.pactl("move-sink-input", str(idx), H.S_SPK)
        return {"index": idx, "rc": rc, "err": e.strip()[:120]}
    timed_leg("move_sink_input", ["--target", H.NS],
              [(2.0, "move_to_spk", move_to_spk)], out)

    # 4. move the ACTIVE stream to a nonexistent sink
    def move_to_garbage(tag):
        idx = sink_input_index(tag)
        if idx is None:
            return {"index": None}
        rc, o, e, _, _ = H.pactl("move-sink-input", str(idx), "no_such_sink")
        return {"index": idx, "rc": rc, "err": e.strip()[:160]}
    timed_leg("move_sink_input_garbage", ["--target", H.NS],
              [(2.0, "move_to_garbage", move_to_garbage)], out)

    # 5. change the default sink under an ACTIVE stream
    def set_default_spk(tag):
        return {"rc": H.pactl("set-default-sink", H.S_SPK)[0],
                "now": H.pactl("get-default-sink")[1].decode().strip()}
    timed_leg("set_default_midrun", ["--target", H.S_SPDIF],
              [(2.0, "set_default_spk", set_default_spk)], out)
    H.pactl("set-default-sink", H.S_SPDIF)
    time.sleep(0.5)

    # 6. suspend the target sink mid-run
    def suspend_ns(tag):
        return {"rc": H.pactl("suspend-sink", H.NS, "1")[0]}
    timed_leg("suspend_target", ["--target", H.NS],
              [(2.0, "suspend_ns", suspend_ns)], out)

    # 7. mute the target sink mid-run (does mute reach the monitor tap?)
    def mute_ns(tag):
        return {"rc": H.pactl("set-sink-mute", H.NS, "1")[0]}
    timed_leg("mute_target", ["--target", H.NS], [(2.0, "mute_ns", mute_ns)],
              out)

    # 8. unload the target, then re-create a sink with the SAME name
    def unload_and_recreate(tag):
        H.unload(m2)
        time.sleep(0.4)
        mid, rc, err = H.load_null(H.NS2)
        return {"reload_module": mid, "rc": rc}
    timed_leg("unload_recreate", ["--target", H.NS2],
              [(2.0, "unload_recreate", unload_and_recreate)], out)

    H.unload(m1)
    out["post_cleanup"] = H.unload_all_mine()
    for f in os.listdir(H.RAW):
        if f.startswith("r78pmonC_"):
            lab = f[len("r78pmonC_"):].rsplit("_", 1)[0]
            if lab not in ("unload_ns", "move_sink_input"):
                os.unlink(os.path.join(H.RAW, f))
    H.save("probe-play-loss-r78p.json", out)


if __name__ == "__main__":
    main()
