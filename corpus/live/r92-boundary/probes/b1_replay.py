#!/usr/bin/env python3
"""B1 — replay the r92 scout's §3 transfer-function pins with an INDEPENDENT
instrument, and re-measure the two report rows its own receipts contradict.

Also: the notch floor in s16 vs f32 (is -93.977 dB a filter response or the
capture-format floor?), and the `delay` control-name class.

argv[1] = reps (default 3).
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig as R

TONE = "r92b_tone.wav"
TONE1K = "r92b_tone1k.wav"


def build_stim():
    R.wav_write(os.path.join(R.SCRATCH, TONE), R.multitone(R.FREQS, 1.2, amp=0.2), fmt="s16")
    R.wav_write(os.path.join(R.SCRATCH, TONE1K), R.single_tone(1000.0, 1.2, amp=0.5), fmt="s16")


# name -> (label, f0, q, gain, rbj_label, links)
GRAPHS = {
    "copy":              ("copy", None, None, None, None),
    "bq_lowpass-1000":   ("bq_lowpass", 1000.0, 0.707, None, "lp"),
    "bq_highpass-1000":  ("bq_highpass", 1000.0, 0.707, None, "hp"),
    "bq_peaking-1000-p6": ("bq_peaking", 1000.0, 1.0, 6.0, "pk"),
    "bq_peaking-1000-m6": ("bq_peaking", 1000.0, 1.0, -6.0, "pk"),
    "bq_notch-1000":     ("bq_notch", 1000.0, 1.0, None, "nt"),
    "bq_allpass-1000":   ("bq_allpass", 1000.0, 1.0, None, "ap"),
    "bq_lowshelf-200-p6": ("bq_lowshelf", 200.0, 0.707, 6.0, "ls"),
    "bq_highshelf-4000-m6": ("bq_highshelf", 4000.0, 0.707, -6.0, "hs"),   # CONTESTED
    "bq_bandpass-1000":  ("bq_bandpass", 1000.0, 1.0, None, "bp"),         # CONTESTED
    "invert":            ("invert", None, None, None, None),
}


def main():
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    t0 = time.time()
    build_stim()
    pf = R.preflight()
    out = {"stage": "b1_replay", "reps": reps, "preflight": pf,
           "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "freqs": R.FREQS, "rate": R.RATE, "win": R.WIN, "graphs": {}}

    for name, (label, f0, q, g, rl) in GRAPHS.items():
        ctl = {}
        if f0 is not None:
            ctl["Freq"] = f0
        if q is not None:
            ctl["Q"] = q
        if g is not None:
            ctl["Gain"] = g
        args = R.fc_args([R.NODE(label, **ctl)])
        ref = R.rbj_gains(rl, f0, q, g or 0.0) if rl else {str(f): 0.0 for f in R.FREQS}
        rows = []
        for rep in range(reps):
            row = R.run_leg(name, args, "dsp", rep, TONE)
            rows.append(row)
            a = row["analysis"]
            print("b1 %-22s r%d a%d valid=%-5s out=%-7s %s | rbj %s" %
                  (name, rep, row["attempt"], row["valid"], a.get("out_bytes"),
                   a.get("gain_db"), ref))
        out["graphs"][name] = {"args": args, "rbj": ref, "rows": rows}

    # ---- param_eq (same peaking) -------------------------------------------
    pe = ("{type=builtin,name=pe,label=param_eq,"
          "config={filters=[{type=bq_peaking,freq=1000.0,gain=6.0,q=1.0}]}}")
    args = R.fc_args([pe])
    rows = []
    for rep in range(reps):
        row = R.run_leg("param_eq", args, "dsp", rep, TONE)
        rows.append(row)
        print("b1 param_eq r%d valid=%s %s" % (rep, row["valid"], row["analysis"].get("gain_db")))
    out["graphs"]["param_eq"] = {"args": args, "rbj": R.rbj_gains("pk", 1000.0, 1.0, 6.0), "rows": rows}

    # ---- the `delay` control-name class ------------------------------------
    dl = ("{type=builtin,name=d,label=delay,config={max-delay=0.05},"
          "control={Delay=0.01}}")
    dl_real = ("{type=builtin,name=d,label=delay,config={max-delay=0.05},"
               "control={Delay (s)=0.01}}")
    dl_q = ("{type=builtin,name=d,label=delay,config={max-delay=0.05},"
            'control={"Delay (s)"=0.01}}')
    for nm, tok in (("delay-typo", dl), ("delay-realname", dl_real), ("delay-realname-q", dl_q)):
        args = R.fc_args([tok])
        rows = []
        for rep in range(reps):
            row = R.run_leg(nm, args, "dsp", rep, TONE)
            rows.append(row)
            print("b1 %-20s r%d valid=%-5s out=%-7s %s" %
                  (nm, rep, row["valid"], row["analysis"].get("out_bytes"), row["analysis"].get("gain_db")))
        out["graphs"][nm] = {"args": args, "rbj": None, "rows": rows}

    # ---- notch floor: s16 vs f32 -------------------------------------------
    nargs = R.fc_args([R.NODE("bq_notch", Freq=1000.0, Q=1.0)])
    out["notch_floor"] = {}
    for fmt in ("s16", "f32"):
        rows = []
        for rep in range(reps):
            row = R.run_leg("notch-%s" % fmt, nargs, "dsp", rep, TONE1K, fmt=fmt)
            rows.append(row)
            a = row["analysis"]
            print("b1 notch-%-3s r%d valid=%-5s out_fmt=%s out_bytes=%s stats=%s gain=%s" %
                  (fmt, rep, row["valid"], a.get("out_fmt"), a.get("out_bytes"),
                   a.get("out_stats"), a.get("gain_db")))
        out["notch_floor"][fmt] = {"args": nargs, "rows": rows}

    out["elapsed_s"] = round(time.time() - t0, 1)
    out["sweep"] = R.sweep()
    out["final"] = R.live_r92b()
    R.jdump(os.path.join(R.REC, "b1_replay.json"), out)
    print("WROTE b1_replay.json (%.1fs)" % (time.time() - t0))
    print("SWEEP clean:", out["sweep"]["clean"], "final:", out["final"])


if __name__ == "__main__":
    main()
