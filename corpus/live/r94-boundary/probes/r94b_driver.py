#!/usr/bin/env python3
"""r94b boundary driver — replay of the r94 scout armed cells under load.

Usage:  R94B_PASS=quiet|load python3 probes/r94b_driver.py <stage> [reps]
Stages: prep laws axes conc witness
Env:    R94B_PASS   pass label used in run dirs and output file names
        R94B_HOGS   number of own CPU hogs to hold for the whole stage

File-only: no PipeWire object is created, no device is opened, no
`pactl set-default-*`, no metadata write.  Every rep is a fresh `sox` process.
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
import r94b_lib as L  # noqa: E402

PASS = os.environ.get("R94B_PASS", "quiet")
HOGS = int(os.environ.get("R94B_HOGS", "0"))
REPS = 3
HOG_RECEIPT = {}

SCR = L.SCRATCH
D = lambda name: SCR / f"r94b_stim_{name}.wav"  # noqa: E731

REF = {}


def ref(name):
    if name not in REF:
        REF[name] = L.i16(D(name))[0]
    return REF[name]


def sox(*parts, gopts=()):
    return [L.SOX, *[str(g) for g in gopts], *[str(p) for p in parts]]


# ------------------------------------------------------------------ cells ---

CELLS = []


def cell(family, name, argv_fn, analysis=None, reps=None, wall=10.0,
         out_cap=64 << 20, extra_env=None, stdout_metrics=False, tags=(),
         no_output=False):
    CELLS.append({"family": family, "name": name, "argv_fn": argv_fn,
                  "analysis": analysis, "reps": reps or REPS, "wall": wall,
                  "out_cap": out_cap, "extra_env": extra_env,
                  "stdout_metrics": stdout_metrics, "tags": list(tags),
                  "no_output": no_output})


def run_cells(reps_override=None):
    cells_here = list(CELLS)
    CELLS.clear()  # each stage runs only the cells it declared
    out_cells = []
    for c in cells_here:
        reps = reps_override or c["reps"]
        rows = []
        for rep in range(reps):
            out = SCR / f"r94b_{PASS}_{c['family']}_{c['name']}_r{rep}.wav"
            if out.exists():
                out.unlink()
            argv = c["argv_fn"](rep, out)
            leg_dir = L.RUNS / PASS / c["family"] / c["name"] / f"rep{rep}"
            meta = L.run_bounded(argv, leg_dir, wall=c["wall"], out_path=out,
                                 out_cap=c["out_cap"], extra_env=c["extra_env"],
                                 want_stdout=c["stdout_metrics"])
            m = {}
            if c["analysis"] is not None and (c["no_output"] or out.exists()):
                try:
                    m = c["analysis"](out, meta, leg_dir)
                except Exception as e:  # noqa: BLE001
                    m = {"analysis_error": f"{type(e).__name__}: {e}"}
            rows.append({"rep": rep, "argv": argv, "rc": meta["rc"],
                         "wall_s": meta["wall_s"], "killed": meta["killed"],
                         "out_bytes": meta["out_bytes"], "out_sha256": meta["out_sha256"],
                         "stdout_sha256": meta.get("stdout_sha256"),
                         "loadavg1_before": meta["loadavg1_before"],
                         "loadavg1_after": meta["loadavg1_after"],
                         "stderr_head": meta["stderr_head"], "metrics": m})
        shas = [r["out_sha256"] for r in rows if r["out_sha256"]]
        stream = [r["metrics"].get("_text_sha256") for r in rows
                  if r["metrics"].get("_text_sha256")]
        out_cells.append({
            "family": c["family"], "name": c["name"], "tags": c["tags"],
            "argv": rows[0]["argv"] if rows else None, "reps_n": reps,
            "reps": rows, "stable": len(set(shas)) == 1 and len(shas) == reps,
            "n_distinct_shas": len(set(shas)), "n_outputs": len(shas),
            "n_distinct_stream_shas": len(set(stream)) if stream else None,
            "metrics": rows[0]["metrics"] if rows else {},
            "rcs": [r["rc"] for r in rows],
        })
    return out_cells


def receipt(stage, cells, t0, hogs=None, notes=None, extra=None):
    payload = {"pass": PASS, "hogs": HOGS, "reps_default": REPS,
               "host": L.host_context(),
               "witness_start": L.default_node_witness(),
               "settings_start": L.settings_witness(),
               "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t0)),
               "notes": notes or [], "cells": cells}
    if hogs is not None:
        payload["hog_set"] = hogs
    if HOG_RECEIPT:
        payload["hog_set"] = HOG_RECEIPT
    if extra:
        payload.update(extra)
    p = L.write_receipt(f"{stage}-{PASS}", payload)
    n_reps = sum(c.get("reps_n", len(c.get("rows", []))) for c in cells)
    print(f"[{stage}-{PASS}] {len(cells)} cells, {n_reps} reps -> {p}", flush=True)
    return p


# ------------------------------------------------------------- analysis fns --

def a_basic(path, meta, leg_dir):
    return L.basic_metrics(path)


def a_vs_rint(name, factor):
    r = ref(name)

    def f(path, meta, leg_dir):
        got, _ = L.i16(path)
        out = L.basic_metrics(path)
        exp = np.rint(r.astype(np.float64) * factor).astype(np.int64)
        k = min(len(exp), len(got))
        d = np.abs(exp[:k] - got[:k])
        out["mismatch_vs_rint"] = int(np.count_nonzero(d))
        out["max_abs_diff_vs_rint"] = int(d.max()) if k else None
        out["first8_ch0"] = got[:8, 0].tolist()
        return out
    return f


def a_rounding_candidates(name, factor):
    r = ref(name)

    def f(path, meta, leg_dir):
        got, _ = L.i16(path)
        out = L.basic_metrics(path)
        x = r.astype(np.float64) * factor
        for nm, cand in (("floor", np.floor(x)), ("trunc", np.trunc(x)),
                         ("rint", np.rint(x)), ("ceil", np.ceil(x))):
            v = cand.astype(np.int64)
            k = min(len(v), len(got))
            d = np.abs(v[:k] - got[:k])
            out[f"mismatch_{nm}"] = int(np.count_nonzero(d))
            out[f"maxdiff_{nm}"] = int(d.max()) if k else None
        return out
    return f


def a_rate_bands(path, meta, leg_dir):
    arr, m = L.read_wav(path)
    out = L.basic_metrics(path)
    for f0 in (997.0, 20000.0, 21100.0, 23000.0):
        out[f"band_{int(f0)}hz_db"] = round(L.band_level_db(arr, m["rate"], f0), 3)
    return out


def a_seam(name):
    r = ref(name)

    def f(path, meta, leg_dir):
        got, _ = L.i16(path)
        out = L.basic_metrics(path)
        n = len(got)
        tiled = r[np.arange(n) % len(r), 0]
        d = np.abs(tiled - got[:, 0])
        out["mismatch_vs_tiling"] = int(np.count_nonzero(d))
        out["maxdiff_vs_tiling"] = int(d.max()) if n else None
        return out
    return f


def a_downmix(name="a"):
    r = ref(name)

    def f(path, meta, leg_dir):
        got, _ = L.i16(path)
        Lc, Rc = r[:, 0], r[:, 1]
        cands = {"L_plus_R": Lc + Rc,
                 "half_L_plus_R": np.rint((Lc + Rc) / 2.0),
                 "half_up_floor": np.floor((Lc + Rc + 1) / 2.0),
                 "mean_int": (Lc + Rc) // 2,
                 "sqrt2_half": np.rint((Lc + Rc) / 2.0 ** 0.5),
                 "L_only": Lc}
        out = L.basic_metrics(path)
        for k, v in cands.items():
            d = np.abs(np.clip(v, -32768, 32767) - got[:len(v), 0])
            out[f"mismatch_{k}"] = int(np.count_nonzero(d))
            out[f"maxdiff_{k}"] = int(d.max()) if len(d) else None
        return out
    return f


def a_env(name, positions):
    r = ref(name)

    def f(path, meta, leg_dir):
        got, _ = L.i16(path)
        out = L.basic_metrics(path)
        env = {}
        for p in positions:
            if 0 <= p < len(got):
                src = float(r[p, 0])
                env[f"frame{p}"] = {"out": int(got[p, 0]), "in": int(r[p, 0]),
                                    "gain": (round(float(got[p, 0]) / src, 8) if src != 0 else None)}
        out["envelope"] = env
        out["first_frame"] = int(got[0, 0])
        return out
    return f


def a_silence(path, meta, leg_dir):
    got, _ = L.i16(path)
    out = L.basic_metrics(path)
    nz = np.nonzero(got[:, 0])[0]
    out["first_nonzero_frame"] = int(nz[0]) if len(nz) else None
    out["last_nonzero_frame"] = int(nz[-1]) if len(nz) else None
    out["trailing_zero_frames"] = int(len(got) - 1 - nz[-1]) if len(nz) else len(got)
    out["first8_ints"] = got[:8, 0].tolist()
    out["last8_ints"] = got[-8:, 0].tolist()
    return out


def a_pad(path, meta, leg_dir):
    got, _ = L.i16(path)
    out = L.basic_metrics(path)
    nz = np.nonzero(got[:, 0])[0]
    out["first_nonzero_frame"] = int(nz[0]) if len(nz) else None
    out["last_nonzero_frame"] = int(nz[-1]) if len(nz) else None
    out["zero_frames_total"] = int(np.count_nonzero(got[:, 0] == 0))
    return out


def a_conv(name="f"):
    src, _ = L.read_wav(D(name))

    def f(path, meta, leg_dir):
        arr, _ = L.read_wav(path)
        out = L.basic_metrics(path)
        got = np.rint(arr * 32768.0).astype(np.int64)
        exact = np.rint(src * 32768.0).astype(np.int64)
        k = min(len(got), len(exact))
        d = got[:k, 0] - exact[:k, 0]
        out["mismatch_vs_round"] = int(np.count_nonzero(d))
        out["max_abs_err"] = int(np.abs(d).max()) if k else None
        out["err_rms"] = float(np.sqrt(np.mean(d.astype(np.float64) ** 2))) if k else None
        return out
    return f


def a_clip(path, meta, leg_dir):
    got, _ = L.i16(path)
    return {"clipped_ge32767": int(np.count_nonzero(np.abs(got) >= 32767)),
            "clipped_ge32766": int(np.count_nonzero(np.abs(got) >= 32766)),
            "peak_db": [round(L.peak_db(L.read_wav(path)[0][:, c]), 4)
                        for c in range(got.shape[1])],
            "first8_ch0": got[:8, 0].tolist()}


def a_identity(name):
    def f(path, meta, leg_dir):
        return {"byte_identical_to_stim": L.sha256_file(path) == L.sha256_file(D(name)),
                "out_sha256": L.sha256_file(path), "stim_sha256": L.sha256_file(D(name))}
    return f


def a_pair(argv_b, name_b="vol_db"):
    """Run a second argv in the same rep and compare the two outputs."""
    def f(path, meta, leg_dir):
        out_b = Path(str(path).replace(".wav", "_b.wav"))
        if out_b.exists():
            out_b.unlink()
        meta_b = L.run_bounded(argv_b(out_b), Path(leg_dir) / "pair_b",
                               wall=10.0, out_path=out_b)
        a1, _ = L.read_wav(path)
        a2, _ = L.read_wav(out_b)
        k = min(len(a1), len(a2))
        return {"same_sha": L.sha256_file(path) == L.sha256_file(out_b),
                "max_abs_diff": float(np.max(np.abs(a1[:k] - a2[:k]))) if k else None,
                "frames": [len(a1), len(a2)], "sha_a": L.sha256_file(path),
                "sha_b": L.sha256_file(out_b), "rc_b": meta_b["rc"]}
    return f


def a_stat(stream="stderr", kind="kv"):
    def f(path, meta, leg_dir):
        p = Path(leg_dir) / stream
        txt = p.read_text(errors="replace") if p.exists() else ""
        if not txt.strip():  # fall back to the other stream
            other = "stdout" if stream == "stderr" else "stderr"
            q = Path(leg_dir) / other
            if q.exists():
                txt = q.read_text(errors="replace")
        out = {"_text_sha256": L.sha256_bytes(txt.encode()), "text_head": txt[:600],
               "stream_used": stream}
        if kind == "kv":
            for line in txt.splitlines():
                if ":" in line:
                    k, _, v = line.partition(":")
                    out[" ".join(k.split())] = v.strip()
        elif kind == "json":
            try:
                out["json"] = json.loads(txt)
            except Exception as e:  # noqa: BLE001
                out["json_error"] = str(e)
        elif kind == "ebur":
            for line in txt.splitlines():
                m = re.match(r"\s*(EBUR128 [A-Za-z ]+?|I|LRA|Threshold|Peak)\s*:\s*(-?[\d.]+)", line)
                if m:
                    out[m.group(1).strip()] = float(m.group(2))
        return out
    return f


# ------------------------------------------------------------------- prep ---

def stage_prep(reps):
    t0 = time.time()
    stim = L.build_stimuli()
    scout_prep = json.loads((L.SCOUT / "receipts" / "prep.json").read_text())
    scout_stim = scout_prep["notes"][0]["stimuli"]
    mapping = {k: k.replace("r94s_stim_", "r94b_stim_") for k in scout_stim}
    cmp_rows = []
    for sname, ssha in sorted(scout_stim.items()):
        mine = stim[mapping[sname]]
        cmp_rows.append({"scout": sname, "mine": mapping[sname], "scout_sha256": ssha,
                         "mine_sha256": mine, "match": ssha == mine})
    # smoke: does a canonical -D leg reproduce the scout's exact output bytes?
    smoke = []
    a = D("a")
    b = D("b")
    scout_dither = json.loads((L.SCOUT / "receipts" / "dither_D.json").read_text())
    scout_gainD = json.loads((L.SCOUT / "receipts" / "gain_D.json").read_text())
    scout_rateD = json.loads((L.SCOUT / "receipts" / "rate_D.json").read_text())

    def sleg(argv, out, name, srcreceipt):
        if out.exists():
            out.unlink()
        meta = L.run_bounded(argv, L.RUNS / PASS / "prep" / name / "rep0",
                             wall=10.0, out_path=out)
        scout_leg = next((l for l in srcreceipt["legs"] if l["name"] == name), None)
        scout_sha = scout_leg["reps"][0]["out_sha256"] if scout_leg else None
        return {"name": name, "argv": argv, "out_sha256": meta["out_sha256"],
                "scout_out_sha256": scout_sha, "match": meta["out_sha256"] == scout_sha,
                "out_bytes": meta["out_bytes"]}

    smoke.append(sleg(sox(a, SCR / f"r94b_{PASS}_prep_gain_m6.wav", "gain", "-6", gopts=["-D"]),
                      SCR / f"r94b_{PASS}_prep_gain_m6.wav", "gain_m6", scout_gainD))
    smoke.append(sleg(sox(b, SCR / f"r94b_{PASS}_prep_rate44100.wav", "rate", "44100", gopts=["-D"]),
                      SCR / f"r94b_{PASS}_prep_rate44100.wav", "rate44100_default", scout_rateD))
    smoke.append(sleg(sox(a, SCR / f"r94b_{PASS}_prep_copy.wav", gopts=["-D"]),
                      SCR / f"r94b_{PASS}_prep_copy.wav", "copy_plain", scout_dither))
    cells = [{"name": "stimulus_sha_crosscheck", "rows": cmp_rows,
              "all_match": all(r["match"] for r in cmp_rows)},
             {"name": "scout_output_sha_smoke", "rows": smoke,
              "all_match": all(r["match"] for r in smoke)}]
    receipt("prep", cells, t0, notes=[{"stimuli": stim}])
    return cells


# ------------------------------------------------------------------- laws ---

def stage_laws(reps):
    t0 = time.time()
    a, b, c, c2 = D("a"), D("b"), D("c"), D("c2")
    f, h, i, j = D("f"), D("h"), D("i"), D("j")
    P = ["-D"]

    # --- D: determinism matrix
    cell("D", "gain_m6_default", lambda r, o: sox(a, o, "gain", "-6"),
         a_vs_rint("a", 10 ** (-6 / 20)), reps=5)
    cell("D", "gain_m6_D", lambda r, o: sox(a, o, "gain", "-6", gopts=P),
         a_vs_rint("a", 10 ** (-6 / 20)), reps=3)
    cell("D", "dither_explicit_default", lambda r, o: sox(f, "-b", "16", o, "dither"),
         a_conv(), reps=5)
    cell("D", "dither_explicit_R", lambda r, o: sox(f, "-b", "16", o, "dither", gopts=["-R"]),
         a_conv(), reps=5)
    cell("D", "dither_explicit_D", lambda r, o: sox(f, "-b", "16", o, "dither", gopts=P),
         a_conv(), reps=5)
    cell("D", "dither_s_R", lambda r, o: sox(f, "-b", "16", o, "dither", "-s", gopts=["-R"]),
         a_conv(), reps=3)
    cell("D", "dither_p12_R", lambda r, o: sox(f, "-b", "16", o, "dither", "-p", "12", gopts=["-R"]),
         a_conv(), reps=3)
    cell("D", "f32_to_s16_plain", lambda r, o: sox(f, "-b", "16", o), a_conv(), reps=5)
    cell("D", "f32_to_s24_plain", lambda r, o: sox(f, "-b", "24", o), a_basic, reps=3)
    cell("D", "f32_to_s32_plain", lambda r, o: sox(f, "-b", "32", o), a_basic, reps=3)
    cell("D", "copy_plain", lambda r, o: sox(a, o), a_identity("a"), reps=3)
    cell("D", "rate_same_identity", lambda r, o: sox(b, o, "rate", "48000"), a_identity("b"), reps=3)
    cell("D", "gain_0_identity", lambda r, o: sox(a, o, "gain", "0"), a_identity("a"), reps=3)
    cell("D", "s16_to_s24_gain", lambda r, o: sox(a, "-b", "24", o, "gain", "-6"), a_basic, reps=3)
    cell("D", "gain_m6_R", lambda r, o: sox(a, o, "gain", "-6", gopts=["-R"]),
         a_vs_rint("a", 10 ** (-6 / 20)), reps=3)

    # --- G: gain / vol / norm
    cell("G", "vol_amp_0.5_D", lambda r, o: sox(a, o, "vol", "0.5", gopts=P),
         a_rounding_candidates("a", 0.5), reps=3)
    cell("G", "vol_db_m6.0206_D", lambda r, o: sox(a, o, "vol", "-6.0206", "d", gopts=P),
         a_rounding_candidates("a", 10 ** (-6.0206 / 20)), reps=3)
    cell("G", "vol_pow_0.5_D", lambda r, o: sox(a, o, "vol", "0.5", "p", gopts=P),
         a_rounding_candidates("a", 0.5 ** 0.5), reps=3)
    cell("G", "vol_spelling_delta", lambda r, o: sox(a, o, "vol", "0.5", gopts=P),
         a_pair(lambda o2: sox(a, o2, "vol", "-6.0206", "d", gopts=P)), reps=3)
    cell("G", "gain_n_D", lambda r, o: sox(a, o, "gain", "-n", gopts=P), a_basic, reps=3)
    cell("G", "gain_e_D", lambda r, o: sox(a, o, "gain", "-e", gopts=P), a_basic, reps=3)
    cell("G", "gain_b_D", lambda r, o: sox(a, o, "gain", "-b", gopts=P), a_basic, reps=3)
    cell("G", "gain_h_m6_D", lambda r, o: sox(a, o, "gain", "-h", "-6", gopts=P), a_basic, reps=3)
    cell("G", "gain_h_m6_reclaim_D", lambda r, o: sox(a, o, "gain", "-h", "-6", "gain", "-r", gopts=P),
         a_basic, reps=3)

    # --- R: rate length / alias / pitch
    rates = [("44100", "b"), ("22050", "b"), ("22054", "b"), ("24050", "b"),
             ("11025", "b"), ("44101", "b"), ("96000", "b"), ("32000", "b"),
             ("8000", "b"), ("48000", "b"),
             ("44100", "i"), ("22050", "i"), ("96000", "i"), ("32000", "i"), ("22054", "i")]
    for rate, sn in rates:
        cell("R", f"rate{rate}_{sn}", (lambda rr, ss: lambda r, o: sox(D(ss), o, "rate", rr, gopts=P))(rate, sn),
             a_rate_bands, reps=3, tags=["length"])
    for nm, fl in (("default", []), ("q", ["-q"]), ("m", ["-m"]), ("v", ["-v"]),
                   ("a", ["-a"]), ("q_a", ["-q", "-a"]), ("m_a", ["-m", "-a"])):
        cell("R", f"rate44100_23k_{nm}",
             (lambda ff: lambda r, o: sox(j, o, "rate", *ff, "44100", gopts=P))(fl),
             a_rate_bands, reps=3, tags=["alias"])
    for nm, fl in (("default", []), ("q", ["-q"]), ("v", ["-v"])):
        cell("R", f"rate44100_20k_{nm}",
             (lambda ff: lambda r, o: sox(h, o, "rate", *ff, "44100", gopts=P))(fl),
             a_rate_bands, reps=3, tags=["alias"])
    cell("R", "rate44100_default_nodither_off",
         lambda r, o: sox(b, o, "rate", "44100"), a_rate_bands, reps=3, tags=["nondet"])

    # --- M: remix / channels
    for nm, fx in (("remix_1", ["remix", "1"]), ("remix_1_2", ["remix", "1,2"]),
                   ("remix_m_1_2", ["remix", "-m", "1,2"]), ("remix_a_1_2", ["remix", "-a", "1,2"]),
                   ("remix_p_1_2", ["remix", "-p", "1,2"]), ("channels_1", ["channels", "1"])):
        cell("M", nm, (lambda f2: lambda r, o: sox(a, o, *f2, gopts=P))(fx), a_downmix(), reps=3)
    for nm, fx in (("remix_swap_2_1", ["remix", "2", "1"]), ("remix_left_only", ["remix", "1", "0"]),
                   ("remix_right_only", ["remix", "0", "1"]), ("remix_v_half", ["remix", "1v0.5", "2v0.5"]),
                   ("remix_p_minus6", ["remix", "1p-6"])):
        cell("M", nm, (lambda f2: lambda r, o: sox(a, o, *f2, gopts=P))(fx), a_basic, reps=3)
    cell("M", "mono_to_stereo_1_1", lambda r, o: sox(b, o, "remix", "1", "1", gopts=P), a_basic, reps=3)

    # --- T: trim
    trims = [("trim_0_0.1", ["trim", "0", "0.1"]), ("trim_0.1", ["trim", "0.1"]),
             ("trim_0.1_0.1", ["trim", "0.1", "0.1"]), ("trim_0_0.10001", ["trim", "0", "0.10001"]),
             ("trim_0_0.09999", ["trim", "0", "0.09999"]), ("trim_0_0.09995", ["trim", "0", "0.09995"]),
             ("trim_0_0.09997917", ["trim", "0", "0.09997917"]),
             ("trim_0_0.09998958", ["trim", "0", "0.09998958"]),
             ("trim_0_0.1000104", ["trim", "0", "0.1000104"]),
             ("trim_0_0.1000208", ["trim", "0", "0.1000208"]),
             ("trim_0_0.10003125", ["trim", "0", "0.10003125"]),
             ("trim_0_minus0.1", ["trim", "0", "-0.1"]), ("trim_0_eq0.1", ["trim", "0", "=0.1"]),
             ("trim_0_100", ["trim", "0", "100"]), ("trim_0.2_0.2", ["trim", "0.2", "0.2"]),
             ("trim_0_0", ["trim", "0", "0"]), ("trim_0_1e-9", ["trim", "0", "1e-9"]),
             ("trim_0_1s", ["trim", "0", "1s"]), ("trim_0_4800s", ["trim", "0", "4800s"]),
             ("trim_0_0.1s", ["trim", "0", "0.1s"]), ("trim_0_1sec", ["trim", "0", "1sec"]),
             ("trim_plus_0.05plus0.05", ["trim", "0.05+0.05"])]
    for nm, fx in trims:
        cell("T", nm, (lambda f2: lambda r, o: sox(b, o, *f2, gopts=P))(fx), a_basic, reps=3)

    # --- F: fade
    pos_in = [0, 480, 960, 1200, 1920, 2400, 2880, 3600, 3840, 4320, 4799, 4800, 6000, 11999]
    pos_out = [0, 7200, 8400, 9600, 10200, 10800, 11400, 11999]
    cell("F", "fade_in_0.1", lambda r, o: sox(b, o, "fade", "0.1", gopts=P), a_env("b", pos_in), reps=3)
    cell("F", "fade_out_stop0.25_len0.1", lambda r, o: sox(b, o, "fade", "0", "0.25", "0.1", gopts=P),
         a_env("b", pos_out), reps=3, tags=["truncation"])
    cell("F", "fade_out_stop0.15_len0.1", lambda r, o: sox(b, o, "fade", "0", "0.15", "0.1", gopts=P),
         a_env("b", pos_out), reps=3, tags=["truncation"])
    cell("F", "fade_out_stop0.2_len0.05", lambda r, o: sox(b, o, "fade", "0", "0.2", "0.05", gopts=P),
         a_env("b", pos_out), reps=3, tags=["truncation"])
    for ty in ("q", "h", "t", "l", "p", "s"):
        cell("F", f"fade_in_{ty}_0.1", (lambda t: lambda r, o: sox(b, o, "fade", t, "0.1", gopts=P))(ty),
             a_env("b", pos_in), reps=3, tags=["curve"])

    # --- P: repeat / pad / silence
    cell("P", "repeat_2", lambda r, o: sox(b, o, "repeat", "2", gopts=P), a_seam("b"), reps=3)
    cell("P", "repeat_1", lambda r, o: sox(b, o, "repeat", "1", gopts=P), a_seam("b"), reps=3)
    cell("P", "repeat_0", lambda r, o: sox(b, o, "repeat", "0", gopts=P), a_seam("b"), reps=3)
    cell("P", "repeat_neg1", lambda r, o: sox(b, o, "repeat", "-1", gopts=P), a_basic, reps=3)
    cell("P", "pad_0.1_0.2", lambda r, o: sox(b, o, "pad", "0.1", "0.2", gopts=P), a_pad, reps=3)
    cell("P", "pad_0.05_at_0.05", lambda r, o: sox(b, o, "pad", "0.05@0.05", gopts=P), a_pad, reps=3)
    cell("P", "pad_pct50", lambda r, o: sox(b, o, "pad", "%50", gopts=P), a_pad, reps=3)
    cell("P", "silence_c2_above", lambda r, o: sox(c2, o, "silence", "1", "0.1", "1%", gopts=P),
         a_silence, reps=3, tags=["window"])
    cell("P", "silence_c2_both", lambda r, o: sox(c2, o, "silence", "1", "0.1", "1%", "1", "0.1", "1%", gopts=P),
         a_silence, reps=3, tags=["window"])
    cell("P", "silence_c2_both_leave",
         lambda r, o: sox(c2, o, "silence", "-l", "1", "0.1", "1%", "1", "0.1", "1%", gopts=P),
         a_silence, reps=3, tags=["window"])
    cell("P", "silence_c2_both_0.05",
         lambda r, o: sox(c2, o, "silence", "1", "0.1", "1%", "1", "0.05", "1%", gopts=P),
         a_silence, reps=3, tags=["window"])
    cell("P", "silence_0_0.1_1pct", lambda r, o: sox(c, o, "silence", "0", "0.1", "1%", gopts=P),
         a_silence, reps=3, tags=["refusal"])
    cell("P", "silence_neg60d", lambda r, o: sox(c2, o, "silence", "1", "0.05", "-60d", gopts=P),
         a_silence, reps=3, tags=["units"])
    cell("P", "silence_frac", lambda r, o: sox(c2, o, "silence", "1", "0.05", "0.01", gopts=P),
         a_silence, reps=3, tags=["units"])

    # --- S: stat
    for nm, argv, an in (
        ("stat_plain_a", lambda r, o: [L.SOX, str(a), "-n", "stat"], a_stat("stderr", "kv")),
        ("stat_j_a", lambda r, o: [L.SOX, str(a), "-n", "stat", "-j"], a_stat("stdout", "json")),
        ("stat_v_a", lambda r, o: [L.SOX, str(a), "-n", "stat", "-v"], a_stat("stderr", "kv")),
        ("stat_rms_a", lambda r, o: [L.SOX, str(a), "-n", "stat", "-rms"], a_stat("stderr", "kv")),
        ("stat_e_b", lambda r, o: [L.SOX, str(b), "-n", "stat", "-e"], a_stat("stderr", "ebur")),
        ("stat_e_a", lambda r, o: [L.SOX, str(a), "-n", "stat", "-e"], a_stat("stderr", "ebur")),
        ("stats_j_a", lambda r, o: [L.SOX, str(a), "-n", "stats", "-j"], a_stat("stdout", "json")),
    ):
        cell("S", nm, argv, an, reps=3, no_output=True)
    cell("S", "ffmpeg_ebur128_b",
         lambda r, o: [L.FFMPEG, "-hide_banner", "-nostdin", "-i", str(b), "-filter_complex",
                       "ebur128=peak=true", "-f", "null", "-"],
         lambda p, m, ld: {"I_LUFS": (re.search(r"I:\s*(-?[\d.]+) LUFS",
                                                (Path(ld) / "stderr").read_text(errors="replace")) or
                                      [None, None])[1],
                           "text_tail": (Path(ld) / "stderr").read_text(errors="replace")[-400:]},
         reps=3, wall=20.0, tags=["cross-witness"], no_output=True)

    # --- C: chain order
    cell("C", "gain_m6_then_norm_m3", lambda r, o: sox(a, o, "gain", "-6", "norm", "-3", gopts=P),
         a_basic, reps=3)
    cell("C", "norm_m3_then_gain_m6", lambda r, o: sox(a, o, "norm", "-3", "gain", "-6", gopts=P),
         a_basic, reps=3)
    cell("C", "norm_0_only", lambda r, o: sox(a, o, "norm", gopts=P), a_basic, reps=3)
    cell("C", "global_norm_flag", lambda r, o: sox(a, o, gopts=["--norm", "-D"]), a_basic, reps=3)
    cell("C", "gain_p6_G_norm", lambda r, o: sox(a, o, "gain", "6", "norm", "-3", gopts=["-G", "-D"]),
         a_basic, reps=3)

    # --- X: guard
    cell("X", "gain_p12_D", lambda r, o: sox(b, o, "gain", "12", gopts=P), a_clip, reps=3)
    cell("X", "gain_p12_G_D", lambda r, o: sox(b, o, "gain", "12", gopts=["-G", "-D"]), a_clip, reps=3)
    cell("X", "gain_p12_default", lambda r, o: sox(b, o, "gain", "12"), a_clip, reps=3)
    cell("X", "gain_p12_G_default", lambda r, o: sox(b, o, "gain", "12", gopts=["-G"]), a_clip, reps=3)

    cells = run_cells(reps_override=reps)
    receipt("laws", cells, t0)


# ------------------------------------------------------------------- axes ---

def stage_axes(reps):
    t0 = time.time()
    a, b, f = D("a"), D("b"), D("f")
    cells_before = []

    def variant(name, argv_fn, analysis=None, reps_n=None, extra_env=None, tags=()):
        cell("AX", name, argv_fn, analysis or a_basic, reps=reps_n or reps,
             extra_env=extra_env, tags=list(tags))

    # --- flag order / placement (canonical baseline cells are in the laws pass)
    variant("canonical_D", lambda r, o: sox(a, o, "gain", "-6", gopts=["-D"]),
            a_vs_rint("a", 10 ** (-6 / 20)), tags=["baseline"])
    variant("D_between_in_out", lambda r, o: [L.SOX, str(a), "-D", str(o), "gain", "-6"],
            a_vs_rint("a", 10 ** (-6 / 20)), tags=["order"])
    variant("D_after_out_before_effect", lambda r, o: [L.SOX, str(a), str(o), "-D", "gain", "-6"],
            a_vs_rint("a", 10 ** (-6 / 20)), tags=["order"])
    variant("D_after_effect_args", lambda r, o: [L.SOX, str(a), str(o), "gain", "-6", "-D"],
            a_vs_rint("a", 10 ** (-6 / 20)), tags=["order", "probe"])
    variant("no_dither_longform", lambda r, o: sox(a, o, "gain", "-6", gopts=["--no-dither"]),
            a_vs_rint("a", 10 ** (-6 / 20)), tags=["order"])
    variant("D_R_order", lambda r, o: sox(a, o, "gain", "-6", gopts=["-D", "-R"]),
            a_vs_rint("a", 10 ** (-6 / 20)), tags=["order"])
    variant("R_D_order", lambda r, o: sox(a, o, "gain", "-6", gopts=["-R", "-D"]),
            a_vs_rint("a", 10 ** (-6 / 20)), tags=["order"])
    variant("dither_R_canonical", lambda r, o: sox(f, "-b", "16", o, "dither", gopts=["-R"]),
            a_conv(), reps_n=5, tags=["baseline"])
    variant("dither_R_after_infile", lambda r, o: [L.SOX, str(f), "-R", "-b", "16", str(o), "dither"],
            a_conv(), reps_n=5, tags=["order"])
    variant("dither_R_D_combo", lambda r, o: sox(f, "-b", "16", o, "dither", gopts=["-R", "-D"]),
            a_conv(), reps_n=5, tags=["order"])
    variant("dither_R_after_effect", lambda r, o: [L.SOX, str(f), "-b", "16", str(o), "dither", "-R"],
            a_conv(), reps_n=5, tags=["order", "probe"])

    # --- PipeWire client-config env axis (per-process only; no global write)
    base_env = {}
    for nm, env in (
        ("pw_quantum_64", {"PIPEWIRE_QUANTUM": "64"}),
        ("pw_quantum_2048", {"PIPEWIRE_QUANTUM": "2048"}),
        ("pw_quantum_8192", {"PIPEWIRE_QUANTUM": "8192"}),
        ("pw_rate_44100", {"PIPEWIRE_RATE": "44100"}),
        ("pw_rate_96000", {"PIPEWIRE_RATE": "96000"}),
        ("pw_latency", {"PIPEWIRE_LATENCY": "64/48000"}),
        ("pw_node_other_sink", {"PIPEWIRE_NODE": "alsa_output.usb-Generic_USB_Audio-00.HiFi__Speaker__sink"}),
        ("pulse_sink_other", {"PULSE_SINK": "alsa_output.usb-Generic_USB_Audio-00.HiFi__Speaker__sink"}),
        ("pulse_source_mic", {"PULSE_SOURCE": "alsa_input.usb-Generic_USB_Audio-00.HiFi__Mic__source"}),
        ("all_pw_env", {"PIPEWIRE_QUANTUM": "32", "PIPEWIRE_RATE": "44100",
                        "PIPEWIRE_LATENCY": "32/44100",
                        "PULSE_SINK": "alsa_output.usb-Generic_USB_Audio-00.HiFi__Headphones__sink"}),
    ):
        variant(f"gain_D_{nm}", lambda r, o: sox(a, o, "gain", "-6", gopts=["-D"]),
                a_vs_rint("a", 10 ** (-6 / 20)), extra_env=env, tags=["pw-env"])
        variant(f"rate_D_{nm}", lambda r, o: sox(b, o, "rate", "44100", gopts=["-D"]),
                a_rate_bands, extra_env=env, tags=["pw-env"])
    variant("gain_D_env_control", lambda r, o: sox(a, o, "gain", "-6", gopts=["-D"]),
            a_vs_rint("a", 10 ** (-6 / 20)), extra_env=base_env, tags=["pw-env"])

    # --- sox internal buffer axis (the sox analogue of a quantum knob)
    for nm, gopts in (("buffer_4096", ["-D", "--buffer", "4096"]),
                      ("buffer_16384", ["-D", "--buffer", "16384"]),
                      ("buffer_1024", ["-D", "--buffer", "1024"]),
                      ("input_buffer_4096", ["-D", "--input-buffer", "4096"])):
        variant(f"gain_{nm}", lambda r, o, g=gopts: sox(a, o, "gain", "-6", gopts=g),
                a_vs_rint("a", 10 ** (-6 / 20)), tags=["buffer"])
        variant(f"rate_{nm}", lambda r, o, g=gopts: sox(b, o, "rate", "44100", gopts=g),
                a_rate_bands, tags=["buffer"])
        variant(f"silence_{nm}", lambda r, o, g=gopts: sox(D("c2"), o, "silence", "1", "0.1", "1%",
                                                            "1", "0.1", "1%", gopts=g),
                a_silence, tags=["buffer"])

    cells = run_cells(reps_override=reps)
    receipt("axes", cells, t0,
            notes=[{"pw_env_note": "per-process env only; no global metadata/config write",
                    "default_node_note": "default-node witness recorded per pass; global toggle "
                                         "not performed (active sibling sink-inputs present)"}])
    return cells_before


# ------------------------------------------------------------------- conc ---

CONC = []


def conc_cell(name, argv_fn, reps=16, wall=30.0):
    CONC.append({"name": name, "argv_fn": argv_fn, "reps": reps, "wall": wall})


def stage_conc(reps):
    t0 = time.time()
    a, b, f = D("a"), D("b"), D("f")
    conc_cell("conc16_gain_D", lambda r, o: sox(a, o, "gain", "-6", gopts=["-D"]))
    conc_cell("conc16_gain_default", lambda r, o: sox(a, o, "gain", "-6"))
    conc_cell("conc16_dither_R", lambda r, o: sox(f, "-b", "16", o, "dither", gopts=["-R"]))
    conc_cell("conc16_dither_default", lambda r, o: sox(f, "-b", "16", o, "dither"))
    conc_cell("conc16_rate_D", lambda r, o: sox(b, o, "rate", "44100", gopts=["-D"]))

    import subprocess
    import signal as _sig
    import resource as _res

    conc_here = list(CONC)
    CONC.clear()
    cells = []
    for c in conc_here:
        procs = []
        outs = []
        la0 = L.loadavg1()
        for rep in range(c["reps"]):
            out = SCR / f"r94b_{PASS}_conc_{c['name']}_r{rep}.wav"
            if out.exists():
                out.unlink()
            argv = c["argv_fn"](rep, out)
            leg_dir = L.RUNS / PASS / "conc" / c["name"] / f"rep{rep}"
            leg_dir.mkdir(parents=True, exist_ok=True)
            (leg_dir / "cmd").write_text(json.dumps(argv))
            env = dict(os.environ)
            env["LC_ALL"] = "C"

            def _preexec():
                _res.setrlimit(_res.RLIMIT_CORE, (0, 0))
            of = open(leg_dir / "stdout", "wb")
            ef = open(leg_dir / "stderr", "wb")
            p = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=of, stderr=ef,
                                 start_new_session=True, env=env, preexec_fn=_preexec)
            procs.append((p, of, ef, out, leg_dir, argv))
        la1 = L.loadavg1()
        deadline = time.time() + c["wall"]
        rows = []
        for p, of, ef, out, leg_dir, argv in procs:
            try:
                p.wait(timeout=max(1.0, deadline - time.time()))
                rc = p.returncode
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(os.getpgid(p.pid), _sig.SIGKILL)
                except (ProcessLookupError, PermissionError):
                    pass
                rc = None
            of.close()
            ef.close()
            sha = L.sha256_file(out) if out.exists() else None
            rows.append({"argv": argv, "rc": rc, "out_sha256": sha,
                         "out_bytes": out.stat().st_size if out.exists() else None,
                         "stderr_head": (leg_dir / "stderr").read_text(errors="replace")[:200]})
        shas = [r["out_sha256"] for r in rows if r["out_sha256"]]
        cells.append({"name": c["name"], "reps_n": c["reps"], "reps": rows,
                      "n_distinct_shas": len(set(shas)), "n_outputs": len(shas),
                      "stable": len(set(shas)) == 1 and len(shas) == c["reps"],
                      "loadavg1_before": la0, "loadavg1_after": la1,
                      "rcs": [r["rc"] for r in rows]})
        print(f"  conc {c['name']}: {len(set(shas))} distinct shas / {len(shas)}", flush=True)
    receipt("conc", cells, t0)
    return cells


# ---------------------------------------------------------------- witness ---

def _witness_cells():
    w = L.default_node_witness()
    s = L.settings_witness()
    census = {}
    try:
        import subprocess as sp
        ps = sp.run(["ps", "-eo", "pid,ppid,etimes,pcpu,args"], capture_output=True, text=True).stdout
        census["ps_lines_total"] = len(ps.splitlines())
        census["own_r94b_procs"] = [l.strip()[:180] for l in ps.splitlines() if "r94b_" in l]
        census["foreign_seat_procs"] = [l.strip()[:180] for l in ps.splitlines()
                                        if re.search(r"(r9[0-9][a-z]?-|battery|godot|measure_audio)", l)
                                        and "r94b_" not in l][:40]
        census["yes_procs"] = len([l for l in ps.splitlines() if re.search(r"\byes\b\s*$", l)])
    except Exception as e:  # noqa: BLE001
        census["ps_error"] = str(e)
    try:
        import subprocess as sp
        pws = sp.run(["/usr/bin/pw-cli", "ls", "Node"], capture_output=True, text=True, timeout=15).stdout
        names = re.findall(r'node\.name = "([^"]+)"', pws)
        census["pw_node_names"] = names
        census["pw_foreign_named"] = [n for n in names if re.match(r"r9[0-9][a-z]?", n)]
        census["pw_own_named"] = [n for n in names if n.startswith("r94b_")]
    except Exception as e:  # noqa: BLE001
        census["pw_error"] = str(e)
    return [{"name": "witness", "default_node": w, "settings": s, "census": census,
             "loadavg": L.loadavg()}]


def stage_witness(reps):
    t0 = time.time()
    cells = _witness_cells()
    receipt("witness", cells, t0)
    return cells


def stage_census(reps):
    t0 = time.time()
    cells = _witness_cells()
    receipt("census", cells, t0)
    return cells


def stage_all(reps):
    stage_witness(reps)
    stage_laws(reps)
    stage_axes(reps)
    stage_conc(reps)


STAGES = {"prep": stage_prep, "laws": stage_laws, "axes": stage_axes,
          "conc": stage_conc, "witness": stage_witness, "census": stage_census,
          "all": stage_all}


def main():
    stage = sys.argv[1]
    reps = int(sys.argv[2]) if len(sys.argv) > 2 else None
    warmup_s = float(os.environ.get("R94B_HOG_WARMUP", "0"))
    hogs = L.HogSet(HOGS).start() if HOGS > 0 else None
    if hogs is not None:
        if warmup_s > 0:
            print(f"  warming {HOGS} hogs for {warmup_s:g}s ...", flush=True)
            hogs.warmup(warmup_s)
        HOG_RECEIPT.update(hogs.receipt())
    try:
        STAGES[stage](reps)
    finally:
        if hogs is not None:
            hogs.stop()
            HOG_RECEIPT.update(hogs.receipt())
            (L.RUNS / PASS / f"hogs-{stage}.json").write_text(json.dumps(HOG_RECEIPT, indent=1))
            print(f"  hogs stopped: alive={hogs.alive()} loadavg={hogs.loadavg_after} "
                  f"cpu={HOG_RECEIPT.get('cpu_at_stop')}", flush=True)


if __name__ == "__main__":
    main()
