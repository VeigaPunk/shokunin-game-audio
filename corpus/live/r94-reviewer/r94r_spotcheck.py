#!/usr/bin/env python3
"""r94 REVIEWER independent spot re-derivation.

Own RIFF writer/reader, raw /usr/bin/sox invocations, own numpy laws. Nothing
here imports the author's family: the only shared inputs are the stimulus
DEFINITIONS (documented in the author report + pinned by the r94 scout's
prep.json shas) and the receipt VALUES being re-derived.

Prefix r94r_. File-only: no device, no PipeWire object, no module, no
set-default-*. Every child is wall-bounded and killed by process group.
"""
import hashlib
import json
import os
import re
import signal
import struct
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

REPO = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
ROOT = REPO / "corpus"
SCRATCH = ROOT / "live" / "r94-reviewer" / "scratch"
SCRATCH.mkdir(parents=True, exist_ok=True)
SOX = "/usr/bin/sox"
RATE = 48000
WALL = 25.0
PREP = ROOT / "live" / "r94-scout" / "receipts" / "prep.json"
SCOUT_SCRATCH = ROOT / "live" / "r94-scout" / "scratch"
SCOUT_RECEIPTS = ROOT / "live" / "r94-scout" / "receipts"
RECEIPT = ROOT / "live" / "runs" / "20261016T085514726246Z-sox-r94" / "measurements.json"

OUT = {"checks": [], "legs": {}, "stimuli": {}, "env": {}}
FAILED = []


# --------------------------------------------------------------- own RIFF --
def write_pcm16(path, data, rate=RATE):
    arr = np.asarray(data)
    if arr.ndim == 1:
        arr = arr[:, None]
    frames, ch = arr.shape
    body = arr.astype("<i2").tobytes()
    blk = ch * 2
    fmt = struct.pack("<HHIIHH", 1, ch, rate, rate * blk, blk, 16)
    payload = b"WAVE" + b"fmt " + struct.pack("<I", len(fmt)) + fmt
    payload += b"data" + struct.pack("<I", len(body)) + body
    Path(path).write_bytes(b"RIFF" + struct.pack("<I", len(payload)) + payload)


def write_f32(path, data, rate=RATE):
    arr = np.asarray(data)
    if arr.ndim == 1:
        arr = arr[:, None]
    frames, ch = arr.shape
    body = arr.astype("<f4").tobytes()
    blk = ch * 4
    fmt = struct.pack("<HHIIHH", 3, ch, rate, rate * blk, blk, 32)
    payload = b"WAVE" + b"fmt " + struct.pack("<I", len(fmt)) + fmt
    payload += b"fact" + struct.pack("<I", 4) + struct.pack("<I", frames)
    payload += b"data" + struct.pack("<I", len(body)) + body
    Path(path).write_bytes(b"RIFF" + struct.pack("<I", len(payload)) + payload)


def read_wav(path):
    raw = Path(path).read_bytes()
    assert raw[:4] == b"RIFF" and raw[8:12] == b"WAVE", f"not RIFF: {path}"
    pos, fmt, data, fact = 12, None, None, None
    while pos + 8 <= len(raw):
        cid = raw[pos:pos + 4]
        size = int.from_bytes(raw[pos + 4:pos + 8], "little")
        body = raw[pos + 8:pos + 8 + size]
        if cid == b"fmt ":
            fmt = body
        elif cid == b"data":
            data = body
        elif cid == b"fact":
            fact = body
        pos += 8 + size + (size & 1)
    tag, ch, rate, _br, _ba, bits = struct.unpack("<HHIIHH", fmt[:16])
    if tag == 3 and bits == 32:
        arr = np.frombuffer(data[:len(data) - len(data) % (4 * ch)], "<f4").astype(np.float64)
        scale = 1.0
    elif tag == 1 and bits == 16:
        arr = np.frombuffer(data[:len(data) - len(data) % (2 * ch)], "<i2").astype(np.float64)
        scale = 32768.0
    elif tag == 1 and bits == 32:
        arr = np.frombuffer(data[:len(data) - len(data) % (4 * ch)], "<i4").astype(np.float64)
        scale = 2147483648.0
    elif tag == 1 and bits == 24:
        b = np.frombuffer(data[:len(data) - len(data) % (3 * ch)], np.uint8).reshape(-1, 3)
        v = (b[:, 0].astype(np.int32) | (b[:, 1].astype(np.int32) << 8)
             | (b[:, 2].astype(np.int32) << 16))
        v = np.where(v & 0x800000, v - 0x1000000, v)
        arr = v.astype(np.float64)
        scale = 8388608.0
    else:
        raise ValueError(f"unsupported fmt tag={tag} bits={bits}")
    frames = arr.size // ch
    arr = arr[:frames * ch].reshape(frames, ch) / scale
    return arr, {"channels": ch, "rate": rate, "bits": bits, "fmt_tag": tag,
                 "frames": frames, "fact": fact}


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def run(argv, timeout=WALL):
    """Bounded raw sox spawn; returns rc, stderr text, wall."""
    proc = subprocess.Popen([str(a) for a in argv], stdout=subprocess.DEVNULL,
                            stderr=subprocess.PIPE, stdin=subprocess.DEVNULL,
                            start_new_session=True,
                            preexec_fn=lambda: __import__("resource").setrlimit(
                                __import__("resource").RLIMIT_CORE, (0, 0)))
    t0 = time.monotonic()
    try:
        _o, err = proc.communicate(timeout=timeout)
        killed = False
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except OSError:
            pass
        _o, err = proc.communicate()
        killed = True
    return {"rc": proc.returncode, "wall_s": round(time.monotonic() - t0, 3),
            "stderr": (err or b"").decode(errors="replace"), "killed": killed}


