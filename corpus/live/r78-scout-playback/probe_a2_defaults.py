#!/usr/bin/env python3
"""Probe A2 — fallback SEMANTICS (which default?) + `--target 0` deep dive.

A1 showed every unresolvable playback target landing on the SPDIF sink.  Two
questions remain:
  (i) is the fallback "the CURRENT default sink" or a fixed node?
  (ii) `--target 0` stalled with no consumer — is the stream published-but-
       unlinked (r78's capture-side `target_0_unlinked`), and does a manual
       pw-link pin start the flow (r78's pin law, playback side)?
"""
import json
import os
import signal
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r78p as H


def meta_defaults():
    rc, out, err, _, _ = H.sh(["pw-metadata", "-n", "default"], timeout=6)
    lines = [l for l in out.decode(errors="replace").splitlines()
             if "default.audio" in l]
    return {"rc": rc, "lines": lines}


def run_leg(label, args, out, timeout=9.0, sample_every=0.4):
    tag = "r78pA2_" + label
    argv = ["pw-play", "-P", f"node.name={tag}", *args, H.TONE]
    mon = H.Monitors(tag="r78pmonA2_" + label)
    leg = H.one_leg(mon, argv, tag, probe_at=0.85, timeout=timeout,
                    sample_every=sample_every)
    leg["label"], leg["requested"] = label, args
    out["legs"].append(leg)
    print(f"{label:24s} rc={leg['rc']} wall={leg['wall_s']:5.2f} "
          f"mine={leg['carried']} foreign={leg['foreign']} "
          f"links={sorted({p for v in leg['mid'].get('links', {}).values() for p in v})} "
          f"tgt={leg['mid'].get('props', {}).get('target.object')}",
          flush=True)
    return leg


def main():
    out = {"probe": "playback-fallback-semantics-r78p", "legs": [],
           "toolchain": H.toolchain()}
    m1, _, _ = H.load_null(H.NS)
    m2, _, _ = H.load_null(H.NS2)
    time.sleep(0.5)
    H.make_tone(dur=1.6)

    out["default_before"] = {
        "pactl": H.pactl("get-default-sink")[1].decode().strip(),
        "metadata": meta_defaults()}
    H.pactl("set-default-sink", H.S_SPK)
    time.sleep(0.8)
    out["default_after_switch_to_spk"] = {
        "pactl": H.pactl("get-default-sink")[1].decode().strip(),
        "metadata": meta_defaults()}
    run_leg("switched_no_target", [], out)
    run_leg("switched_at_default_sink", ["--target", "@DEFAULT_SINK@"], out)
    run_leg("switched_garbage", ["--target", "no_such_sink_xyz"], out)
    run_leg("switched_spk_control", ["--target", H.S_SPK], out)
    run_leg("switched_default_word", ["--target", "default"], out)
    H.pactl("set-default-sink", H.S_SPDIF)
    time.sleep(0.8)
    out["default_restored"] = {
        "pactl": H.pactl("get-default-sink")[1].decode().strip(),
        "metadata": meta_defaults()}
    run_leg("restored_no_target", [], out)
    run_leg("restored_garbage", ["--target", "no_such_sink_xyz"], out)

    # ---- `--target 0` deep dive: published? linked ever? pinned? ----------
    tag = "r78pA2_zero_deep"
    argv = ["pw-play", "-P", f"node.name={tag}", "--target", "0", H.TONE]
    mon = H.Monitors(tag="r78pmonA2_zero_deep")
    mon.start()
    t0 = time.monotonic()
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    trace = []
    for k in range(6):
        time.sleep(0.45)
        nodes = H.pw_nodes()
        rc, po, _, _, _ = H.sh(["pw-link", "-o"], timeout=5)
        ports = [p for p in po.decode(errors="replace").splitlines()
                 if tag in p]
        trace.append({"t": round(time.monotonic() - t0, 2),
                      "alive": proc.poll() is None,
                      "node_present": tag in nodes,
                      "props": H.prop_slice(nodes.get(tag, {})),
                      "out_ports": ports,
                      "consumers": H.consumers_of(H.pwlink(), tag)})
    # manual pin: does an unlinked playback stream start flowing?
    pin = []
    for p in trace[-1]["out_ports"]:
        dst = p.split(":")[-1].replace("output_", "")
        target = f"{H.NS}:playback_{dst}"
        pin.append([f"pw-link {p} {target}",
                    H.sh(["pw-link", p, target], timeout=6)[0]])
    time.sleep(1.0)
    mid_after_pin = {"consumers": H.consumers_of(H.pwlink(), tag),
                     "alive": proc.poll() is None}
    try:
        so, se = proc.communicate(timeout=6)
        rc, err, to = proc.returncode, se.decode(errors="replace"), False
    except subprocess.TimeoutExpired:
        proc.kill()
        so, se = proc.communicate()
        rc, err, to = None, se.decode(errors="replace"), True
    wall = round(time.monotonic() - t0, 3)
    time.sleep(0.5)
    caps = mon.stop()
    out["zero_deep"] = {"trace": trace, "pin": pin,
                        "after_pin": mid_after_pin, "rc": rc,
                        "stderr": err.strip()[:300], "wall_s": wall,
                        "timed_out": to, "caps": caps,
                        "carried": [k for k, v in caps.items()
                                    if v["verdict"] in ("mine", "mine_r_tag")]}

    H.unload(m1)
    H.unload(m2)
    for f in os.listdir(H.RAW):
        if f.startswith("r78pmonA2_"):
            lab = f[len("r78pmonA2_"):].rsplit("_", 1)[0]
            if lab not in ("zero_deep", "switched_garbage"):
                os.unlink(os.path.join(H.RAW, f))
    H.save("probe-play-fallback-semantics-r78p.json", out)


if __name__ == "__main__":
    main()
