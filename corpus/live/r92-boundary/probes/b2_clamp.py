#!/usr/bin/env python3
"""B2 — clamp edge-cases and the un-probed surfaces of the biquad control lattice.

Targets (scout claim 9 = "clamping is per-control, not uniform"):
  * Gain exactly at / just past both advertised bounds (max 20, min -120)
  * Q at / past its advertised max (10), negative Q, absurd Q
  * Freq ABOVE Nyquist: identity guard vs alias vs clamp -- 49000/97000 alias
    exactly onto 1000 Hz, so they are a binary discriminator (RBJ(1000) vs 0 dB)
  * Freq = 0 / negative: "silence" -- is it zeros, or NaN written to s16?
    (f32 capture distinguishes)
  * the direct coefficient controls b0,b1,b2,a0,a1,a2 (never fed by the scout),
    including a0 = 0 (division by zero)

argv[1] = reps (default 3).
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig as R

TONE = "r92b_tone.wav"


def main():
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    t0 = time.time()
    R.wav_write(os.path.join(R.SCRATCH, TONE), R.multitone(R.FREQS, 1.2, amp=0.2), fmt="s16")
    pf = R.preflight()
    out = {"stage": "b2_clamp", "reps": reps, "preflight": pf,
           "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "freqs": R.FREQS, "graphs": {}, "fmt_legs": {}}

    ID = {str(f): 0.0 for f in R.FREQS}

    # name -> (node, expected RBJ gains, note)
    legs = [
        ("gain-20",      R.NODE("bq_peaking", Freq=1000.0, Q=1.0, Gain=20.0),   R.rbj_gains("pk", 1000, 1, 20),  "exact advertised max"),
        ("gain-20.5",    R.NODE("bq_peaking", Freq=1000.0, Q=1.0, Gain=20.5),   R.rbj_gains("pk", 1000, 1, 20),  "past max -> clamp?"),
        ("gain--120",    R.NODE("bq_peaking", Freq=1000.0, Q=1.0, Gain=-120.0), R.rbj_gains("pk", 1000, 1, -120), "exact advertised min"),
        ("gain--120.5",  R.NODE("bq_peaking", Freq=1000.0, Q=1.0, Gain=-120.5), R.rbj_gains("pk", 1000, 1, -120), "past min -> clamp?"),
        ("gain-0",       R.NODE("bq_peaking", Freq=1000.0, Q=1.0, Gain=0.0),    R.rbj_gains("pk", 1000, 1, 0),   "zero gain"),
        ("Q-10",         R.NODE("bq_lowpass", Freq=1000.0, Q=10.0),             R.rbj_gains("lp", 1000, 10),     "exact advertised max"),
        ("Q-10.5",       R.NODE("bq_lowpass", Freq=1000.0, Q=10.5),             R.rbj_gains("lp", 1000, 10),     "past max -> clamp?"),
        ("Q--1",         R.NODE("bq_lowpass", Freq=1000.0, Q=-1.0),             R.rbj_gains("lp", 1000, 0),      "negative Q -> 0/default?"),
        ("Q-1e9",        R.NODE("bq_lowpass", Freq=1000.0, Q=1e9),              R.rbj_gains("lp", 1000, 10),     "absurd Q -> clamp?"),
        ("freq-49000",   R.NODE("bq_lowpass", Freq=49000.0, Q=0.707),           R.rbj_gains("lp", 1000, 0.707),  "alias->1000Hz if unguarded"),
        ("freq-97000",   R.NODE("bq_lowpass", Freq=97000.0, Q=0.707),           R.rbj_gains("lp", 1000, 0.707),  "double alias->1000Hz"),
        ("freq-24000",   R.NODE("bq_lowpass", Freq=24000.0, Q=0.707),           R.rbj_gains("lp", 24000, 0.707), "exactly Nyquist"),
        ("freq-24001",   R.NODE("bq_lowpass", Freq=24001.0, Q=0.707),           R.rbj_gains("lp", 24001, 0.707), "1 Hz past Nyquist"),
        ("freq-0",       R.NODE("bq_lowpass", Freq=0.0, Q=0.707),               R.rbj_gains("lp", 0.5, 0.707),   "degenerate (scout: silence)"),
        ("freq-neg",     R.NODE("bq_lowpass", Freq=-1000.0, Q=0.707),           R.rbj_gains("lp", -1000, 0.707), "negative (scout: silence)"),
        ("coef-unity",   R.NODE("bq_lowpass", Freq=1000.0, Q=0.707, b0=1, b1=0, b2=0, a0=1, a1=0, a2=0), ID, "direct coeff override -> unity?"),
        ("coef-a0zero",  R.NODE("bq_lowpass", Freq=1000.0, Q=0.707, b0=1, b1=0, b2=0, a0=0, a1=0, a2=0), None, "a0=0 -> div by zero"),
    ]

    for name, node, ref, note in legs:
        args = R.fc_args([node])
        rows = []
        for rep in range(reps):
            row = R.run_leg(name, args, "dsp", rep, TONE)
            rows.append(row)
            a = row["analysis"]
            print("b2 %-13s r%d a%d valid=%-5s out=%-7s %s | ref %s" %
                  (name, rep, row["attempt"], row["valid"], a.get("out_bytes"),
                   a.get("gain_db"), ref))
        out["graphs"][name] = {"args": args, "rbj": ref, "note": note, "rows": rows}

    # ---- f32 captures for the legs whose value is below the s16 floor -------
    fmt_legs = [
        ("f32-gain--120",  R.NODE("bq_peaking", Freq=1000.0, Q=1.0, Gain=-120.0)),
        ("f32-gain--120.5", R.NODE("bq_peaking", Freq=1000.0, Q=1.0, Gain=-120.5)),
        ("f32-freq-0",     R.NODE("bq_lowpass", Freq=0.0, Q=0.707)),
        ("f32-freq-neg",   R.NODE("bq_lowpass", Freq=-1000.0, Q=0.707)),
        ("f32-coef-a0zero", R.NODE("bq_lowpass", Freq=1000.0, Q=0.707, b0=1, b1=0, b2=0, a0=0, a1=0, a2=0)),
        ("f32-notch",      R.NODE("bq_notch", Freq=1000.0, Q=1.0)),
    ]
    for name, node in fmt_legs:
        args = R.fc_args([node])
        rows = []
        for rep in range(reps):
            row = R.run_leg(name, args, "dsp", rep, TONE, fmt="f32")
            rows.append(row)
            a = row["analysis"]
            print("b2 %-17s r%d valid=%-5s out_fmt=%s out=%-7s %s stats=%s" %
                  (name, rep, row["valid"], a.get("out_fmt"), a.get("out_bytes"),
                   a.get("gain_db"), a.get("out_stats")))
        out["fmt_legs"][name] = {"args": args, "rows": rows}

    out["elapsed_s"] = round(time.time() - t0, 1)

    # ---- pw-cli EOF abort (claim 10) — client-only, no graph contact --------
    eof = []
    for rep in range(3):
        r = R.run(["pw-cli"], wall=8.0, stdin_data=b"")
        eof.append({"rc": r.rc, "timed_out": r.timed_out, "err": r.err.strip()[-300:],
                    "out": r.out.strip()[-200:]})
        print("b2 pw-cli-eof r%d rc=%s err=%r" % (rep, r.rc, r.err.strip()[-160:]))
    quit_ok = []
    for rep in range(3):
        r = R.run(["pw-cli"], wall=8.0, stdin_data=b"quit\n")
        quit_ok.append({"rc": r.rc, "out": r.out.strip()[-200:]})
        print("b2 pw-cli-quit r%d rc=%s" % (rep, r.rc))
    out["pwcli_eof"] = {"eof": eof, "quit": quit_ok}

    out["sweep"] = R.sweep()
    out["final"] = R.live_r92b()
    R.jdump(os.path.join(R.REC, "b2_clamp.json"), out)
    print("WROTE b2_clamp.json (%.1fs)" % (time.time() - t0))
    print("SWEEP clean:", out["sweep"]["clean"], "final:", out["final"])


if __name__ == "__main__":
    main()
