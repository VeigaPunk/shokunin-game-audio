#!/usr/bin/env python3
"""r94 VERIFIER — independent live re-derivation (own code, own argv, own
stimuli, own RIFF reader).

Nothing here is imported from the fixture: the stimulus definitions are
rebuilt with this seat's own writer, every sox invocation is this seat's own
argv, every product is parsed by this seat's own RIFF reader, and the results
are compared against (a) the scout's prep.json stimulus shas and (b) the
author's receipt fields.

Usage: r94v_live.py [--receipt PATH] [--json OUT]
"""
import argparse
import hashlib
import json
import math
import os
import re as _re
import struct
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LANE = HERE.parent                      # corpus/live/r94-verifier
SCRATCH = LANE / "scratch"
TREE = LANE / "tree"
SCOUT = TREE / "corpus" / "live" / "r94-scout" / "receipts"
SOX = "/usr/bin/sox"
FFMPEG = "/usr/bin/ffmpeg"
RATE = 48000
TAG = f"r94v_{os.getpid()}"

ROWS = []


def check(law, cond, detail=""):
    st = "PASS" if cond else "FAIL"
    ROWS.append({"law": law, "status": st, "detail": str(detail)[:300]})
    if not cond:
        print(f"FAIL {law}: {detail}"[:400])
    return cond


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


# ------------------------------------------------------------- own RIFF I/O
def write_pcm16(path, data, rate=RATE):
    a = np.asarray(data)
    if a.ndim == 1:
        a = a[:, None]
    frames, ch = a.shape
    body = a.astype("<i2").tobytes()
    blk = ch * 2
    fmt = struct.pack("<HHIIHH", 1, ch, rate, rate * blk, blk, 16)
    riff = (b"WAVE" + b"fmt " + struct.pack("<I", len(fmt)) + fmt +
            b"data" + struct.pack("<I", len(body)) + body)
    Path(path).write_bytes(b"RIFF" + struct.pack("<I", len(riff)) + riff)


def write_f32(path, data, rate=RATE):
    a = np.asarray(data)
    if a.ndim == 1:
        a = a[:, None]
    frames, ch = a.shape
    body = a.astype("<f4").tobytes()
    blk = ch * 4
    fmt = struct.pack("<HHIIHH", 3, ch, rate, rate * blk, blk, 32)
    riff = (b"WAVE" + b"fmt " + struct.pack("<I", len(fmt)) + fmt +
            b"fact" + struct.pack("<I", 4) + struct.pack("<I", frames) +
            b"data" + struct.pack("<I", len(body)) + body)
    Path(path).write_bytes(b"RIFF" + struct.pack("<I", len(riff)) + riff)