def sox_leg(name, tail, infile, reps=1):
    """One leg: raw sox, per-rep product, own read. Returns a record."""
    shas, paths, recs, arrs = [], [], [], []
    for r in range(reps):
        op = SCRATCH / f"r94r_{name}_r{r}.wav"
        try:
            op.unlink()
        except OSError:
            pass
        argv = [SOX] + [str(t).replace("{in}", str(infile)).replace("{out}", str(op))
                        for t in tail]
        rec = run(argv)
        s = sha(op) if op.exists() else None
        shas.append(s)
        paths.append(op)
        recs.append({"rc": rec["rc"], "sha": s, "wall_s": rec["wall_s"],
                     "stderr": rec["stderr"][:400], "killed": rec["killed"]})
        if op.exists() and rec["rc"] == 0:
            try:
                a, m = read_wav(op)
                arrs.append(a)
                recs[-1]["meta"] = {k: v for k, v in m.items() if k != "fact"}
            except (ValueError, AssertionError) as exc:
                recs[-1]["meta_error"] = str(exc)[:120]
                arrs.append(None)
        else:
            arrs.append(None)
    distinct = sorted({s for s in shas if s})
    return {"name": name, "argv": [str(a).replace(str(infile), "<in>")
                                   .replace(str(SCRATCH / f"r94r_{name}_r0.wav"), "<out>")
                                   for a in ([SOX] + list(tail))],
            "rc": recs[0]["rc"], "reps_n": reps, "shas": shas,
            "n_distinct": len(distinct), "stable": len(distinct) == 1 and shas[0],
            "reps": recs, "arr": arrs[0], "meta": recs[0].get("meta")}


def peak_db(arr):
    if arr is None or arr.size == 0:
        return None
    p = float(np.abs(arr).max())
    return None if p <= 0 else round(20.0 * np.log10(p), 6)


def band_db(arr, rate, freq, half=10.0):
    """Own Hann-windowed band level, NO cross-seat offset constant: used only
    for RELATIVE comparisons between legs measured by the same estimator."""
    x = np.asarray(arr).reshape(-1)
    if x.size == 0:
        return None
    w = np.hanning(x.size)
    n = 1 << int(np.ceil(np.log2(max(x.size, 16))))
    spec = np.abs(np.fft.rfft(x * w, n))
    fr = np.fft.rfftfreq(n, 1.0 / rate)
    sel = (fr >= freq - half) & (fr <= freq + half)
    if not sel.any():
        return None
    power = float((spec[sel] ** 2).sum())
    norm = float(w.sum()) / 2.0
    if power <= 0 or norm <= 0:
        return None
    return round(10.0 * np.log10(power / (norm ** 2)), 6)


def check(cid, ok, detail, measured=None, receipt=None):
    OUT["checks"].append({"id": cid, "ok": bool(ok), "detail": detail,
                          "measured": measured, "receipt": receipt})
    if not ok:
        FAILED.append(f"{cid}: {detail}")
    print(("PASS " if ok else "FAIL ") + cid + " | " + str(detail)[:220], flush=True)
    return ok


def rleg(entry, name):
    return REC.json_legs[entry][name]


class REC:
    json_legs = {}


def load_receipt():
    doc = json.loads(RECEIPT.read_text())
    m = doc["measurements"]
    REC.json_legs = {k: v["legs"] for k, v in m.items() if k.startswith("sox")}
    return m


def scout_ref(receipt_file, legname):
    """Read the r94 scout's receipt directly (cross-seat witness)."""
    p = SCOUT_RECEIPTS / receipt_file
    if not p.is_file():
        return None
    doc = json.loads(p.read_text())
    for leg in doc.get("legs", []) or []:
        if isinstance(leg, dict) and leg.get("name") == legname:
            reps = leg.get("reps") or [{}]
            return {"sha": reps[0].get("out_sha256"), "metrics": reps[0].get("metrics")}
    return None


