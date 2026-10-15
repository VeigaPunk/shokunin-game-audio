#!/usr/bin/env python3
"""r94 scout driver — SoX_ng v14.8.0.1 effect/DSP lattice, staged.

Usage: python3 probes/r94driver.py <stage> [reps]
Stages: prep gain rate remix trim fade repeat_pad_silence dither stat chain
Env:    R94_PREFIX="-D"   -> insert global sox options (e.g. -D no-dither)
        R94_SUFFIX="_D"   -> receipt/run/output suffix for that pass

All writes under corpus/live/r94-scout/. File-only: no PipeWire object is ever
created, no device is opened (never `-d`/`-p`/`play`/`rec`).
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r94lib as L  # noqa: E402

REPS = 3
PREFIX = os.environ.get("R94_PREFIX", "").split()
SUFFIX = os.environ.get("R94_SUFFIX", "")


# ------------------------------------------------------------------ helpers --

def i16(path):
    arr, meta = L.read_wav(path)
    return np.rint(arr * 32768.0).astype(np.int64), meta


def basic_metrics(path):
    arr, meta = L.read_wav(path)
    out = {
        "frames": meta["frames"], "channels": meta["channels"], "rate": meta["rate"],
        "duration_s": round(meta["duration"], 6), "bits": meta["bits"],
        "peak_db": [round(L.peak_db(arr[:, c]), 4) for c in range(arr.shape[1])],
        "rms_db": [round(L.rms_db(arr[:, c]), 4) for c in range(arr.shape[1])],
    }
    for c in range(arr.shape[1]):
        f, a = L.tone_hz(arr[:, c], meta["rate"], lo=100.0)
        out[f"tone{c}"] = {"hz": round(f, 3) if f else None,
                           "db": round(a, 3) if a is not None else None}
    return out


def leg(stage, name, mk_argv, analysis=None, reps=REPS, wall=10.0, out_cap=64 << 20,
        out_path_fn=None, expect_kill=False):
    stage_d = stage + SUFFIX
    reps_out = []
    for rep in range(reps):
        if out_path_fn is None:
            out = L.SCRATCH / f"r94s_{stage_d}_{name}_r{rep}.wav"
        else:
            out = out_path_fn(rep)
        if isinstance(out, Path) and out.exists():
            out.unlink()
        argv = mk_argv(out)
        leg_dir = L.RUNS / stage_d / name / f"rep{rep}"
        meta = L.run_bounded(argv, leg_dir, wall=wall, out_path=out, out_cap=out_cap)
        m = {}
        if analysis and meta.get("out_sha256"):
            try:
                m = analysis(out, meta)
            except Exception as e:
                m = {"analysis_error": f"{type(e).__name__}: {e}"}
        reps_out.append({
            "argv": argv, "rc": meta["rc"], "wall_s": meta["wall_s"],
            "killed": meta["killed"], "out_bytes": meta["out_bytes"],
            "out_sha256": meta["out_sha256"], "metrics": m,
            "stderr_head": meta["stderr_head"],
        })
    shas = {r["out_sha256"] for r in reps_out}
    summary = {
        "name": name, "argv": reps_out[0]["argv"] if reps_out else None,
        "reps": reps_out, "stable": len(shas) == 1,
        "n_distinct_shas": len(shas), "expect_kill": expect_kill,
    }
    if reps_out and reps_out[0]["metrics"]:
        summary["metrics"] = reps_out[0]["metrics"]
    return summary


def receipt(stage, legs, t0, notes=None):
    payload = {
        "host": L.host_context(),
        "prefix": PREFIX, "suffix": SUFFIX,
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t0)),
        "reps_default": REPS, "notes": notes or [], "legs": legs,
    }
    p = L.write_receipt(stage + SUFFIX, payload)
    print(f"[{stage}{SUFFIX}] {len(legs)} legs -> {p}", flush=True)


def sox(*parts):
    return [L.SOX, *PREFIX, *[str(p) for p in parts]]


# --------------------------------------------------------------------- prep --

STIM = {}


def build_stimuli():
    rate = 48000
    t_a = np.arange(48000) / rate
    a = np.column_stack([
        np.rint(16384.0 * np.sin(2 * np.pi * 1000.0 * t_a)),
        np.rint(8192.0 * np.sin(2 * np.pi * 1500.0 * t_a)),
    ]).astype("<i2")
    L.write_wav_pcm16(L.SCRATCH / "r94s_stim_a.wav", a, rate)

    t_b = np.arange(12000) / rate
    b = np.rint(16384.0 * np.sin(2 * np.pi * 997.0 * t_b)).astype("<i2")
    L.write_wav_pcm16(L.SCRATCH / "r94s_stim_b.wav", b, rate)

    c = np.zeros(19200, dtype="<i2")
    t_c = np.arange(9600) / rate
    c[4800:14400] = np.rint(16384.0 * np.sin(2 * np.pi * 997.0 * t_c)).astype("<i2")
    L.write_wav_pcm16(L.SCRATCH / "r94s_stim_c.wav", c, rate)

    f = (0.5 * np.sin(2 * np.pi * 997.0 * t_b)).astype("<f4")
    L.write_wav_f32(L.SCRATCH / "r94s_stim_f.wav", f, rate)

    h = np.rint(16384.0 * np.sin(2 * np.pi * 20000.0 * t_b)).astype("<i2")
    L.write_wav_pcm16(L.SCRATCH / "r94s_stim_h.wav", h, rate)

    i = np.rint(16384.0 * np.sin(2 * np.pi * 997.0 * np.arange(12001) / rate)).astype("<i2")
    L.write_wav_pcm16(L.SCRATCH / "r94s_stim_i.wav", i, rate)

    j = np.rint(16384.0 * np.sin(2 * np.pi * 23000.0 * t_b)).astype("<i2")
    L.write_wav_pcm16(L.SCRATCH / "r94s_stim_j.wav", j, rate)

    rng = np.random.default_rng(94)
    r = rng.integers(-32768, 32768, size=4800, dtype=np.int64).astype("<i2")
    L.write_wav_pcm16(L.SCRATCH / "r94s_stim_r.wav", r, rate)

    # c2: silence 0.1 + tone 0.2 + silence 0.15 (below-periods margin)
    c2 = np.zeros(21600, dtype="<i2")
    t_c2 = np.arange(9600) / rate
    c2[4800:14400] = np.rint(16384.0 * np.sin(2 * np.pi * 997.0 * t_c2)).astype("<i2")
    L.write_wav_pcm16(L.SCRATCH / "r94s_stim_c2.wav", c2, rate)

    for p in sorted(L.SCRATCH.glob("r94s_stim_*.wav")):
        STIM[p.name] = L.sha256_file(p)


def stage_prep(reps):
    t0 = time.time()
    build_stimuli()
    legs = []
    leg_dir = L.RUNS / "prep" / "sox_decode" / "rep0"
    meta = L.run_bounded([L.SOX, str(L.SCRATCH / "r94s_stim_a.wav"), "-t", "f32", "-"],
                         leg_dir, wall=10.0)
    sox_bytes = (leg_dir / "stdout").read_bytes()
    sox_arr = np.frombuffer(sox_bytes, dtype="<f4").astype(np.float64)
    own_arr, _ = L.read_wav(L.SCRATCH / "r94s_stim_a.wav")
    n = min(sox_arr.size, own_arr.size)
    legs.append({
        "name": "reader_crosscheck",
        "argv": [L.SOX, "r94s_stim_a.wav", "-t", "f32", "-"],
        "sox_float_count": int(sox_arr.size), "own_float_count": int(own_arr.size),
        "max_abs_diff_sox_vs_own": float(np.max(np.abs(sox_arr[:n] - own_arr.reshape(-1)[:n]))) if n else None,
        "rc": meta["rc"], "sha256_sox_stdout": L.sha256_bytes(sox_bytes),
    })
    receipt("prep", legs, t0, notes=[{"stimuli": STIM}])


# --------------------------------------------------------------------- gain --

def _gain_metrics_factory(ref_path, factor):
    ref, _ = i16(ref_path)

    def analysis(path, meta):
        got, _ = i16(path)
        out = basic_metrics(path)
        exp = np.rint(ref.astype(np.float64) * factor).astype(np.int64)
        k = min(len(exp), len(got))
        diff = np.abs(exp[:k] - got[:k])
        out["mismatch_vs_rint_formula"] = int(np.count_nonzero(diff))
        out["max_abs_diff_vs_formula"] = int(diff.max()) if k else None
        out["first8_ch0"] = got[:8, 0].tolist()
        out["first8_expected_ch0"] = exp[:8, 0].tolist()
        out["clipped_samples"] = int(np.count_nonzero(np.abs(got) >= 32767))
        return out
    return analysis


def _vol_amp_analysis(ref_path, factor):
    """Which integer rounding does the amplitude form use? (floor/trunc/rint/ceil)"""
    ref, _ = i16(ref_path)

    def analysis(path, meta):
        got, _ = i16(path)
        out = basic_metrics(path)
        x = ref.astype(np.float64) * factor
        for nm, cand in (("floor", np.floor(x)), ("trunc", np.trunc(x)),
                         ("rint", np.rint(x)), ("ceil", np.ceil(x))):
            v = cand.astype(np.int64)
            k = min(len(v), len(got))
            d = np.abs(v[:k] - got[:k])
            out[f"mismatch_{nm}"] = int(np.count_nonzero(d))
            out[f"maxdiff_{nm}"] = int(d.max()) if k else None
        return out
    return analysis


def stage_gain(reps):
    t0 = time.time()
    a = L.SCRATCH / "r94s_stim_a.wav"
    b = L.SCRATCH / "r94s_stim_b.wav"
    legs = []
    f6 = 10 ** (-6.0 / 20)
    fp6 = 10 ** (6.0 / 20)
    legs.append(leg("gain", "gain_m6", lambda o: sox(a, o, "gain", "-6"),
                    _gain_metrics_factory(a, f6), reps=reps))
    legs.append(leg("gain", "gain_p6", lambda o: sox(b, o, "gain", "6"),
                    _gain_metrics_factory(b, fp6), reps=reps))
    legs.append(leg("gain", "gain_0", lambda o: sox(a, o, "gain", "0"),
                    _gain_metrics_factory(a, 1.0), reps=reps))
    legs.append(leg("gain", "gain_n", lambda o: sox(a, o, "gain", "-n"),
                    lambda p, m: basic_metrics(p) | {
                        "first8_ints_ch0": np.rint(L.read_wav(p)[0][:, 0] * 32768).astype(int)[:8].tolist()},
                    reps=reps))
    legs.append(leg("gain", "gain_n_m6", lambda o: sox(a, o, "gain", "-n", "-6"),
                    lambda p, m: basic_metrics(p), reps=reps))
    legs.append(leg("gain", "gain_e", lambda o: sox(a, o, "gain", "-e"),
                    lambda p, m: basic_metrics(p), reps=reps))
    legs.append(leg("gain", "gain_b", lambda o: sox(a, o, "gain", "-b"),
                    lambda p, m: basic_metrics(p), reps=reps))
    legs.append(leg("gain", "gain_h_m6", lambda o: sox(a, o, "gain", "-h", "-6"),
                    lambda p, m: basic_metrics(p), reps=reps))
    legs.append(leg("gain", "gain_h_m6_reclaim", lambda o: sox(a, o, "gain", "-h", "-6", "gain", "-r"),
                    lambda p, m: basic_metrics(p), reps=reps))
    legs.append(leg("gain", "vol_amp_0.5", lambda o: sox(a, o, "vol", "0.5"),
                    _vol_amp_analysis(a, 0.5), reps=reps))
    legs.append(leg("gain", "vol_db_m6.0206", lambda o: sox(a, o, "vol", "-6.0206", "d"),
                    _gain_metrics_factory(a, 10 ** (-6.0206 / 20)), reps=reps))
    legs.append(leg("gain", "vol_pow_0.5", lambda o: sox(a, o, "vol", "0.5", "p"),
                    _vol_amp_analysis(a, 0.5 ** 0.5), reps=reps))
    legs.append(leg("gain", "vol_invert", lambda o: sox(b, o, "vol", "-1"),
                    lambda p, m: basic_metrics(p) | {
                        "first8_ints": np.rint(L.read_wav(p)[0][:, 0] * 32768).astype(int)[:8].tolist()},
                    reps=reps))
    legs.append(leg("gain", "global_v_0.5", lambda o: sox("-v", "0.5", a, o),
                    _vol_amp_analysis(a, 0.5), reps=reps))
    receipt("gain", legs, t0)


# --------------------------------------------------------------------- rate --

def _rate_metrics(path, meta, probe_hz=(997.0, 20000.0, 23000.0, 21100.0)):
    arr, m = L.read_wav(path)
    out = basic_metrics(path)
    for f0 in probe_hz:
        out[f"band_{int(f0)}hz_db"] = round(L.band_level_db(arr, m["rate"], f0), 3)
    return out


def stage_rate(reps):
    t0 = time.time()
    b = L.SCRATCH / "r94s_stim_b.wav"
    h = L.SCRATCH / "r94s_stim_h.wav"
    i = L.SCRATCH / "r94s_stim_i.wav"
    j = L.SCRATCH / "r94s_stim_j.wav"
    legs = []
    for q, flag in (("default", None), ("q", "-q"), ("m", "-m"), ("v", "-v")):
        fl = [flag] if flag else []
        legs.append(leg("rate", f"rate44100_{q}",
                        (lambda f: lambda o: sox(b, o, "rate", *f, "44100"))(fl),
                        _rate_metrics, reps=reps))
    for r in ("96000", "22050", "22054", "24050", "32000", "8000", "11025", "44101", "48000"):
        legs.append(leg("rate", f"rate{r}", (lambda rr: lambda o: sox(b, o, "rate", rr))(r),
                        _rate_metrics, reps=reps))
    for r in ("44100", "22050", "96000", "32000", "22054"):
        legs.append(leg("rate", f"rate{r}_odd12001", (lambda rr: lambda o: sox(i, o, "rate", rr))(r),
                        _rate_metrics, reps=reps))
    legs.append(leg("rate", "rate44100_20k_default", lambda o: sox(h, o, "rate", "44100"),
                    _rate_metrics, reps=reps))
    legs.append(leg("rate", "rate44100_20k_q", lambda o: sox(h, o, "rate", "-q", "44100"),
                    _rate_metrics, reps=reps))
    legs.append(leg("rate", "rate44100_20k_v", lambda o: sox(h, o, "rate", "-v", "44100"),
                    _rate_metrics, reps=reps))
    for nm, fl in (("default", []), ("alias_a", ["-a"]), ("q", ["-q"]), ("q_alias_a", ["-q", "-a"]),
                   ("m_alias_a", ["-m", "-a"])):
        legs.append(leg("rate", f"rate44100_23k_{nm}",
                        (lambda f: lambda o: sox(j, o, "rate", *f, "44100"))(fl),
                        _rate_metrics, reps=reps))
    legs.append(leg("rate", "rate44100_minphase_M",
                    lambda o: sox(b, o, "rate", "-v", "-M", "44100"),
                    _rate_metrics, reps=reps))
    receipt("rate", legs, t0)


# -------------------------------------------------------------------- remix --

def stage_remix(reps):
    t0 = time.time()
    a = L.SCRATCH / "r94s_stim_a.wav"
    b = L.SCRATCH / "r94s_stim_b.wav"
    legs = []

    def downmix_analysis(path, meta):
        got, _ = i16(path)
        ref, _ = i16(a)
        Lc, Rc = ref[:, 0], ref[:, 1]
        cands = {
            "L_plus_R": Lc + Rc,
            "half_L_plus_R": np.rint((Lc + Rc) / 2.0),
            "half_up_floor": np.floor((Lc + Rc + 1) / 2.0),
            "mean_int": (Lc + Rc) // 2,
            "sqrt2_half": np.rint((Lc + Rc) / 2.0 ** 0.5),
            "L_only": Lc,
        }
        out = basic_metrics(path)
        for k, v in cands.items():
            d = np.abs(np.clip(v, -32768, 32767) - got[:len(v), 0])
            out[f"mismatch_{k}"] = int(np.count_nonzero(d))
            out[f"maxdiff_{k}"] = int(d.max()) if len(d) else None
        return out

    def sel_analysis(path, meta):
        return basic_metrics(path) | {
            "first8_ints": np.rint(L.read_wav(path)[0][:, 0] * 32768).astype(int)[:8].tolist()}

    for name, fx, an in (
        ("remix_1", ["remix", "1"], downmix_analysis),
        ("remix_1_2_sum", ["remix", "1,2"], downmix_analysis),
        ("remix_m_1_2", ["remix", "-m", "1,2"], downmix_analysis),
        ("remix_a_1_2", ["remix", "-a", "1,2"], downmix_analysis),
        ("remix_p_1_2", ["remix", "-p", "1,2"], downmix_analysis),
        ("channels_1", ["channels", "1"], downmix_analysis),
        ("remix_swap_2_1", ["remix", "2", "1"], sel_analysis),
        ("remix_left_only", ["remix", "1", "0"], sel_analysis),
        ("remix_right_only", ["remix", "0", "1"], sel_analysis),
        ("remix_v_half", ["remix", "1v0.5", "2v0.5"], sel_analysis),
        ("remix_p_minus6", ["remix", "1p-6"], sel_analysis),
    ):
        legs.append(leg("remix", name, (lambda f: lambda o: sox(a, o, *f))(fx), an, reps=reps))
    legs.append(leg("remix", "mono_to_stereo_1_1", lambda o: sox(b, o, "remix", "1", "1"),
                    lambda p, m: basic_metrics(p) | {
                        "first8_ch0": np.rint(L.read_wav(p)[0][:, 0] * 32768).astype(int)[:8].tolist(),
                        "first8_ch1": np.rint(L.read_wav(p)[0][:, 1] * 32768).astype(int)[:8].tolist()},
                    reps=reps))
    receipt("remix", legs, t0)


# --------------------------------------------------------------------- trim --

def stage_trim(reps):
    t0 = time.time()
    b = L.SCRATCH / "r94s_stim_b.wav"
    legs = []
    forms = [
        ("trim_0_0.1", ["trim", "0", "0.1"]),
        ("trim_0.1", ["trim", "0.1"]),
        ("trim_0.1_0.1", ["trim", "0.1", "0.1"]),
        ("trim_0_0.10001", ["trim", "0", "0.10001"]),
        ("trim_0_0.09999", ["trim", "0", "0.09999"]),
        ("trim_0_0.09995", ["trim", "0", "0.09995"]),
        ("trim_0_0.09997917", ["trim", "0", "0.09997917"]),
        ("trim_0_0.09998958", ["trim", "0", "0.09998958"]),
        ("trim_0_0.1000104", ["trim", "0", "0.1000104"]),
        ("trim_0_0.1000208", ["trim", "0", "0.1000208"]),
        ("trim_0_0.10003125", ["trim", "0", "0.10003125"]),
        ("trim_0_minus0.1", ["trim", "0", "-0.1"]),
        ("trim_0_eq0.1", ["trim", "0", "=0.1"]),
        ("trim_0_100", ["trim", "0", "100"]),
        ("trim_0.2_0.2", ["trim", "0.2", "0.2"]),
        ("trim_0_0", ["trim", "0", "0"]),
        ("trim_0_1e-9", ["trim", "0", "1e-9"]),
        ("trim_0_1s", ["trim", "0", "1s"]),
        ("trim_0_4800s", ["trim", "0", "4800s"]),
        ("trim_0_0.1s", ["trim", "0", "0.1s"]),
        ("trim_0_1sec", ["trim", "0", "1sec"]),
        ("trim_plus_0.05plus0.05", ["trim", "0.05+0.05"]),
    ]
    for name, fx in forms:
        legs.append(leg("trim", name, (lambda f: lambda o: sox(b, o, *f))(fx),
                        lambda p, m: basic_metrics(p) | {
                            "first4_ints": np.rint(L.read_wav(p)[0][:, 0] * 32768).astype(int)[:4].tolist()},
                        reps=reps))
    receipt("trim", legs, t0)


# --------------------------------------------------------------------- fade --

def stage_fade(reps):
    t0 = time.time()
    b = L.SCRATCH / "r94s_stim_b.wav"
    ref, _ = i16(b)
    legs = []

    def env_analysis(positions):
        def analysis(path, meta):
            got, _ = i16(path)
            out = basic_metrics(path)
            env = {}
            for p in positions:
                if 0 <= p < len(got):
                    r = float(ref[p, 0]) if ref[p, 0] != 0 else float("nan")
                    env[f"frame{p}"] = {
                        "out": int(got[p, 0]), "in": int(ref[p, 0]),
                        "gain": (round(float(got[p, 0]) / r, 8) if r == r and r != 0 else None),
                    }
            out["envelope"] = env
            out["first_frame"] = int(got[0, 0])
            return out
        return analysis

    pos_in = [0, 480, 960, 1200, 1920, 2400, 2880, 3600, 3840, 4320, 4799, 4800, 6000, 11999]
    pos_out = [0, 7200, 8400, 9600, 10200, 10800, 11400, 11999]
    legs.append(leg("fade", "fade_in_0.1", lambda o: sox(b, o, "fade", "0.1"),
                    env_analysis(pos_in), reps=reps))
    legs.append(leg("fade", "fade_out_stop0.25_len0.1",
                    lambda o: sox(b, o, "fade", "0", "0.25", "0.1"),
                    env_analysis(pos_out), reps=reps))
    legs.append(leg("fade", "fade_out_stop0.15_len0.1",
                    lambda o: sox(b, o, "fade", "0", "0.15", "0.1"),
                    env_analysis(pos_out), reps=reps))
    legs.append(leg("fade", "fade_out_stop0.2_len0.05",
                    lambda o: sox(b, o, "fade", "0", "0.2", "0.05"),
                    env_analysis(pos_out), reps=reps))
    for ty in ("q", "h", "t", "l", "p", "s"):
        legs.append(leg("fade", f"fade_in_{ty}_0.1",
                        (lambda t: lambda o: sox(b, o, "fade", t, "0.1"))(ty),
                        env_analysis(pos_in), reps=reps))
    receipt("fade", legs, t0)


# ------------------------------------------------- repeat / pad / silence ----

def stage_repeat_pad_silence(reps):
    t0 = time.time()
    b = L.SCRATCH / "r94s_stim_b.wav"
    c = L.SCRATCH / "r94s_stim_c.wav"
    ref, _ = i16(b)
    legs = []

    def seam_analysis(path, meta):
        got, _ = i16(path)
        out = basic_metrics(path)
        n = len(got)
        tiled = ref[np.arange(n) % len(ref), 0]
        d = np.abs(tiled - got[:, 0])
        out["mismatch_vs_tiling"] = int(np.count_nonzero(d))
        out["maxdiff_vs_tiling"] = int(d.max()) if n else None
        return out

    legs.append(leg("repeat", "repeat_2", lambda o: sox(b, o, "repeat", "2"), seam_analysis, reps=reps))
    legs.append(leg("repeat", "repeat_1", lambda o: sox(b, o, "repeat", "1"), seam_analysis, reps=reps))
    legs.append(leg("repeat", "repeat_0", lambda o: sox(b, o, "repeat", "0"), seam_analysis, reps=reps))
    legs.append(leg("repeat", "repeat_neg1", lambda o: sox(b, o, "repeat", "-1"), seam_analysis, reps=reps))
    legs.append(leg("repeat", "repeat_0_then_trim",
                    lambda o: sox(b, o, "repeat", "0", "trim", "0", "0.5"),
                    seam_analysis, reps=reps, wall=8.0, out_cap=32 << 20))

    def pad_analysis(path, meta):
        got, _ = i16(path)
        out = basic_metrics(path)
        n = len(got)
        nz = np.nonzero(got[:, 0])[0]
        out["first_nonzero_frame"] = int(nz[0]) if len(nz) else None
        out["last_nonzero_frame"] = int(nz[-1]) if len(nz) else None
        out["zero_frames_total"] = int(np.count_nonzero(got[:, 0] == 0))
        return out

    legs.append(leg("pad", "pad_0.1_0.2", lambda o: sox(b, o, "pad", "0.1", "0.2"), pad_analysis, reps=reps))
    legs.append(leg("pad", "pad_0.05_at_0.05", lambda o: sox(b, o, "pad", "0.05@0.05"), pad_analysis, reps=reps))
    legs.append(leg("pad", "pad_pct50", lambda o: sox(b, o, "pad", "%50"), pad_analysis, reps=reps))

    def sil_analysis(path, meta):
        got, _ = i16(path)
        out = basic_metrics(path)
        out["first8_ints"] = got[:8, 0].tolist()
        out["last8_ints"] = got[-8:, 0].tolist()
        return out

    legs.append(leg("silence", "silence_1_0.1_1pct",
                    lambda o: sox(c, o, "silence", "1", "0.1", "1%"), sil_analysis, reps=reps))
    legs.append(leg("silence", "silence_lead_leave",
                    lambda o: sox(c, o, "silence", "-l", "1", "0.1", "1%"), sil_analysis, reps=reps))
    legs.append(leg("silence", "silence_0_0.1_1pct",
                    lambda o: sox(c, o, "silence", "0", "0.1", "1%"), sil_analysis, reps=reps))
    legs.append(leg("silence", "silence_both_1_0.1_1pct",
                    lambda o: sox(c, o, "silence", "1", "0.1", "1%", "1", "0.1", "1%"),
                    sil_analysis, reps=reps))
    legs.append(leg("silence", "silence_both_leave",
                    lambda o: sox(c, o, "silence", "-l", "1", "0.1", "1%", "1", "0.1", "1%"),
                    sil_analysis, reps=reps))
    legs.append(leg("silence", "silence_1_0.05_0.01frac",
                    lambda o: sox(c, o, "silence", "1", "0.05", "0.01"), sil_analysis, reps=reps))
    legs.append(leg("silence", "silence_1_0.05_neg60d",
                    lambda o: sox(c, o, "silence", "1", "0.05", "-60d"), sil_analysis, reps=reps))
    # below-periods law needs margin: c2 = 0.1 s silence + 0.2 s tone + 0.15 s silence
    c2 = L.SCRATCH / "r94s_stim_c2.wav"

    def sil2_analysis(path, meta):
        got, _ = i16(path)
        out = basic_metrics(path)
        nz = np.nonzero(got[:, 0])[0]
        out["first_nonzero_frame"] = int(nz[0]) if len(nz) else None
        out["last_nonzero_frame"] = int(nz[-1]) if len(nz) else None
        out["trailing_zero_frames"] = int(len(got) - 1 - nz[-1]) if len(nz) else len(got)
        out["first8_ints"] = got[:8, 0].tolist()
        out["last8_ints"] = got[-8:, 0].tolist()
        return out
    legs.append(leg("silence", "c2_silence_above_only",
                    lambda o: sox(c2, o, "silence", "1", "0.1", "1%"), sil2_analysis, reps=reps))
    legs.append(leg("silence", "c2_silence_both_0.1",
                    lambda o: sox(c2, o, "silence", "1", "0.1", "1%", "1", "0.1", "1%"),
                    sil2_analysis, reps=reps))
    legs.append(leg("silence", "c2_silence_both_leave",
                    lambda o: sox(c2, o, "silence", "-l", "1", "0.1", "1%", "1", "0.1", "1%"),
                    sil2_analysis, reps=reps))
    legs.append(leg("silence", "c2_silence_both_0.05",
                    lambda o: sox(c2, o, "silence", "1", "0.1", "1%", "1", "0.05", "1%"),
                    sil2_analysis, reps=reps))
    receipt("repeat_pad_silence", legs, t0)


# ------------------------------------------------------------------- dither --

def stage_dither(reps):
    t0 = time.time()
    f = L.SCRATCH / "r94s_stim_f.wav"
    a = L.SCRATCH / "r94s_stim_a.wav"
    b = L.SCRATCH / "r94s_stim_b.wav"
    legs = []

    def conv_metrics(path, meta):
        arr, _ = L.read_wav(path)
        out = basic_metrics(path)
        src, _ = L.read_wav(f)
        got = np.rint(arr * 32768.0).astype(np.int64)
        exact = np.rint(src * 32768.0).astype(np.int64)
        k = min(len(got), len(exact))
        d = got[:k, 0] - exact[:k, 0]
        out["mismatch_vs_round"] = int(np.count_nonzero(d))
        out["max_abs_err"] = int(np.abs(d).max()) if k else None
        out["err_rms"] = float(np.sqrt(np.mean(d.astype(np.float64) ** 2))) if k else None
        return out

    legs.append(leg("dither", "f32_to_s16_plain", lambda o: sox(f, "-b", "16", o), conv_metrics, reps=5))
    legs.append(leg("dither", "f32_to_s16_dither", lambda o: sox(f, "-b", "16", o, "dither"),
                    conv_metrics, reps=5))
    legs.append(leg("dither", "f32_to_s16_dither_R",
                    lambda o: [L.SOX, *PREFIX, "-R", str(f), "-b", "16", str(o), "dither"],
                    conv_metrics, reps=5))
    legs.append(leg("dither", "f32_to_s16_dither_s", lambda o: sox(f, "-b", "16", o, "dither", "-s"),
                    conv_metrics, reps=5))
    legs.append(leg("dither", "f32_to_s16_dither_s_R",
                    lambda o: [L.SOX, *PREFIX, "-R", str(f), "-b", "16", str(o), "dither", "-s"],
                    conv_metrics, reps=5))
    legs.append(leg("dither", "f32_to_s16_dither_p12_R",
                    lambda o: [L.SOX, *PREFIX, "-R", str(f), "-b", "16", str(o), "dither", "-p", "12"],
                    conv_metrics, reps=3))
    legs.append(leg("dither", "f32_to_s24_plain", lambda o: sox(f, "-b", "24", o), basic_metrics, reps=3))
    legs.append(leg("dither", "f32_to_s32_plain", lambda o: sox(f, "-b", "32", o), basic_metrics, reps=3))

    def copy_metrics(path, meta):
        same = L.sha256_file(path) == L.sha256_file(a)
        return {"byte_identical_to_input": bool(same)}

    legs.append(leg("dither", "copy_plain", lambda o: sox(a, o), copy_metrics, reps=3))

    def s16_gain_metrics(path, meta):
        got, _ = i16(path)
        ref, _ = i16(a)
        exp = np.rint(ref.astype(np.float64) * 10 ** (-6.0 / 20)).astype(np.int64)
        k = min(len(got), len(exp))
        d = got[:k] - exp[:k]
        return {
            "mismatch_vs_formula": int(np.count_nonzero(d)),
            "max_abs_err": int(np.abs(d).max()) if k else None,
            "err_rms": float(np.sqrt(np.mean(d.astype(np.float64) ** 2))) if k else None,
            "first8_ch0": got[:8, 0].tolist(),
        }
    legs.append(leg("dither", "s16_gain_m6", lambda o: sox(a, o, "gain", "-6"), s16_gain_metrics, reps=3))
    # 24-bit output: auto-dither condition is `ofile precision < 24`
    legs.append(leg("dither", "s16_to_s24_gain",
                    lambda o: sox(a, "-b", "24", o, "gain", "-6"), basic_metrics, reps=3))
    # rate at the same rate is SOX_EFF_NULL
    def ident_metrics(path, meta):
        return {"byte_identical_to_input": L.sha256_file(path) == L.sha256_file(b)}
    legs.append(leg("dither", "rate_same_rate_identity",
                    lambda o: sox(b, o, "rate", "48000"), ident_metrics, reps=3))
    legs.append(leg("dither", "gain_integer_p6",
                    lambda o: sox(b, o, "gain", "6"), basic_metrics, reps=3))

    def clip_metrics(path, meta):
        got, _ = i16(path)
        return {"clipped_ge32767": int(np.count_nonzero(np.abs(got) >= 32767)),
                "clipped_ge32766": int(np.count_nonzero(np.abs(got) >= 32766)),
                "peak_db": [round(L.peak_db(L.read_wav(path)[0][:, c]), 4)
                            for c in range(got.shape[1])],
                "first8_ch0": got[:8, 0].tolist()}
    legs.append(leg("guard", "gain_p12", lambda o: sox(b, o, "gain", "12"), clip_metrics, reps=3))
    legs.append(leg("guard", "gain_p12_G", lambda o: sox("-G", b, o, "gain", "12"), clip_metrics, reps=3))
    receipt("dither", legs, t0)


# --------------------------------------------------------------------- stat --

def stage_stat(reps):
    t0 = time.time()
    a = L.SCRATCH / "r94s_stim_a.wav"
    b = L.SCRATCH / "r94s_stim_b.wav"
    legs = []

    def mk_stat_leg(name, argv_builder, parser, stream="stderr"):
        reps_out = []
        for rep in range(reps):
            leg_dir = L.RUNS / "stat" / name / f"rep{rep}"
            meta = L.run_bounded(argv_builder(), leg_dir, wall=10.0)
            txt = (leg_dir / stream).read_text(errors="replace")
            m = parser(txt)
            m["_text_sha256"] = L.sha256_bytes(txt.encode())
            reps_out.append({"argv": argv_builder(), "rc": meta["rc"], "wall_s": meta["wall_s"],
                             "killed": meta["killed"], "metrics": m, "text": txt[:2000]})
        shas = {r["metrics"]["_text_sha256"] for r in reps_out}
        return {"name": name, "argv": reps_out[0]["argv"], "reps": reps_out,
                "stable": len(shas) == 1, "n_distinct_shas": len(shas),
                "metrics": reps_out[0]["metrics"], "text": reps_out[0]["text"]}

    def parse_stat(txt):
        out = {}
        for line in txt.splitlines():
            if ":" in line:
                k, _, v = line.partition(":")
                out[k.strip()] = v.strip()
        return out

    def parse_json(txt):
        try:
            return {"json": json.loads(txt)}
        except Exception as e:
            return {"json_error": str(e), "raw_head": txt[:200]}

    def parse_ebur(txt):
        out = {}
        for line in txt.splitlines():
            m = re.match(r"\s*(EBUR128 [A-Za-z ]+?|I|LRA|Threshold|Peak)\s*:\s*(-?[\d.]+)", line)
            if m:
                out[m.group(1).strip()] = float(m.group(2))
        return out

    legs.append(mk_stat_leg("stat_plain_a", lambda: [L.SOX, str(a), "-n", "stat"], parse_stat))
    legs.append(mk_stat_leg("stat_j_a", lambda: [L.SOX, str(a), "-n", "stat", "-j"], parse_json))
    legs.append(mk_stat_leg("stat_rms_a", lambda: [L.SOX, str(a), "-n", "stat", "-rms"], parse_stat))
    legs.append(mk_stat_leg("stat_v_a", lambda: [L.SOX, str(a), "-n", "stat", "-v"], parse_stat))
    legs.append(mk_stat_leg("stat_e_b", lambda: [L.SOX, str(b), "-n", "stat", "-e"], parse_ebur))
    legs.append(mk_stat_leg("stat_e_h_b", lambda: [L.SOX, str(b), "-n", "stat", "-e", "-h"], parse_ebur))
    legs.append(mk_stat_leg("stat_e_a", lambda: [L.SOX, str(a), "-n", "stat", "-e"], parse_ebur))
    legs.append(mk_stat_leg("stats_j_a", lambda: [L.SOX, str(a), "-n", "stats", "-j"], parse_json))
    legs.append(mk_stat_leg("stat_freq_b", lambda: [L.SOX, str(b), "-n", "stat", "-freq"], parse_stat))

    def ff_ebur():
        leg_dir = L.RUNS / "stat" / "ffmpeg_ebur128_b" / "rep0"
        meta = L.run_bounded([L.FFMPEG, "-hide_banner", "-nostdin", "-i", str(b),
                              "-filter_complex", "ebur128=peak=true", "-f", "null", "-"],
                             leg_dir, wall=20.0)
        txt = (leg_dir / "stderr").read_text(errors="replace")
        vals = {}
        for key, pat in (("I", r"I:\s*(-?[\d.]+) LUFS"), ("LRA", r"LRA:\s*(-?[\d.]+) LU"),
                         ("Peak", r"Peak:\s*(-?[\d.]+) dBFS")):
            m = re.search(pat, txt)
            if m:
                vals[key] = float(m.group(1))
        return {"name": "ffmpeg_ebur128_b", "argv": [L.FFMPEG, "-i", "stim_b.wav",
                "-filter_complex", "ebur128=peak=true", "-f", "null", "-"],
                "rc": meta["rc"], "metrics": vals, "text": txt[:2000]}
    legs.append(ff_ebur())
    receipt("stat", legs, t0)


# -------------------------------------------------------------------- chain --

def stage_chain(reps):
    t0 = time.time()
    a = L.SCRATCH / "r94s_stim_a.wav"
    legs = []
    legs.append(leg("chain", "gain_m6_then_norm_m3",
                    lambda o: sox(a, o, "gain", "-6", "norm", "-3"),
                    lambda p, m: basic_metrics(p), reps=reps))
    legs.append(leg("chain", "norm_m3_then_gain_m6",
                    lambda o: sox(a, o, "norm", "-3", "gain", "-6"),
                    lambda p, m: basic_metrics(p), reps=reps))
    legs.append(leg("chain", "norm_m3_only", lambda o: sox(a, o, "norm", "-3"),
                    lambda p, m: basic_metrics(p), reps=reps))
    legs.append(leg("chain", "norm_0_only", lambda o: sox(a, o, "norm"),
                    lambda p, m: basic_metrics(p), reps=reps))
    legs.append(leg("chain", "global_norm_flag", lambda o: sox("--norm", a, o),
                    lambda p, m: basic_metrics(p), reps=reps))
    legs.append(leg("chain", "gain_p6_G_norm", lambda o: sox("-G", a, o, "gain", "6", "norm", "-3"),
                    lambda p, m: basic_metrics(p), reps=reps))
    legs.append(leg("chain", "vol_amp_0.5", lambda o: sox(a, o, "vol", "0.5"),
                    lambda p, m: basic_metrics(p), reps=reps))
    legs.append(leg("chain", "vol_db_m6.0206", lambda o: sox(a, o, "vol", "-6.0206", "d"),
                    lambda p, m: basic_metrics(p), reps=reps))
    # equivalence of the two vol forms (sha compare inside one rep)
    v1 = L.SCRATCH / f"r94s_chain{SUFFIX}_vol_amp_0.5_r0.wav"
    v2 = L.SCRATCH / f"r94s_chain{SUFFIX}_vol_db_m6.0206_r0.wav"
    if v1.exists() and v2.exists():
        arr1, _ = L.read_wav(v1)
        arr2, _ = L.read_wav(v2)
        k = min(len(arr1), len(arr2))
        legs.append({"name": "vol_forms_equivalence",
                     "same_sha": L.sha256_file(v1) == L.sha256_file(v2),
                     "max_abs_diff": float(np.max(np.abs(arr1[:k] - arr2[:k]))) if k else None,
                     "frames": [len(arr1), len(arr2)]})
    receipt("chain", legs, t0)


STAGES = {
    "prep": stage_prep, "gain": stage_gain, "rate": stage_rate, "remix": stage_remix,
    "trim": stage_trim, "fade": stage_fade, "repeat_pad_silence": stage_repeat_pad_silence,
    "dither": stage_dither, "stat": stage_stat, "chain": stage_chain,
}


def main():
    stage = sys.argv[1]
    reps = int(sys.argv[2]) if len(sys.argv) > 2 else REPS
    if stage == "all":
        stage_prep(reps)
        for s in ("gain", "rate", "remix", "trim", "fade", "repeat_pad_silence",
                  "dither", "stat", "chain"):
            STAGES[s](reps)
        return
    STAGES[stage](reps)


if __name__ == "__main__":
    main()
