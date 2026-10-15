#!/usr/bin/env python3
"""B3 — vary the convolver IR (content, rate, length, format, tail) and replay the
sample-exactness pin UNDER LOAD.

The sharp test: the captured post-tap must equal the *file's own quantised IR*
convolved with the delta stimulus, sample by sample. Report the residual in LSBs
of s16, not just "two impulses 64 apart".

argv[1] = reps (default 2), argv[2] = pins reps (default 3).
"""
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig as R

DELTA = "r92b_delta.wav"


def conv_err(an, ir_path, ir_off=0, stim_val=32767.0 / 32768.0, extra_gain=1.0, span=None):
    """Compare the captured post-tap against IR*stim, aligned on the ref impulse."""
    op = an.get("_out_path")
    if not op or not os.path.exists(op):
        return {"err": "no capture"}
    ir = R.wav_read(ir_path)["x"]
    xo = R.wav_read(op)["x"]
    rf = an.get("ref_first")
    if not rf:
        return {"err": "no ref impulse"}
    r0 = rf[0]
    n = span or (len(ir) + 64)
    j0 = ir_off
    seg = xo[r0 + j0: r0 + j0 + n]
    exp = np.zeros(n)
    src = ir[:n]
    exp[:len(src)] = src * stim_val * extra_gain
    m = min(len(seg), n)
    if m <= 0:
        return {"err": "empty window"}
    d = (seg[:m] - exp[:m]) * 32768.0
    return {"n_compared": int(m), "max_abs_err_lsb": round(float(np.max(np.abs(d))), 3),
            "n_over_1lsb": int(np.sum(np.abs(d) > 1.0)), "n_over_2lsb": int(np.sum(np.abs(d) > 2.0)),
            "first_errs_lsb": [round(float(v), 3) for v in d[:6]],
            "max_abs_capture": round(float(np.max(np.abs(xo))), 6)}


