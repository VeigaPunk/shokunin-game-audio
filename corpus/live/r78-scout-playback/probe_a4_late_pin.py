#!/usr/bin/env python3
"""Probe A4 — mechanism of the late-pin silence.

A3: pinning an unlinked `--target 0` playback stream IMMEDIATELY carries audio;
pinning it 1.5 s later creates the links, lets pw-play consume the file at
real-time rate (rc=0), and delivers pure digital silence to every monitor.
`pw-cli info` showed the unlinked stream `state: "suspended"`.

This probe asks: whose suspension is it — the stream's or the SINK's — and what
un-suspends it (sink resume / a second normal stream / a re-link)?
"""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r78p as H

TONE6 = os.path.join(H.RAW, "tone_r78p_6s.wav")
TONE_B = os.path.join(H.RAW, "tone_b_2k3k.wav")   # L 2 kHz / R 3 kHz


def nid(name):
    for n, props in H.pw_nodes().items():
        if n == name:
            return props.get("object.id") or props.get("object.serial")
    return None


def state_of(name):
    i = nid(name)
    if i is None:
        return None
    rc, out, err, _, _ = H.sh(["pw-cli", "info", str(i)], timeout=6)
    for l in out.decode(errors="replace").splitlines():
        if "state:" in l:
            return l.strip().strip('*').strip()
    return "?"


def main():
    out = {"probe": "playback-late-pin-mechanism-r78p", "legs": [],
           "toolchain": H.toolchain()}
    m1, _, _ = H.load_null(H.NS)
    time.sleep(0.5)
    H.make_tone(dur=1.6)
    H.make_tone(TONE6, dur=6.0)
    H.make_tone(TONE_B, dur=1.6, freq=2000.0)

    def leg(label, stall, tone, actions=(), win=0.25, deadline=14.0,
            control_at=None):
        tag = "r78pA4_" + label
        mon = H.Monitors(tag="r78pmonA4_" + label, win=win)
        mon.start()
        argv = ["pw-play", "-P", f"node.name={tag}", "--target", "0", tone]
        t0 = time.monotonic()
        proc = subprocess.Popen(argv, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        rec = {"label": label, "argv": argv, "samples": [], "actions": []}
        ctrl_proc = None
        if stall:
            time.sleep(stall)
        rec["samples"].append({
            "t": round(time.monotonic() - t0, 2), "when": "pre-pin",
            "stream_state": state_of(tag), "sink_state": state_of(H.NS),
            "consumers": H.consumers_of(H.pwlink(), tag)})
        res = []
        for ch in ("FL", "FR"):
            res.append([f"pin {ch}", H.sh(
                ["pw-link", f"{tag}:output_{ch}",
                 f"{H.NS}:playback_{ch}"], timeout=6)[0]])
        rec["actions"].append({"pin": res})
        for at, name, fn in actions:
            while time.monotonic() - t0 < at:
                time.sleep(0.05)
            r = fn(tag)
            rec["actions"].append({"t": round(time.monotonic() - t0, 2),
                                   "event": name, "result": r})
        if control_at:
            while time.monotonic() - t0 < control_at:
                time.sleep(0.05)
            ctrl_proc = subprocess.Popen(
                ["pw-play", "-P", "node.name=r78pA4_ctrlB", "--target", H.NS,
                 TONE_B], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            rec["actions"].append({"t": round(time.monotonic() - t0, 2),
                                   "event": "control_B_play", "result": "ok"})
        for k in range(4):
            time.sleep(0.5)
            rec["samples"].append({
                "t": round(time.monotonic() - t0, 2), "when": f"post{k}",
                "stream_state": state_of(tag), "sink_state": state_of(H.NS),
                "consumers": H.consumers_of(H.pwlink(), tag),
                "alive": proc.poll() is None})
        if ctrl_proc:
            try:
                ctrl_proc.wait(timeout=4)
            except subprocess.TimeoutExpired:
                ctrl_proc.kill()
        try:
            so, se = proc.communicate(timeout=max(1.0, deadline -
                                                  (time.monotonic() - t0)))
            rc, err, to = proc.returncode, se.decode(errors="replace"), False
        except subprocess.TimeoutExpired:
            proc.kill()
            so, se = proc.communicate()
            rc, err, to = None, se.decode(errors="replace"), True
        rec.update({"rc": rc, "stderr": err.strip()[:200],
                    "wall_s": round(time.monotonic() - t0, 3),
                    "timed_out": to})
        time.sleep(0.4)
        caps = mon.stop()
        rec["caps"] = caps
        rec["tone_windows"] = {k: v["mine"] for k, v in caps.items()
                               if v["mine"]}
        rec["rtag_windows"] = {k: v["mine_r_tag"] for k, v in caps.items()
                               if v["mine_r_tag"]}
        rec["foreign_windows"] = {k: v["foreign"] for k, v in caps.items()
                                  if v["foreign"]}
        rec["carried"] = [k for k, v in caps.items()
                          if v["verdict"] in ("mine", "mine_r_tag")]
        out["legs"].append(rec)
        print(f"{label:20s} rc={rc} wall={rec['wall_s']:5.2f} "
              f"mine={rec['carried']} windows={rec['tone_windows']} "
              f"rtag={rec['rtag_windows']} foreign={rec['foreign_windows']}",
              flush=True)
        return rec

    def resume_sink(tag):
        a = H.pactl("suspend-sink", H.NS, "1")
        time.sleep(0.3)
        b = H.pactl("suspend-sink", H.NS, "0")
        return {"suspend1": a[0], "suspend0": b[0]}

    def relink(tag):
        r = []
        for ch in ("FL", "FR"):
            r.append(H.sh(["pw-link", "-d", f"{tag}:output_{ch}",
                           f"{H.NS}:playback_{ch}"], timeout=5)[0])
        time.sleep(0.3)
        for ch in ("FL", "FR"):
            r.append(H.sh(["pw-link", f"{tag}:output_{ch}",
                           f"{H.NS}:playback_{ch}"], timeout=5)[0])
        return r

    def link_spdif(tag):
        r = []
        for ch in ("FL", "FR"):
            r.append(H.sh(["pw-link", f"{tag}:output_{ch}",
                           f"{H.S_SPDIF}:playback_{ch}"], timeout=5)[0])
        return r

    leg("early_pin", 0.0, H.TONE)
    leg("late_pin", 1.5, H.TONE)
    leg("late_pin_resume", 1.5, TONE6, actions=[(2.2, "resume_sink",
                                                resume_sink)])
    leg("late_pin_relink", 1.5, TONE6, actions=[(2.2, "relink", relink)])
    leg("late_pin_control_b", 1.5, TONE6, control_at=4.0)
    leg("late_pin_then_spdif", 1.5, TONE6, actions=[(2.2, "link_spdif",
                                                    link_spdif)])

    H.unload(m1)
    # keep the ns witness for every leg + spdif for the two key legs
    for f in os.listdir(H.RAW):
        if f.startswith("r78pmonA4_"):
            keep = f.endswith("_ns.wav") or (
                f.endswith("_spdif.wav")
                and (f.startswith("r78pmonA4_late_pin_") or
                     f.startswith("r78pmonA4_late_pin_ctrl")))
            if not keep:
                os.unlink(os.path.join(H.RAW, f))
    H.save("probe-play-late-pin-r78p.json", out)


if __name__ == "__main__":
    main()