# ------------------------------------------------------------------ stimuli --
def build_stimuli():
    t_a = np.arange(48000) / RATE
    a = np.column_stack([np.rint(16384.0 * np.sin(2 * np.pi * 1000.0 * t_a)),
                         np.rint(8192.0 * np.sin(2 * np.pi * 1500.0 * t_a))]).astype("<i2")
    write_pcm16(SCRATCH / "r94r_stim_a.wav", a)

    t_b = np.arange(12000) / RATE
    b = np.rint(16384.0 * np.sin(2 * np.pi * 997.0 * t_b)).astype("<i2")
    write_pcm16(SCRATCH / "r94r_stim_b.wav", b)

    c = np.zeros(19200, dtype="<i2")
    c[4800:14400] = np.rint(16384.0 * np.sin(2 * np.pi * 997.0 * np.arange(9600) / RATE))
    write_pcm16(SCRATCH / "r94r_stim_c.wav", c)

    f = (0.5 * np.sin(2 * np.pi * 997.0 * t_b)).astype("<f4")
    write_f32(SCRATCH / "r94r_stim_f.wav", f)

    h = np.rint(16384.0 * np.sin(2 * np.pi * 20000.0 * t_b)).astype("<i2")
    write_pcm16(SCRATCH / "r94r_stim_h.wav", h)

    i = np.rint(16384.0 * np.sin(2 * np.pi * 997.0 * np.arange(12001) / RATE)).astype("<i2")
    write_pcm16(SCRATCH / "r94r_stim_i.wav", i)

    j = np.rint(16384.0 * np.sin(2 * np.pi * 23000.0 * t_b)).astype("<i2")
    write_pcm16(SCRATCH / "r94r_stim_j.wav", j)

    rng = np.random.default_rng(94)
    r = rng.integers(-32768, 32768, size=4800, dtype=np.int64).astype("<i2")
    write_pcm16(SCRATCH / "r94r_stim_r.wav", r)

    c2 = np.zeros(21600, dtype="<i2")
    c2[4800:14400] = np.rint(16384.0 * np.sin(2 * np.pi * 997.0 * np.arange(9600) / RATE))
    write_pcm16(SCRATCH / "r94r_stim_c2.wav", c2)

    stim = {k: SCRATCH / f"r94r_stim_{k}.wav" for k in "abcfhijr"}
    stim["c2"] = SCRATCH / "r94r_stim_c2.wav"

    prep_shas = {}
    if PREP.is_file():
        doc = json.loads(PREP.read_text())
        for note in doc.get("notes", []) or []:
            if isinstance(note, dict) and isinstance(note.get("stimuli"), dict):
                prep_shas.update(note["stimuli"])
    rec_shas = json.loads(RECEIPT.read_text())["measurements"]["sox_det_r94_probe"]["stimuli"]["sha256"]

    for k, p in sorted(stim.items()):
        s = sha(p)
        mine_vs_receipt = (s == rec_shas.get(k))
        prep = prep_shas.get(f"r94s_stim_{k}.wav")
        mine_vs_prep = (s == prep) if prep else None
        # content-level comparison against the scout's own stimulus file
        content = None
        sp = SCOUT_SCRATCH / f"r94s_stim_{k}.wav"
        if sp.is_file():
            mine, _m1 = read_wav(p)
            theirs, _m2 = read_wav(sp)
            content = bool(mine.shape == theirs.shape and
                           np.array_equal(np.rint(mine * 32768 if mine.dtype.kind == "f" else mine),
                                          np.rint(theirs * 32768 if theirs.dtype.kind == "f" else theirs)))
        OUT["stimuli"][k] = {"mine": s, "receipt": rec_shas.get(k),
                             "scout_prep": prep, "mine_vs_receipt": mine_vs_receipt,
                             "mine_vs_scout_prep": mine_vs_prep,
                             "content_vs_scout_file": content,
                             "scout_file_sha": sha(sp) if sp.is_file() else None}
        check(f"stim_{k}_rebuild_matches_receipt", mine_vs_receipt,
              f"own rebuild sha {s[:16]} vs receipt {str(rec_shas.get(k))[:16]}")
        if prep:
            check(f"stim_{k}_rebuild_matches_scout_prep", mine_vs_prep,
                  f"own rebuild vs scout prep.json {prep[:16]}")
        if content is not None:
            check(f"stim_{k}_content_equals_scout_file", content,
                  "own rebuild sample matrix equals the scout's own stimulus file")
    return stim


