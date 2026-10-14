#!/usr/bin/env python3
"""r72-boundary: build the 3-decoder (sox / ffmpeg / libsndfile) verdict
lattice over the 9-member transport corpus from measured receipts:

  sox      latest committed r67/r68/r69 transport receipts (extract_prior.py)
  ffmpeg   latest committed r71 ffprobe transport receipt
  sndfile  this seat's fresh r72 arm receipt (probe_sndfile_r72.py)

Acceptance per arm: sox exit_code==0; ffmpeg ffmpeg_exit==0;
libsndfile read_frames is not None (open+read succeeded).
Output: lattice.json (per member x transport + derived classes).
"""
import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE.parent.parent

prior = json.load(open(HERE / "prior-verdicts.json"))
runs = sorted((HERE / "runs").glob("*-sndfile-transport-r72/measurements.json"))
assert runs, "no sndfile r72 receipt found"
snd_receipt = json.load(open(runs[-1]))

MEMBER_KEYS = {
    "dec_act": "dec_act", "dec_hcom": "dec_hcom",
    "posttable_nomatch": "posttable", "txw_piperefuse": "txw_piperefuse",
    "extsuffix_wav": "extsuffix_wav", "extsuffix_bin": "extsuffix_bin",
    "extsuffix_txw": "extsuffix_txw", "extsuffix_f32": "extsuffix_f32",
    "extsuffix_snd": "extsuffix_snd",
}
TRANSPORTS = ("file", "stdin_pipe", "redirected_fd", "fifo_path")

out = {"sndfile_receipt": str(runs[-1].relative_to(CORPUS)), "members": {}}

for member, key in MEMBER_KEYS.items():
    sox_entry = prior["sox"][key]
    ff_entry = prior["ffmpeg"][key]
    snd_entry = snd_receipt["measurements"][f"sndfile_{member}_r72_probe"]

    sox_arm = {}
    for g in sox_entry["transport_verdict_groups"]:
        for t in g["transports"]:
            sox_arm[t] = {"accept": g["exit_code"] == 0,
                          "detected": g["sox_detected_format"],
                          "route": g["sox_route"], "samples": g["samples_read"],
                          "error": g["error"]}
    ff_arm = {}
    for g in ff_entry["transport_verdict_groups"]:
        for t in g["transports"]:
            ff_arm[t] = {"accept": g["ffmpeg_exit"] == 0,
                         "detected": g["ffprobe_format"],
                         "ffmpeg_exit": g["ffmpeg_exit"], "error": g["ffmpeg_error"]}
    snd_arm = {}
    for t in TRANSPORTS:
        a = snd_entry["transport_axis"][t]
        snd_arm[t] = {"accept": a["read_frames"] is not None,
                      "detected": a["format_name"], "read_frames": a["read_frames"],
                      "frames": a["frames"], "error": a["error"]}

    def acc_set(arm):
        return {t for t in TRANSPORTS if arm[t]["accept"]}

    sox_set, ff_set, snd_set = acc_set(sox_arm), acc_set(ff_arm), acc_set(snd_arm)
    all3 = sox_set & ff_set & snd_set
    sox_only = sox_set - ff_set - snd_set
    snd_only = snd_set - ff_set - sox_set
    ff_only = ff_set - sox_set - snd_set
    any_set = sox_set | ff_set | snd_set

    out["members"][member] = {
        "path": sox_entry["path"],
        "acceptance": {"sox": sorted(sox_set), "ffmpeg": sorted(ff_set),
                       "sndfile": sorted(snd_set)},
        "classes": {
            "all_three": sorted(all3),
            "sox_only": sorted(sox_only),
            "sndfile_only": sorted(snd_only),
            "ffmpeg_only": sorted(ff_only),
            "reject_all": sorted(set(TRANSPORTS) - any_set),
        },
        "detected_labels": {
            "sox": sorted({sox_arm[t]["detected"] for t in TRANSPORTS
                           if sox_arm[t]["detected"]}),
            "ffmpeg": sorted({ff_arm[t]["detected"] for t in TRANSPORTS
                              if ff_arm[t]["detected"]}),
            "sndfile": sorted({snd_arm[t]["detected"] for t in TRANSPORTS
                               if snd_arm[t]["detected"]}),
        },
        "reject_reasons": {
            "sox": sorted({sox_arm[t]["error"] for t in TRANSPORTS
                           if not sox_arm[t]["accept"] and sox_arm[t]["error"]}),
            "ffmpeg": sorted({ff_arm[t]["error"] for t in TRANSPORTS
                              if not ff_arm[t]["accept"] and ff_arm[t]["error"]}),
            "sndfile": sorted({snd_arm[t]["error"] for t in TRANSPORTS
                               if not snd_arm[t]["accept"] and snd_arm[t]["error"]}),
        },
        "transport_axis": {"sox": sox_arm, "ffmpeg": ff_arm, "sndfile": snd_arm},
        "sox_transport_fork": sox_entry["transport_fork"],
        "ffmpeg_transport_fork": ff_entry["transport_fork"],
        "sndfile_transport_fork": snd_entry["transport_fork"],
    }

# member-level classes (any-transport acceptance)
member_classes = {"all_three": [], "sox_only": [], "sndfile_only": [],
                  "ffmpeg_only": [], "reject_all": [], "mixed_no_sole": []}
for member, m in out["members"].items():
    a = m["acceptance"]
    s, f, l = set(a["sox"]), set(a["ffmpeg"]), set(a["sndfile"])
    if not (s | f | l):
        member_classes["reject_all"].append(member)
    elif s and not f and not l:
        member_classes["sox_only"].append(member)
    elif l and not f and not s:
        member_classes["sndfile_only"].append(member)
    elif f and not s and not l:
        member_classes["ffmpeg_only"].append(member)
    elif s == f == l:
        member_classes["all_three"].append(member)
    else:
        member_classes["mixed_no_sole"].append(member)
out["member_level_classes"] = member_classes

# detect-label universes
labels = {"sox": set(), "ffmpeg": set(), "sndfile": set()}
rejects = {"sox": set(), "ffmpeg": set(), "sndfile": set()}
for m in out["members"].values():
    for d, ls in m["detected_labels"].items():
        labels[d].update(ls)
    for d, ls in m["reject_reasons"].items():
        rejects[d].update(ls)
out["detect_label_universe"] = {k: sorted(v) for k, v in labels.items()}
out["reject_reason_universe"] = {k: sorted(v) for k, v in rejects.items()}

(HERE / "lattice.json").write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps({"member_level_classes": member_classes,
                  "detect_label_universe": out["detect_label_universe"]}, indent=1))
