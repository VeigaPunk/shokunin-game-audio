#!/usr/bin/env python3
"""r84b sivolpin — discriminator matrix for monitor-stream tap visibility of
set-sink-input-volume mid-run. Varies: restore-key entry state (fresh role vs
existing Music entry vs pre-written entry) and action (volume vs mute).
Namespace r84b_*. No tracked writes."""
import json, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r84b_probe as R

PROBE = "pF4-sivolpin"

def spawn(role, name, wav, role_prop=True):
    cmd = ["pw-play", "-P", f"node.name={name}"]
    if role_prop: cmd += ["-P", f"media.role={role}"]
    cmd += ["--target", R.NS, wav]
    return R.Proc(cmd)

def prewrite(role, pct):
    p = spawn(role, "r84b_pre", R.tone_short())
    time.sleep(0.5)
    ia = R.si_index("r84b_pre")
    r = R.run(["pactl", "set-sink-input-volume", str(ia), pct], 4)
    for _ in range(40):
        if not p.alive(): break
        time.sleep(0.1)
    p.finish(); time.sleep(0.3)
    return r["rc"]

def run_leg(tag, role, pre, action):
    pa = spawn(role, "r84b_ta", R.tone_long(9))
    pb = spawn(role, "r84b_tb", R.tone_b())
    time.sleep(0.6)
    ia = R.si_index("r84b_ta")
    pre_si = R.si_witness("r84b_ta")
    p, o = R.parec_pin(["-d", R.NS, "--monitor-stream", str(ia)], 6.6, tag)
    acts = [(2.4, ["pactl", "set-sink-input-volume", str(ia), "50%"])] if action == "vol" else \
           [(2.4, ["pactl", "set-sink-input-mute", str(ia), "1"]),
            (4.4, ["pactl", "set-sink-input-mute", str(ia), "0"])]
    r, x, _o = R.fin_parec(p, o, 6.6, actions=acts)
    time.sleep(0.3)
    post_si = R.si_witness("r84b_ta")
    w = R.windows(_o, win=0.25)
    before = [row["peak"] for row in w if 1.0 <= row["t0"] <= 2.2]
    after = [row["peak"] for row in w if 2.6 <= row["t0"] <= 4.2]
    extra = {"role": role, "prewrite": pre, "action": action, "idxA": ia,
             "pre_si": pre_si, "post_si": post_si,
             "amps_before": before, "amps_after": after, "sig": x["sig"]}
    R.record_leg(PROBE, tag, 0, r, extra)
    pa.kill(); pb.kill(); pa.finish(); pb.finish()
    try: _o.unlink()
    except FileNotFoundError: pass
    time.sleep(0.3)
    return extra

def main():
    results = {"loadavg_start": R.loadavg()}
    s1 = R.load_ns(R.NS)
    assert s1["verified"]
    try:
        matrix = [
            ("D1_music_noentry",   "Music",      None, "vol"),
            ("D2_fresh_noentry",   "R84Bfresh1", None, "vol"),
            ("D3_music_prewrite100", "Music",    "100%", "vol"),
            ("D4_music_noentry_rep", "Music",    None, "vol"),
            ("D5_fresh_mute",      "R84Bfresh2", None, "mute"),
        ]
        for tag, role, pre, action in matrix:
            rc = prewrite(role, pre) if pre else None
            ex = run_leg(tag, role, pre, action)
            ex["prewrite_rc"] = rc
            results[tag] = ex
            print(f"{tag:22s} pre_si={ex['pre_si'][0]['value_percent'] if ex['pre_si'] else None} "
                  f"post_si={ex['post_si'][0]['value_percent'] if ex['post_si'] else None} "
                  f"before={ex['amps_before']} after={ex['amps_after']} sig={ex['sig']}")
        results["loadavg_end"] = R.loadavg()
        (R.RCPTS / "pF4-sivolpin.json").write_text(json.dumps(results, indent=1))
    finally:
        R.unload_idx(s1["idx"], R.NS)
    print("DONE sivolpin")

if __name__ == "__main__":
    sys.exit(main() or 0)
