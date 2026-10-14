#!/usr/bin/env python3
"""r72-scout: 3-decoder verdict lattice over the canonical 9-member x
4-transport corpus.

Inputs (all read-only / scratch):
  prior-verdicts.json   sox committed receipts + r71 ffmpeg receipt
  runs/sndfile-matrix-run1.json   this seat's libsndfile measurement

Acceptance predicates (per decoder, per member x transport cell):
  sox      accept  = exit_code == 0 and samples_read not None
  ffmpeg   accept  = ffmpeg_exit == 0        (ffprobe_format is the detect)
  sndfile  accept  = opened and read_frames > 0
Detection predicates:
  sox      detected = sox_detected_format is not None
  ffmpeg   detected = ffprobe_format is not None
  sndfile  detected = opened is True
Extra sndfile tier: error == 'File contains data in an unimplemented format.'
  (magic recognized, no reader compiled) -> classify 'recognized_refused'.

Emits lattice.json / lattice.tsv and the per-decoder accept/detect cell sets
+ exclusive-class checks for the wave claim.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
TRANSPORTS = ("file", "stdin_pipe", "redirected_fd", "fifo_path")
ARM_ATTR = {"file": "named+seekable", "stdin_pipe": "anon+pipe",
            "redirected_fd": "anon+seekable", "fifo_path": "named+pipe"}

CLAIM = {
    "sox_only": "txw-seekable {file, redirected_fd} + .f32-named {file, fifo_path}",
    "sndfile_only": ".snd-named {file, fifo_path}",
    "ffmpeg": "superset on detect",
}


def verdicts():
    prior = json.loads((HERE / "prior-verdicts.json").read_text())
    snd = json.loads((HERE / "runs" / "sndfile-matrix-run1.json").read_text())
    rows = {}
    for member, p in prior["members"].items():
        rows[member] = {}
        for t in TRANSPORTS:
            sa = p["sox_arms"][t]
            fa = p["ffmpeg_arms"][t]
            na = snd["members"][member]["transport_axis"][t]
            rows[member][t] = {
                "sox_detect": sa["sox_detected_format"],
                "sox_accept": bool(sa["exit_code"] == 0
                                   and sa["samples_read"] is not None),
                "sox_exit": sa["exit_code"],
                "sox_samples": sa["samples_read"],
                "sox_error": sa["error"],
                "ffmpeg_detect": fa["ffprobe_format"],
                "ffmpeg_accept": fa["ffmpeg_exit"] == 0,
                "ffmpeg_exit": fa["ffmpeg_exit"],
                "sndfile_detect": bool(na["opened"]),
                "sndfile_accept": bool(na["opened"]
                                       and (na.get("read_frames") or 0) > 0),
                "sndfile_format": na.get("format_name"),
                "sndfile_read": na.get("read_frames"),
                "sndfile_error": None if na.get("error") in (None, "No Error.")
                else na.get("error"),
            }
    return rows


def cell_class(v):
    acc = tuple(name for name in ("sox", "ffmpeg", "sndfile")
                if v[f"{name}_accept"])
    if v["sndfile_error"] == "File contains data in an unimplemented format.":
        acc = acc + ("sndfile_refused",)
    return acc


def main():
    rows = verdicts()
    out = {"claim": CLAIM, "cells": {}, "classes": {},
           "accept_sets": {}, "detect_sets": {}, "checks": {}}
    class_map = {}
    for member, arms in rows.items():
        out["cells"][member] = {}
        for t, v in arms.items():
            cls = cell_class(v)
            out["cells"][member][t] = {**v, "accept_class": list(cls)}
            class_map.setdefault(cls, []).append(f"{member}/{t}")
    for cls, cells in sorted(class_map.items()):
        out["classes"]["+".join(cls) if cls else "none"] = cells

    def accept_cells(name):
        return {f"{m}/{t}" for m, arms in rows.items() for t, v in arms.items()
                if v[f"{name}_accept"]}

    def detect_cells(name):
        return {f"{m}/{t}" for m, arms in rows.items() for t, v in arms.items()
                if v[f"{name}_detect"]}

    sox_a, ff_a, sf_a = accept_cells("sox"), accept_cells("ffmpeg"), accept_cells("sndfile")
    sox_d, ff_d, sf_d = detect_cells("sox"), detect_cells("ffmpeg"), detect_cells("sndfile")
    out["accept_sets"] = {"sox": sorted(sox_a), "ffmpeg": sorted(ff_a),
                          "sndfile": sorted(sf_a),
                          "sox_only": sorted(sox_a - ff_a - sf_a),
                          "ffmpeg_only": sorted(ff_a - sox_a - sf_a),
                          "sndfile_only": sorted(sf_a - sox_a - ff_a),
                          "all_three": sorted(sox_a & ff_a & sf_a),
                          "none": sorted({f"{m}/{t}" for m in rows for t in TRANSPORTS}
                                         - sox_a - ff_a - sf_a)}
    out["detect_sets"] = {"sox": sorted(sox_d), "ffmpeg": sorted(ff_d),
                          "sndfile": sorted(sf_d),
                          "sox_only": sorted(sox_d - ff_d - sf_d),
                          "ffmpeg_only": sorted(ff_d - sox_d - sf_d),
                          "sndfile_only": sorted(sf_d - sox_d - ff_d),
                          "ffmpeg_subset_of_sndfile": ff_d <= sf_d,
                          "ffmpeg_subset_of_sox": ff_d <= sox_d,
                          "sndfile_subset_of_ffmpeg": sf_d <= ff_d,
                          "sndfile_subset_of_sox": sf_d <= sox_d}
    checks = {}
    checks["sox_only_cells"] = sorted(sox_a - ff_a - sf_a)
    checks["sox_only_matches_claim"] = (
        checks["sox_only_cells"] == sorted(
            [f"txw_piperefuse/{t}" for t in ("file", "redirected_fd")]
            + [f"extsuffix_f32/{t}" for t in ("file", "fifo_path")]))
    checks["sndfile_only_cells"] = sorted(sf_a - sox_a - ff_a)
    checks["sndfile_only_matches_claim"] = (
        checks["sndfile_only_cells"] == sorted(
            [f"extsuffix_snd/{t}" for t in ("file", "fifo_path")]))
    checks["sndfile_named_cells_ffmpeg_rejects"] = sorted(
        [f"extsuffix_snd/{t}" for t in ("file", "fifo_path") if
         f"extsuffix_snd/{t}" in sf_a and f"extsuffix_snd/{t}" not in ff_a])
    checks["sndfile_named_cells_sox_accepts_too"] = sorted(
        [f"extsuffix_snd/{t}" for t in ("file", "fifo_path") if
         f"extsuffix_snd/{t}" in sf_a and f"extsuffix_snd/{t}" in sox_a])
    checks["ffmpeg_only_accept_cells"] = sorted(ff_a - sox_a - sf_a)
    checks["ffmpeg_detect_is_superset_of"] = {
        "sox": ff_d >= sox_d, "sndfile": ff_d >= sf_d}
    checks["ffmpeg_detect_subset_of"] = {
        "sox": ff_d <= sox_d, "sndfile": ff_d <= sf_d}
    out["checks"] = checks

    (HERE / "lattice.json").write_text(json.dumps(out, indent=1) + "\n")
    # tsv
    tsv = ["member\ttransport\tarm\tsox_detect\tsox_accept\tsox_samples\tffmpeg_detect\tffmpeg_accept\tsndfile_detect\tsndfile_format\tsndfile_read\tsndfile_error\taccept_class"]
    for m, arms in rows.items():
        for t, v in arms.items():
            tsv.append("\t".join(str(x) for x in (
                m, t, ARM_ATTR[t], v["sox_detect"] or "", v["sox_accept"],
                v["sox_samples"] if v["sox_samples"] is not None else "",
                v["ffmpeg_detect"] or "", v["ffmpeg_accept"],
                v["sndfile_detect"], v["sndfile_format"] or "",
                v["sndfile_read"] if v["sndfile_read"] is not None else "",
                v["sndfile_error"] or "", "+".join(cell_class(v)) or "none")))
    (HERE / "lattice.tsv").write_text("\n".join(tsv) + "\n")
    print(json.dumps(out["checks"], indent=1))
    print("\nexclusive accept classes:")
    for cls, cells in sorted(out["classes"].items()):
        print(f"  {cls:42s} {len(cells):2d}  {', '.join(cells)}")


if __name__ == "__main__":
    main()
