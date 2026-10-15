#!/usr/bin/env python3
"""Post-hoc analysis of the B3 IR captures: alignment-corrected sample-exactness,
the resampled-kernel shape of a 44.1 kHz IR, the stereo-IR channel choice, and
the delay legs' true shift. Read-only over scratch/*.wav.

usage: python3 analyze_ir.py [out.json]
"""
import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig as R

S = R.SCRATCH
STIM = 32767.0 / 32768.0


def ir_of(name):
    p = os.path.join(S, name)
    x = R.wav_read(p)["x"]
    if x.ndim > 1:
        x = x[:, 0]
    return x


def best_align(xo, exp, ref_first, lo=-4096, hi=4096, span=4096):
    best = None
    for lag in range(lo, hi + 1):
        i0 = ref_first + lag
        if i0 < 0 or i0 + span > len(xo):
            continue
        d = (xo[i0:i0 + span] - exp[:span]) * 32768.0
        r = float(np.max(np.abs(d)))
        if best is None or r < best[1]:
            best = (lag, r)
    return best


def main():
    outp = sys.argv[1] if len(sys.argv) > 1 else os.path.join(R.REC, "b3_posthoc.json")
    res = {}

    # ---- convolver legs: residual at the best lag --------------------------
    cases = {
        "ir-2tap": ("r92b_ir_2tap.wav", 1.0),
        "ir-2tap-g0.5": ("r92b_ir_2tap.wav", 0.5),
        "load-ir-2tap": ("r92b_ir_2tap.wav", 1.0),
        "ir-d100": ("r92b_ir_d100.wav", 1.0),
        "ir-decay512": ("r92b_ir_decay512.wav", 1.0),
        "ir-tail1500-t1024": ("r92b_ir_tail1500.wav", 1.0),
        "ir-tail1500-t4096": ("r92b_ir_tail1500.wav", 1.0),
        "ir-dc64": ("r92b_ir_dc64.wav", 1.0),
        "ir-s24": ("r92b_ir_s24.wav", 1.0),
        "ir-f32file": ("r92b_ir_f32.wav", 1.0),
    }
    for leg, (irf, g) in cases.items():
        ir = ir_of(irf)
        exp = np.zeros(8192)
        m = min(len(ir), 8192)
        exp[:m] = ir[:m] * STIM * g
        rows = []
        for op in sorted(glob.glob(os.path.join(S, "%s_out_*_0.wav" % leg))):
            rp = op.replace("_out_", "_ref_")
            if not os.path.exists(rp):
                continue
            xo = R.wav_read(op)["x"]
            xr = R.wav_read(rp)["x"]
            rf = np.nonzero(np.abs(xr) > 1e-4)[0]
            if not len(rf):
                rows.append({"out": os.path.basename(op), "err": "no ref impulse"})
                continue
            r0 = int(rf[0])
            lag, r = best_align(xo, exp, r0)
            rows.append({"out": os.path.basename(op), "ref_first": r0, "best_lag": lag,
                         "max_err_lsb_at_best_lag": round(r, 3),
                         "out_len": len(xo), "ir_len": len(ir)})
        res[leg] = rows
        print("%-20s %s" % (leg, [(x.get("best_lag"), x.get("max_err_lsb_at_best_lag")) for x in rows]))

    # ---- 44.1 kHz IR: shape of the rate-converted kernel -------------------
    for op in sorted(glob.glob(os.path.join(S, "ir-d100-44k_out_*_0.wav"))):
        rp = op.replace("_out_", "_ref_")
        xo = R.wav_read(op)["x"]
        xr = R.wav_read(rp)["x"]
        r0 = int(np.nonzero(np.abs(xr) > 1e-4)[0][0])
        seg = xo[r0:r0 + 4096]
        nz = np.nonzero(np.abs(seg) > 1e-5)[0]
        pk = int(np.argmax(np.abs(seg)))
        top = sorted([(int(i), round(float(seg[i]), 5)) for i in nz],
                     key=lambda t: -abs(t[1]))[:6]
        res.setdefault("ir-d100-44k", []).append(
            {"out": os.path.basename(op), "ref_first": r0, "kernel_first": int(nz[0]) if len(nz) else None,
             "kernel_last": int(nz[-1]) if len(nz) else None, "kernel_peak_idx": pk,
             "kernel_peak": round(float(seg[pk]), 5), "n_nonzero": int(len(nz)), "top": top})
        print("44k kernel:", res["ir-d100-44k"][-1])

    # ---- stereo IR: which channel survives ---------------------------------
    for op in sorted(glob.glob(os.path.join(S, "ir-stereo_out_*_0.wav"))):
        rp = op.replace("_out_", "_ref_")
        xo = R.wav_read(op)["x"]
        xr = R.wav_read(rp)["x"]
        r0 = int(np.nonzero(np.abs(xr) > 1e-4)[0][0])
        seg = xo[r0:r0 + 4096]
        nz = [(int(i), round(float(seg[i]), 5)) for i in np.nonzero(np.abs(seg) > 1e-4)[0]]
        res.setdefault("ir-stereo", []).append({"out": os.path.basename(op), "ref_first": r0, "impulses": nz})
        print("stereo IR:", res["ir-stereo"][-1])

    # ---- delay legs: impulse shift -----------------------------------------
    for leg in ("delay-real-q", "delay-real-q-over", "delay-typo"):
        rows = []
        for op in sorted(glob.glob(os.path.join(S, "%s_out_*_0.wav" % leg))):
            rp = op.replace("_out_", "_ref_")
            xo = R.wav_read(op)["x"]
            xr = R.wav_read(rp)["x"]
            of = np.nonzero(np.abs(xo) > 1e-4)[0]
            rf = np.nonzero(np.abs(xr) > 1e-4)[0]
            rows.append({"out": os.path.basename(op),
                         "out_first": int(of[0]) if len(of) else None,
                         "ref_first": int(rf[0]) if len(rf) else None,
                         "shift": (int(of[0]) - int(rf[0])) if len(of) and len(rf) else None,
                         "n_impulses": int(len(of))})
        res[leg] = rows
        print("%-18s %s" % (leg, [(x.get("shift"), x.get("n_impulses")) for x in rows]))

    # ---- gain4 clipping ----------------------------------------------------
    for op in sorted(glob.glob(os.path.join(S, "ir-gain4_out_*_0.wav"))):
        rp = op.replace("_out_", "_ref_")
        xo = R.wav_read(op)["x"]
        xr = R.wav_read(rp)["x"]
        r0 = int(np.nonzero(np.abs(xr) > 1e-4)[0][0])
        seg = xo[r0:r0 + 200]
        nz = [(int(i), round(float(seg[i]), 6)) for i in np.nonzero(np.abs(seg) > 1e-4)[0]]
        res.setdefault("ir-gain4", []).append({"out": os.path.basename(op), "impulses": nz,
                                               "max_abs": round(float(np.max(np.abs(xo))), 6)})
        print("gain4:", res["ir-gain4"][-1])

    R.jdump(outp, res)
    print("WROTE", outp)


if __name__ == "__main__":
    main()
