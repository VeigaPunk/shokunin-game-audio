#!/usr/bin/env python3
"""r72-boundary edge probes for the libsndfile transport arm.

probe-a  fifo writer-hold sweep (dec_act + extsuffix_snd, holds x reps):
         does libsndfile-on-fifo have a writer-hold verdict band like the
         sox ffmpeg bridge (r70) / a flat profile like direct ffmpeg (r71)?
probe-b  truncation sweep on named file arm: min-prefix verdict cliffs for
         dec_act (RIFF/WAVE), txw_piperefuse (LM8953), extsuffix_snd
         (no-magic .snd fallback), extsuffix_f32 (no-fallback control).
probe-c  extension-case sweep: does the post-sniff fallback fire on .SND /
         .Snd / .GSM / .AU / .VOX etc. (frontier left case unmeasured)?
probe-d  read-exhaust on the .snd file arm: info.frames=512 vs first
         sf_readf_short=500 — where do the 12 frames go?

Results: edge_results_probe-{a,b,c,d}.json in this directory.
"""
import json
import os
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import probe_sndfile_r72 as P  # noqa: E402

CORPUS = P.CORPUS
SND_BYTES = (CORPUS / "live" / "round-69" / "extsuffix_nomatch.snd").read_bytes()
SND_MEMBER = CORPUS / "live" / "round-69" / "extsuffix_nomatch.snd"
ACT_MEMBER = CORPUS / "live" / "round-66" / "pair_dec_act.wav"
TXW_MEMBER = CORPUS / "live" / "round-68" / "txw_piperefuse.wav"
F32_MEMBER = CORPUS / "live" / "round-69" / "extsuffix_nomatch.f32"
HOLDS = (0.0, 0.05, 0.2, 0.5, 1.0)
REPS = 5


def sig(a):
    return (a["format_name"], a["read_frames"], a["error"])


def probe_a():
    out = {"probe": "a: fifo writer-hold sweep", "holds_s": list(HOLDS),
           "reps_per_hold": REPS, "members": {}}
    for member, path in (("dec_act", ACT_MEMBER), ("extsuffix_snd", SND_MEMBER)):
        data = path.read_bytes()
        cells = []
        for hold in HOLDS:
            reps = []
            for rep in range(REPS):
                t0 = time.monotonic()
                a = P.bounded(P.arm_fifo, path, data, hold)
                reps.append({"rep": rep, "verdict": sig(a),
                             "frames": a["frames"], "sf_seekable": a["sf_seekable"],
                             "elapsed_s": round(time.monotonic() - t0, 3)})
            dist = {}
            for r in reps:
                k = json.dumps(r["verdict"])
                dist[k] = dist.get(k, 0) + 1
            cells.append({"fifo_writer_hold_s": hold,
                          "reps": reps,
                          "verdict_distribution": [
                              {"signature": json.loads(k), "count": c}
                              for k, c in sorted(dist.items(), key=lambda kv: -kv[1])]})
        out["members"][member] = {"path": str(path.relative_to(CORPUS)),
                                  "hold_cells": cells}
    return out


def probe_b():
    sizes = (0, 1, 4, 6, 8, 12, 16, 32, 44, 64, 100, 128, 157, 158, 200, 256,
             300, 400, 512, 600)
    out = {"probe": "b: truncation sweep (named file arm, basename preserved)",
           "members": {}}
    for member, path in (("dec_act", ACT_MEMBER), ("txw_piperefuse", TXW_MEMBER),
                         ("extsuffix_snd", SND_MEMBER), ("extsuffix_f32", F32_MEMBER)):
        data = path.read_bytes()
        rows = []
        with tempfile.TemporaryDirectory(prefix="sndfile-r72-trunc-") as tmp:
            tpath = Path(tmp) / path.name
            for n in sorted({*sizes, len(data)}):
                if n > len(data):
                    continue
                tpath.write_bytes(data[:n])
                a = P.bounded(P.arm_file, tpath)
                rows.append({"prefix_bytes": n, "verdict": sig(a),
                             "frames": a["frames"], "samplerate": a["samplerate"],
                             "channels": a["channels"]})
        out["members"][member] = {"path": str(path.relative_to(CORPUS)),
                                  "file_bytes": len(data), "rows": rows}
    return out