# ---------------------------------------------------------------------- main --
def main():
    OUT["env"] = {"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                  "sox_version": run([SOX, "--version"])["stderr"].strip()
                  if False else subprocess.run([SOX, "--version"], capture_output=True)
                  .stdout.decode().strip(),
                  "sox_sha256": sha(SOX), "loadavg": Path("/proc/loadavg").read_text().strip(),
                  "numpy": np.__version__, "python": sys.version.split()[0],
                  "receipt": str(RECEIPT)}
    m = load_receipt()
    stim = build_stimuli()
    A, B, C, C2, F, H, I, J = (stim["a"], stim["b"], stim["c"], stim["c2"], stim["f"],
                               stim["h"], stim["i"], stim["j"])
    ain, _ = read_wav(A)
    bin_arr, _ = read_wav(B)
    f_arr, _ = read_wav(F)
    c2_arr, _ = read_wav(C2)
    Ai = ain * 32768.0
    Bi = bin_arr[:, 0] * 32768.0          # 1-D ints of the mono stimulus
    Li, Ri = Ai[:, 0], Ai[:, 1]

    # =============================================================== det ===
    g_def = sox_leg("det_gain_m6_default", ["{in}", "{out}", "gain", "-6"], A, reps=5)
    check("det_gain_m6_default_nondeterministic", g_def["n_distinct"] >= 2,
          f"{g_def['n_distinct']} distinct shas over 5 fresh processes",
          g_def["n_distinct"], rleg("sox_det_r94_probe", "det_gain_m6_default")["n_distinct_shas"])
    g_d = sox_leg("det_gain_m6_D", ["-D", "{in}", "{out}", "gain", "-6"], A, reps=3)
    check("det_gain_m6_D_stable", g_d["stable"],
          f"{g_d['n_distinct']} distinct over 3 reps")
    ref = scout_ref("gain_D.json", "gain_m6")
    check("det_gain_m6_D_equals_scout_bytes", ref is not None and g_d["shas"][0] == ref["sha"],
          f"own {str(g_d['shas'][0])[:16]} vs scout gain_D.json:gain_m6 "
          f"{str(ref and ref['sha'])[:16]}",
          g_d["shas"][0], ref and ref["sha"])
    check("det_gain_m6_D_matches_receipt",
          g_d["shas"][0] == rleg("sox_det_r94_probe", "det_gain_m6_D")["out_sha256"],
          "own -D gain -6 bytes equal the r94 receipt's")
    check("det_gain_m6_default_bytes_differ_from_D",
          g_def["shas"][0] != g_d["shas"][0],
          "the default leg is dither-carried, the -D leg is not (distinct bytes)")

    for nm, infile, tail in (("det_gain0_identity", A, ["gain", "0"]),
                             ("det_passthrough_identity", A, []),
                             ("det_pad_pct50_identity", B, ["pad", "%50"])):
        leg = sox_leg(nm, ["-D", "{in}", "{out}"] + tail, infile)
        check(f"{nm}_byte_identical_to_stimulus", leg["shas"][0] == sha(infile),
              f"{nm} output sha {str(leg['shas'][0])[:16]} vs stimulus {sha(infile)[:16]}")

    copy_leg = sox_leg("det_copy_token_not_an_effect", ["-D", "{in}", "{out}", "copy"], A)
    check("det_copy_token_refuses_rc2",
          copy_leg["rc"] == 2 and "can't open input file" in copy_leg["reps"][0]["stderr"],
          f"rc={copy_leg['rc']} stderr={copy_leg['reps'][0]['stderr'].strip()[:90]}",
          copy_leg["rc"], rleg("sox_det_r94_probe", "det_copy_token_not_an_effect")["rc"])

    f24 = sox_leg("det_f32_to_s24", ["{in}", "-b", "24", "{out}"], F, reps=5)
    check("det_f32_to_s24_stable", f24["stable"] and f24["n_distinct"] == 1,
          f"{f24['n_distinct']} distinct over 5 reps (>=24 bit suppresses auto-dither)")
    f16 = sox_leg("det_f32_to_s16_plain", ["{in}", "-b", "16", "{out}"], F, reps=5)
    check("det_f32_to_s16_nondeterministic", f16["n_distinct"] >= 2,
          f"{f16['n_distinct']} distinct over 5 reps (<24 bit keeps the auto-dither)")
    order_after = sox_leg("det_flag_order_after_infile", ["{in}", "-D", "{out}", "gain", "-6"], A)
    check("det_flag_order_after_infile_same_bytes",
          order_after["shas"][0] == g_d["shas"][0],
          "a -D placed after the infile yields the same bytes as before it")

    # ============================================================== gain ===
    gm6 = sox_leg("gain_m6_rint", ["-D", "{in}", "{out}", "gain", "-6"], A)
    if gm6["arr"] is not None:
        want = np.rint(ain * 10 ** (-6 / 20) * 32768.0)
        d = np.abs(gm6["arr"] * 32768.0 - want)
        n = int(np.count_nonzero(d > 0))
        check("gain_m6_equals_rint_formula", n == 0,
              f"mismatch {n} vs rint(x*10^(-6/20)); max abs diff {float(d.max())}",
              n, rleg("sox_gain_r94_probe", "gain_m6_rint")["mismatch_vs_rint_formula"])
        check("gain_m6_peaks", abs(peak_db(gm6["arr"]) - (-12.0211)) < 5e-4,
              f"peak {peak_db(gm6['arr'])} (receipt [-12.0211, -18.0406])")

    va = sox_leg("vol_amp_0.5", ["-D", "{in}", "{out}", "vol", "0.5"], A)
    vd = sox_leg("vol_db_m6_0206", ["-D", "{in}", "{out}", "vol", "-6.0206", "d"], A)
    vp = sox_leg("vol_pow_0.5", ["-D", "{in}", "{out}", "vol", "0.5", "p"], A)
    if va["arr"] is not None:
        o = va["arr"] * 32768.0
        n_ceil = int(np.count_nonzero(np.abs(o - np.ceil(ain * 0.5 * 32768.0)) > 0))
        n_rint = int(np.count_nonzero(np.abs(o - np.rint(ain * 0.5 * 32768.0)) > 0))
        check("vol_amp_is_ceil_path", n_ceil == 0,
              f"mismatch vs ceil {n_ceil}; vs rint {n_rint}",
              {"ceil": n_ceil, "rint": n_rint},
              {"ceil": rleg("sox_gain_r94_probe", "vol_amp_0.5")["mismatch_vs_ceil"],
               "rint": rleg("sox_gain_r94_probe", "vol_amp_0.5")["mismatch_vs_rint_formula"]})
        check("vol_amp_is_not_nearest_path", n_rint > 0,
              f"rint mismatch {n_rint} (the discriminator)")
    if vd["arr"] is not None:
        n = int(np.count_nonzero(np.abs(vd["arr"] * 32768.0
                                        - np.rint(ain * 10 ** (-6.0206 / 20) * 32768.0)) > 0))
        check("vol_db_is_rint_path", n == 0, f"mismatch {n} vs rint")
    if vp["arr"] is not None:
        n = int(np.count_nonzero(np.abs(vp["arr"] * 32768.0
                                        - np.rint(ain * np.sqrt(0.5) * 32768.0)) > 0))
        check("vol_pow_is_rint_sqrt_path", n == 0,
              f"mismatch {n} vs rint(x*sqrt(0.5)) = -3.0103 dB; peak {peak_db(vp['arr'])}",
              peak_db(vp["arr"]), rleg("sox_gain_r94_probe", "vol_pow_0.5")["metrics"]["peak_db"])
    if va["arr"] is not None and vd["arr"] is not None:
        d = np.abs(va["arr"] * 32768.0 - vd["arr"] * 32768.0)
        n = int(np.count_nonzero(d > 0))
        rr = rleg("sox_gain_r94_probe", "vol_spelling_delta")
        check("vol_spellings_differ_by_1lsb",
              n > 0 and float(d.max()) == 1.0 and va["shas"][0] != vd["shas"][0],
              f"n_diff {n} max {float(d.max())} LSB; receipt n_diff {rr['n_diff_samples']} "
              f"max {rr['max_abs_diff_lsb']}", {"n": n, "max": float(d.max())},
              {"n": rr["n_diff_samples"], "max": rr["max_abs_diff_lsb"]})
    ch1 = sox_leg("chain_gain_then_norm", ["-D", "{in}", "{out}", "gain", "-6", "norm", "-3"], A)
    ch2 = sox_leg("chain_norm_then_gain", ["-D", "{in}", "{out}", "norm", "-3", "gain", "-6"], A)
    check("chain_order_is_content_visible",
          abs(peak_db(ch1["arr"]) - (-3.0)) < 5e-3 and abs(peak_db(ch2["arr"]) - (-8.9996)) < 5e-3,
          f"gain,norm peak {peak_db(ch1['arr'])}; norm,gain peak {peak_db(ch2['arr'])} "
          f"(receipt -2.999988 / -8.999645)",
          {"a": peak_db(ch1["arr"]), "b": peak_db(ch2["arr"])},
          {"a": rleg("sox_gain_r94_probe", "chain_gain_then_norm")["metrics"]["peak_db"],
           "b": rleg("sox_gain_r94_probe", "chain_norm_then_gain")["metrics"]["peak_db"]})

    # ============================================================== rate ===
    for nm, infile, rate, exp in (("len_12000_to_44100", B, 44100, 11025),
                                  ("len_12001_to_44100", I, 44100, 11026),
                                  ("len_12000_to_22050", B, 22050, 5512),
                                  ("len_12000_to_24050", B, 24050, 6013),
                                  ("len_12000_to_11025", B, 11025, 2756)):
        leg = sox_leg(nm, ["-D", "{in}", "{out}", "rate", str(rate)], infile)
        got = (leg["meta"] or {}).get("frames")
        check(f"{nm}_frames", got == exp,
              f"own frames {got} vs receipt {rleg('sox_rate_r94_probe', nm)['metrics']['frames']}",
              got, rleg("sox_rate_r94_probe", nm)["metrics"]["frames"])

    al = {}
    for nm, infile, tail in (("alias_23k_default", J, ["rate", "44100"]),
                             ("alias_23k_v", J, ["rate", "-v", "44100"]),
                             ("alias_23k_q", J, ["rate", "-q", "44100"]),
                             ("alias_23k_a", J, ["rate", "-a", "44100"]),
                             ("alias_20k_default", H, ["rate", "44100"]),
                             ("alias_20k_l", H, ["rate", "-l", "44100"]),
                             ("alias_20k_a", H, ["rate", "-a", "44100"])):
        leg = sox_leg(nm, ["-D", "{in}", "{out}"] + tail, infile)
        leg["peak"] = peak_db(leg["arr"])
        leg["band21100"] = band_db(leg["arr"], 44100, 21100.0) if leg["arr"] is not None else None
        leg["band20000"] = band_db(leg["arr"], 44100, 20000.0) if leg["arr"] is not None else None
        al[nm] = leg
        check(f"{nm}_sha_matches_receipt",
              leg["shas"][0] == rleg("sox_rate_r94_probe", nm)["out_sha256"],
              "own bytes equal the receipt's")

    d23, v23, q23, a23 = (al["alias_23k_default"], al["alias_23k_v"],
                          al["alias_23k_q"], al["alias_23k_a"])
    # estimator-free falsification check: the -v rejection sits at the default's
    # level (band-to-peak gap), NOT 25 dB lower like the 20 kHz default row.
    gap = lambda L: (L["band21100"] - L["peak"]) if L["band21100"] is not None else None
    check("rate_v_not_130db_below_default",
          gap(v23) is not None and gap(d23) is not None and abs(gap(v23) - gap(d23)) < 1.0,
          f"own band-minus-peak: default {gap(d23):.3f} dB, -v {gap(v23):.3f} dB "
          f"(difference {abs(gap(v23) - gap(d23)):.3f} dB; a -130 dB -v would be ~25 dB lower)",
          {"default": gap(d23), "v": gap(v23)})
    check("rate_v_bytes_differ_from_default", v23["shas"][0] != d23["shas"][0],
          "-v is a different filter (distinct bytes) at the same rejection level")
    check("rate_130db_home_is_20k_default",
          gap(al["alias_20k_default"]) is not None and
          gap(al["alias_20k_default"]) < gap(d23) - 20.0,
          f"own 20k-default band-minus-peak {gap(al['alias_20k_default']):.3f} dB vs "
          f"23k-default {gap(d23):.3f} dB (receipt -129.588 vs -104.386 = 25.2 dB apart)",
          {"20k_default": gap(al["alias_20k_default"]), "23k_default": gap(d23)})
    check("rate_q_folds_to_21100",
          q23["peak"] is not None and q23["band21100"] is not None and
          abs(q23["band21100"] - q23["peak"]) < 3.0 and q23["peak"] > -20.0,
          f"own -q peak {q23['peak']} dB with the 21.1 kHz band at {q23['band21100']:.3f} dB "
          f"(the tone FOLDS; receipt peak -6.172)",
          {"peak": q23["peak"], "band": q23["band21100"]},
          {"peak": rleg("sox_rate_r94_probe", "alias_23k_q")["peak_db_overall"],
           "band": rleg("sox_rate_r94_probe", "alias_23k_q")["band_21100hz_db"]})
    check("rate_20k_l_is_the_hole",
          al["alias_20k_l"]["peak"] is not None and al["alias_20k_a"]["peak"] is not None and
          abs((al["alias_20k_l"]["peak"] - al["alias_20k_a"]["peak"]) - (-23.020)) < 0.1,
          f"own -l peak {al['alias_20k_l']['peak']} vs -a peak {al['alias_20k_a']['peak']} "
          f"(= -23.02 dB hole at 20 kHz)",
          {"l": al["alias_20k_l"]["peak"], "a": al["alias_20k_a"]["peak"]},
          {"l": rleg("sox_rate_r94_probe", "alias_20k_l")["peak_db_overall"],
           "a": rleg("sox_rate_r94_probe", "alias_20k_a")["peak_db_overall"]})
    qa = sox_leg("rate_q_a_refusal", ["-D", "{in}", "{out}", "rate", "-q", "-a", "44100"], J)
    check("rate_q_a_refuses",
          qa["rc"] == 1 and "override options only work at higher quality levels"
          in qa["reps"][0]["stderr"],
          f"rc={qa['rc']} stderr={qa['reps'][0]['stderr'].strip()[:80]}")

    # ============================================================= remix ===
    r1 = sox_leg("remix_1_selects_L", ["-D", "{in}", "{out}", "remix", "1"], A)
    if r1["arr"] is not None:
        n = int(np.count_nonzero(np.abs(r1["arr"][:, 0] * 32768.0 - Li) > 0))
        nm_ = int(np.count_nonzero(np.abs(r1["arr"][:, 0] * 32768.0 - (Li + Ri) / 2) > 0))
        check("remix_1_selects_channel_1", n == 0 and nm_ > 0,
              f"mismatch vs L {n}; vs (L+R)/2 {nm_}", {"vs_L": n, "vs_mean": nm_},
              {"vs_L": rleg("sox_remix_r94_probe", "remix_1_selects_L")["mismatch"],
               "vs_mean": rleg("sox_remix_r94_probe", "remix_1_selects_L")["mismatch_vs_mean"]})
    auto = sox_leg("remix_1_2_auto", ["-D", "{in}", "{out}", "remix", "1,2"], A)
    ch1_leg = sox_leg("channels_1", ["-D", "{in}", "{out}", "channels", "1"], A)
    if auto["arr"] is not None:
        n = int(np.count_nonzero(np.abs(auto["arr"][:, 0] * 32768.0
                                        - np.floor((Li + Ri + 1.0) / 2.0)) > 0))
        nn = int(np.count_nonzero(np.abs(auto["arr"][:, 0] * 32768.0
                                         - np.rint((Li + Ri) / 2.0)) > 0))
        check("downmix_is_floor_LpRp1_over_2", n == 0 and nn > 0,
              f"mismatch vs floor((L+R+1)/2) {n}; vs rint((L+R)/2) {nn}",
              {"floor": n, "rint": nn},
              {"floor": rleg("sox_remix_r94_probe", "remix_1_2_auto")["mismatch"],
               "rint": rleg("sox_remix_r94_probe", "remix_1_2_auto")["mismatch_vs_nearest_even"]})
    check("channels_1_same_bytes_as_remix_1_2", ch1_leg["shas"][0] == auto["shas"][0],
          "channels 1 and remix 1,2 are the same bytes")
    mm = sox_leg("remix_m_1_2", ["-D", "{in}", "{out}", "remix", "-m", "1,2"], A)
    if mm["arr"] is not None:
        n = int(np.count_nonzero(np.abs(mm["arr"][:, 0] * 32768.0 - (Li + Ri)) > 0))
        check("remix_m_is_exact_sum", n == 0, f"mismatch {n} vs exact L+R")
    r01 = sox_leg("remix_0_1_zero_then_in1", ["-D", "{in}", "{out}", "remix", "0", "1"], A)
    if r01["arr"] is not None:
        n0 = int(np.count_nonzero(np.abs(r01["arr"][:, 0]) > 0))
        n1 = int(np.count_nonzero(np.abs(r01["arr"][:, 1] * 32768.0 - Li) > 0))
        check("remix_0_1_is_zero_then_input1", n0 == 0 and n1 == 0,
              f"ch0 nonzero {n0}; ch1 vs L mismatch {n1} -> [silence, L] "
              f"(receipt peak [None, -6.0206])")

    # ============================================================== trim ===
    t1 = sox_leg("trim_0_1s", ["-D", "{in}", "{out}", "trim", "0", "1s"], B)
    t4800 = sox_leg("trim_0_4800s", ["-D", "{in}", "{out}", "trim", "0", "4800s"], B)
    check("trim_s_suffix_is_samples",
          (t1["meta"] or {}).get("frames") == 1 and (t4800["meta"] or {}).get("frames") == 4800,
          f"trim 0 1s -> {(t1['meta'] or {}).get('frames')} frame(s); "
          f"trim 0 4800s -> {(t4800['meta'] or {}).get('frames')} frames")
    tsec = sox_leg("trim_0_1sec", ["-D", "{in}", "{out}", "trim", "0", "1sec"], B)
    check("trim_1sec_refuses",
          tsec["rc"] == 1 and "cannot parse position" in tsec["reps"][0]["stderr"],
          f"rc={tsec['rc']} stderr={tsec['reps'][0]['stderr'].strip()[:90]}")
    t01 = sox_leg("trim_0_0.1", ["-D", "{in}", "{out}", "trim", "0", "0.1"], B)
    if t01["arr"] is not None:
        n = int(np.count_nonzero(np.abs(t01["arr"][:, 0] * 32768.0 - Bi[:4800]) > 0))
        check("trim_is_sample_exact",
              (t01["meta"] or {}).get("frames") == 4800 and n == 0,
              f"frames {(t01['meta'] or {}).get('frames')}; mismatch vs input head {n}",
              {"frames": (t01["meta"] or {}).get("frames"), "mismatch": n},
              {"frames": rleg("sox_trim_r94_probe", "trim_0_0.1")["metrics"]["frames"],
               "mismatch": rleg("sox_trim_r94_probe", "trim_0_0.1")["mismatch_vs_input_head"]})
    t0 = sox_leg("trim_0_0", ["-D", "{in}", "{out}", "trim", "0", "0"], B)
    check("trim_0_0_is_valid_zero_frame",
          t0["rc"] == 0 and (t0["meta"] or {}).get("frames") == 0,
          f"rc={t0['rc']} frames={(t0['meta'] or {}).get('frames')}")

    # ============================================================== fade ===
    f15 = sox_leg("fade_stop_0.15_len_0.1", ["-D", "{in}", "{out}", "fade", "0", "0.15", "0.1"], B)
    f20 = sox_leg("fade_stop_0.2_len_0.05", ["-D", "{in}", "{out}", "fade", "0", "0.2", "0.05"], B)
    check("fade_stop_positional_truncates",
          (f15["meta"] or {}).get("frames") == 7200 and (f20["meta"] or {}).get("frames") == 9600,
          f"fade 0 0.15 0.1 -> {(f15['meta'] or {}).get('frames')} frames; "
          f"fade 0 0.2 0.05 -> {(f20['meta'] or {}).get('frames')} frames (input 12000)",
          {"a": (f15["meta"] or {}).get("frames"), "b": (f20["meta"] or {}).get("frames")},
          {"a": rleg("sox_fade_r94_probe", "fade_stop_0.15_len_0.1")["metrics"]["frames"],
           "b": rleg("sox_fade_r94_probe", "fade_stop_0.2_len_0.05")["metrics"]["frames"]})
    flog = sox_leg("fade_log_100db", ["-D", "{in}", "{out}", "fade", "l", "0.1"], B)
    ratios = {}
    if flog["arr"] is not None:
        for x in (0.5, 0.75, 0.9):
            f_ = int(round(x * 4800))
            ratios[str(x)] = round(float(flog["arr"][f_, 0] * 32768.0 / Bi[f_]), 6)
    want = {str(x): round(10 ** (-5 * (1 - x)), 6) for x in (0.5, 0.75, 0.9)}
    ok = all(ratios.get(k) is not None and
             abs(ratios[k] - want[k]) / want[k] <= 0.03 for k in want)
    check("fade_log_is_100db_per_span", ok,
          f"own out/in {ratios} vs 10^(-5(1-x)) {want}",
          ratios, rleg("sox_fade_r94_probe", "fade_log_100db")["envelope_measured"])
    fdef = sox_leg("fade_default_type", ["-D", "{in}", "{out}", "fade", "0.1"], B)
    check("fade_default_type_is_l", fdef["shas"][0] == flog["shas"][0],
          "`fade 0.1` is byte-identical to `fade l 0.1`")

    # ============================================== repeat / pad / silence ===
    rep2 = sox_leg("repeat_2", ["-D", "{in}", "{out}", "repeat", "2"], B)
    if rep2["arr"] is not None:
        tiled = np.tile(Bi, 3)[:rep2["arr"].shape[0]]
        n = int(np.count_nonzero(np.abs(rep2["arr"][:, 0] * 32768.0 - tiled) > 0))
        check("repeat_2_is_N_additional_copies",
              (rep2["meta"] or {}).get("frames") == 36000 and n == 0,
              f"frames {(rep2['meta'] or {}).get('frames')} (3N); tiling mismatch {n}",
              {"frames": (rep2["meta"] or {}).get("frames"), "mismatch": n},
              {"frames": rleg("sox_repeat_pad_silence_r94_probe", "repeat_2")["metrics"]["frames"],
               "mismatch": rleg("sox_repeat_pad_silence_r94_probe", "repeat_2")["mismatch_vs_tiling"]})
    pad = sox_leg("pad_0.1_0.2", ["-D", "{in}", "{out}", "pad", "0.1", "0.2"], B)
    if pad["arr"] is not None:
        ints = np.rint(pad["arr"][:, 0] * 32768.0).astype("int64")
        nz = np.nonzero(ints)[0]
        check("pad_inserts_at_both_ends",
              (pad["meta"] or {}).get("frames") == 26400 and int(nz[0]) == 4801
              and int(nz[-1]) == 16799,
              f"frames {(pad['meta'] or {}).get('frames')}; first_nonzero {int(nz[0])}; "
              f"last_nonzero {int(nz[-1])}",
              {"frames": (pad["meta"] or {}).get("frames"), "first": int(nz[0]), "last": int(nz[-1])},
              {"frames": rleg("sox_repeat_pad_silence_r94_probe", "pad_0.1_0.2")["metrics"]["frames"],
               "first": rleg("sox_repeat_pad_silence_r94_probe", "pad_0.1_0.2")["first_nonzero_frame"],
               "last": rleg("sox_repeat_pad_silence_r94_probe", "pad_0.1_0.2")["last_nonzero_frame"]})
    sil = sox_leg("silence_above_only", ["-D", "{in}", "{out}", "silence", "1", "0.1", "1%"], C2)
    if sil["arr"] is not None:
        ints = np.rint(sil["arr"][:, 0] * 32768.0).astype("int64")
        trail = 0
        for v in ints[::-1]:
            if v != 0:
                break
            trail += 1
        check("silence_cuts_leading_at_window_lag",
              (sil["meta"] or {}).get("frames") == 21600 - 4804 and trail == 7200,
              f"frames {(sil['meta'] or {}).get('frames')} = 21600-4804; trailing zeros {trail}",
              {"frames": (sil["meta"] or {}).get("frames"), "trail": trail},
              {"frames": rleg("sox_repeat_pad_silence_r94_probe", "silence_above_only")["metrics"]["frames"],
               "trail": rleg("sox_repeat_pad_silence_r94_probe", "silence_above_only")["trailing_zero_frames"]})
    both = sox_leg("silence_both_0.1", ["-D", "{in}", "{out}", "silence", "1", "0.1", "1%",
                                        "1", "0.1", "1%"], C2)
    if both["arr"] is not None:
        ints = np.rint(both["arr"][:, 0] * 32768.0).astype("int64")
        trail = 0
        for v in ints[::-1]:
            if v != 0:
                break
            trail += 1
        check("silence_below_side_keeps_window_minus_1", trail == 959,
              f"trailing zeros {trail} = rate/50 - 1",
              trail, rleg("sox_repeat_pad_silence_r94_probe", "silence_both_0.1")["trailing_zero_frames"])

    # ======================================================= dither / stat ===
    ds = sox_leg("dither_s_R", ["-R", "{in}", "-b", "16", "{out}", "dither", "-s"], F, reps=3)
    if ds["arr"] is not None:
        ints = np.rint(ds["arr"].reshape(-1) * 32768.0)
        want_i = np.rint(f_arr.reshape(-1) * 32768.0)
        n = min(ints.size, want_i.size)
        e = np.abs(ints[:n] - want_i[:n])
        mx, rms = int(e.max()), round(float(np.sqrt((e ** 2).mean())), 6)
        rr = rleg("sox_dither_stat_r94_probe", "dither_s_R")
        check("dither_s_R_envelope", ds["stable"] and mx == rr["max_abs_err"]
              and abs(rms - rr["err_rms"]) < 1e-9,
              f"own max {mx} rms {rms}; receipt max {rr['max_abs_err']} rms {rr['err_rms']}",
              {"max": mx, "rms": rms}, {"max": rr["max_abs_err"], "rms": rr["err_rms"]})
        ref = scout_ref("dither_D.json", "f32_to_s16_dither_s_R")
        check("dither_s_R_equals_scout_bytes",
              ref is not None and ds["shas"][0] == ref["sha"],
              f"own {str(ds['shas'][0])[:16]} vs scout {str(ref and ref['sha'])[:16]}")
    dp = sox_leg("dither_p12_R", ["-R", "{in}", "-b", "16", "{out}", "dither", "-p", "12"], F)
    if dp["arr"] is not None:
        ints = np.rint(dp["arr"].reshape(-1) * 32768.0)
        want_i = np.rint(f_arr.reshape(-1) * 32768.0)
        n = min(ints.size, want_i.size)
        e = np.abs(ints[:n] - want_i[:n])
        rr = rleg("sox_dither_stat_r94_probe", "dither_p12_R")
        check("dither_p12_envelope", int(e.max()) == rr["max_abs_err"]
              and abs(round(float(np.sqrt((e ** 2).mean())), 6) - rr["err_rms"]) < 1e-9,
              f"own max {int(e.max())} rms {round(float(np.sqrt((e ** 2).mean())), 6)}; "
              f"receipt max {rr['max_abs_err']} rms {rr['err_rms']}",
              {"max": int(e.max()), "rms": round(float(np.sqrt((e ** 2).mean())), 6)},
              {"max": rr["max_abs_err"], "rms": rr["err_rms"]})

    # sox `stat` on the 1 s stereo stimulus, cross-computed with own numpy.
    st_txt = run([SOX, str(A), "-n", "stat"])
    txt = st_txt["stderr"]
    def field(pat):
        mm = re.search(pat, txt, re.M)
        return float(mm.group(1)) if mm else None
    got_rms = field(r"^RMS\s+amplitude:\s+(-?[\d.eE+-]+)")
    got_delta = field(r"^Maximum delta:\s+(-?[\d.eE+-]+)")
    got_vol = field(r"^Volume adjustment:\s+(-?[\d.eE+-]+)")
    own_rms = round(float(np.sqrt((ain.reshape(-1) ** 2).mean())), 6)
    inter = Ai.reshape(-1)
    own_delta = round(float(np.abs(np.diff(inter)).max() / 32768.0), 6)
    per_ch_delta = round(float(np.abs(np.diff(Ai, axis=0)).max() / 32768.0), 6)
    rec_stat = rleg("sox_dither_stat_r94_probe", "stat_plain_a")
    check("stat_RMS_is_interleaved_quadratic_mean",
          got_rms is not None and abs(got_rms - own_rms) < 1e-6,
          f"sox printed {got_rms}; own numpy interleaved quadratic mean {own_rms}",
          got_rms, own_rms)
    check("stat_Maximum_delta_is_interleaved",
          got_delta is not None and abs(got_delta - own_delta) < 1e-6 and own_delta != per_ch_delta,
          f"sox printed {got_delta}; own interleaved max|diff| {own_delta} "
          f"(per-channel would be {per_ch_delta})", got_delta,
          {"interleaved": own_delta, "per_channel": per_ch_delta})
    check("stat_Volume_adjustment", got_vol == 2.0, f"sox printed {got_vol} (1/peak 0.5)")

    freq_txt = run([SOX, str(A), "-n", "stat", "-freq"])["stderr"]
    nums = [ln for ln in freq_txt.splitlines() if re.match(r"^\s*[\d.]+\s+[\d.]+\s*$", ln)]
    freqs = [float(ln.split()[0]) for ln in nums]
    step = round(freqs[1] - freqs[0], 6) if len(freqs) > 1 else None
    samples = int(re.search(r"Samples read:\s+(\d+)", freq_txt).group(1))
    n_spec = -(-samples // 4096)
    rec_freq = rleg("sox_dither_stat_r94_probe", "stat_freq_a")
    check("stat_freq_line_law",
          step == round(48000 / 4096.0, 6) and len(nums) == 2048 * n_spec,
          f"own {len(nums)} numeric lines = 2048*{n_spec} (samples {samples}), step {step} Hz; "
          f"receipt {rec_freq['numeric_lines']} lines step {rec_freq['step_hz']}",
          {"lines": len(nums), "step": step, "spectra": n_spec},
          {"lines": rec_freq["numeric_lines"], "step": rec_freq["step_hz"],
           "spectra": rec_freq["spectra_expected"]})

    OUT["legs"] = {k: {kk: vv for kk, vv in v.items() if kk not in ("arr",)}
                   for k, v in {
                       **{l["name"]: l for l in (g_def, g_d, gm6, va, vd, vp, ch1, ch2, r1, auto,
                                                 ch1_leg, mm, r01, t1, t4800, tsec, t01, t0, f15,
                                                 f20, flog, fdef, rep2, pad, sil, both, ds, dp)},
                       **{k: v for k, v in al.items()}}.items()}
    OUT["failed"] = FAILED
    (ROOT / "live" / "r94-reviewer" / "r94r_spotcheck.json").write_text(
        json.dumps(OUT, indent=1, default=str))
    print(f"\n=== {len(OUT['checks'])} checks, {len(FAILED)} failed ===")
    for f in FAILED:
        print("FAILED:", f)
    return 0


if __name__ == "__main__":
    sys.exit(main())
