#!/usr/bin/env python3
"""r72-scout: cross-check this seat's measurements against the frontier
seat's independent artifacts (corpus/live/frontier-sndfile/).

  1. sndfile cells: runs/sndfile-matrix-run1.json vs frontier
     runs/sndfile-matrix.json (frontier key 'posttable' == 'posttable_nomatch')
     -- two harnesses: this seat's child-process leg vs frontier's in-process
     direct ctypes.
  2. sox+ffmpeg rows: prior-verdicts.tsv vs frontier runs/prior-verdicts.tsv
     -- independent receipt extraction (frontier cites earlier runs of the
     same modes; values must be identical = byte-stable mode receipts).

Writes crosscheck.json.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FRONTIER = ROOT / "corpus" / "live" / "frontier-sndfile"
TRANSPORTS = ("file", "stdin_pipe", "redirected_fd", "fifo_path")
FIELDS = ("format_name", "read_frames", "frames", "samplerate", "channels",
          "sf_seekable")


def norm(err):
    return None if err in (None, "No Error.") else err


def sndfile_cells():
    mine = json.loads((HERE / "runs" / "sndfile-matrix-run1.json").read_text())
    front = json.loads((FRONTIER / "runs" / "sndfile-matrix.json").read_text())
    diffs, checked = [], 0
    for member, e in mine["members"].items():
        fkey = "posttable" if member == "posttable_nomatch" else member
        for t in TRANSPORTS:
            a = e["transport_axis"][t]
            b = front[fkey]["arms"][t]
            checked += 1
            for f in FIELDS:
                if a.get(f) != b.get(f):
                    diffs.append({"member": member, "transport": t, "field": f,
                                  "mine": a.get(f), "frontier": b.get(f)})
            if norm(a.get("error")) != norm(b.get("error")):
                diffs.append({"member": member, "transport": t, "field": "error",
                              "mine": norm(a.get("error")),
                              "frontier": norm(b.get("error"))})
    return {"cells_checked": checked, "diffs": diffs}


def prior_rows():
    """sox + ffmpeg per member x transport: this seat's receipt extraction
    (prior-verdicts.json) vs the frontier seat's prior-verdicts.tsv."""
    def read_front():
        rows = {}
        for line in (FRONTIER / "runs" / "prior-verdicts.tsv").read_text().splitlines()[1:]:
            f = line.split("\t")
            member = "posttable_nomatch" if f[0] == "posttable" else f[0]
            rows[(member, f[1], f[2])] = {
                "detected": f[3] if f[3] != "None" else None,
                "exit": f[4] if f[4] != "None" else None,
                "samples": f[5] if f[5] not in ("None", "-") else None,
                "error": f[7] if f[7] != "None" else None}
        return rows

    mine_json = json.loads((HERE / "prior-verdicts.json").read_text())
    mine = {}
    for member, e in mine_json["members"].items():
        for t, a in e["sox_arms"].items():
            mine[(member, "sox", t)] = {
                "detected": a["sox_detected_format"], "exit": str(a["exit_code"]),
                "samples": None if a["samples_read"] is None else str(a["samples_read"]),
                "error": a["error"]}
        for t, a in e["ffmpeg_arms"].items():
            mine[(member, "ffmpeg", t)] = {
                "detected": a["ffprobe_format"], "exit": str(a["ffmpeg_exit"]),
                "samples": None, "error": a["ffmpeg_error"]}
    front = read_front()
    diffs = []
    for key in sorted(set(mine) & set(front)):
        for f in ("detected", "exit", "samples", "error"):
            a, b = mine[key][f], front[key][f]
            if a != b:
                diffs.append({"key": key, "field": f, "mine": a,
                              "frontier": b})
    return {"rows_checked": len(set(mine) & set(front)),
            "keys_only_mine": sorted(set(mine) - set(front)),
            "keys_only_frontier": sorted(set(front) - set(mine)),
            "diffs": diffs}


def main():
    out = {"sndfile_cells": sndfile_cells(), "prior_rows": prior_rows()}
    (HERE / "crosscheck.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
