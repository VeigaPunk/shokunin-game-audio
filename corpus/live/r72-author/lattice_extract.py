#!/usr/bin/env python3
"""r72 3-decoder lattice, derived by THIS seat from committed receipts.

sox    : newest transport_<member>_r6{7,8,9}_probe receipt per member
         (accept = exit_code==0 and samples_read>0)
ffmpeg : newest *-ffprobe-transport-r71 receipt, ffprobe_<m>_r71_probe
         (accept = ffmpeg_exit==0)
sndfile: this seat's fresh *-sndfile-transport-r72 receipt,
         sndfile_<m>_r72_probe (accept = read_frames is not None and >0)

Arm order f/p/r/q = file, stdin_pipe, redirected_fd, fifo_path.
"""
import json, re
from pathlib import Path

RUNS = Path("/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/runs")
ARMS = ("file", "stdin_pipe", "redirected_fd", "fifo_path")
MEMBERS = ["dec_act", "dec_hcom", "posttable_nomatch", "txw_piperefuse",
           "extsuffix_wav", "extsuffix_bin", "extsuffix_txw",
           "extsuffix_f32", "extsuffix_snd"]

# member -> sox receipt mode suffix
SOX_SUFFIX = {
    "dec_act": "transport-dec-act-r67",
    "dec_hcom": "transport-dec-hcom-r67",
    "posttable_nomatch": "transport-posttable-nomatch-r68",
    "txw_piperefuse": "transport-txw-piperefuse-r68",
    "extsuffix_wav": "transport-extsuffix-wav-r69",
    "extsuffix_bin": "transport-extsuffix-bin-r69",
    "extsuffix_txw": "transport-extsuffix-txw-r69",
    "extsuffix_f32": "transport-extsuffix-f32-r69",
    "extsuffix_snd": "transport-extsuffix-snd-r69",
}


def newest(suffix):
    cands = sorted(d for d in RUNS.iterdir() if d.name.endswith("Z-" + suffix))
    assert cands, suffix
    rec = cands[-1] / "measurements.json"
    return rec, json.load(open(rec))


def vec_sox(member):
    rec, d = newest(SOX_SUFFIX[member])
    e = d["measurements"][f"transport_{member}_{SOX_SUFFIX[member][-3:] if False else ''}" +
                        ""] if False else None
    # find the transport_<member>_r6X_probe key
    key = next(k for k in d["measurements"]
               if k.startswith(f"transport_{member}_"))
    e = d["measurements"][key]
    v = "".join("Y" if (e["transport_axis"][t]["exit_code"] == 0 and
                        (e["transport_axis"][t]["samples_read"] or 0) > 0)
                else "." for t in ARMS)
    return v, rec, key


def vec_ffmpeg(member):
    rec, d = newest("ffprobe-transport-r71")
    e = d["measurements"][f"ffprobe_{member}_r71_probe"]
    v = "".join("Y" if e["transport_axis"][t]["ffmpeg_exit"] == 0
                else "." for t in ARMS)
    return v, rec


def vec_sndfile(member):
    rec, d = newest("sndfile-transport-r72")
    e = d["measurements"][f"sndfile_{member}_r72_probe"]
    v = "".join("Y" if (e["transport_axis"][t]["read_frames"] or 0) > 0
                else "." for t in ARMS)
    return v, rec


def main():
    print(f"{'member':<18}| {'sox':<28}| {'ffmpeg':<28}| {'sndfile':<28}")
    print(f"{'':<18}| {'f  p  r  q':<28}| {'f  p  r  q':<28}| {'f  p  r  q':<28}")
    classes = {}
    for m in MEMBERS:
        sv, srec, skey = vec_sox(m)
        fv, frec = vec_ffmpeg(m)
        nv, nrec = vec_sndfile(m)
        fmt = lambda v: "  ".join(v)
        print(f"{m:<18}| {fmt(sv):<28}| {fmt(fv):<28}| {fmt(nv):<28}")
        classes.setdefault((sv, fv, nv), []).append(m)
    print("\nclasses (sox|ffmpeg|sndfile arm-vectors):")
    for k, v in sorted(classes.items()):
        print("  ", k, v)
    print("\nmember-level (accept-any-arm):")
    ml = {}
    for m in MEMBERS:
        sv, _, _ = vec_sox(m); fv, _ = vec_ffmpeg(m); nv, _ = vec_sndfile(m)
        ml.setdefault(("Y" in sv, "Y" in fv, "Y" in nv), []).append(m)
    for k, v in sorted(ml.items()):
        print("  ", k, v)
    # provenance
    print("\nsources:")
    seen = set()
    for m in MEMBERS:
        for _, rec, *_ in (vec_sox(m), vec_ffmpeg(m), vec_sndfile(m)):
            r = rec if isinstance(rec, Path) else rec[0] if isinstance(rec, tuple) else rec
    for m in MEMBERS:
        sv, srec, _ = vec_sox(m); fv, frec = vec_ffmpeg(m); nv, nrec = vec_sndfile(m)
        for r in (srec, frec, nrec):
            seen.add(str(r))
    for s in sorted(seen):
        print("  ", s)


if __name__ == "__main__":
    main()
