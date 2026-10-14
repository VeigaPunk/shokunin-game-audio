#!/usr/bin/env python3
"""r72-verifier: independent 3-decoder lattice extract.

Pulls per-member verdicts from the LATEST committed (git-tracked) receipt of
each prior mode, plus any r72 sndfile receipt passed on argv. Writes a
normalized verdict per member x arm for each decoder so the lattice claim
can be checked mechanically rather than by eye.

Usage:
  python3 extract_lattice.py [sndfile_receipt.json ...]
Output: corpus/live/r72-verifier/lattice.json + stdout summary.
"""
import glob
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                    "..", "..", ".."))
RUNS = os.path.join(ROOT, "corpus", "live", "runs")

# member -> (committed receipt mode suffix, measurement key)
SOX_MODES = {
    "dec_act": ("-transport-dec-act-r67", "transport_dec_act_r67_probe"),
    "dec_hcom": ("-transport-dec-hcom-r67", "transport_dec_hcom_r67_probe"),
    "posttable_nomatch": ("-transport-posttable-nomatch-r68",
                          "transport_posttable_nomatch_r68_probe"),
    "txw_piperefuse": ("-transport-txw-piperefuse-r68",
                       "transport_txw_piperefuse_r68_probe"),
    "extsuffix_wav": ("-transport-extsuffix-wav-r69",
                      "transport_extsuffix_wav_r69_probe"),
    "extsuffix_bin": ("-transport-extsuffix-bin-r69",
                      "transport_extsuffix_bin_r69_probe"),
    "extsuffix_txw": ("-transport-extsuffix-txw-r69",
                      "transport_extsuffix_txw_r69_probe"),
    "extsuffix_f32": ("-transport-extsuffix-f32-r69",
                      "transport_extsuffix_f32_r69_probe"),
    "extsuffix_snd": ("-transport-extsuffix-snd-r69",
                      "transport_extsuffix_snd_r69_probe"),
}


def committed_receipt(suffix):
    """Latest git-tracked receipt whose run dir ends with `suffix`."""
    paths = subprocess.run(
        ["git", "ls-files", f"corpus/live/runs/*{suffix}/measurements.json"],
        cwd=ROOT, capture_output=True, text=True).stdout.split()
    if not paths:
        return None
    path = sorted(paths)[-1]
    return os.path.join(ROOT, path)


def sox_verdict(arm):
    """Normalize a sox transport arm to a compact verdict."""
    if arm.get("error"):
        return "REJ:%s" % arm["error"][:60]
    return "ACC:%s/%s s=%s" % (arm.get("sox_detected_format"),
                               arm.get("sox_route"), arm.get("samples_read"))


def ffmpeg_verdict(arm):
    if arm.get("ffmpeg_exit") == 0:
        return "ACC:%s" % arm.get("ffprobe_format")
    return "REJ:%s" % (arm.get("ffprobe_format"),
                       )[0] or "REJ:exit%s" % arm.get("ffmpeg_exit")


def main():
    lat = {"sox": {}, "ffmpeg": {}, "sndfile": {}}
    receipt_used = {}
    for member, (suffix, key) in SOX_MODES.items():
        rp = committed_receipt(suffix)
        receipt_used.setdefault("sox", {})[member] = rp
        if not rp:
            continue
        m = json.load(open(rp))["measurements"][key]
        lat["sox"][member] = {t: sox_verdict(a)
                              for t, a in m["transport_axis"].items()}

    rp71 = committed_receipt("-ffprobe-transport-r71")
    receipt_used["ffmpeg"] = rp71
    if rp71:
        meas = json.load(open(rp71))["measurements"]
        for key, m in meas.items():
            if "_r71_probe" not in key or "transport_axis" not in m:
                continue
            member = m.get("pair_member") or key.split("_r71")[0]
            lat["ffmpeg"][member] = {
                t: ffmpeg_verdict(a) for t, a in m["transport_axis"].items()}

    for arg in sys.argv[1:]:
        meas = json.load(open(arg))["measurements"]
        receipt_used.setdefault("sndfile", []).append(arg)
        for key, m in meas.items():
            if "_r72_probe" not in key and "sndfile" not in key:
                continue
            member = m.get("pair_member") or key
            axis = m.get("transport_axis") or {}
            lat["sndfile"][member] = {
                t: ("ACC:%s rd=%s" % (a.get("format_name") or
                                      a.get("sndfile_format"),
                                      a.get("read_frames"))
                    if (a.get("format_name") or a.get("sndfile_format") or
                        a.get("read_frames"))
                    else "REJ:%s" % (a.get("error") or ""))[:80]
                for t, a in axis.items()}

    out = {"receipts": receipt_used, "lattice": lat}
    dst = os.path.join(os.path.dirname(__file__), "lattice.json")
    with open(dst, "w") as fh:
        json.dump(out, fh, indent=1)
    members = sorted(set(list(lat["sox"]) + list(lat["ffmpeg"]) +
                         list(lat["sndfile"])))
    for mem in members:
        print("==", mem)
        for dec in ("sox", "ffmpeg", "sndfile"):
            arms = lat[dec].get(mem)
            if arms:
                print("  %-7s %s" % (dec, " | ".join(
                    "%s:%s" % (t, v) for t, v in arms.items())))
    print("wrote", dst)


if __name__ == "__main__":
    main()
