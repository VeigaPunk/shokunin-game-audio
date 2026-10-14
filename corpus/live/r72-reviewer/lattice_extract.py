#!/usr/bin/env python3
"""r72-reviewer: extract the committed sox (r67/r68/r69 transport) and ffmpeg
(r71 ffprobe) per-arm verdicts for the 9 canonical members, so the 3-decoder
lattice can be checked against committed receipts rather than re-derived.

Read-only over corpus/live/runs/*/measurements.json. Latest receipt per mode
wins (lexicographic timestamp in the run dir name).
"""
import glob, json, os, sys

MEMBER_MODES = {
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
ARMS = ("file", "stdin_pipe", "redirected_fd", "fifo_path")


def latest(mode):
    runs = sorted(glob.glob(f"corpus/live/runs/*-{mode}/measurements.json"))
    return runs[-1] if runs else None


def sox_rows():
    out = {}
    for member, mode in MEMBER_MODES.items():
        p = latest(mode)
        d = json.load(open(p))
        key = [k for k in d["measurements"] if k.endswith("_probe")][0]
        entry = d["measurements"][key]
        out[member] = {"receipt": p, "key": key,
                       "arms": {a: {k: entry["transport_axis"][a][k] for k in
                                    ("sox_detected_format", "sox_route", "exit_code",
                                     "samples_read", "error")} for a in ARMS},
                       "fork": entry["transport_fork"]}
    return out


def ffmpeg_rows():
    p = latest("ffprobe-transport-r71")
    d = json.load(open(p))
    out = {}
    for k, entry in d["measurements"].items():
        if not (k.startswith("ffprobe_") and k.endswith("_r71_probe")):
            continue
        member = k[len("ffprobe_"):-len("_r71_probe")]
        out[member] = {"receipt": p,
                       "arms": {a: {kk: entry["transport_axis"][a][kk] for kk in
                                    ("ffprobe_format", "probe_score", "ffprobe_exit",
                                     "ffmpeg_exit", "ffmpeg_error")} for a in ARMS},
                       "fork": entry["transport_fork"]}
    return out


def sndfile_rows():
    p = "corpus/live/r72-reviewer/sndfile-matrix.json"
    d = json.load(open(p))
    out = {}
    for member, v in d["members"].items():
        name = {"posttable": "posttable_nomatch"}.get(member, member)
        out[name] = {"receipt": p,
                     "arms": {a: {kk: v["arms"][a][kk] for kk in
                                  ("format_name", "frames", "read_frames", "error")}
                              for a in ARMS}}
    return out


def main():
    sox, ff, sf = sox_rows(), ffmpeg_rows(), sndfile_rows()
    print("member\tarm\tsox(det/exit/samples|err)\tffmpeg(fmt/probe_exit/dec_exit|err)\tlibsndfile(fmt/frames/read|err)")
    for member in MEMBER_MODES:
        for a in ARMS:
            s = sox[member]["arms"][a]
            f = ff[member]["arms"][a]
            g = sf[member]["arms"][a]
            print("\t".join([
                member, a,
                f"{s['sox_detected_format'] or '-'}/{s['exit_code']}/{s['samples_read'] if s['samples_read'] is not None else '-'}|{s['error'] or 'ok'}",
                f"{f['ffprobe_format'] or '-'}/{f['ffprobe_exit']}/{f['ffmpeg_exit']}|{f['ffmpeg_error'] or 'ok'}",
                f"{g['format_name'] or '-'}/{g['frames']}/{g['read_frames']}|{g['error'] or 'ok'}",
            ]))
    print("\n# receipts")
    for member in MEMBER_MODES:
        print(f"# {member}: sox={sox[member]['receipt']} ({sox[member]['key']}) "
              f"ffmpeg={ff[member]['receipt']}")


if __name__ == "__main__":
    main()
