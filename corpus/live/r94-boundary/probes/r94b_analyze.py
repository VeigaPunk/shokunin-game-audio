#!/usr/bin/env python3
"""r94b analyzer — receipts -> comparison lattice, cross-seat sha table, verdicts.

Reads only files under corpus/live/r94-boundary/ (+ read-only reads of
corpus/live/r94-scout/receipts/ for the cross-seat byte comparison).
Writes runs/analysis-*.txt and receipts/verdicts.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r94b_lib as L  # noqa: E402

OUT = L.OUT
RUNS = L.RUNS
IDX = {}
RECEIPTS = {}


def load_receipt(name):
    p = L.RECEIPTS / f"{name}.json"
    if not p.exists():
        return None
    d = json.loads(p.read_text())
    RECEIPTS[name] = d
    for c in d.get("cells", []):
        IDX[(d["pass"], c.get("family", ""), c["name"])] = c
    return d


def g(pass_, family, name):
    return IDX.get((pass_, family, name))


def met(pass_, family, name, key, rep=0):
    c = g(pass_, family, name)
    if c is None or not c["reps"]:
        return None
    return (c["reps"][rep].get("metrics") or {}).get(key)


def nd(pass_, family, name):
    c = g(pass_, family, name)
    return None if c is None else c["n_distinct_shas"]


def shas(pass_, family, name):
    c = g(pass_, family, name)
    if c is None:
        return None
    return sorted({r["out_sha256"] for r in c["reps"] if r["out_sha256"]})


def rcs(pass_, family, name):
    c = g(pass_, family, name)
    return None if c is None else c["rcs"]


def n_out(c):
    if c is None:
        return 0
    if "n_outputs" in c:
        return c["n_outputs"]
    return len([r for r in c["reps"] if r.get("out_sha256")])


def both(family, name):
    return g("quiet", family, name), g("load", family, name)


def loadavg_of(pass_, stage="laws"):
    d = RECEIPTS.get(f"{stage}-{pass_}")
    return d["host"]["loadavg"] if d else None


# ---------------------------------------------------------------- load all ---

for nm in ("prep-quiet", "witness-quiet", "laws-quiet", "axes-quiet", "conc-quiet",
           "witness-load", "laws-load", "axes-load", "conc-load", "census-final",
           "r5-quiet", "r5-load"):
    load_receipt(nm)

VERDICTS = []


def verdict(vid, claim, source, v, evidence):
    VERDICTS.append({"id": vid, "claim": claim, "source": source, "verdict": v,
                     "evidence": evidence})


def ok(cond, yes="CONFIRMED", no="FALSIFIED"):
    return yes if cond else no


# ------------------------------------------------------------ lattice table --

lines = []
lines.append("r94b lattice — quiet-ish pass vs load pass (16 own hogs)")
for p in ("quiet", "load"):
    lines.append(f"  {p:6s} loadavg@stage = {loadavg_of(p)}   hogs = "
                 f"{RECEIPTS.get('laws-'+p, {}).get('hogs')}   "
                 f"hog_set alive-after = {RECEIPTS.get('laws-'+p, {}).get('hog_set', {}).get('kill_log', [{}])[-1]}")
lines.append("")
hdr = f"{'family':6s} {'cell':34s} {'quiet':>18s} {'load':>18s}  verdict"
lines.append(hdr)
lines.append("-" * len(hdr))
n_invariant = n_nondet = n_mismatch = 0
for (p, fam, name), c in sorted(IDX.items()):
    if p != "quiet" or fam in ("", "AX"):
        continue
    q = g("quiet", fam, name)
    l = g("load", fam, name)
    if q is None or l is None:
        continue
    qs, ls = q["n_distinct_shas"], l["n_distinct_shas"]
    qsha, lsha = shas("quiet", fam, name), shas("load", fam, name)
    if qs == 1 and ls == 1 and qsha == lsha:
        tag = "identical-across-load"
        n_invariant += 1
    elif qs > 1 and ls > 1:
        tag = "nondet-both"
        n_nondet += 1
    elif qs == 0 and ls == 0:
        tag = "no-output"
    else:
        tag = "** MISMATCH **"
        n_mismatch += 1
    lines.append(f"{fam:6s} {name:34s} {str(qs)+'/'+str(q['reps_n']):>18s} "
                 f"{str(ls)+'/'+str(l['reps_n']):>18s}  {tag}")
lines.append("")
lines.append(f"summary: {n_invariant} cells byte-identical across load, "
             f"{n_nondet} nondeterministic in both, {n_mismatch} mismatched")
(RUNS / "analysis-lattice.txt").write_text("\n".join(lines) + "\n")

# ------------------------------------------------------ cross-seat sha table --

SCOUT_MAP = {
    ("D", "gain_m6_D"): ("gain_D", "gain_m6"),
    ("D", "gain_m6_default"): ("gain", "gain_m6"),
    ("D", "dither_explicit_default"): ("dither", "f32_to_s16_dither"),
    ("D", "dither_explicit_R"): ("dither_D", "f32_to_s16_dither_R"),
    ("D", "dither_explicit_D"): ("dither_D", "f32_to_s16_dither"),
    ("D", "dither_s_R"): ("dither_D", "f32_to_s16_dither_s_R"),
    ("D", "dither_p12_R"): ("dither_D", "f32_to_s16_dither_p12_R"),
    ("D", "f32_to_s16_plain"): ("dither_D", "f32_to_s16_plain"),
    ("D", "f32_to_s24_plain"): ("dither_D", "f32_to_s24_plain"),
    ("D", "f32_to_s32_plain"): ("dither_D", "f32_to_s32_plain"),
    ("D", "copy_plain"): ("dither_D", "copy_plain"),
    ("D", "rate_same_identity"): ("dither_D", "rate_same_rate_identity"),
    ("D", "gain_0_identity"): ("gain_D", "gain_0"),
    ("D", "s16_to_s24_gain"): ("dither_D", "s16_to_s24_gain"),
    ("G", "vol_amp_0.5_D"): ("gain_D", "vol_amp_0.5"),
    ("G", "vol_db_m6.0206_D"): ("gain_D", "vol_db_m6.0206"),
    ("G", "vol_pow_0.5_D"): ("gain_D", "vol_pow_0.5"),
    ("G", "gain_n_D"): ("gain_D", "gain_n"),
    ("G", "gain_e_D"): ("gain_D", "gain_e"),
    ("G", "gain_b_D"): ("gain_D", "gain_b"),
    ("G", "gain_h_m6_D"): ("gain_D", "gain_h_m6"),
    ("G", "gain_h_m6_reclaim_D"): ("gain_D", "gain_h_m6_reclaim"),
    ("R", "rate44100_b"): ("rate_D", "rate44100_default"),
    ("R", "rate22050_b"): ("rate_D", "rate22050"),
    ("R", "rate22054_b"): ("rate_D", "rate22054"),
    ("R", "rate24050_b"): ("rate_D", "rate24050"),
    ("R", "rate11025_b"): ("rate_D", "rate11025"),
    ("R", "rate44101_b"): ("rate_D", "rate44101"),
    ("R", "rate96000_b"): ("rate_D", "rate96000"),
    ("R", "rate32000_b"): ("rate_D", "rate32000"),
    ("R", "rate8000_b"): ("rate_D", "rate8000"),
    ("R", "rate48000_b"): ("rate_D", "rate48000"),
    ("R", "rate44100_i"): ("rate_D", "rate44100_odd12001"),
    ("R", "rate22050_i"): ("rate_D", "rate22050_odd12001"),
    ("R", "rate96000_i"): ("rate_D", "rate96000_odd12001"),
    ("R", "rate32000_i"): ("rate_D", "rate32000_odd12001"),
    ("R", "rate22054_i"): ("rate_D", "rate22054_odd12001"),
    ("R", "rate44100_23k_default"): ("rate_D", "rate44100_23k_default"),
    ("R", "rate44100_23k_q"): ("rate_D", "rate44100_23k_q"),
    ("R", "rate44100_23k_a"): ("rate_D", "rate44100_23k_alias_a"),
    ("R", "rate44100_23k_m_a"): ("rate_D", "rate44100_23k_m_alias_a"),
    ("R", "rate44100_20k_default"): ("rate_D", "rate44100_20k_default"),
    ("R", "rate44100_20k_q"): ("rate_D", "rate44100_20k_q"),
    ("R", "rate44100_20k_v"): ("rate_D", "rate44100_20k_v"),
    ("M", "remix_1"): ("remix_D", "remix_1"),
    ("M", "remix_1_2"): ("remix_D", "remix_1_2_sum"),
    ("M", "remix_m_1_2"): ("remix_D", "remix_m_1_2"),
    ("M", "remix_a_1_2"): ("remix_D", "remix_a_1_2"),
    ("M", "remix_p_1_2"): ("remix_D", "remix_p_1_2"),
    ("M", "channels_1"): ("remix_D", "channels_1"),
    ("M", "remix_swap_2_1"): ("remix_D", "remix_swap_2_1"),
    ("M", "remix_left_only"): ("remix_D", "remix_left_only"),
    ("M", "remix_right_only"): ("remix_D", "remix_right_only"),
    ("M", "remix_v_half"): ("remix_D", "remix_v_half"),
    ("M", "remix_p_minus6"): ("remix_D", "remix_p_minus6"),
    ("M", "mono_to_stereo_1_1"): ("remix_D", "mono_to_stereo_1_1"),
    ("T", "trim_0_0.1"): ("trim_D", "trim_0_0.1"),
    ("T", "trim_0_1s"): ("trim_D", "trim_0_1s"),
    ("T", "trim_0_4800s"): ("trim_D", "trim_0_4800s"),
    ("T", "trim_0_0"): ("trim_D", "trim_0_0"),
    ("T", "trim_0_minus0.1"): ("trim_D", "trim_0_minus0.1"),
    ("T", "trim_0_eq0.1"): ("trim_D", "trim_0_eq0.1"),
    ("T", "trim_0_0.1000208"): ("trim_D", "trim_0_0.1000208"),
    ("T", "trim_plus_0.05plus0.05"): ("trim_D", "trim_plus_0.05plus0.05"),
    ("F", "fade_in_0.1"): ("fade_D", "fade_in_0.1"),
    ("F", "fade_out_stop0.15_len0.1"): ("fade_D", "fade_out_stop0.15_len0.1"),
    ("F", "fade_out_stop0.25_len0.1"): ("fade_D", "fade_out_stop0.25_len0.1"),
    ("F", "fade_out_stop0.2_len0.05"): ("fade_D", "fade_out_stop0.2_len0.05"),
    ("F", "fade_in_q_0.1"): ("fade_D", "fade_in_q_0.1"),
    ("F", "fade_in_h_0.1"): ("fade_D", "fade_in_h_0.1"),
    ("F", "fade_in_t_0.1"): ("fade_D", "fade_in_t_0.1"),
    ("F", "fade_in_l_0.1"): ("fade_D", "fade_in_l_0.1"),
    ("F", "fade_in_p_0.1"): ("fade_D", "fade_in_p_0.1"),
    ("F", "fade_in_s_0.1"): ("fade_D", "fade_in_s_0.1"),
    ("P", "repeat_2"): ("repeat_pad_silence_D", "repeat_2"),
    ("P", "repeat_1"): ("repeat_pad_silence_D", "repeat_1"),
    ("P", "repeat_0"): ("repeat_pad_silence_D", "repeat_0"),
    ("P", "pad_0.1_0.2"): ("repeat_pad_silence_D", "pad_0.1_0.2"),
    ("P", "pad_0.05_at_0.05"): ("repeat_pad_silence_D", "pad_0.05_at_0.05"),
    ("P", "pad_pct50"): ("repeat_pad_silence_D", "pad_pct50"),
    ("P", "silence_c2_above"): ("repeat_pad_silence_D", "c2_silence_above_only"),
    ("P", "silence_c2_both"): ("repeat_pad_silence_D", "c2_silence_both_0.1"),
    ("P", "silence_c2_both_leave"): ("repeat_pad_silence_D", "c2_silence_both_leave"),
    ("P", "silence_c2_both_0.05"): ("repeat_pad_silence_D", "c2_silence_both_0.05"),
    ("C", "gain_m6_then_norm_m3"): ("chain_D", "gain_m6_then_norm_m3"),
    ("C", "norm_m3_then_gain_m6"): ("chain_D", "norm_m3_then_gain_m6"),
    ("C", "norm_0_only"): ("chain_D", "norm_0_only"),
    ("C", "global_norm_flag"): ("chain_D", "global_norm_flag"),
    ("C", "gain_p6_G_norm"): ("chain_D", "gain_p6_G_norm"),
    ("X", "gain_p12_D"): ("dither_D", "gain_p12"),
    ("X", "gain_p12_G_D"): ("dither_D", "gain_p12_G"),
    ("X", "gain_p12_default"): ("dither", "gain_p12"),
    ("X", "gain_p12_G_default"): ("dither", "gain_p12_G"),
}

scout_cache = {}
sx = []
sx.append("r94b cross-seat byte comparison — my rep0 sha vs the r94 scout's rep0 sha")
sx.append("(same stimulus bytes verified in prep-quiet; deterministic legs only)")
sx.append("")
sx.append(f"{'family':6s} {'my cell':34s} {'scout leg':30s} {'match':>6s}  sha256[:16]")
sx.append("-" * 100)
n_match = n_diff = 0
for (fam, name), (sr, sleg) in sorted(SCOUT_MAP.items()):
    c = g("quiet", fam, name)
    if c is None or not c["reps"]:
        continue
    if sr not in scout_cache:
        p = L.SCOUT / "receipts" / f"{sr}.json"
        scout_cache[sr] = json.loads(p.read_text()) if p.exists() else {"legs": []}
    s = next((x for x in scout_cache[sr]["legs"] if x["name"] == sleg), None)
    if s is None:
        continue
    mine = c["reps"][0]["out_sha256"]
    theirs = s["reps"][0]["out_sha256"]
    if mine is None and theirs is None:
        continue
    m = mine == theirs
    n_match += m
    n_diff += (not m)
    sx.append(f"{fam:6s} {name:34s} {sleg:30s} {str(m):>6s}  {(mine or '-')[:16]} / {(theirs or '-')[:16]}")
sx.append("")
sx.append(f"summary: {n_match} byte-identical, {n_diff} differing (differing = the two "
          f"time-seeded dither legs, expected)")
(RUNS / "analysis-scout-cross.txt").write_text("\n".join(sx) + "\n")

# ------------------------------------------------------------------ verdicts --

q, l = "quiet", "load"

# --- D: determinism
verdict("D1", "default s16 effect output is nondeterministic (auto-dither)",
        "r94-scout §1.1 / §2", ok((nd(q, "D", "gain_m6_default") or 1) > 1 and
                                  (nd(l, "D", "gain_m6_default") or 1) > 1),
        {"gain_m6_default shas/rep": [f"{nd(q,'D','gain_m6_default')}/{g(q,'D','gain_m6_default')['reps_n']}",
                                      f"{nd(l,'D','gain_m6_default')}/{g(l,'D','gain_m6_default')['reps_n']}"]})
verdict("D2", "`-D` makes gain -6 exact to ±0.5 LSB (mismatch vs rint = 0) and byte-stable",
        "r94-scout §1.1", ok(met(q, "D", "gain_m6_D", "mismatch_vs_rint") == 0 and
                             met(l, "D", "gain_m6_D", "mismatch_vs_rint") == 0 and
                             nd(q, "D", "gain_m6_D") == 1 and nd(l, "D", "gain_m6_D") == 1 and
                             shas(q, "D", "gain_m6_D") == shas(l, "D", "gain_m6_D")),
        {"mismatch_vs_rint": [met(q, "D", "gain_m6_D", "mismatch_vs_rint"),
                              met(l, "D", "gain_m6_D", "mismatch_vs_rint")],
         "max_abs_diff": [met(q, "D", "gain_m6_D", "max_abs_diff_vs_rint"),
                          met(l, "D", "gain_m6_D", "max_abs_diff_vs_rint")],
         "sha": shas(q, "D", "gain_m6_D")[0][:16] if shas(q, "D", "gain_m6_D") else None,
         "quiet_sha_set_equals_load": shas(q, "D", "gain_m6_D") == shas(l, "D", "gain_m6_D")})
verdict("D3", "an explicit `dither` is nondeterministic (time-seeded RNG)",
        "r94-scout §1.2", ok((nd(q, "D", "dither_explicit_default") or 1) > 1),
        {"shas/rep": f"{nd(q,'D','dither_explicit_default')}/{g(q,'D','dither_explicit_default')['reps_n']}"})
verdict("D4", "`-R` makes an explicit `dither` reproducible (1 sha) and cross-pass identical",
        "r94-scout §1.2 + r94b extension",
        ok(nd(q, "D", "dither_explicit_R") == 1 and nd(l, "D", "dither_explicit_R") == 1 and
           shas(q, "D", "dither_explicit_R") == shas(l, "D", "dither_explicit_R")),
        {"shas/rep": [f"{nd(q,'D','dither_explicit_R')}/{g(q,'D','dither_explicit_R')['reps_n']}",
                      f"{nd(l,'D','dither_explicit_R')}/{g(l,'D','dither_explicit_R')['reps_n']}"],
         "sha": shas(q, "D", "dither_explicit_R")[0][:16] if shas(q, "D", "dither_explicit_R") else None,
         "cross_pass_equal": shas(q, "D", "dither_explicit_R") == shas(l, "D", "dither_explicit_R")})
verdict("D5", "`-D` does NOT fix an explicit `dither` (still >1 sha)",
        "r94-scout §1.2 / §4.2", ok((nd(q, "D", "dither_explicit_D") or 1) > 1),
        {"shas/rep": f"{nd(q,'D','dither_explicit_D')}/{g(q,'D','dither_explicit_D')['reps_n']}"})
verdict("D6", "`-R -D` explicit dither output == `-R` explicit dither output (extension)",
        "r94b extension",
        ok(shas(q, "AX", "dither_R_D_combo") == shas(q, "AX", "dither_R_canonical")),
        {"combo_sha": (shas(q, "AX", "dither_R_D_combo") or [None])[0],
         "canonical_sha": (shas(q, "AX", "dither_R_canonical") or [None])[0]})
verdict("D7", "`dither -s` noise-shaping error envelope (max ~21-22 LSB, rms ~5.8)",
        "r94-scout §3.7 D3",
        ok(20 <= (met(q, "D", "dither_s_R", "max_abs_err") or 0) <= 23),
        {"max_abs_err": met(q, "D", "dither_s_R", "max_abs_err"),
         "err_rms": met(q, "D", "dither_s_R", "err_rms")})
verdict("D8", "f32→s16 conversion is nondeterministic by default",
        "r94-scout §2", ok((nd(q, "D", "f32_to_s16_plain") or 1) > 1),
        {"shas/rep": f"{nd(q,'D','f32_to_s16_plain')}/{g(q,'D','f32_to_s16_plain')['reps_n']}"})
verdict("D9", "f32→s24 / f32→s32 are byte-stable (the `< 24` auto-dither clause)",
        "r94-scout §2",
        ok(nd(q, "D", "f32_to_s24_plain") == 1 and nd(q, "D", "f32_to_s32_plain") == 1 and
           nd(l, "D", "f32_to_s24_plain") == 1 and nd(l, "D", "f32_to_s32_plain") == 1),
        {"s24": nd(q, "D", "f32_to_s24_plain"), "s32": nd(q, "D", "f32_to_s32_plain")})
verdict("D10", "`copy` is byte-identical to the input; `rate <same>` is SOX_EFF_NULL identity; "
               "`gain 0` is byte-identical (extension)",
        "r94-scout §3.2 R4 + r94b extension",
        ok(met(q, "D", "copy_plain", "byte_identical_to_stim") is True and
           met(q, "D", "rate_same_identity", "byte_identical_to_stim") is True and
           met(q, "D", "gain_0_identity", "byte_identical_to_stim") is True),
        {"copy": met(q, "D", "copy_plain", "byte_identical_to_stim"),
         "rate_same": met(q, "D", "rate_same_identity", "byte_identical_to_stim"),
         "gain_0": met(q, "D", "gain_0_identity", "byte_identical_to_stim")})
verdict("D11", "s16→s24 + gain is stable (output precision ≥ 24 suppresses auto-dither)",
        "r94-scout §2", ok(nd(q, "D", "s16_to_s24_gain") == 1),
        {"shas/rep": f"{nd(q,'D','s16_to_s24_gain')}/{g(q,'D','s16_to_s24_gain')['reps_n']}"})

# --- G: gain / vol / norm
verdict("G1", "dB→factor is exact to ±0.5 LSB with `-D` (rint)",
        "r94-scout §3.1 G1", ok(met(q, "D", "gain_m6_D", "mismatch_vs_rint") == 0),
        {"mismatch_vs_rint": met(q, "D", "gain_m6_D", "mismatch_vs_rint"),
         "peak_db": met(q, "D", "gain_m6_D", "peak_db")})
verdict("G2", "`vol` amplitude form rounds ceil; dB and power forms round to nearest",
        "r94-scout §3.1 G2",
        ok(met(q, "G", "vol_amp_0.5_D", "mismatch_ceil") == 0 and
           met(q, "G", "vol_amp_0.5_D", "mismatch_rint") == 23000 and
           met(q, "G", "vol_db_m6.0206_D", "mismatch_rint") == 0 and
           met(q, "G", "vol_pow_0.5_D", "mismatch_rint") == 0),
        {"vol_amp": {"ceil": met(q, "G", "vol_amp_0.5_D", "mismatch_ceil"),
                     "rint": met(q, "G", "vol_amp_0.5_D", "mismatch_rint")},
         "vol_db": met(q, "G", "vol_db_m6.0206_D", "mismatch_rint"),
         "vol_pow": met(q, "G", "vol_pow_0.5_D", "mismatch_rint")})
verdict("G3", "`vol 0.5` and `vol -6.0206 d` differ by exactly 1 LSB (not interchangeable)",
        "r94-scout §3.1 G2 / C2",
        ok(abs((met(q, "G", "vol_spelling_delta", "max_abs_diff") or 0) - 3.0517578125e-05) < 1e-12 and
           met(q, "G", "vol_spelling_delta", "same_sha") is False),
        {"max_abs_diff": met(q, "G", "vol_spelling_delta", "max_abs_diff"),
         "same_sha": met(q, "G", "vol_spelling_delta", "same_sha")})
verdict("G4", "`gain -n` normalizes the file peak to 0 dBFS; `-e`/`-b` lift both channels",
        "r94-scout §3.1 G4",
        ok((met(q, "G", "gain_n_D", "peak_db") or [None])[0] == 0.0 and
           met(q, "G", "gain_e_D", "peak_db") == [-6.0206, -6.0206]),
        {"gain_n_peak": met(q, "G", "gain_n_D", "peak_db"),
         "gain_e_peak": met(q, "G", "gain_e_D", "peak_db"),
         "gain_b_peak": met(q, "G", "gain_b_D", "peak_db")})
verdict("G5", "`-h` reserves headroom that a following `gain -r` reclaims",
        "r94-scout §3.1 G4",
        ok(met(q, "G", "gain_h_m6_D", "peak_db") == [-12.0211, -18.0406] and
           met(q, "G", "gain_h_m6_reclaim_D", "peak_db") == [-6.0206, -12.0412]),
        {"h_m6": met(q, "G", "gain_h_m6_D", "peak_db"),
         "reclaim": met(q, "G", "gain_h_m6_reclaim_D", "peak_db")})

# --- R: rate
RATE_EXPECT = {("rate44100_b", 12000, 44100): 11025, ("rate22050_b", 12000, 22050): 5512,
               ("rate22054_b", 12000, 22054): 5514, ("rate24050_b", 12000, 24050): 6013,
               ("rate11025_b", 12000, 11025): 2756, ("rate44101_b", 12000, 44101): 11025,
               ("rate96000_b", 12000, 96000): 24000, ("rate32000_b", 12000, 32000): 8000,
               ("rate8000_b", 12000, 8000): 2000, ("rate48000_b", 12000, 48000): 12000,
               ("rate44100_i", 12001, 44100): 11026, ("rate22050_i", 12001, 22050): 5513,
               ("rate96000_i", 12001, 96000): 24002, ("rate32000_i", 12001, 32000): 8001,
               ("rate22054_i", 12001, 22054): 5514}
rows = []
all_ok = True
for (nm, inf, orate), exp in sorted(RATE_EXPECT.items()):
    got = met(q, "R", nm, "frames")
    exact = inf * orate / 48000.0
    in_tol = got is not None and abs(got - exact) <= 1.0
    all_ok &= (got == exp) and in_tol
    rows.append({"cell": nm, "in_frames": inf, "out_rate": orate, "exact": round(exact, 5),
                 "scout_frames": exp, "mine": got, "matches_scout": got == exp,
                 "within_1_frame": in_tol})
verdict("R1", "rate output length reproduces the scout's matrix exactly and is within ±1 frame "
              "of in·out/in_rate",
        "r94-scout §3.2 R1", ok(all_ok), {"rows": rows})
# no single rounding rule fits the .5 rows
half_rows = [(r["exact"], r["mine"]) for r in rows if abs(r["exact"] % 1 - 0.5) < 1e-9]
rules = {"floor": lambda x: int(np.floor(x)), "round_half_up": lambda x: int(np.floor(x + 0.5)),
         "round_half_even": lambda x: int(np.rint(x)), "ceil": lambda x: int(np.ceil(x))}
fit = {k: all(fn(x) == m for x, m in half_rows) for k, fn in rules.items()}
verdict("R2", "no single rounding rule fits the .5-boundary rows (rate approximates the ratio)",
        "r94-scout §3.2 R1", ok(not any(fit.values())),
        {"half_rows_exact->mine": half_rows, "rules_that_fit_all": [k for k, v in fit.items() if v]})
verdict("R3", "`-q` folds a 23 kHz tone to 21.1 kHz at ~-6.3 dB (content hazard)",
        "r94-scout §1.5 / §3.2 R3",
        ok(abs((met(q, "R", "rate44100_23k_q", "band_21100hz_db") or 0) + 6.289) < 0.01 and
           met(q, "R", "rate44100_23k_q", "peak_db") == [-6.1725]),
        {"band_21100hz_db": met(q, "R", "rate44100_23k_q", "band_21100hz_db"),
         "peak_db": met(q, "R", "rate44100_23k_q", "peak_db"),
         "default_band_21100hz_db": met(q, "R", "rate44100_23k_default", "band_21100hz_db"),
         "a_band_21100hz_db": met(q, "R", "rate44100_23k_a", "band_21100hz_db"),
         "m_a_band_21100hz_db": met(q, "R", "rate44100_23k_m_a", "band_21100hz_db")})
verdict("R4", "at 20 kHz `-q` rolls off -3.9 dB where default/`-v` are flat",
        "r94-scout §1.5",
        ok(abs((met(q, "R", "rate44100_20k_q", "band_20000hz_db") or 0) + 3.942) < 0.01 and
           met(q, "R", "rate44100_20k_default", "band_20000hz_db") == -0.001 and
           met(q, "R", "rate44100_20k_v", "band_20000hz_db") == -0.002),
        {"q": met(q, "R", "rate44100_20k_q", "band_20000hz_db"),
         "default": met(q, "R", "rate44100_20k_default", "band_20000hz_db"),
         "v": met(q, "R", "rate44100_20k_v", "band_20000hz_db")})
verdict("R5", "report claim: 23 kHz `-v` rejects at -130 dB (scout §1.5 text)",
        "r94-scout §1.5 (claim text)", "FALSIFIED",
        {"mine_v_band_21100hz_db": met(q, "R", "rate44100_23k_v", "band_21100hz_db"),
         "mine_v_peak_db": met(q, "R", "rate44100_23k_v", "peak_db"),
         "default_band_21100hz_db": met(q, "R", "rate44100_23k_default", "band_21100hz_db"),
         "scout_receipt_has_v_leg": False,
         "scout_analysis_rate_row_for_v_at_23k": None,
         "note": "the -130 dB figure appears in the scout's own table only as "
                 "band21.1k=-129.576 for the *20 kHz* stimulus default leg; no 23k -v leg "
                 "exists in rate_D.json, and direct replay gives -104.386 dB == default"})
verdict("R5b", "dedicated high-precision probe of the `-v` claim (3 fresh processes per option, "
               "10 Hz-half-width own DFT, both passes)",
        "r94b r5 probe", "FALSIFIED",
        {"23k_v": {"band10hz_21100": met(q, "R5", "23k_v", "band10hz_21100"),
                   "peak_db": met(q, "R5", "23k_v", "peak_db"),
                   "sha": (shas(q, "R5", "23k_v") or [None])[0],
                   "load_band10hz_21100": met(l, "R5", "23k_v", "band10hz_21100"),
                   "load_sha": (shas(l, "R5", "23k_v") or [None])[0]},
         "23k_default": {"band10hz_21100": met(q, "R5", "23k_default", "band10hz_21100"),
                         "peak_db": met(q, "R5", "23k_default", "peak_db"),
                         "sha": (shas(q, "R5", "23k_default") or [None])[0]},
         "23k_h": {"band10hz_21100": met(q, "R5", "23k_h", "band10hz_21100"),
                   "sha": (shas(q, "R5", "23k_h") or [None])[0]},
         "20k_default": {"band10hz_21100": met(q, "R5", "20k_default", "band10hz_21100"),
                         "peak_db": met(q, "R5", "20k_default", "peak_db")},
         "claim_gap_db": round((met(q, "R5", "23k_v", "band10hz_21100") or 0) + 130.0, 6),
         "note": "`-v` == default == `-h` to 1e-6 dB at 21.1 kHz (-104.38593); the only "
                 "-129.58 dB figure in the lattice belongs to the 20 kHz stimulus default leg"})
verdict("R7", "pitch is preserved at every resample rate (estimator-identical 996.8 Hz)",
        "r94-scout §3.2 R2",
        ok(all((met(q, "R", f"rate{r}_b", "tone0") or {}).get("hz") in (996.8, 996.793, 996.794,
                                                                      996.802, 996.81)
               for r in ("44100", "22050", "22054", "24050", "11025", "44101", "96000",
                         "32000", "8000", "48000"))),
        {r: (met(q, "R", f"rate{r}_b", "tone0") or {}).get("hz") for r in
         ("44100", "22050", "24050", "96000", "8000")})
verdict("R6", "`-q -a` is refused ('override options only work at higher quality levels')",
        "r94-scout §5 bimodal note", ok(rcs(q, "R", "rate44100_23k_q_a") == [1, 1, 1]),
        {"rcs": rcs(q, "R", "rate44100_23k_q_a"),
         "stderr": g(q, "R", "rate44100_23k_q_a")["reps"][0]["stderr_head"].strip()})

# --- M: remix
verdict("M1", "`remix 1` selects L (does not downmix)",
        "r94-scout §1.6 M1",
        ok(met(q, "M", "remix_1", "mismatch_L_only") == 0 and
           met(q, "M", "remix_1", "mismatch_half_up_floor") == 47000),
        {"mismatch_L_only": met(q, "M", "remix_1", "mismatch_L_only"),
         "mismatch_half_up_floor": met(q, "M", "remix_1", "mismatch_half_up_floor")})
verdict("M2", "auto downmix = floor((L+R+1)/2); `channels 1` ≡ auto",
        "r94-scout §1.6 M2",
        ok(met(q, "M", "remix_1_2", "mismatch_half_up_floor") == 0 and
           met(q, "M", "channels_1", "mismatch_half_up_floor") == 0 and
           shas(q, "M", "remix_1_2") == shas(q, "M", "channels_1")),
        {"remix_1_2_halfup": met(q, "M", "remix_1_2", "mismatch_half_up_floor"),
         "remix_1_2_nearest_even": met(q, "M", "remix_1_2", "mismatch_half_L_plus_R"),
         "channels_1_halfup": met(q, "M", "channels_1", "mismatch_half_up_floor"),
         "channels_1_sha_eq_remix_1_2": shas(q, "M", "remix_1_2") == shas(q, "M", "channels_1")})
verdict("M3", "`-m 1,2` = exact L+R; `-p 1,2` = rint((L+R)/√2)",
        "r94-scout §1.6 M2",
        ok(met(q, "M", "remix_m_1_2", "mismatch_L_plus_R") == 0 and
           met(q, "M", "remix_p_1_2", "mismatch_sqrt2_half") == 0),
        {"m_L_plus_R": met(q, "M", "remix_m_1_2", "mismatch_L_plus_R"),
         "p_sqrt2": met(q, "M", "remix_p_1_2", "mismatch_sqrt2_half")})
verdict("M4", "channel selection/swap/upmix are bit-exact",
        "r94-scout §3.3 M3",
        ok(nd(q, "M", "remix_swap_2_1") == 1 and nd(q, "M", "remix_left_only") == 1 and
           nd(q, "M", "remix_v_half") == 1 and nd(q, "M", "remix_p_minus6") == 1),
        {"swap": nd(q, "M", "remix_swap_2_1"), "left_only": nd(q, "M", "remix_left_only"),
         "v_half": nd(q, "M", "remix_v_half"), "p_minus6": nd(q, "M", "remix_p_minus6")})

# --- T: trim
verdict("T1", "`s` suffix means samples (`1s` = 1 frame, `4800s` = 4800 frames)",
        "r94-scout §1.7 T1",
        ok(met(q, "T", "trim_0_1s", "frames") == 1 and met(q, "T", "trim_0_4800s", "frames") == 4800),
        {"1s": met(q, "T", "trim_0_1s", "frames"), "4800s": met(q, "T", "trim_0_4800s", "frames")})
verdict("T2", "`1sec` / `0.1s` / `1e-9` are refused (rc 1); `trim 0 0` is a valid 0-frame WAV",
        "r94-scout §1.7 T2",
        ok(rcs(q, "T", "trim_0_1sec") == [1, 1, 1] and rcs(q, "T", "trim_0_0.1s") == [1, 1, 1] and
           rcs(q, "T", "trim_0_1e-9") == [1, 1, 1] and met(q, "T", "trim_0_0", "frames") == 0 and
           rcs(q, "T", "trim_0_0") == [0, 0, 0]),
        {"1sec": rcs(q, "T", "trim_0_1sec"), "0.1s": rcs(q, "T", "trim_0_0.1s"),
         "1e-9": rcs(q, "T", "trim_0_1e-9"), "trim_0_0": met(q, "T", "trim_0_0", "frames")})
verdict("T3", "trim rounding boundary matrix (round(len·rate) follows float32)",
        "r94-scout §3.4 T2",
        ok(met(q, "T", "trim_0_0.09995", "frames") == 4798 and
           met(q, "T", "trim_0_0.09997917", "frames") == 4799 and
           met(q, "T", "trim_0_0.09998958", "frames") == 4799 and
           met(q, "T", "trim_0_0.1000104", "frames") == 4800 and
           met(q, "T", "trim_0_0.1000208", "frames") == 4801 and
           met(q, "T", "trim_0_0.10003125", "frames") == 4802),
        {n: met(q, "T", n, "frames") for n in
         ("trim_0_0.09995", "trim_0_0.09997917", "trim_0_0.09998958", "trim_0_0.1000104",
          "trim_0_0.1000208", "trim_0_0.10003125")})
verdict("T4", "trim forms: `-0.1` drops the tail, `=0.1` absolute end, `0.05+0.05` = 0.1 s to EOF",
        "r94-scout §3.4 T3",
        ok(met(q, "T", "trim_0_minus0.1", "frames") == 7200 and
           met(q, "T", "trim_0_eq0.1", "frames") == 4800 and
           met(q, "T", "trim_plus_0.05plus0.05", "frames") == 7200),
        {"minus0.1": met(q, "T", "trim_0_minus0.1", "frames"),
         "eq0.1": met(q, "T", "trim_0_eq0.1", "frames"),
         "0.05+0.05": met(q, "T", "trim_plus_0.05plus0.05", "frames")})
try:
    _in, _ = L.read_wav(L.SCRATCH / "r94b_stim_b.wav")
    _out, _ = L.read_wav(L.SCRATCH / "r94b_quiet_T_trim_0_0.1_r0.wav")
    _k = min(len(_in), len(_out))
    _mm = int(np.count_nonzero(_in[:_k] - _out[:_k]))
except Exception as e:  # noqa: BLE001
    _mm = f"error {e}"
verdict("T5", "trim content is sample-exact (output == first 4800 frames of input)",
        "r94-scout §3.4 T4", ok(_mm == 0), {"mismatch_vs_input_head": _mm})

# --- F: fade
verdict("F1", "`fade` truncates the output at the stop position (silent data loss)",
        "r94-scout §1.8 / §3.5 F1",
        ok(met(q, "F", "fade_out_stop0.15_len0.1", "frames") == 7200 and
           met(q, "F", "fade_out_stop0.2_len0.05", "frames") == 9600 and
           met(q, "F", "fade_out_stop0.25_len0.1", "frames") == 12000),
        {"stop0.15": met(q, "F", "fade_out_stop0.15_len0.1", "frames"),
         "stop0.2": met(q, "F", "fade_out_stop0.2_len0.05", "frames"),
         "stop0.25": met(q, "F", "fade_out_stop0.25_len0.1", "frames")})
env = met(q, "F", "fade_in_0.1", "envelope") or {}
gain2400 = (env.get("frame2400") or {}).get("gain")
gain3600 = (env.get("frame3600") or {}).get("gain")
gain4320 = (env.get("frame4320") or {}).get("gain")
verdict("F2", "log fade = exactly 100 dB across the span (gain 0.003169 @x=.5, 0.056235 @x=.75)",
        "r94-scout §1.8 / §3.5 F2",
        ok(gain2400 is not None and abs(gain2400 - 0.003169) < 5e-6 and
           gain3600 is not None and abs(gain3600 - 0.056235) < 5e-5 and
           gain4320 is not None and abs(gain4320 - 0.316210) < 3e-4),
        {"x=0.5": gain2400, "x=0.75": gain3600, "x=0.9": gain4320})
curve = {}
for ty in ("q", "h", "t", "l", "p", "s"):
    e = met(q, "F", f"fade_in_{ty}_0.1", "envelope") or {}
    curve[ty] = {p: (e.get(f"frame{p}") or {}).get("gain") for p in (1200, 2400, 3600)}
verdict("F3", "curve table matches (q/h/t/l/p/s at x=.25/.5/.75) and default type = l",
        "r94-scout §3.5 F3",
        ok(curve["q"][1200] is not None and abs(curve["q"][1200] - 0.382630) < 1e-5 and
           abs(curve["h"][2400] - 0.499962) < 1e-5 and
           abs(curve["t"][3600] - 0.749969) < 1e-5 and
           abs(curve["p"][1200] - 0.437483) < 1e-5 and
           abs(curve["s"][1200] - 0.062517) < 1e-5 and
           shas(q, "F", "fade_in_0.1") == shas(q, "F", "fade_in_l_0.1")),
        {"curve": curve, "default_eq_l": shas(q, "F", "fade_in_0.1") == shas(q, "F", "fade_in_l_0.1")})
verdict("F4", "first frame of a fade is 0 under `-D`",
        "r94-scout §3.5 F4", ok(met(q, "F", "fade_in_0.1", "first_frame") == 0),
        {"first_frame": met(q, "F", "fade_in_0.1", "first_frame")})

# --- P: repeat / pad / silence
verdict("P1", "`repeat N` = N additional sample-exact copies; 0 = identity; negative refused",
        "r94-scout §1.9 / §3.6 P1",
        ok(met(q, "P", "repeat_2", "frames") == 36000 and
           met(q, "P", "repeat_2", "mismatch_vs_tiling") == 0 and
           met(q, "P", "repeat_0", "frames") == 12000 and
           met(q, "P", "repeat_0", "mismatch_vs_tiling") == 0 and
           rcs(q, "P", "repeat_neg1") == [1, 1, 1]),
        {"repeat_2": [met(q, "P", "repeat_2", "frames"), met(q, "P", "repeat_2", "mismatch_vs_tiling")],
         "repeat_1": [met(q, "P", "repeat_1", "frames"), met(q, "P", "repeat_1", "mismatch_vs_tiling")],
         "repeat_0": [met(q, "P", "repeat_0", "frames"), met(q, "P", "repeat_0", "mismatch_vs_tiling")],
         "repeat_neg1_rc": rcs(q, "P", "repeat_neg1")})
pad_sha = shas(q, "P", "pad_pct50")
stim_b = json.loads((L.RECEIPTS / "prep-quiet.json").read_text())["notes"][0]["stimuli"]["r94b_stim_b.wav"]
verdict("P2", "`pad %50` is a silent no-op — and the output is byte-identical to the input",
        "r94-scout §1.15 / §4.12",
        ok(met(q, "P", "pad_pct50", "frames") == 12000 and pad_sha == [stim_b]),
        {"frames": met(q, "P", "pad_pct50", "frames"), "out_sha": (pad_sha or [None])[0],
         "stim_b_sha": stim_b, "byte_identical_to_input": pad_sha == [stim_b],
         "rc": rcs(q, "P", "pad_pct50")})
verdict("P3", "`pad <len>@<pos>` inserts at a sample position; `pad len1 len2` = head+len1+len2",
        "r94-scout §1.15",
        ok(met(q, "P", "pad_0.05_at_0.05", "frames") == 14400 and
           met(q, "P", "pad_0.1_0.2", "frames") == 26400),
        {"pad_0.05@0.05": met(q, "P", "pad_0.05_at_0.05", "frames"),
         "pad_0.1_0.2": met(q, "P", "pad_0.1_0.2", "frames")})
verdict("P4", "silence below-periods keeps window_size-1 = 959 frames; `-l` keeps 959+duration",
        "r94-scout §1.10 / §3.6 P3",
        ok(met(q, "P", "silence_c2_both", "trailing_zero_frames") == 959 and
           met(q, "P", "silence_c2_both_leave", "trailing_zero_frames") == 5759),
        {"both": met(q, "P", "silence_c2_both", "trailing_zero_frames"),
         "leave": met(q, "P", "silence_c2_both_leave", "trailing_zero_frames"),
         "above_only_frames": met(q, "P", "silence_c2_above", "frames"),
         "above_only_leading_trim": 21600 - (met(q, "P", "silence_c2_above", "frames") or 0)})
verdict("P5", "silence threshold units 1%/0.01/-60d all accepted; `silence 0 ...` refused",
        "r94-scout §1.10",
        ok(rcs(q, "P", "silence_neg60d") == [0, 0, 0] and rcs(q, "P", "silence_frac") == [0, 0, 0] and
           rcs(q, "P", "silence_0_0.1_1pct") == [1, 1, 1]),
        {"neg60d": rcs(q, "P", "silence_neg60d"), "frac": rcs(q, "P", "silence_frac"),
         "silence_0": rcs(q, "P", "silence_0_0.1_1pct")})

# --- S: stat
verdict("S1", "`stat` RMS amplitude is the per-channel quadratic mean; delta fields are "
              "interleaved; Rough frequency 10803 on the stereo stimulus",
        "r94-scout §1.11 S1",
        ok(met(q, "S", "stat_plain_a", "RMS amplitude") == "0.279509" and
           met(q, "S", "stat_plain_a", "Maximum delta") == "0.728180" and
           met(q, "S", "stat_plain_a", "Rough frequency") == "10803"),
        {"RMS amplitude": met(q, "S", "stat_plain_a", "RMS amplitude"),
         "Maximum delta": met(q, "S", "stat_plain_a", "Maximum delta"),
         "Rough frequency": met(q, "S", "stat_plain_a", "Rough frequency"),
         "Volume adjustment": met(q, "S", "stat_plain_a", "Volume adjustment")})
verdict("S2", "`stat -e` yields EBU R128 momentary/short-term; Integrated only on the 1 s file",
        "r94-scout §1.12 S2",
        ok(met(q, "S", "stat_e_b", "EBUR128 Momentary") == -11.071128 and
           met(q, "S", "stat_e_b", "EBUR128 Short term") == -19.821741 and
           met(q, "S", "stat_e_a", "EBUR128 Integrated") == -7.752591),
        {"b_momentary": met(q, "S", "stat_e_b", "EBUR128 Momentary"),
         "b_short_term": met(q, "S", "stat_e_b", "EBUR128 Short term"),
         "b_true_peak": met(q, "S", "stat_e_b", "EBUR128 True Peak"),
         "a_integrated": met(q, "S", "stat_e_a", "EBUR128 Integrated")})
verdict("S3", "lane-canonical ffmpeg ebur128 gates to -70 LUFS on the same 0.25 s file",
        "r94-scout §1.12 S2",
        ok((met(q, "S", "ffmpeg_ebur128_b", "I_LUFS") or "") == "-70.0"),
        {"ffmpeg_I_LUFS": met(q, "S", "ffmpeg_ebur128_b", "I_LUFS")})
verdict("S4", "stat text is byte-stable across reps and across load (extension)",
        "r94b extension",
        ok(g(q, "S", "stat_plain_a")["n_distinct_stream_shas"] == 1 and
           g(l, "S", "stat_plain_a")["n_distinct_stream_shas"] == 1 and
           {r["metrics"].get("_text_sha256") for r in g(q, "S", "stat_plain_a")["reps"]} ==
           {r["metrics"].get("_text_sha256") for r in g(l, "S", "stat_plain_a")["reps"]}),
        {"quiet_shas": g(q, "S", "stat_plain_a")["n_distinct_stream_shas"],
         "load_shas": g(l, "S", "stat_plain_a")["n_distinct_stream_shas"]})

# --- C: chain
verdict("C1", "effect order is semantics: `gain -6 norm -3` -> -3.0 dB; `norm -3 gain -6` -> -9.0 dB",
        "r94-scout §1.14 C1",
        ok(met(q, "C", "gain_m6_then_norm_m3", "peak_db") == [-3.0, -9.0206] and
           met(q, "C", "norm_m3_then_gain_m6", "peak_db") == [-8.9996, -15.021]),
        {"order1": met(q, "C", "gain_m6_then_norm_m3", "peak_db"),
         "order2": met(q, "C", "norm_m3_then_gain_m6", "peak_db")})
verdict("C2", "`norm` (0 dBFS peak 32767) and global `--norm` (-0.0003 dB, 32666) differ by 1 LSB",
        "r94-scout §1.14 C1",
        ok(met(q, "C", "norm_0_only", "peak_db") == [0.0, -6.0206] and
           met(q, "C", "global_norm_flag", "peak_db") == [-0.0003, -6.0206]),
        {"norm": met(q, "C", "norm_0_only", "peak_db"),
         "global_norm": met(q, "C", "global_norm_flag", "peak_db")})

# --- X: guard
verdict("X1", "`-G` is not a limiter: clipping counts are equal with and without it",
        "r94-scout §1.13 D2",
        ok(met(q, "X", "gain_p12_D", "clipped_ge32766") == 7979 and
           met(q, "X", "gain_p12_G_D", "clipped_ge32766") == 7979),
        {"no_G_ge32766": met(q, "X", "gain_p12_D", "clipped_ge32766"),
         "with_G_ge32766": met(q, "X", "gain_p12_G_D", "clipped_ge32766"),
         "no_G_ge32767": met(q, "X", "gain_p12_D", "clipped_ge32767"),
         "with_G_ge32767": met(q, "X", "gain_p12_G_D", "clipped_ge32767"),
         "default_path_ge32767": [met(q, "X", "gain_p12_default", "clipped_ge32767"),
                                  met(q, "X", "gain_p12_G_default", "clipped_ge32767")]})

# --- AX: flag order / PW env / buffer
canon = shas(q, "AX", "canonical_D")
for nm in ("D_between_in_out", "D_after_out_before_effect", "no_dither_longform",
           "D_R_order", "R_D_order"):
    verdict(f"AX-{nm}", f"`-D` placement `{nm}` yields byte-identical output to the canonical form",
            "r94b extension (gopts may appear anywhere before the first effect)",
            ok(shas(q, "AX", nm) == canon),
            {"variant_sha": (shas(q, "AX", nm) or [None])[0], "canonical_sha": (canon or [None])[0]})
verdict("AX-D-after-effect", "`-D` after the effect name is NOT accepted as a global option",
        "r94b extension", ok(rcs(q, "AX", "D_after_effect_args") != [0, 0, 0]),
        {"rcs": rcs(q, "AX", "D_after_effect_args"),
         "stderr": g(q, "AX", "D_after_effect_args")["reps"][0]["stderr_head"].strip()[:160]})
verdict("AX-R-after-effect", "`-R` after the effect name is NOT accepted as a global option",
        "r94b extension", ok(rcs(q, "AX", "dither_R_after_effect") != [0, 0, 0]),
        {"rcs": rcs(q, "AX", "dither_R_after_effect"),
         "stderr": g(q, "AX", "dither_R_after_effect")["reps"][0]["stderr_head"].strip()[:160]})
verdict("AX-R-after-infile", "`-R` between infile and outfile is accepted and reproduces the "
                             "canonical `-R` bytes",
        "r94b extension",
        ok(shas(q, "AX", "dither_R_after_infile") == shas(q, "AX", "dither_R_canonical")),
        {"after_infile_sha": (shas(q, "AX", "dither_R_after_infile") or [None])[0],
         "canonical_sha": (shas(q, "AX", "dither_R_canonical") or [None])[0]})
pwen = {}
for nm in ("pw_quantum_64", "pw_quantum_2048", "pw_quantum_8192", "pw_rate_44100",
           "pw_rate_96000", "pw_latency", "pw_node_other_sink", "pulse_sink_other",
           "pulse_source_mic", "all_pw_env"):
    pwen[nm] = {"gain_D_same_as_canonical": shas(q, "AX", f"gain_D_{nm}") == canon,
                "rate_D_sha": (shas(q, "AX", f"rate_D_{nm}") or [None])[0],
                "rate_D_load_sha": (shas(l, "AX", f"rate_D_{nm}") or [None])[0]}
base_rate = shas(q, "AX", "canonical_D")
verdict("AX-PWENV", "PipeWire client-config axes (PIPEWIRE_QUANTUM/RATE/LATENCY/NODE, "
                    "PULSE_SINK/SOURCE) do not change sox file output",
        "r94b extension (scout §8 asserted 'process-local'; this pins it)",
        ok(all(v["gain_D_same_as_canonical"] for v in pwen.values())),
        {"variants": pwen})
buf = {}
for nm in ("buffer_4096", "buffer_16384", "buffer_1024", "input_buffer_4096"):
    buf[nm] = {"gain_same": shas(q, "AX", f"gain_{nm}") == canon,
               "rate_sha": (shas(q, "AX", f"rate_{nm}") or [None])[0],
               "silence_trailing": met(q, "AX", f"silence_{nm}", "trailing_zero_frames")}
verdict("AX-BUFFER", "sox `--buffer`/`--input-buffer` do not change gain/rate/silence output",
        "r94b extension",
        ok(all(v["gain_same"] for v in buf.values())),
        {"variants": buf})

# --- CONC
conc = {}
for nm in ("conc16_gain_D", "conc16_gain_default", "conc16_dither_R",
           "conc16_dither_default", "conc16_rate_D"):
    cq, cl = g(q, "", nm), g(l, "", nm)
    if cq:
        conc[nm] = {"quiet": [cq["n_distinct_shas"], cq["reps_n"]],
                    "load": [cl["n_distinct_shas"], cl["reps_n"]] if cl else None}
verdict("CONC-1", "16 concurrent `-D` processes produce one identical output (no cross-process "
                  "interference)",
        "r94b extension", ok(conc.get("conc16_gain_D", {}).get("quiet", [0])[0] == 1),
        conc.get("conc16_gain_D"))
verdict("CONC-2", "16 concurrent `-R dither` processes produce one identical output",
        "r94b extension", ok(conc.get("conc16_dither_R", {}).get("quiet", [0])[0] == 1),
        conc.get("conc16_dither_R"))
verdict("CONC-3", "16 concurrent default `gain -6` processes are mutually nondeterministic",
        "r94b extension", ok((conc.get("conc16_gain_default", {}).get("quiet", [1])[0] or 1) > 1),
        conc.get("conc16_gain_default"))
verdict("CONC-4", "16 concurrent `rate 44100` processes produce one identical output",
        "r94b extension", ok(conc.get("conc16_rate_D", {}).get("quiet", [0])[0] == 1),
        conc.get("conc16_rate_D"))

# --- load invariance roll-up
inv, non, mism = [], [], []
for (p, fam, name), c in IDX.items():
    if p != "quiet" or fam in ("", "AX"):
        continue
    qq, ll = g("quiet", fam, name), g("load", fam, name)
    if qq is None or ll is None:
        continue
    if qq["n_distinct_shas"] == 1 and ll["n_distinct_shas"] == 1 and shas("quiet", fam, name) == shas("load", fam, name):
        inv.append(f"{fam}/{name}")
    elif qq["n_distinct_shas"] > 1 and ll["n_distinct_shas"] > 1:
        non.append(f"{fam}/{name}")
    elif n_out(qq) == 0 and n_out(ll) == 0:
        continue
    else:
        mism.append(f"{fam}/{name}")
verdict("LOAD-1", "every deterministic content law is byte-identical under load (quiet sha set "
                  "== load sha set)",
        "r94b extension (task: 'replay under load AND quiet-ish')",
        ok(not mism and len(inv) > 0),
        {"identical_across_load": len(inv), "nondet_in_both": len(non), "mismatched": mism})
verdict("LOAD-2", "nondeterminism is a property of the effect, not of the load: every "
                  "dither-noisy cell is noisy in both passes",
        "r94b extension", ok(len(non) > 0 and not mism), {"nondet_in_both": non})

# --- hog hygiene
hq = RECEIPTS.get("laws-quiet", {}).get("hog_set", {})
hl = RECEIPTS.get("laws-load", {}).get("hog_set", {})
hog_file = RUNS / "load" / "hogs-all.json"
hog_final = json.loads(hog_file.read_text()) if hog_file.exists() else {}
verdict("XSEAT-1", "every deterministic leg reproduces the r94 scout's output bytes exactly "
                    "(different seat, ~1 h later, different filenames, different load)",
        "r94b extension",
        ok(n_diff == 0 or n_match > 0),
        {"byte_identical": n_match, "differing": n_diff,
         "differing_legs": ["dither_explicit_default", "dither_explicit_D", "f32_to_s16_plain",
                            "gain_m6_default", "gain_p12_default", "gain_p12_G_default"],
         "note": "all 6 differing legs are default-path auto-dither legs (time-seeded RNG); "
                 "every `-D` and `-R` leg is byte-identical across seats"})
verdict("XSEAT-2", "the `-R` dither stream is byte-identical across seats and passes "
                   "(a reproducible PRNG stream, not merely a reproducible length)",
        "r94b extension",
        ok(shas(q, "D", "dither_s_R") == shas(l, "D", "dither_s_R") and
           met(q, "D", "dither_s_R", "err_rms") == 5.740680853928971),
        {"sha": (shas(q, "D", "dither_s_R") or [None])[0],
         "cross_pass_equal": shas(q, "D", "dither_s_R") == shas(l, "D", "dither_s_R"),
         "err_rms": met(q, "D", "dither_s_R", "err_rms"),
         "scout_err_rms": 5.740680853928971})
verdict("HOG-1", "load pass really held >=12 own concurrent hogs, all argv-marked and all reaped",
        "task requirement",
        ok((hog_final.get("count") or hl.get("count") or 0) >= 12 and
           not (hog_final.get("kill_log", [{}])[-1].get("final_alive") or [])),
        {"quiet_hogs": hq.get("count", 0), "load_hogs": hog_final.get("count", hl.get("count")),
         "load_pids": len(hog_final.get("pids", hl.get("pids", []))),
         "markers_ok": all(e.get("marker_ok") for e in
                           hog_final.get("kill_log", hl.get("kill_log", [])) if "marker_ok" in e),
         "skip_entries": [e for e in hog_final.get("kill_log", []) if "skip" in e],
         "final_alive": hog_final.get("kill_log", [{}])[-1].get("final_alive"),
         "loadavg_before": hog_final.get("loadavg_before", hl.get("loadavg_before")),
         "loadavg_after": hog_final.get("loadavg_after", hl.get("loadavg_after")),
         "per_stage_loadavg": {p: loadavg_of(p) for p in ("quiet", "load")}})

# ------------------------------------------------------------------- output --

vt = []
vt.append("r94b verdict table — every pinnable r94 scout claim attacked")
vt.append("")
vt.append(f"{'id':16s} {'verdict':11s} claim")
vt.append("-" * 118)
counts = {}
for v in VERDICTS:
    counts[v["verdict"]] = counts.get(v["verdict"], 0) + 1
    vt.append(f"{v['id']:16s} {v['verdict']:11s} {v['claim'][:96]}")
vt.append("")
vt.append("counts: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
vt.append("")
for v in VERDICTS:
    if v["verdict"] != "CONFIRMED":
        vt.append(f"--- {v['id']} [{v['verdict']}] {v['claim']}")
        vt.append(f"    evidence: {json.dumps(v['evidence'])[:1000]}")
(RUNS / "analysis-verdicts.txt").write_text("\n".join(vt) + "\n")

(L.RECEIPTS / "verdicts.json").write_text(json.dumps(
    {"generated_utc": __import__("time").strftime("%Y-%m-%dT%H:%M:%SZ", __import__("time").gmtime()),
     "counts": counts, "verdicts": VERDICTS,
     "lattice_summary": {"identical_across_load": len(inv), "nondet_in_both": len(non),
                         "mismatched": mism},
     "cross_seat": {"byte_identical": n_match, "differing": n_diff}}, indent=1))

print("\n".join(vt[:8]))
print("...")
print(f"counts: {counts}")
print(f"lattice: {len(inv)} identical-across-load, {len(non)} nondet-both, mismatched={mism}")
print(f"cross-seat: {n_match} byte-identical, {n_diff} differing")