def main():
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    pins = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    t0 = time.time()
    S = R.SCRATCH
    R.wav_write(os.path.join(S, DELTA), np.concatenate([np.zeros(100), [1.0], np.zeros(4095)]), fmt="s16")
    R.wav_write(os.path.join(S, "r92b_tone.wav"), R.multitone(R.FREQS, 4.0, amp=0.2), fmt="s16")

    files = {}
    files["2tap"] = R.ir_wav(os.path.join(S, "r92b_ir_2tap.wav"), [(0, 1.0), (64, 0.5)])["path"]
    files["negtap"] = R.ir_wav(os.path.join(S, "r92b_ir_negtap.wav"), [(0, 1.0), (32, -0.5)])["path"]
    files["d100"] = R.ir_wav(os.path.join(S, "r92b_ir_d100.wav"), [(100, 1.0)])["path"]
    files["decay512"] = R.decay_ir(os.path.join(S, "r92b_ir_decay512.wav"), taps_n=512, decay=0.99)["path"]
    # long IR with a spike in the tail: does `tailsize` truncate it?
    tail = np.zeros(4096)
    tail[0] = 1.0
    tail[1500] = 0.9
    files["tail1500"] = R.wav_write(os.path.join(S, "r92b_ir_tail1500.wav"), tail)["path"]
    # same delta at 100 samples, but the IR file claims 44100 Hz
    files["d100_44k"] = R.ir_wav(os.path.join(S, "r92b_ir_d100_44k.wav"), [(100, 1.0)], rate=44100)["path"]
    # stereo IR into a mono chain
    st = np.zeros((4096, 2))
    st[10, 0] = 1.0
    st[20, 1] = 0.7
    files["stereo"] = R.wav_write(os.path.join(S, "r92b_ir_stereo.wav"),
                                  st.reshape(-1), fmt="s16", ch=2)["path"]
    files["s24"] = R.ir_wav(os.path.join(S, "r92b_ir_s24.wav"), [(0, 1.0), (64, 0.5)], fmt="s24")["path"]
    files["f32file"] = R.ir_wav(os.path.join(S, "r92b_ir_f32.wav"), [(0, 1.0), (64, 0.5)], fmt="f32")["path"]
    dc = np.full(64, 1.0 / 64.0)
    files["dc64"] = R.wav_write(os.path.join(S, "r92b_ir_dc64.wav"), dc)["path"]
    # malformed candidates
    files["empty"] = os.path.join(S, "r92b_ir_empty.wav")
    open(files["empty"], "wb").close()
    files["text"] = os.path.join(S, "r92b_ir_text.wav")
    with open(files["text"], "w") as f:
        f.write("this is not a wav file\n" * 40)
    files["dir"] = os.path.join(S, "r92b_ir_dir.wav")
    os.makedirs(files["dir"], exist_ok=True)
    files["missing"] = "/nonexistent/r92b_ir.wav"

    pf = R.preflight()
    out = {"stage": "b3_ir", "reps": reps, "pin_reps": pins, "preflight": pf,
           "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "files": {k: {"path": v, "bytes": os.path.getsize(v) if os.path.exists(v) and os.path.isfile(v) else None}
                     for k, v in files.items()},
           "graphs": {}}

    def ir_args(path, **cfg):
        c = ",".join("%s=%s" % kv for kv in cfg.items())
        return R.fc_args(["{type=builtin,name=cv,label=convolver,config={filename=%s%s}}" %
                          (path, ("," + c) if c else "")])

    def leg(name, args, reps_n, ir_path=None, debug="3", **kw):
        rows = []
        for rep in range(reps_n):
            row = R.run_leg(name, args, "ir", rep, DELTA, debug=debug)
            a = row["analysis"]
            a["_out_path"] = os.path.join(S, "%s_out_%s_%d_%d.wav" % (name, name, rep, row["attempt"]))
            if ir_path:
                a["conv"] = conv_err(a, ir_path, **kw)
            rows.append(row)
            print("b3 %-20s r%d a%d valid=%-5s out=%-7s n_gt=%-4s gap=%-5s ratio=%-10s d=%s %s" %
                  (name, rep, row["attempt"], row["valid"], a.get("out_bytes"), a.get("out_n_gt"),
                   a.get("peak_gap"), a.get("peak_ratio_signed"), a.get("delta_samples"),
                   a.get("conv", {})))
        out["graphs"][name] = {"args": args, "debug": debug, "rows": rows}

    # --- the pins ------------------------------------------------------------
    leg("ir-2tap", ir_args(files["2tap"], blocksize=1024, tailsize=1024, gain=1.0), pins, files["2tap"])
    leg("ir-d100", ir_args(files["d100"], blocksize=1024, tailsize=1024), pins, files["d100"])
    leg("ir-2tap-g0.5", ir_args(files["2tap"], blocksize=1024, tailsize=1024, gain=0.5), pins, files["2tap"],
        extra_gain=0.5)

    # --- delay: the real control name (quoted) actually armed? --------------
    #     0.01 s @48k = 480 samples; max-delay=0.05 -> 2400 samples
    leg("delay-real-q", R.fc_args(['{type=builtin,name=d,label=delay,config={max-delay=0.05},'
                                   'control={"Delay (s)"=0.01}}']), pins)
    leg("delay-real-q-over", R.fc_args(['{type=builtin,name=d,label=delay,config={max-delay=0.05},'
                                        'control={"Delay (s)"=0.1}}']), reps)
    leg("delay-typo", R.fc_args(["{type=builtin,name=d,label=delay,config={max-delay=0.05},"
                                 "control={Delay=0.01}}"]), reps)

    # --- content / rate / length / format variation --------------------------
    leg("ir-negtap", ir_args(files["negtap"], blocksize=1024, tailsize=1024), reps, files["negtap"])
    leg("ir-decay512", ir_args(files["decay512"], blocksize=1024, tailsize=4096), reps, files["decay512"])
    leg("ir-tail1500-t1024", ir_args(files["tail1500"], blocksize=1024, tailsize=1024), reps, files["tail1500"])
    leg("ir-tail1500-t4096", ir_args(files["tail1500"], blocksize=1024, tailsize=4096), reps, files["tail1500"])
    leg("ir-d100-44k", ir_args(files["d100_44k"], blocksize=1024, tailsize=1024), reps, files["d100_44k"])
    leg("ir-stereo", ir_args(files["stereo"], blocksize=1024, tailsize=1024), reps)
    leg("ir-s24", ir_args(files["s24"], blocksize=1024, tailsize=1024), reps)
    leg("ir-f32file", ir_args(files["f32file"], blocksize=1024, tailsize=1024), reps)
    leg("ir-dc64", ir_args(files["dc64"], blocksize=1024, tailsize=1024), reps, files["dc64"])
    leg("ir-gain4", ir_args(files["2tap"], blocksize=1024, tailsize=1024, gain=4.0), reps)
    leg("ir-noconfig", R.fc_args(["{type=builtin,name=cv,label=convolver}"]), reps)
    for bad in ("missing", "empty", "text", "dir"):
        leg("ir-bad-%s" % bad, ir_args(files[bad], blocksize=1024, tailsize=1024), reps)
    # the scout measured "zero [E]/[W]" at PIPEWIRE_DEBUG=3 only: re-arm the two
    # silent legs at level 5 and count the diagnostics at each level.
    leg("ir-bad-missing-dbg5", ir_args(files["missing"], blocksize=1024, tailsize=1024), reps, debug="5")
    leg("ir-noconfig-dbg5", R.fc_args(["{type=builtin,name=cv,label=convolver}"]), reps, debug="5")

    # --- the pins under load -------------------------------------------------
    lg = R.LoadGen(6).start()
    lsink = R.sink_load(R.LOAD_SINK)
    lp = R.Bg(["pw-play", "--target", R.LOAD_SINK, os.path.join(S, "r92b_tone.wav")], wall=90.0)
    time.sleep(1.0)
    out["load"] = {"burners": 6, "sink": lsink, "player_alive": lp.alive()}
    try:
        leg("load-ir-2tap", ir_args(files["2tap"], blocksize=1024, tailsize=1024, gain=1.0), pins, files["2tap"])
    finally:
        lp.stop()
        lg.stop()
        out["load"]["sink_unload"] = R.sink_unload(R.LOAD_SINK, lsink["id"]) if lsink.get("id") else None

    out["elapsed_s"] = round(time.time() - t0, 1)
    out["sweep"] = R.sweep()
    out["final"] = R.live_r92b()
    R.jdump(os.path.join(R.REC, "b3_ir.json"), out)
    print("WROTE b3_ir.json (%.1fs)" % (time.time() - t0))
    print("SWEEP clean:", out["sweep"]["clean"], "final:", out["final"])


if __name__ == "__main__":
    main()
