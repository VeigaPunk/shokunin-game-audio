#!/usr/bin/env python3
"""r73 reviewer: extract the *decoder-axis* rows for the hcom member from committed
receipts (sox r67, ffmpeg r71, libsndfile r72) so the consumer claim's
"opposite polarity" comparison is against measured decoder rows, not prose."""
import glob
import json
import os

REPO = os.path.expanduser("~/Projects/shokunin/audio-shokunin")
RUNS = os.path.join(REPO, "corpus/live/runs")


def latest(pat):
    ds = sorted(glob.glob(os.path.join(RUNS, pat)))
    return ds[-1] if ds else None


def entries(path):
    d = json.load(open(os.path.join(path, "measurements.json")))
    return d["measurements"]


def show(label, runpat, key_contains, fields):
    run = latest(runpat)
    print(f"\n== {label}  ({os.path.basename(run) if run else 'MISSING'})")
    if not run:
        return
    for name, e in entries(run).items():
        if key_contains not in name:
            continue
        axis = e.get("transport_axis") or {}
        print(f"   {name}: fork={e.get('transport_fork')} protocol={e.get('transport_protocol')}")
        for t, arm in axis.items():
            row = {f: arm.get(f) for f in fields}
            print(f"     {t:14s} named={arm.get('named')} seekable={arm.get('seekable')} {row}")


show("sox r67 (dec_hcom)", "*transport-dec-hcom-r67", "dec_hcom",
     ["sox_detected_format", "sox_route", "exit_code", "samples_read", "error"])
show("ffmpeg r71 (dec_hcom)", "*ffprobe-transport-r71", "dec_hcom",
     ["ffprobe_format", "probe_score", "ffprobe_exit", "ffmpeg_exit", "ffmpeg_error"])
show("libsndfile r72 (dec_hcom)", "*sndfile-transport-r72", "dec_hcom",
     ["format_name", "read_frames", "frames", "error"])

# and the txw / extsuffix members for the same polarity question
show("sox r68 (txw_piperefuse)", "*transport-txw-piperefuse-r68", "txw",
     ["sox_detected_format", "sox_route", "exit_code", "samples_read", "error"])
show("ffmpeg r71 (txw_piperefuse)", "*ffprobe-transport-r71", "txw_piperefuse",
     ["ffprobe_format", "ffprobe_exit", "ffmpeg_exit", "ffmpeg_error"])
show("libsndfile r72 (txw_piperefuse)", "*sndfile-transport-r72", "txw_piperefuse",
     ["format_name", "read_frames", "error"])
