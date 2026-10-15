#!/usr/bin/env python3
"""Probe A3 — (1) real default-sink switch semantics, (2) `--target 0` pin law.

A2 found `pactl set-default-sink X` returns rc=0 but does NOT change the
default (verified twice: get-default-sink + `pw-metadata -n default`).  So the
native switch is `pw-metadata -n default 0 default.audio.sink '{"name":X}'`.

A2 also found `--target 0` publishing ports, never linking, stalling — then
consuming the file to completion after a manual `pw-link` pin, yet the pinned
sink's monitor stayed silent.  That contradiction is measured here.
"""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r78p as H


def md_get():
    rc, out, err, _, _ = H.sh(["pw-metadata", "-n", "default"], timeout=6)
    for l in out.decode(errors="replace").splitlines():
        if "default.audio.sink" in l:
            return l.split("value:")[-1].strip()
    return None


def md_set(name):
    rc, out, err, _, _ = H.sh(
        ["pw-metadata", "-n", "default", "0", "default.audio.sink",
         json.dumps({"name": name})], timeout=6)
    return {"rc": rc, "err": err.strip()[:120], "now": md_get()}


def run_leg(label, args, out, timeout=9.0, tone=None):
    tag = "r78pA3_" + label
    argv = ["pw-play", "-P", f"node.name={tag}", *args, tone or H.TONE]
    mon = H.Monitors(tag="r78pmonA3_" + label)
    leg = H.one_leg(mon, argv, tag, probe_at=0.85, timeout=timeout,
                    sample_every=0.4)
    leg["label"], leg["requested"] = label, args
    out["legs"].append(leg)
    print(f"{label:26s} rc={leg['rc']} wall={leg['wall_s']:5.2f} "
          f"mine={leg['carried']} foreign={leg['foreign']} "
          f"links={sorted({p for v in leg['mid'].get('links', {}).values() for p in v})} "
          f"tgt={leg['mid'].get('props', {}).get('target.object')}", flush=True)
    return leg


def node_id(name):
    for n, props in H.pw_nodes().items():
        if n == name:
            return props.get("object.id") or props.get("object.serial")
    return None


def pwcli_info(nid):
    rc, out, err, _, _ = H.sh(["pw-cli", "info", str(nid)], timeout=6)
    txt = out.decode(errors="replace")
    keep = [l.strip() for l in txt.splitlines()
            if any(k in l for k in ("state", "format", "error", "id:", "name"))]
    return keep[:14]


def pwtop(tag):
    rc, out, err, _, _ = H.sh(["pw-top", "-b", "-n", "1"], timeout=8)
    return [l.rstrip() for l in out.decode(errors="replace").splitlines()
            if tag in l or "ERR" in l][:6]


def sink_inputs(tag):
    rc, out, err, _, _ = H.sh(["pactl", "-f", "json", "list", "sink-inputs"],
                              timeout=8)
    try:
        d = json.loads(out.decode(errors="replace"))
    except Exception:
        return []
    res = []
    for si in d:
        p = si.get("properties", {})
        if tag in str(p.get("node.name")) or tag in str(
                p.get("application.name")):
            res.append({"index": si.get("index"), "sink": si.get("sink"),
                        "props": {k: p.get(k) for k in
                                  ("node.name", "application.name",
                                   "target.object")}})
    return res


