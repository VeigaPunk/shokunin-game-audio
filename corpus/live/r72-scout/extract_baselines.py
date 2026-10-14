#!/usr/bin/env python3
"""r72-scout: extract committed sox + r71 ffmpeg per-member x transport
baselines for the canonical 9-member transport corpus (TRANSPORT_R71_MEMBERS).

Source evidence = committed receipts under corpus/live/runs/ (read-only).
Latest receipt per mode (newest timestamp), mirroring the frontier seat's
"latest per mode" convention. Writes scratch JSON/TSV only.

sox cells: sox_detected_format / sox_route / exit_code / samples_read / error
ffmpeg cells: ffprobe_format / ffprobe_exit / ffprobe_error / ffmpeg_exit /
              ffmpeg_error  (from the `ffprobe_*_r71_probe` entries)
"""
import json
import glob
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]          # audio-shokunin
RUNS = ROOT / "corpus" / "live" / "runs"
OUT = Path(__file__).resolve().parent

# member -> (sox mode, sox measurement key, r71 ffprobe key)
MEMBER_MODES = {
    "dec_act": ("probe-transport-dec-act-r67", "transport_dec_act_r67_probe"),
    "dec_hcom": ("probe-transport-dec-hcom-r67", "transport_dec_hcom_r67_probe"),
    "posttable_nomatch": ("probe-transport-posttable-nomatch-r68",
                          "transport_posttable_nomatch_r68_probe"),
    "txw_piperefuse": ("probe-transport-txw-piperefuse-r68",
                       "transport_txw_piperefuse_r68_probe"),
    "extsuffix_wav": ("probe-transport-extsuffix-wav-r69",
                      "transport_extsuffix_wav_r69_probe"),
    "extsuffix_bin": ("probe-transport-extsuffix-bin-r69",
                      "transport_extsuffix_bin_r69_probe"),
    "extsuffix_txw": ("probe-transport-extsuffix-txw-r69",
                      "transport_extsuffix_txw_r69_probe"),
    "extsuffix_f32": ("probe-transport-extsuffix-f32-r69",
                      "transport_extsuffix_f32_r69_probe"),
    "extsuffix_snd": ("probe-transport-extsuffix-snd-r69",
                      "transport_extsuffix_snd_r69_probe"),
}
R71_MODE = "probe-ffprobe-transport-r71"
TRANSPORTS = ("file", "stdin_pipe", "redirected_fd", "fifo_path")


def latest_per_mode():
    newest = {}
    for p in sorted(glob.glob(str(RUNS / "*" / "measurements.json"))):
        try:
            m = json.load(open(p))
        except (json.JSONDecodeError, OSError):
            continue
        mode = m.get("mode")
        if mode:
            newest[mode] = (p, m)      # sorted paths -> last wins (newest)
    return newest


def main():
    newest = latest_per_mode()
    r71_path, r71 = newest[R71_MODE]
    out = {"sources": {"ffprobe_r71_receipt": r71_path},
             "members": {}}
    tsv = ["member\ttransport\tsox_detected\tsox_route\tsox_exit\tsox_samples\tsox_error"
           "\tffprobe_format\tffprobe_exit\tffmpeg_exit\tffmpeg_error"]
    for member, (mode, skey) in MEMBER_MODES.items():
        receipt_path, receipt = newest[mode]
        sox = receipt["measurements"][skey]
        ff = r71["measurements"][f"ffprobe_{member}_r71_probe"]
        entry = {"sox_receipt": receipt_path, "sox_key": skey,
                 "sndfile_mode": None,
                 "path": sox["path"],
                 "sox_arms": {}, "ffmpeg_arms": {}}
        for t in TRANSPORTS:
            sa = sox["transport_axis"][t]
            fa = ff["transport_axis"][t]
            entry["sox_arms"][t] = {
                "sox_detected_format": sa["sox_detected_format"],
                "sox_route": sa["sox_route"],
                "exit_code": sa["exit_code"],
                "samples_read": sa["samples_read"],
                "error": sa["error"],
                "named": sa["named"], "seekable": sa["seekable"]}
            entry["ffmpeg_arms"][t] = {
                "ffprobe_format": fa["ffprobe_format"],
                "ffprobe_exit": fa["ffprobe_exit"],
                "ffprobe_error": fa["ffprobe_error"],
                "ffmpeg_exit": fa["ffmpeg_exit"],
                "ffmpeg_error": fa["ffmpeg_error"],
                "named": fa["named"], "seekable": fa["seekable"]}
            tsv.append("\t".join(str(x) for x in (
                member, t, sa["sox_detected_format"], sa["sox_route"],
                sa["exit_code"], sa["samples_read"], sa["error"] or "",
                fa["ffprobe_format"] or "", fa["ffprobe_exit"],
                fa["ffmpeg_exit"], fa["ffmpeg_error"] or "")))
        out["members"][member] = entry
    (OUT / "prior-verdicts.json").write_text(json.dumps(out, indent=1) + "\n")
    (OUT / "prior-verdicts.tsv").write_text("\n".join(tsv) + "\n")
    print(f"wrote {OUT/'prior-verdicts.json'} ({len(out['members'])} members)")
    print(f"ffprobe r71 source: {r71_path}")


if __name__ == "__main__":
    main()
