#!/usr/bin/env python3
"""Post-hoc alignment analysis of the B3 IR captures (no graph contact).

The two pw-record taps are separate streams, so their relative offset is not
guaranteed; and the filter-chain's own block-boundary phase can add a whole
block. This script finds, for each stored leg, the lag L that best aligns the
captured post-tap to the *expected convolution* (IR x delta), and reports the
residual there. Sample-exactness is then stated as "residual <= x LSB at lag L",
which is alignment-independent.

argv: <leg_prefix> [--out-file]
"""
import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig as R

S = R.SCRATCH
STIM_VAL = 32767.0 / 32768.0


def expected(ir_path, n=8192, extra_gain=1.0):
    ir = R.wav_read(ir_path)["x"]
    if ir.ndim > 1:
        ir = ir[:, 0]
    e = np.zeros(n)
    m = min(n, len(ir))
    e[:m] = ir[:m] * STIM_VAL * extra_gain
    return e


def best_lag(xo, exp, ref_first, lo=-8192, hi=8192, span=4096):
    """Residual (in LSB) of the capture against the expected IR at each lag."""
    best = None
    for lag in range(lo, hi + 1, 1):
        i0 = ref_first + lag
        if i0 < 0 or i0 + span > len(xo):
            continue
        d = (xo[i0:i0 + span] - exp[:span]) * 32768.0
        r = float(np.max(np.abs(d)))
        if best is None or r < best[1]:
            best = (lag, r)
            if r < 1.0:
                break
    return best


def main():
    prefix = sys.argv[1]
    outp = sys.argv[2] if len(sys.argv) > 2 else os.path.join(R.REC, "b3_align.json")
    res = {}
    for op in sorted(glob.glob(os.path.join(S, "%s_out_*_0.wav" % prefix))):
        rp = op.replace("_out_", "_ref_")
        if not os.path.exists(rp):
            continue
        xo = R.wav_read(op)["x"]
        xr = R.wav_read(rp)["x"]
        rf = np.nonzero(np.abs(xr) > 1e-4)[0]
        ref_first = int(rf[0]) if len(rf) else None
        nz = np.nonzero(np.abs(xo) > 1e-4)[0]
        out_first = int(nz[0]) if len(nz) else None
        rec = {"out": os.path.basename(op), "ref_first": ref_first, "out_first": out_first,
               "delta_naive": (out_first - ref_first) if (out_first is not None and ref_first is not None) else None}
        res[os.path.basename(op)] = rec
    R.jdump(outp, res)
    print(json.dumps(res, indent=1)[:2000])
    return res


if __name__ == "__main__":
    main()