def read_riff(path):
    """Own reader -> (float matrix, meta). Raises on anything not RIFF."""
    raw = Path(path).read_bytes()
    if raw[:4] != b"RIFF" or raw[8:12] != b"WAVE":
        raise ValueError("not RIFF/WAVE")
    pos, fmt, data = 12, None, None
    while pos + 8 <= len(raw):
        cid = raw[pos:pos + 4]
        n = int.from_bytes(raw[pos + 4:pos + 8], "little")
        body = raw[pos + 8:pos + 8 + n]
        if cid == b"fmt ":
            fmt = body
        elif cid == b"data":
            data = body
        pos += 8 + n + (n & 1)
    tag, ch, rate, _br, _ba, bits = struct.unpack("<HHIIHH", fmt[:16])
    if tag == 0xFFFE and len(fmt) >= 26:
        tag = int.from_bytes(fmt[24:26], "little")
    if tag == 1 and bits == 16:
        arr = np.frombuffer(data, "<i2").astype(np.float64) / 32768.0
    elif tag == 1 and bits == 24:
        b = np.frombuffer(data, "u1").reshape(-1, 3).astype(np.int32)
        v = (b[:, 0] | (b[:, 1] << 8) | (b[:, 2] << 16))
        v = np.where(v >= 1 << 23, v - (1 << 24), v).astype(np.float64)
        arr = v / 8388608.0
    elif tag == 1 and bits == 32:
        arr = np.frombuffer(data, "<i4").astype(np.float64) / 2147483648.0
    elif tag == 3 and bits == 32:
        arr = np.frombuffer(data, "<f4").astype(np.float64)
    else:
        raise ValueError(f"unsupported fmt tag={tag} bits={bits}")
    return arr.reshape(-1, ch), {"rate": rate, "channels": ch, "bits": bits,
                                 "frames": len(arr) // ch, "fmt_tag": tag}


def run(argv, timeout=25.0, env=None):
    p = subprocess.run([str(a) for a in argv], stdout=subprocess.DEVNULL,
                       stderr=subprocess.PIPE, stdin=subprocess.DEVNULL,
                       timeout=timeout, env=env)
    return p.returncode, p.stderr.decode(errors="replace")


def sox_leg(name, tail, infile, reps=1, pre=None, mid=None, env=None):
    """This seat's own leg: fresh process per rep, own product path.

    argv = sox [pre] <in> [mid] <out> [tail] — the three positional slots are
    explicit because sox's grammar (global options before the first effect,
    output options between infile and outfile) is part of what is measured.
    """
    shas, rcs, errs, paths = [], [], [], []
    for r in range(reps):
        op = SCRATCH / f"{TAG}_{name}_r{r}.wav"
        if op.exists():
            op.unlink()
        argv = [SOX] + [str(t) for t in (pre or [])] + [str(infile)]
        argv += [str(t) for t in (mid or [])] + [str(op)]
        argv += [str(t) for t in tail]
        rc, err = run(argv, env=env)
        shas.append(sha(op) if op.exists() else None)
        rcs.append(rc)
        errs.append(err)
        paths.append(op)
    return {"name": name, "shas": shas, "rcs": rcs, "errs": errs,
            "paths": paths,
            "n_distinct": len({s for s in shas if s}),
            "sha": shas[0]}


def band_db(arr, rate, f0, half=600.0):
    """Own band estimator: Hann-windowed DFT power summed over the bins in
    [f0-half, f0+half], expressed in dB relative to a full-scale sine
    (amplitude 1.0 -> 0 dB). Independent of the fixture's estimator."""
    x = arr[:, 0] if arr.ndim > 1 else arr
    if x.size < 4096:
        return None
    n = 1 << int(math.floor(math.log2(min(x.size, 262144))))
    seg = x[:n]
    w = np.hanning(n)
    spec = np.fft.rfft(seg * w)
    f = np.fft.rfftfreq(n, 1.0 / rate)
    lo, hi = f0 - half, f0 + half
    m = (f >= lo) & (f <= hi)
    p = float(np.sum(np.abs(spec[m]) ** 2))
    # full-scale sine power with the same window and a two-sided sum
    pfull = float(np.sum(np.abs(np.fft.rfft(np.sin(2 * np.pi * f0 *
                                             np.arange(n) / rate) * w)) ** 2))
    if p <= 0:
        return -300.0
    return round(10 * math.log10(p / pfull), 6)


def db_amp(v):
    return None if v is None or v == 0 else round(20 * math.log10(abs(v)), 6)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--receipt", default=str(
        sorted((TREE / "corpus" / "live" / "runs").glob("*sox-r94/"
               "measurements.json"))[0]))
    ap.add_argument("--json", default=str(HERE / "r94v-live.json"))
    args = ap.parse_args()
    SCRATCH.mkdir(parents=True, exist_ok=True)
    rec = json.loads(Path(args.receipt).read_text())["measurements"]
    det = rec["sox_det_r94_probe"]["legs"]
    gain = rec["sox_gain_r94_probe"]["legs"]
    rate_l = rec["sox_rate_r94_probe"]["legs"]
    remix_l = rec["sox_remix_r94_probe"]["legs"]
    trim_l = rec["sox_trim_r94_probe"]["legs"]
    fade_l = rec["sox_fade_r94_probe"]["legs"]
    rps_l = rec["sox_repeat_pad_silence_r94_probe"]["legs"]
    dst_l = rec["sox_dither_stat_r94_probe"]["legs"]
    prep = json.loads((SCOUT / "prep.json").read_text())
    scout_stim = {}
    for note in prep.get("notes", []) or []:
        if isinstance(note, dict) and isinstance(note.get("stimuli"), dict):
            scout_stim.update(note["stimuli"])

    # ---------------------------------------------------------- stimuli
    t_a = np.arange(48000) / RATE
    A = SCRATCH / f"{TAG}_stim_a.wav"
    write_pcm16(A, np.column_stack([np.rint(16384.0 * np.sin(2 * np.pi * 1000.0 * t_a)),
                                    np.rint(8192.0 * np.sin(2 * np.pi * 1500.0 * t_a))]))
    t_b = np.arange(12000) / RATE
    B = SCRATCH / f"{TAG}_stim_b.wav"
    write_pcm16(B, np.rint(16384.0 * np.sin(2 * np.pi * 997.0 * t_b)))
    c = np.zeros(19200)
    t_c = np.arange(9600) / RATE
    c[4800:14400] = np.rint(16384.0 * np.sin(2 * np.pi * 997.0 * t_c))
    C = SCRATCH / f"{TAG}_stim_c.wav"
    write_pcm16(C, c)
    c2 = np.zeros(21600)
    c2[4800:14400] = np.rint(16384.0 * np.sin(2 * np.pi * 997.0 * t_c))
    C2 = SCRATCH / f"{TAG}_stim_c2.wav"
    write_pcm16(C2, c2)
    F = SCRATCH / f"{TAG}_stim_f.wav"
    write_f32(F, (0.5 * np.sin(2 * np.pi * 997.0 * t_b)).astype("<f4"))
    H = SCRATCH / f"{TAG}_stim_h.wav"
    write_pcm16(H, np.rint(16384.0 * np.sin(2 * np.pi * 20000.0 * t_b)))
    I = SCRATCH / f"{TAG}_stim_i.wav"
    write_pcm16(I, np.rint(16384.0 * np.sin(2 * np.pi * 997.0 * np.arange(12001) / RATE)))
    J = SCRATCH / f"{TAG}_stim_j.wav"
    write_pcm16(J, np.rint(16384.0 * np.sin(2 * np.pi * 23000.0 * t_b)))
    R = SCRATCH / f"{TAG}_stim_r.wav"
    write_pcm16(R, np.random.default_rng(94).integers(-32768, 32768, 4800,
                                                      dtype=np.int64))
    stim = {"a": A, "b": B, "c": C, "c2": C2, "f": F, "h": H, "i": I,
            "j": J, "r": R}
    for k, p in stim.items():
        got = sha(p)
        exp = scout_stim.get(f"r94s_stim_{k}.wav")
        check(f"stim.{k}.scout_sha", exp is not None and got == exp,
              f"own {got[:16]} vs scout {str(exp)[:16]}")
    stim_sha = {k: sha(p) for k, p in stim.items()}
    check("stim.receipt_agrees", stim_sha["a"] ==
          rec["sox_det_r94_probe"]["stimuli"]["sha256"]["a"],
          "own stimulus a vs author receipt")

    # ------------------------------------------------- determinism classes
    leg = sox_leg("det_default", ["gain", "-6"], A, reps=5)
    check("det.default_gain_m6.nondeterministic", leg["n_distinct"] >= 2,
          f"own distinct={leg['n_distinct']}/5 (receipt: "
          f"{det['det_gain_m6_default']['n_distinct_shas']}/5)")
    check("det.default_gain_m6.rc0", all(r == 0 for r in leg["rcs"]), leg["rcs"])
    leg = sox_leg("det_D", ["-D", "gain", "-6"], A, reps=3)
    check("det.D_gain_m6.stable", leg["n_distinct"] == 1, f"{leg['n_distinct']}/3")
    check("det.D_gain_m6.sha_eq_receipt", leg["sha"] == det["det_gain_m6_D"]["out_sha256"],
          f"own {str(leg['sha'])[:16]} vs receipt "
          f"{str(det['det_gain_m6_D']['out_sha256'])[:16]}")
    check("det.D_gain_m6.sha_eq_scout",
          leg["sha"] == det["det_gain_m6_D"]["scout_ref"]["expected_sha256"],
          "own vs scout gain_D.json:gain_m6")
    leg = sox_leg("det_dither_default", ["dither"], F, reps=5, mid=["-b", "16"])
    check("det.explicit_dither.nondeterministic", leg["n_distinct"] >= 2,
          f"{leg['n_distinct']}/5 rc={leg['rcs'][0]} {leg['errs'][0][:60]!r}")
    leg = sox_leg("det_dither_D", ["dither"], F, reps=5, pre=["-D"],
                  mid=["-b", "16"])
    check("det.D_does_not_fix_explicit_dither", leg["n_distinct"] >= 2,
          f"{leg['n_distinct']}/5 (D suppresses only the AUTOMATIC dither)")
    leg = sox_leg("det_dither_R", ["dither"], F, reps=3, pre=["-R"],
                  mid=["-b", "16"])
    check("det.R_fixes_explicit_dither", leg["n_distinct"] == 1,
          f"{leg['n_distinct']}/3")
    leg_R = leg
    leg = sox_leg("det_dither_RD", ["dither"], F, reps=3, pre=["-R", "-D"],
                  mid=["-b", "16"])
    check("det.RD_eq_R", leg["sha"] == leg_R["sha"] and leg["sha"] is not None,
          "bytes")
    leg = sox_leg("det_f32_s16", [], F, reps=5, mid=["-b", "16"])
    check("det.f32_to_s16.nondeterministic", leg["n_distinct"] >= 2,
          f"{leg['n_distinct']}/5")
    leg = sox_leg("det_f32_s24", [], F, reps=5, mid=["-b", "24"])
    check("det.f32_to_s24.stable", leg["n_distinct"] == 1, f"{leg['n_distinct']}/5")
    leg = sox_leg("det_f32_s32", [], F, reps=5, mid=["-b", "32"])
    check("det.f32_to_s32.stable", leg["n_distinct"] == 1, f"{leg['n_distinct']}/5")
    # identity legs vs own stimulus bytes
    for name, infile, tail in (("gain0", A, ["gain", "0"]),
                               ("passthrough", A, []),
                               ("rate_same", B, ["rate", "48000"]),
                               ("pad_pct50", B, ["pad", "%50"])):
        leg = sox_leg(f"id_{name}", ["-D"] + tail, infile)
        exp = sha(infile)
        check(f"det.{name}.identity", leg["sha"] == exp,
              f"own {str(leg['sha'])[:16]} vs stimulus {exp[:16]}")
    rc, err = run([SOX, "-D", str(A), str(SCRATCH / f"{TAG}_copy.wav"), "copy"])
    check("det.copy_token_not_an_effect",
          rc == 2 and "can't open input file" in err,
          f"rc={rc} err={err.strip()[:80]!r}")
    # flag order + buffer + env invariance (own argv)
    order = {}
    for label, argv in (("before", [SOX, "-D", str(A), str(SCRATCH / f"{TAG}_o_before.wav"),
                                    "gain", "-6"]),
                        ("after_in", [SOX, str(A), "-D", str(SCRATCH / f"{TAG}_o_afterin.wav"),
                                      "gain", "-6"]),
                        ("after_out", [SOX, str(A), str(SCRATCH / f"{TAG}_o_afterout.wav"),
                                       "-D", "gain", "-6"]),
                        ("no_dither", [SOX, "--no-dither", str(A),
                                       str(SCRATCH / f"{TAG}_o_nd.wav"), "gain", "-6"])):
        rc, _ = run(argv)
        op = Path(argv[3] if label == "before" else argv[3])
        order[label] = sha(op) if op.exists() and rc == 0 else None
    check("det.flag_order.invariant", len({s for s in order.values() if s}) == 1,
          f"{order}")
    bufs = {}
    for label, opts in (("control", []), ("b1024", ["--buffer", "1024"]),
                        ("b16384", ["--buffer", "16384"])):
        op = SCRATCH / f"{TAG}_buf_{label}.wav"
        rc, _ = run([SOX, "-D"] + opts + [str(A), str(op), "gain", "-6"])
        bufs[label] = sha(op) if op.exists() and rc == 0 else None
    check("det.buffer.invariant", len({s for s in bufs.values() if s}) == 1, bufs)
    envs = {}
    for label, extra in (("control", {}),
                         ("pw", {"PIPEWIRE_QUANTUM": "32", "PIPEWIRE_RATE": "44100",
                                 "PIPEWIRE_LATENCY": "64", "PIPEWIRE_NODE": f"{TAG}_nope",
                                 "PULSE_SINK": f"{TAG}_nope",
                                 "PULSE_SOURCE": f"{TAG}_nope"})):
        op = SCRATCH / f"{TAG}_env_{label}.wav"
        e = dict(os.environ)
        e.update(extra)
        rc, _ = run([SOX, "-D", str(A), str(op), "gain", "-6"], env=e)
        envs[label] = sha(op) if op.exists() and rc == 0 else None
    check("det.client_env.inert", len({s for s in envs.values() if s}) == 1, envs)
    rc, err = run([SOX, str(A), str(SCRATCH / f"{TAG}_gopt.wav"), "gain", "-6", "-D"])
    check("det.gopt_after_effect_refuses", rc == 1 and "usage" in err,
          f"rc={rc} err={err.strip()[:90]!r}")

    # ------------------------------------------------------------ gain
    ain, _ = read_riff(A)
    op = SCRATCH / f"{TAG}_gain_m6.wav"
    run([SOX, "-D", str(A), str(op), "gain", "-6"])
    out, _ = read_riff(op)
    xi = np.rint(ain * 32768.0)
    xo = np.rint(out * 32768.0)
    want = np.rint(ain * 10 ** (-6 / 20) * 32768.0)
    n = int(np.count_nonzero(xo - want))
    check("gain.m6.rounds_to_nearest", n == 0,
          f"own mismatch vs rint(x*10^(-6/20)) = {n}")
    pk = [db_amp(np.abs(out[:, c]).max()) for c in range(out.shape[1])]
    check("gain.m6.peaks", abs(pk[0] + 12.0211) < 5e-3 and abs(pk[1] + 18.0406) < 5e-3,
          f"own peak_db={pk} vs receipt {gain['gain_m6_rint']['metrics']['peak_db']}")
    op = SCRATCH / f"{TAG}_vol_amp.wav"
    run([SOX, "-D", str(A), str(op), "vol", "0.5"])
    va, _ = read_riff(op)
    op = SCRATCH / f"{TAG}_vol_db.wav"
    run([SOX, "-D", str(A), str(op), "vol", "-6.0206", "d"])
    vd, _ = read_riff(op)
    n_ceil = int(np.count_nonzero(np.rint(va * 32768.0) - np.ceil(ain * 0.5 * 32768.0)))
    n_rint = int(np.count_nonzero(np.rint(va * 32768.0) - np.rint(ain * 0.5 * 32768.0)))
    check("gain.vol_amp_rounds_ceil", n_ceil == 0 and n_rint > 0,
          f"ceil mismatch={n_ceil} rint mismatch={n_rint}")
    n_diff = int(np.count_nonzero(np.rint(va * 32768.0) - np.rint(vd * 32768.0)))
    mx = float(np.max(np.abs(np.rint(va * 32768.0) - np.rint(vd * 32768.0))))
    check("gain.vol_spellings_1lsb_apart",
          n_diff == 23000 and mx == 1.0 and sha(op) != sha(SCRATCH / f"{TAG}_vol_amp.wav"),
          f"own n_diff={n_diff} max={mx} (receipt: "
          f"{gain['vol_spelling_delta']['n_diff_samples']}/"
          f"{gain['vol_spelling_delta']['max_abs_diff_lsb']})")
    op = SCRATCH / f"{TAG}_vol_pow.wav"
    run([SOX, "-D", str(A), str(op), "vol", "0.5", "p"])
    vp, _ = read_riff(op)
    n = int(np.count_nonzero(np.rint(vp * 32768.0) -
                             np.rint(ain * math.sqrt(0.5) * 32768.0)))
    check("gain.vol_pow_is_sqrt_gain", n == 0,
          f"own mismatch vs rint(x*sqrt(0.5)) = {n} (the p form is a POWER ratio)")

    # ------------------------------------------------------------ rate
    for name, infile, orate, want in (("12000->44100", B, 44100, 11025),
                                      ("12001->44100", I, 44100, 11026),
                                      ("12000->22050", B, 22050, 5512),
                                      ("12000->24050", B, 24050, 6013),
                                      ("12000->11025", B, 11025, 2756),
                                      ("12000->32000", B, 32000, 8000)):
        op = SCRATCH / f"{TAG}_rate_{name.replace('->', '_')}.wav"
        rc, err = run([SOX, "-D", str(infile), str(op), "rate", str(orate)])
        _, meta = read_riff(op)
        check(f"rate.{name}.frames", meta["frames"] == want,
              f"own frames={meta['frames']} want={want} rc={rc} err={err[:60]!r}")
    op = SCRATCH / f"{TAG}_alias_q.wav"
    run([SOX, "-D", str(J), str(op), "rate", "-q", "44100"])
    q, _ = read_riff(op)
    op = SCRATCH / f"{TAG}_alias_default.wav"
    run([SOX, "-D", str(J), str(op), "rate", "44100"])
    dflt, _ = read_riff(op)
    op = SCRATCH / f"{TAG}_alias_a.wav"
    run([SOX, "-D", str(H), str(op), "rate", "-a", "44100"])
    a20, _ = read_riff(op)
    op = SCRATCH / f"{TAG}_alias_20k_default.wav"
    run([SOX, "-D", str(H), str(op), "rate", "44100"])
    d20, _ = read_riff(op)
    def peak_db(x):
        m = float(np.abs(x).max())
        return None if m == 0 else round(20 * math.log10(m), 6)

    # Convention-free comparisons: every band level is expressed relative to
    # the same leg's own overall peak, so this seat's estimator convention
    # (0 dB = full-scale sine) cancels out. The fixture's absolute numbers are
    # quoted alongside for the reader.
    p_q, p_d, p_a, p_d20 = (peak_db(q), peak_db(dflt), peak_db(a20),
                            peak_db(d20))
    bq = band_db(q, 44100, 21100.0)
    bd = band_db(dflt, 44100, 21100.0)
    ba = band_db(a20, 44100, 20000.0)
    ba21 = band_db(a20, 44100, 21100.0)
    bd20 = band_db(d20, 44100, 21100.0)
    bt20 = band_db(d20, 44100, 20000.0)
    rq = None if None in (bq, p_q) else round(bq - p_q, 4)
    rd = None if None in (bd, p_d) else round(bd - p_d, 4)
    ra = None if None in (ba, p_a) else round(ba - p_a, 4)
    ra21 = None if None in (ba21, p_a) else round(ba21 - p_a, 4)
    r20 = None if None in (bd20, bt20) else round(bd20 - bt20, 4)
    check("rate.q_folds_23k_to_21k", rq is not None and rq > -10.0,
          f"own -q: 21.1 kHz band {bq} dB = {rq} dB rel. own peak (the fold is "
          f"a HAZARD: within ~6 dB of the leg's own peak, vs the default leg's "
          f"{rd} dB rejection); fixture: band "
          f"{rate_l['alias_23k_q']['band_21100hz_db']} vs peak "
          f"{rate_l['alias_23k_q']['peak_db_overall']}")
    check("rate.default_rejects_23k", rd is not None and rd < -10.0,
          f"own default: {bd} dB = {rd} dB rel. peak; fixture: "
          f"{rate_l['alias_23k_default']['band_21100hz_db']} vs "
          f"{rate_l['alias_23k_default']['peak_db_overall']}")
    check("rate.a_flat_at_20k", ra is not None and abs(ra) < 1.5,
          f"own -a: 20 kHz band {ba} dB = {ra} dB rel. peak (fixture "
          f"band_20000hz_db={rate_l['alias_20k_a']['band_20000hz_db']})")
    check("rate.a_best_alias_rejection", ra21 is not None and ra21 < -60.0,
          f"own -a: 21.1 kHz band {ba21} dB = {ra21} dB rel. peak (fixture "
          f"{rate_l['alias_20k_a']['band_21100hz_db']} vs peak "
          f"{rate_l['alias_20k_a']['peak_db_overall']})")
    check("rate.20k_default_carries_the_deep_floor",
          r20 is not None and rd is not None and r20 < -40.0 and r20 < rd - 10.0,
          f"own 20 kHz-stimulus default: 21.1 kHz band {bd20} dB = {r20} dB "
          f"below its OWN 20 kHz tone {bt20} dB, vs the 23 kHz row's {rd} dB — "
          f"the deep floor belongs to the 20 kHz default row (fixture: "
          f"{rate_l['alias_20k_default']['band_21100hz_db']} vs 23 kHz "
          f"{rate_l['alias_23k_default']['band_21100hz_db']})")
    rc, err = run([SOX, "-D", str(J), str(SCRATCH / f"{TAG}_qa.wav"),
                   "rate", "-q", "-a", "44100"])
    check("rate.q_a_refusal", rc == 1 and "override options" in err,
          f"rc={rc} err={err.strip()[:90]!r}")
    op = SCRATCH / f"{TAG}_rate_same.wav"
    run([SOX, "-D", str(B), str(op), "rate", "48000"])
    check("rate.same_rate_identity", sha(op) == sha(B), "bytes vs stimulus b")

    # ----------------------------------------------------------- remix
    Li = ain[:, 0] * 32768.0
    Ri = ain[:, 1] * 32768.0
    for name, tail, want in (("remix_1", ["remix", "1"], Li[:, None]),
                             ("remix_1_2", ["remix", "1,2"],
                              np.floor((Li + Ri + 1.0) / 2.0)[:, None]),
                             ("remix_m", ["remix", "-m", "1,2"], (Li + Ri)[:, None]),
                             ("remix_p", ["remix", "-p", "1,2"],
                              np.rint((Li + Ri) / math.sqrt(2.0))[:, None]),
                             ("remix_0_1", ["remix", "0", "1"],
                              np.column_stack([np.zeros_like(Li), Li]))):
        op = SCRATCH / f"{TAG}_{name}.wav"
        run([SOX, "-D", str(A), str(op)] + tail)
        o, _ = read_riff(op)
        n = int(np.count_nonzero(np.rint(o * 32768.0) - want))
        check(f"remix.{name}.sample_exact", n == 0, f"own mismatch={n}")
    op = SCRATCH / f"{TAG}_channels1.wav"
    run([SOX, "-D", str(A), str(op), "channels", "1"])
    check("remix.channels_1_eq_remix_1_2",
          sha(op) == sha(SCRATCH / f"{TAG}_remix_1_2.wav"), "bytes")

    # ------------------------------------------------------------ trim
    bin_arr, _ = read_riff(B)
    for name, tail, want in (("1s", ["trim", "0", "1s"], 1),
                             ("4800s", ["trim", "0", "4800s"], 4800),
                             ("0.1", ["trim", "0", "0.1"], 4800),
                             ("0.1_end", ["trim", "0.1"], 7200),
                             ("neg0.1", ["trim", "0", "-0.1"], 7200),
                             ("eq0.1", ["trim", "0", "=0.1"], 4800),
                             ("plus", ["trim", "0.05+0.05"], 7200),
                             ("100", ["trim", "0", "100"], 12000),
                             ("zero", ["trim", "0", "0"], 0)):
        op = SCRATCH / f"{TAG}_trim_{name}.wav"
        rc, err = run([SOX, "-D", str(B), str(op)] + tail)
        _, meta = read_riff(op)
        check(f"trim.{name}.frames", meta["frames"] == want,
              f"own frames={meta['frames']} want={want} rc={rc}")
    rc, err = run([SOX, "-D", str(B), str(SCRATCH / f"{TAG}_trim_1sec.wav"),
                   "trim", "0", "1sec"])
    check("trim.1sec.refusal", rc == 1 and "cannot parse position" in err,
          f"rc={rc} err={err.strip()[:80]!r}")
    op = SCRATCH / f"{TAG}_trim_0.1.wav"
    run([SOX, "-D", str(B), str(op), "trim", "0", "0.1"])
    o, _ = read_riff(op)
    n = int(np.count_nonzero(np.rint(o[:, 0] * 32768.0) -
                             np.rint(bin_arr[:4800, 0] * 32768.0)))
    check("trim.content_is_input_head", n == 0, f"own mismatch={n}")

    # ------------------------------------------------------------ fade
    for name, tail, want in (("t1", ["fade", "0", "0.15", "0.1"], 7200),
                             ("t2", ["fade", "0", "0.2", "0.05"], 9600),
                             ("t3", ["fade", "0", "0.25", "0.1"], 12000)):
        op = SCRATCH / f"{TAG}_fade_{name}.wav"
        run([SOX, "-D", str(B), str(op)] + tail)
        _, meta = read_riff(op)
        check(f"fade.{name}.truncates", meta["frames"] == want,
              f"own frames={meta['frames']} want={want}")
    op = SCRATCH / f"{TAG}_fade_l.wav"
    run([SOX, "-D", str(B), str(op), "fade", "l", "0.1"])
    fl, _ = read_riff(op)
    bin_i = bin_arr[:, 0] * 32768.0
    bad = []
    for x in (0.5, 0.75, 0.9):
        f = int(round(x * 4800))
        ratio = float(fl[f, 0] * 32768.0 / bin_i[f])
        want_r = 10 ** (-5 * (1 - x))
        if abs(ratio - want_r) / want_r > 0.03:
            bad.append(f"x={x}: {ratio:.6f} vs {want_r:.6f}")
    check("fade.log_100db_per_span", not bad, f"own out-of-tolerance={bad}")
    op = SCRATCH / f"{TAG}_fade_default.wav"
    run([SOX, "-D", str(B), str(op), "fade", "0.1"])
    check("fade.default_type_is_l", sha(op) == sha(SCRATCH / f"{TAG}_fade_l.wav"),
          "bytes")

    # ------------------------------------------------- repeat / pad / silence
    op = SCRATCH / f"{TAG}_repeat2.wav"
    run([SOX, "-D", str(B), str(op), "repeat", "2"])
    o, meta = read_riff(op)
    tiled = np.tile(bin_i, 3)[:meta["frames"]]
    n = int(np.count_nonzero(np.rint(o[:, 0] * 32768.0) - tiled))
    check("rps.repeat_2.three_copies_tiled",
          meta["frames"] == 36000 and n == 0,
          f"own frames={meta['frames']} tiling mismatch={n}")
    op = SCRATCH / f"{TAG}_pad.wav"
    run([SOX, "-D", str(B), str(op), "pad", "0.1", "0.2"])
    o, meta = read_riff(op)
    ints = np.rint(o[:, 0] * 32768.0).astype(np.int64)
    nz = np.nonzero(ints)[0]
    check("rps.pad_0.1_0.2.insertion",
          meta["frames"] == 26400 and int(nz[0]) == 4801 and int(nz[-1]) == 16799,
          f"own frames={meta['frames']} first_nz={int(nz[0])} last_nz={int(nz[-1])}")
    op = SCRATCH / f"{TAG}_sil_above.wav"
    run([SOX, "-D", str(C2), str(op), "silence", "1", "0.1", "1%"])
    o, meta = read_riff(op)
    ints = np.rint(o[:, 0] * 32768.0).astype(np.int64)
    trail = 0
    for v in ints[::-1]:
        if v != 0:
            break
        trail += 1
    check("rps.silence_above_only.window_lag",
          meta["frames"] == 21600 - 4804 and trail == 7200,
          f"own frames={meta['frames']} trailing={trail}")
    op = SCRATCH / f"{TAG}_sil_both.wav"
    run([SOX, "-D", str(C2), str(op), "silence", "1", "0.1", "1%", "1", "0.1", "1%"])
    o, meta = read_riff(op)
    ints = np.rint(o[:, 0] * 32768.0).astype(np.int64)
    trail = 0
    for v in ints[::-1]:
        if v != 0:
            break
        trail += 1
    check("rps.silence_both.keeps_rate_over_50_minus_1", trail == 959,
          f"own trailing={trail} want 48000/50-1=959")
    op = SCRATCH / f"{TAG}_sil_leave.wav"
    run([SOX, "-D", str(C2), str(op), "silence", "-l", "1", "0.1", "1%", "1", "0.1", "1%"])
    o, meta = read_riff(op)
    ints = np.rint(o[:, 0] * 32768.0).astype(np.int64)
    trail = 0
    for v in ints[::-1]:
        if v != 0:
            break
        trail += 1
    check("rps.silence_l.keeps_duration_plus_lag", trail == 5759,
          f"own trailing={trail} want 959+4800=5759")

    # --------------------------------------------------------- dither/stat
    f_arr, _ = read_riff(F)
    op = SCRATCH / f"{TAG}_dither_s.wav"
    run([SOX, "-R", str(F), "-b", "16", str(op), "dither", "-s"])
    o, _ = read_riff(op)
    e = np.abs(np.rint(o.reshape(-1) * 32768.0) -
               np.rint(f_arr.reshape(-1) * 32768.0))
    check("dither.s_R.envelope",
          15 <= int(e.max()) <= 30 and 5.70 <= float(np.sqrt((e ** 2).mean())) <= 5.78,
          f"own max={int(e.max())} rms={float(np.sqrt((e**2).mean())):.6f} "
          f"(receipt max={dst_l['dither_s_R']['max_abs_err']} "
          f"rms={dst_l['dither_s_R']['err_rms']})")
    aim = ain.reshape(-1)
    rc, err = run([SOX, str(A), "-n", "stat"])
    flds = {}
    for ln in err.splitlines():
        if ":" in ln:
            k, v = ln.split(":", 1)
            flds[_re.sub(r"\s+", " ", k).strip()] = v.strip()
    own_rms = float(np.sqrt((aim ** 2).mean()))
    own_delta = float(np.abs(np.diff(aim)).max())
    check("stat.rms_is_interleaved_qmean",
          abs(float(flds.get("RMS amplitude", "nan")) - own_rms) < 1e-5,
          f"sox={flds.get('RMS amplitude')} own={own_rms:.6f}")
    check("stat.max_delta_is_interleaved",
          abs(float(flds.get("Maximum delta", "nan")) - own_delta) < 1e-5,
          f"sox={flds.get('Maximum delta')} own={own_delta:.6f}")
    rc, err = run([SOX, str(B), "-n", "stat", "-freq"])
    nums = [ln for ln in err.splitlines()
            if len(ln.split()) == 2 and ln.split()[0].replace(".", "").isdigit()]
    step = float(nums[1].split()[0]) - float(nums[0].split()[0]) if len(nums) > 1 else None
    check("stat.freq.2048_lines_per_4096_window",
          step == 11.71875 and len(nums) == 2048 * 3,
          f"own step={step} lines={len(nums)} want {2048 * 3}")
    rc, err_s = run([SOX, str(B), "-n", "stat", "-e"])
    rc, err_l = run([SOX, str(A), "-n", "stat", "-e"])
    check("stat.e.length_gate",
          "EBUR128 Momentary" in err_s and "EBUR128 Integrated" not in err_s and
          "EBUR128 Integrated" in err_l,
          "short mono: no Integrated; long stereo: Integrated")
    rc, ferr = run([FFMPEG, "-i", str(B), "-filter_complex", "ebur128=peak=true",
                    "-f", "null", "-"])

    m = _re.search(r"I:\s*(-?[\d.]+)\s*LUFS", ferr)
    check("ffmpeg.ebur128.gates_short_mono",
          m is not None and float(m.group(1)) <= -60.0,
          f"own ffmpeg I={m.group(1) if m else None} LUFS vs sox (no Integrated)")

    # --------------------------------------------------------------- census
    def pactl(args):
        p = subprocess.run(["pactl"] + args, capture_output=True, timeout=12.0)
        return p.stdout.decode(errors="replace")
    mine = []
    for a in (["list", "short", "sinks"], ["list", "short", "sources"],
              ["list", "short", "modules"]):
        mine += [ln.split("\t")[0] for ln in pactl(a).splitlines()
                 if TAG in ln or "r94a_" in ln or "r94v_" in ln]
    check("hygiene.no_own_pipewire_objects", not mine, f"own-tag rows={mine}")

    fails = [r for r in ROWS if r["status"] == "FAIL"]
    print(f"LIVE laws={len(ROWS)} PASS={len(ROWS) - len(fails)} FAIL={len(fails)}")
    out = {"receipt": args.receipt, "tag": TAG, "n_laws": len(ROWS),
           "n_fail": len(fails), "rows": ROWS}
    Path(args.json).write_text(json.dumps(out, indent=1) + "\n")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
