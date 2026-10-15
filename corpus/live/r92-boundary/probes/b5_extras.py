#!/usr/bin/env python3
"""B5 — small closed edges the scout left open (`[?]` items) + two guards:

  * Freq = -24000: the RBJ formula at negative Nyquist is the *identity*
    (b == a), while a "negative freq -> zeros" guard gives digital silence.
    Binary discriminator between "guard" and "formula".
  * `bq_raw`: the per-label raw-coefficient path (scout unknown #6) — does it
    accept `control={b0..a2}` / `config={coefficients=[...]}`?
  * `Gain` on `bq_lowpass`: is the advertised Gain port inert for a label that
    does not use it (advertisement != objects, applied to a control)?

argv[1] = reps (default 2).
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig as R

TONE = "r92b_tone.wav"
COEF = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]     # identity biquad
LP = R.rbj_gains("lp", 1000, 0.707)        # int keys
ID = {f: 0.0 for f in R.FREQS}


def main():
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    t0 = time.time()
    if not os.path.exists(os.path.join(R.SCRATCH, TONE)):
        R.wav_write(os.path.join(R.SCRATCH, TONE), R.multitone(R.FREQS, 1.2, amp=0.2), fmt="s16")
    pf = R.preflight()
    out = {"stage": "b5_extras", "reps": reps, "preflight": pf,
           "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "graphs": {}}

    legs = [
        ("freq--24000", R.NODE("bq_lowpass", Freq=-24000.0, Q=0.707),
         {"identity_0dB": ID, "zeros": "exact digital silence"},
         "guard vs formula discriminator"),
        ("freq-tiny", R.NODE("bq_lowpass", Freq=1e-9, Q=0.707), None, "sub-Hz freq"),
        ("bqraw-coefctl", R.NODE("bq_raw", b0=1.0, b1=0.0, b2=0.0, a0=1.0, a1=0.0, a2=0.0), None,
         "raw label, coeffs via control"),
        ("bqraw-noconfig", R.NODE("bq_raw"), None, "raw label, no config"),
        ("bqraw-coefcfg", "{type=builtin,name=r,label=bq_raw,config={coefficients=[1.0,0.0,0.0,1.0,0.0,0.0]}}",
         None, "raw label, coeffs via config"),
        ("lowpass-gain6", R.NODE("bq_lowpass", Freq=1000.0, Q=0.707, Gain=6.0), LP,
         "is Gain inert on a label that does not use it?"),
    ]
    for name, node, ref, note in legs:
        args = R.fc_args([node])
        rows = []
        for rep in range(reps):
            row = R.run_leg(name, args, "dsp", rep, TONE)
            rows.append(row)
            a = row["analysis"]
            print("b5 %-16s r%d valid=%-5s out=%-7s %s | ref %s" %
                  (name, rep, row["valid"], a.get("out_bytes"), a.get("gain_db"), ref))
            print("      log:", [l for l in row["fc_log"] if "[E]" in l or "[W]" in l or "loaded n_" in l][:3])
        out["graphs"][name] = {"args": args, "rbj": ref, "note": note, "rows": rows}

    out["elapsed_s"] = round(time.time() - t0, 1)
    out["sweep"] = R.sweep()
    out["final"] = R.live_r92b()
    R.jdump(os.path.join(R.REC, "b5_extras.json"), out)
    print("WROTE b5_extras.json (%.1fs)" % (time.time() - t0))
    print("SWEEP clean:", out["sweep"]["clean"], "final:", out["final"])


if __name__ == "__main__":
    main()
