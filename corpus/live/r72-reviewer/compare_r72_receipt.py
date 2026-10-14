#!/usr/bin/env python3
"""r72-reviewer: diff the author's sndfile_*_r72_probe receipt against the
reviewer's independent libsndfile measurement.

Usage: compare_r72_receipt.py <path/to/measurements.json> [more receipts...]

Decisive axes per member x arm:
  accept/reject        (format present & read > 0  vs  open failure)
  read_frames          (decoded frame count; NOT the SF_INFO size estimate)
  error string         (reject reason)

Prints a per-cell table of author-vs-reviewer, then a verdict summary.
"""
import json, sys
from pathlib import Path

ARMS = ("file", "stdin_pipe", "redirected_fd", "fifo_path")
MINE = Path("corpus/live/r72-reviewer/sndfile-matrix.json")


def load_mine():
    d = json.load(open(MINE))
    return {m: v["arms"] for m, v in d["members"].items()}


def pick(entry, keys):
    """First present key wins; returns (value, keyname)."""
    for k in keys:
        if k in entry:
            return entry[k], k
    return None, None


def main(argv):
    mine = load_mine()
    rows = []
    for p in argv:
        d = json.load(open(p))
        for key, entry in d.get("measurements", {}).items():
            if not (key.startswith("sndfile_") and key.endswith("_r72_probe")):
                continue
            member = key[len("sndfile_"):-len("_r72_probe")]
            axis = entry.get("transport_axis") or entry.get("arms") or {}
            for arm in ARMS:
                a = axis.get(arm, {})
                m = mine.get(member, {}).get(arm, {})
                got_fmt, kf = pick(a, ("sndfile_format_name", "format_name", "sndfile_format", "format"))
                got_read, kr = pick(a, ("read_frames", "sndfile_read_frames", "frames_read"))
                got_frames, kg = pick(a, ("frames", "sndfile_frames", "sf_info_frames"))
                got_err, ke = pick(a, ("error", "sndfile_error", "sf_error", "reason"))
                my_accept = m.get("format_name") is not None and (m.get("read_frames") or 0) > 0
                auth_accept = got_fmt is not None and (got_read if isinstance(got_read, int) else 0) > 0
                rows.append({
                    "receipt": p, "key": key, "member": member, "arm": arm,
                    "auth_fmt": got_fmt, "auth_read": got_read, "auth_frames": got_frames,
                    "auth_err": got_err,
                    "my_fmt": m.get("format_name"), "my_read": m.get("read_frames"),
                    "my_frames": m.get("frames"), "my_err": m.get("error"),
                    "agree": (my_accept == auth_accept) and (
                        (not my_accept) or (got_read == m.get("read_frames"))),
                    "keys": (kf, kr, kg, ke),
                })
    print("member\tarm\tauthor(fmt/read/frames|err)\treviewer(fmt/read/frames|err)\tagree")
    for r in rows:
        print(f"{r['member']}\t{r['arm']}\t"
              f"{r['auth_fmt']}/{r['auth_read']}/{r['auth_frames']}|{r['auth_err']}\t"
              f"{r['my_fmt']}/{r['my_read']}/{r['my_frames']}|{r['my_err']}\t"
              f"{'OK' if r['agree'] else 'DIFF'}")
    bad = [r for r in rows if not r["agree"]]
    print(f"\ncells={len(rows)} agree={len(rows)-len(bad)} diff={len(bad)}")
    for r in bad:
        print("  DIFF", r["member"], r["arm"], "author:", r["auth_fmt"], r["auth_read"],
              r["auth_err"], "| reviewer:", r["my_fmt"], r["my_read"], r["my_err"],
              "| keys:", r["keys"])
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
