#!/usr/bin/env python3
"""r94 scout — receipt analyzer: prints the report's verbatim tables."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REC = ROOT / "receipts"


def legs(stage):
    p = REC / f"{stage}.json"
    return json.loads(p.read_text())["legs"] if p.exists() else []


def show(title):
    print(f"\n===== {title} =====")


def determinism_matrix():
    show("determinism matrix (stable = all reps byte-identical)")
    print(f"{'leg':44s} {'default':>10s} {'-D':>10s}")
    names = {}
    for st in ("gain", "rate", "remix", "trim", "fade", "repeat_pad_silence", "dither", "chain"):
        for l in legs(st):
            names[l["name"]] = names.get(l["name"], {})
            names[l["name"]]["default"] = (l.get("stable"), l.get("n_distinct_shas"))
        for l in legs(st + "_D"):
            names[l["name"]] = names.get(l["name"], {})
            names[l["name"]]["-D"] = (l.get("stable"), l.get("n_distinct_shas"))
    for n, v in names.items():
        d = v.get("default")
        dd = v.get("-D")
        f = lambda x: "-" if x is None else (f"stable" if x[0] else f"{x[1]}shas")
        print(f"{n:44s} {f(d):>10s} {f(dd):>10s}")


def gain_laws():
    show("gain laws (-D pass, exact)")
    for l in legs("gain_D"):
        m = l.get("metrics", {})
        if l["name"].startswith("vol") or l["name"] == "global_v_0.5":
            print(f"{l['name']:20s} mism rint={m.get('mismatch_rint')} floor={m.get('mismatch_floor')} "
                  f"trunc={m.get('mismatch_trunc')} ceil={m.get('mismatch_ceil')} "
                  f"mism_vs_formula={m.get('mismatch_vs_rint_formula')}")
        elif "mismatch_vs_rint_formula" in m:
            print(f"{l['name']:20s} mism={m['mismatch_vs_rint_formula']} maxdiff={m['max_abs_diff_vs_formula']} "
                  f"peak={m.get('peak_db')} clip={m.get('clipped_samples')}")


def rate_table():
    show("rate output-length law (in=12000 frames @48k unless marked odd)")
    for l in legs("rate_D"):
        m = l.get("metrics", {})
        if m:
            print(f"{l['name']:26s} frames={m.get('frames'):>7} rate={m.get('rate')} "
                  f"tone={m.get('tone0', {}).get('hz')} peak={m.get('peak_db')}")
    show("rate band/alias laws")
    for l in legs("rate_D"):
        m = l.get("metrics", {})
        if m and ("23k" in l["name"] or "20k" in l["name"]):
            print(f"{l['name']:26s} band20k={m.get('band_20000hz_db')} "
                  f"band21.1k={m.get('band_21100hz_db')} peak={m.get('peak_db')}")


def remix_laws():
    show("remix formulas (-D pass)")
    for l in legs("remix_D"):
        m = l.get("metrics", {})
        keys = [k for k in m if k.startswith("mismatch_")]
        if keys:
            print(f"{l['name']:20s} " + " ".join(f"{k[8:]}={m[k]}" for k in keys))
    show("remix selections (-D)")
    for l in legs("remix_D"):
        m = l.get("metrics", {})
        if "first8_ints" in m or "first8_ch0" in m:
            print(f"{l['name']:20s} peak={m.get('peak_db')} ch={m.get('channels')} "
                  f"first8={m.get('first8_ints') or m.get('first8_ch0')}")


def trim_table():
    show("trim length law (stim_b = 12000 frames)")
    for l in legs("trim_D"):
        m = l.get("metrics", {})
        print(f"{l['name']:26s} rc={l['reps'][0]['rc']} frames={m.get('frames')} "
              f"err={(l['reps'][0]['stderr_head'] or '').splitlines()[:1]}")


def fade_laws():
    show("fade stop/truncation law (-D)")
    f = {l["name"]: l for l in legs("fade_D")}
    for n in ("fade_out_stop0.25_len0.1", "fade_out_stop0.15_len0.1", "fade_out_stop0.2_len0.05"):
        m = f[n]["metrics"]
        print(f"{n:26s} frames={m['frames']}")
    show("fade log 100 dB law (-D): gain vs predicted 10^(-5(1-x))")
    for n in ("fade_in_0.1", "fade_in_l_0.1"):
        m = f[n]["metrics"]
        print(n)
        for k, v in m["envelope"].items():
            fr = int(k[5:])
            x = fr / 4800.0
            pred = 10 ** (-5 * (1 - x)) if x <= 1 else 1.0
            print(f"  frame{fr:5d} x={x:.4f} out={v['out']:7d} gain={v['gain']} pred={pred:.6g}")
    show("fade curves at x=.25/.5/.75 (-D)")
    for n in ("fade_in_q_0.1", "fade_in_h_0.1", "fade_in_t_0.1", "fade_in_p_0.1", "fade_in_s_0.1"):
        env = f[n]["metrics"]["envelope"]
        g = {k: env[k]["gain"] for k in ("frame1200", "frame2400", "frame3600")}
        print(f"{n:20s} {g}")


def rps_laws():
    show("repeat/pad/silence laws (-D)")
    for l in legs("repeat_pad_silence_D"):
        m = l.get("metrics", {})
        print(f"{l['name']:30s} rc={l['reps'][0]['rc']} frames={m.get('frames')} "
              f"mism_tile={m.get('mismatch_vs_tiling')} first_nz={m.get('first_nonzero_frame')} "
              f"last_nz={m.get('last_nonzero_frame')} trail0={m.get('trailing_zero_frames')} "
              f"err={(l['reps'][0]['stderr_head'] or '').splitlines()[:1]}")


def dither_laws():
    show("dither/guard laws")
    for st in ("dither", "dither_D"):
        for l in legs(st):
            m = l.get("metrics", {})
            print(f"[{st:9s}] {l['name']:24s} stable={l['stable']} nd={l['n_distinct_shas']} "
                  f"mism={m.get('mismatch_vs_round', m.get('mismatch_vs_formula'))} "
                  f"maxerr={m.get('max_abs_err')} errrms={m.get('err_rms')} "
                  f"clip67={m.get('clipped_ge32767', m.get('clipped_samples'))} "
                  f"clip66={m.get('clipped_ge32766')} ident={m.get('byte_identical_to_input')}")


def stat_laws():
    show("stat cross-witness")
    for l in legs("stat"):
        m = l.get("metrics", {})
        if l["name"] == "ffmpeg_ebur128_b":
            print(f"ffmpeg ebur128: {m}")
        elif "EBUR128" in json.dumps(m):
            print(f"{l['name']}: {m}")
        else:
            print(f"{l['name']}: {json.dumps(m)[:220]}")


def chain_laws():
    show("chain/order laws (-D)")
    for l in legs("chain_D"):
        m = l.get("metrics", {})
        print(f"{l['name']:24s} peak={m.get('peak_db')} rms={m.get('rms_db')} "
              f"sha={l.get('same_sha')} maxdiff={l.get('max_abs_diff')}")


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    fns = {
        "det": determinism_matrix, "gain": gain_laws, "rate": rate_table, "remix": remix_laws,
        "trim": trim_table, "fade": fade_laws, "rps": rps_laws, "dither": dither_laws,
        "stat": stat_laws, "chain": chain_laws,
    }
    if what == "all":
        for fn in fns.values():
            fn()
    else:
        fns[what]()
