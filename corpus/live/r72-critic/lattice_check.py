#!/usr/bin/env python3
"""r72-critic: machine-checked 3-decoder acceptance lattice on the 9-member
r71 corpus, from COMMITTED receipts + the frontier sndfile matrix.
Acceptance = decoder returned decoded frames (sox exit 0 + samples>0;
ffmpeg ffmpeg_exit==0; sndfile read_frames is not None)."""
import json, glob, os

def latest(mode):
    ds = sorted(glob.glob(f"corpus/live/runs/*-{mode}"))
    assert ds, mode
    return ds[-1]

SOX = {  # member -> (mode, receipt-entry-key)
 "dec_act": ("transport-dec-act-r67", "transport_dec_act_r67_probe"),
 "dec_hcom": ("transport-dec-hcom-r67", "transport_dec_hcom_r67_probe"),
 "posttable_nomatch": ("transport-posttable-nomatch-r68", "transport_posttable_nomatch_r68_probe"),
 "txw_piperefuse": ("transport-txw-piperefuse-r68", "transport_txw_piperefuse_r68_probe"),
 "extsuffix_wav": ("transport-extsuffix-wav-r69", "transport_extsuffix_wav_r69_probe"),
 "extsuffix_bin": ("transport-extsuffix-bin-r69", "transport_extsuffix_bin_r69_probe"),
 "extsuffix_txw": ("transport-extsuffix-txw-r69", "transport_extsuffix_txw_r69_probe"),
 "extsuffix_f32": ("transport-extsuffix-f32-r69", "transport_extsuffix_f32_r69_probe"),
 "extsuffix_snd": ("transport-extsuffix-snd-r69", "transport_extsuffix_snd_r69_probe"),
}
ARMS = ["file", "stdin_pipe", "redirected_fd", "fifo_path"]
sox = {}
for m, (mode, key) in SOX.items():
    j = json.load(open(os.path.join(latest(mode), "measurements.json")))
    e = j["measurements"][key]
    sox[m] = {a: (e["transport_axis"][a]["exit_code"] == 0 and
                  (e["transport_axis"][a].get("samples_read") or 0) > 0)
              for a in ARMS}

ff = {}
j = json.load(open(os.path.join("corpus/live/runs/20261014T141033155858Z-ffprobe-transport-r71", "measurements.json")))
for m in SOX:
    e = j["measurements"][f"ffprobe_{m}_r71_probe"]
    ff[m] = {a: e["transport_axis"][a]["ffmpeg_exit"] == 0 for a in ARMS}

sf = {}
sm = json.load(open("corpus/live/frontier-sndfile/runs/sndfile-matrix.json"))
for m in SOX:
    sm_key = {"posttable_nomatch": "posttable"}.get(m, m)
    sf[m] = {a: sm[sm_key]["arms"][a]["read_frames"] is not None for a in ARMS}

print("member              | sox                          | ffmpeg                       | sndfile")
print("                    | f  p  r  q                   | f  p  r  q                   | f  p  r  q")
for m in SOX:
    def s(d):
        return " ".join(("Y" if d[a] else ".") for a in ARMS)
    print(f"{m:19s} | {s(sox[m]):28s} | {s(ff[m]):28s} | {s(sf[m])}")

print()
classes = {}
for m in SOX:
    key = tuple("".join(("Y" if d[m][a] else "-") for a in ARMS) for d in (sox, ff, sf))
    classes.setdefault(key, []).append(m)
print("classes (sox|ffmpeg|sndfile arm-vectors):")
for key, ms in classes.items():
    print("  ", key, ms)

# member-level classes
ml = {}
for m in SOX:
    key = tuple(any(d[m].values()) for d in (sox, ff, sf))
    ml.setdefault(key, []).append(m)
print("member-level (accept-any-arm):", ml)
