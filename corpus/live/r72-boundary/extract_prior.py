#!/usr/bin/env python3
"""r72-boundary: extract per-member sox (r67/r68/r69) and ffmpeg (r71) verdicts
from the LATEST committed receipt of each mode, for the 3-decoder lattice."""
import json, glob, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RUNS = os.path.join(ROOT, "runs")

MODES = {
    "sox": [("dec_act", "probe-transport-dec-act-r67", "transport_dec_act_r67_probe"),
            ("dec_hcom", "probe-transport-dec-hcom-r67", "transport_dec_hcom_r67_probe"),
            ("posttable", "probe-transport-posttable-nomatch-r68", "transport_posttable_nomatch_r68_probe"),
            ("txw_piperefuse", "probe-transport-txw-piperefuse-r68", "transport_txw_piperefuse_r68_probe"),
            ("extsuffix_wav", "probe-transport-extsuffix-wav-r69", "transport_extsuffix_wav_r69_probe"),
            ("extsuffix_bin", "probe-transport-extsuffix-bin-r69", "transport_extsuffix_bin_r69_probe"),
            ("extsuffix_txw", "probe-transport-extsuffix-txw-r69", "transport_extsuffix_txw_r69_probe"),
            ("extsuffix_f32", "probe-transport-extsuffix-f32-r69", "transport_extsuffix_f32_r69_probe"),
            ("extsuffix_snd", "probe-transport-extsuffix-snd-r69", "transport_extsuffix_snd_r69_probe")],
    "ffmpeg": [("dec_act", "probe-ffprobe-transport-r71", "ffprobe_dec_act_r71_probe"),
               ("dec_hcom", "probe-ffprobe-transport-r71", "ffprobe_dec_hcom_r71_probe"),
               ("posttable", "probe-ffprobe-transport-r71", "ffprobe_posttable_nomatch_r71_probe"),
               ("txw_piperefuse", "probe-ffprobe-transport-r71", "ffprobe_txw_piperefuse_r71_probe"),
               ("extsuffix_wav", "probe-ffprobe-transport-r71", "ffprobe_extsuffix_wav_r71_probe"),
               ("extsuffix_bin", "probe-ffprobe-transport-r71", "ffprobe_extsuffix_bin_r71_probe"),
               ("extsuffix_txw", "probe-ffprobe-transport-r71", "ffprobe_extsuffix_txw_r71_probe"),
               ("extsuffix_f32", "probe-ffprobe-transport-r71", "ffprobe_extsuffix_f32_r71_probe"),
               ("extsuffix_snd", "probe-ffprobe-transport-r71", "ffprobe_extsuffix_snd_r71_probe")],
}

def latest(mode):
    hits = []
    for p in glob.glob(os.path.join(RUNS, "*", "measurements.json")):
        try:
            r = json.load(open(p))
        except Exception:
            continue
        if r.get("mode") == mode:
            hits.append((os.path.basename(os.path.dirname(p)), p))
    return sorted(hits)[-1] if hits else None

out = {"sox": {}, "ffmpeg": {}, "receipts": {}}
for dec, rows in MODES.items():
    for member, mode, key in rows:
        hit = latest(mode)
        if hit is None:
            out[dec][member] = None; continue
        runid, path = hit
        r = json.load(open(path))
        out["receipts"].setdefault(mode, {"run": runid, "path": os.path.relpath(path, os.path.dirname(RUNS) + "/..")})
        out[dec][member] = r["measurements"].get(key)
print(json.dumps(out, indent=1))