def probe_c():
    """Extension-case sweep on identical no-magic bytes (512 B), plus a
    RIFF-content control under two case variants (content precedence)."""
    names = (".snd", ".SND", ".Snd", ".sND", ".au", ".AU", ".Au",
             ".gsm", ".GSM", ".vox", ".VOX", ".Vox", ".wav", ".f32",
             ".ulaw", ".ULAW")
    riff = (CORPUS / "live" / "round-66" / "pair_dec_act.wav").read_bytes()
    rows = []
    with tempfile.TemporaryDirectory(prefix="sndfile-r72-extcase-") as tmp:
        for ext in names:
            p = Path(tmp) / ("member" + ext)
            p.write_bytes(SND_BYTES)
            a = P.bounded(P.arm_file, p)
            rows.append({"ext": ext, "content": "no-magic-512", "verdict": sig(a),
                         "frames": a["frames"], "samplerate": a["samplerate"]})
        for ext in (".snd", ".SND", ".wav"):
            p = Path(tmp) / ("riff" + ext)
            p.write_bytes(riff)
            a = P.bounded(P.arm_file, p)
            rows.append({"ext": ext, "content": "riff-600", "verdict": sig(a),
                         "frames": a["frames"], "samplerate": a["samplerate"]})
    return {"probe": "c: extension-case sweep", "rows": rows}


def probe_d():
    """Read-exhaust: repeated sf_readf_short until 0 on the .snd file arm."""
    import ctypes
    out = {"probe": "d: read-exhaust on extsuffix_nomatch.snd (file arm)",
           "rows": []}
    for member, path in (("extsuffix_snd", SND_MEMBER),
                         ("dec_act", ACT_MEMBER)):
        info = P.SF_INFO()
        snd = P.LIB.sf_open(os.fsencode(str(path)), P.SFM_READ, ctypes.byref(info))
        if not snd:
            out["rows"].append({"member": member, "error": "open failed"})
            continue
        counts = []
        buf = (ctypes.c_short * 4096)()
        for _ in range(10):
            n = P.LIB.sf_readf_short(snd, buf, 4096)
            counts.append(n)
            if n == 0:
                break
        P.LIB.sf_close(snd)
        out["rows"].append({"member": member,
                            "info_frames": info.frames,
                            "read_counts": counts,
                            "total_read": sum(counts)})
    return out


def probe_e():
    """Refinements found by probe-b/c/d:
    e1: exact tier onsets 8..13 B (dec_act WAV tier, txw LM8953 tier)
    e2: .snd ULAW fallback reader offset test — is the first sample read
        from byte 0 or byte 12? (probe-b showed read = N-12, N>=16)
    """
    import ctypes
    out = {"probe": "e: tier onsets + fallback offset", "e1_tier_onsets": {},
           "e2_offset_test": {}}
    for member, path, sizes in (
            ("dec_act", ACT_MEMBER, (8, 9, 10, 11, 12, 13)),
            ("txw_piperefuse", TXW_MEMBER, (8, 9, 10, 11, 12, 13))):
        data = path.read_bytes()
        rows = []
        with tempfile.TemporaryDirectory(prefix="sndfile-r72-ons-") as tmp:
            tpath = Path(tmp) / path.name
            for n in sizes:
                tpath.write_bytes(data[:n])
                a = P.bounded(P.arm_file, tpath)
                rows.append({"prefix_bytes": n, "verdict": sig(a)})
        out["e1_tier_onsets"][member] = rows

    # e2: 16-byte .snd files, first 12 bytes differ, last 4 identical.
    variants = {
        "first12=0x00,last4=0xAA": bytes([0x00] * 12) + bytes([0xAA] * 4),
        "first12=0xFF,last4=0xAA": bytes([0xFF] * 12) + bytes([0xAA] * 4),
        "first12=0x00,last4=0x00": bytes([0x00] * 12) + bytes([0x00] * 4),
    }
    with tempfile.TemporaryDirectory(prefix="sndfile-r72-off-") as tmp:
        for label, data in variants.items():
            p = Path(tmp) / "probe.snd"
            p.write_bytes(data)
            info = P.SF_INFO()
            snd = P.LIB.sf_open(os.fsencode(str(p)), P.SFM_READ, ctypes.byref(info))
            if not snd:
                out["e2_offset_test"][label] = {"error": "open failed"}
                continue
            buf = (ctypes.c_short * 8)()
            n = P.LIB.sf_readf_short(snd, buf, 8)
            samples = [buf[i] for i in range(n)]
            n2 = P.LIB.sf_readf_short(snd, buf, 8)
            P.LIB.sf_close(snd)
            out["e2_offset_test"][label] = {
                "bytes": data.hex(), "info_frames": info.frames,
                "read_counts": [n, n2], "samples": samples}
    return out


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    fns = {"a": probe_a, "b": probe_b, "c": probe_c, "d": probe_d, "e": probe_e}
    for key, fn in fns.items():
        if which not in (key, "all"):
            continue
        result = fn()
        out = HERE / f"edge_results_probe-{key}.json"
        out.write_text(json.dumps(result, indent=1) + "\n")
        print(f"{out} written", file=sys.stderr)


if __name__ == "__main__":
    main()