def pin_leg(label, pin_to, out, stall=1.5, tone=None, deadline=14.0):
    """Play with --target 0, stall, then pin both output ports to pin_to."""
    tag = "r78pA3_" + label
    mon = H.Monitors(tag="r78pmonA3_" + label)
    mon.start()
    argv = ["pw-play", "-P", f"node.name={tag}", "--target", "0",
            tone or H.TONE]
    t0 = time.monotonic()
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    rec = {"label": label, "argv": argv, "pin_to": pin_to, "pre": {},
           "post": {}}
    time.sleep(stall)
    nid = node_id(tag)
    rec["pre"] = {"t": round(time.monotonic() - t0, 2),
                  "alive": proc.poll() is None,
                  "consumers": H.consumers_of(H.pwlink(), tag),
                  "pw_cli": pwcli_info(nid) if nid else None,
                  "pw_top": pwtop(tag),
                  "sink_inputs": sink_inputs(tag),
                  "file_bytes_expected": os.path.getsize(tone or H.TONE)}
    res = []
    for ch in ("FL", "FR"):
        res.append([f"pw-link {tag}:output_{ch} {pin_to}:playback_{ch}",
                    H.sh(["pw-link", f"{tag}:output_{ch}",
                          f"{pin_to}:playback_{ch}"], timeout=6)[0]])
    rec["pin"] = res
    time.sleep(1.0)
    rec["post"] = {"t": round(time.monotonic() - t0, 2),
                   "alive": proc.poll() is None,
                   "consumers": H.consumers_of(H.pwlink(), tag),
                   "pw_top": pwtop(tag),
                   "sink_inputs": sink_inputs(tag),
                   "ns_monitor_link": H.producers_of(H.pwlink(),
                                                     f"r78pmonA3_{label}_ns")}
    try:
        so, se = proc.communicate(timeout=max(1.0, deadline -
                                              (time.monotonic() - t0)))
        rc, err, to = proc.returncode, se.decode(errors="replace"), False
    except subprocess.TimeoutExpired:
        proc.kill()
        so, se = proc.communicate()
        rc, err, to = None, se.decode(errors="replace"), True
    rec.update({"rc": rc, "stderr": err.strip()[:300],
                "wall_s": round(time.monotonic() - t0, 3), "timed_out": to})
    time.sleep(0.6)
    caps = mon.stop()
    rec["caps"] = caps
    rec["carried"] = [k for k, v in caps.items()
                      if v["verdict"] in ("mine", "mine_r_tag")]
    rec["tone_windows"] = {k: v["mine"] for k, v in caps.items() if v["mine"]}
    out["pin_legs"].append(rec)
    print(f"{label:26s} rc={rc} wall={rec['wall_s']:5.2f} mine={rec['carried']} "
          f"tone_windows={rec['tone_windows']} pre_top={rec['pre']['pw_top']} "
          f"post_cons={rec['post']['consumers']}", flush=True)
    return rec


def main():
    out = {"probe": "playback-defaults-and-zero-pin-r78p", "legs": [],
           "pin_legs": [], "toolchain": H.toolchain()}
    m1, _, _ = H.load_null(H.NS)
    m2, _, _ = H.load_null(H.NS2)
    time.sleep(0.5)
    H.make_tone(dur=1.6)
    TONE6 = os.path.join(H.RAW, "tone_r78p_6s.wav")
    H.make_tone(TONE6, dur=6.0)

    out["md_before"] = md_get()
    out["switch_to_spk"] = md_set(H.S_SPK)
    time.sleep(0.6)
    run_leg("md_spk_no_target", [], out)
    run_leg("md_spk_garbage", ["--target", "no_such_sink_xyz"], out)
    run_leg("md_spk_at_default_sink", ["--target", "@DEFAULT_SINK@"], out)
    run_leg("md_spk_default_word", ["--target", "default"], out)
    run_leg("md_spk_explicit_spk", ["--target", H.S_SPK], out)
    run_leg("md_spk_explicit_spdif", ["--target", H.S_SPDIF], out)
    out["switch_back"] = md_set(H.S_SPDIF)
    time.sleep(0.6)
    run_leg("md_back_no_target", [], out)
    run_leg("md_back_garbage", ["--target", "no_such_sink_xyz"], out)

    # ---- pin law --------------------------------------------------------
    pin_leg("pin_baseline", H.NS, out, stall=0.0, tone=H.TONE)
    pin_leg("pin_ns", H.NS, out, stall=1.5, tone=H.TONE)
    pin_leg("pin_spdif", H.S_SPDIF, out, stall=1.5, tone=H.TONE)
    pin_leg("pin_ns_6s", H.NS, out, stall=1.5, tone=TONE6, deadline=14.0)

    H.unload(m1)
    H.unload(m2)
    for f in os.listdir(H.RAW):
        if f.startswith("r78pmonA3_"):
            lab = f[len("r78pmonA3_"):].rsplit("_", 1)[0]
            if lab not in ("pin_ns", "pin_spdif", "md_spk_garbage"):
                os.unlink(os.path.join(H.RAW, f))
    H.save("probe-play-defaults-pin-r78p.json", out)


if __name__ == "__main__":
    main()
