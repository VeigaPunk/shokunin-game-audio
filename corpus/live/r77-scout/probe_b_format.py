#!/usr/bin/env python3
"""R77 scout — FRONTIER 3: format axis on capture.

pw-record --format/--rate/--channels/--channel-map legality against the
source's own format; arecord -f variants on hw:null vs the pulse plugin;
ffmpeg -sample_rate/-channels on -f pulse (input options).

Verdict per leg: refused (rc!=0) | resampled (fmt leaf != request) |
honored (fmt leaf == request) | silent_convert (requested != reported with
rc=0).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r77_probe import (LINE, M_SPDIF, emit, inspect, leg_file, mk,  # noqa: E402
                       out_kind)

TMP = mk()
N = "4800"
FMT_TAG = {1: "PCM", 3: "FLOAT", 6: "ALAW", 7: "ULAW"}


def describe(leg):
    f = leg.get("fmt") or {}
    return {"tag": FMT_TAG.get(f.get("tag"), f.get("tag")),
            "channels": f.get("channels"), "rate": f.get("rate"),
            "bits": f.get("bits")}


def main():
    out = {"probe": "format-axis-r77", "tmp": TMP, "legs": {},
           "source_native": {"Line source": "s24le 2ch 48000Hz",
                             "SPDIF monitor": "s16le 2ch 48000Hz",
                             "Speaker monitor": "s32le 2ch 48000Hz"}}

    # ---- pw-record format/rate/channels ---------------------------------
    pwr = [
        ("baseline_s16_48k_2ch", []),
        ("rate_44100", ["--rate", "44100"]),
        ("rate_96000", ["--rate", "96000"]),
        ("rate_8000", ["--rate", "8000"]),
        ("rate_192000", ["--rate", "192000"]),
        ("ch_1", ["--channels", "1"]),
        ("ch_6", ["--channels", "6"]),
        ("ch_1_map_mono", ["--channels", "1", "--channel-map", "MONO"]),
        ("fmt_s24", ["--format", "s24"]),
        ("fmt_s32", ["--format", "s32"]),
        ("fmt_f32", ["--format", "f32"]),
        ("fmt_f64", ["--format", "f64"]),
        ("fmt_u8", ["--format", "u8"]),
        ("fmt_ulaw", ["--format", "ulaw"]),
        ("fmt_s16_rate_44100", ["--format", "s16", "--rate", "44100"]),
        ("rate_44100_ch_1", ["--rate", "44100", "--channels", "1"]),
        ("quality_0", ["-q", "0"]),
        ("quality_15", ["-q", "15"]),
        ("badfmt_bogus", ["--format", "bogus"]),
        ("badrate_0", ["--rate", "0"]),
        ("badch_0", ["--channels", "0"]),
        ("ch_1_map_stereo_mismatch", ["--channels", "1",
                                      "--channel-map", "FL,FR"]),
    ]
    for label, extra in pwr:
        p = os.path.join(TMP, f"fmt_{label}.wav")
        leg = leg_file(f"pwrecord:{label}",
                       ["pw-record", "--target", LINE, "-n", N] + extra + [p],
                       p)
        out["legs"][f"pwrecord|{label}"] = {
            "request": extra, "reported": describe(leg),
            "kind": out_kind(inspect(p)) if os.path.exists(p) else "missing",
            **leg}

    # ---- pw-record monitor-format (SPDIF monitor native s16le) ----------
    for label, extra in [("mon_s16", []), ("mon_f32", ["--format", "f32"]),
                         ("mon_rate_44100", ["--rate", "44100"]),
                         ("mon_ch_1", ["--channels", "1"])]:
        p = os.path.join(TMP, f"monfmt_{label}.wav")
        leg = leg_file(f"pwrecord_mon:{label}",
                       ["pw-record", "-P", "stream.capture.sink=true",
                        "--target", M_SPDIF, "-n", N] + extra + [p], p)
        out["legs"][f"pwrecord_monitor|{label}"] = {
            "request": extra, "reported": describe(leg),
            "kind": out_kind(inspect(p)) if os.path.exists(p) else "missing",
            **leg}

    # ---- arecord -f variants: hw:0,0 vs null vs pulse plugin ------------
    arec = [
        ("cd_s16_44k", ["-f", "cd"]),
        ("dat_s16_48k", ["-f", "dat"]),
        ("S16_LE", ["-f", "S16_LE"]),
        ("S24_3LE", ["-f", "S24_3LE"]),
        ("S32_LE", ["-f", "S32_LE"]),
        ("FLOAT_LE", ["-f", "FLOAT_LE"]),
        ("U8", ["-f", "U8"]),
        ("bogus_fmt", ["-f", "BOGUS"]),
        ("r44100", ["-r", "44100", "-f", "S16_LE"]),
        ("r96000", ["-r", "96000", "-f", "S16_LE"]),
        ("c1", ["-c", "1", "-f", "S16_LE"]),
        ("c6", ["-c", "6", "-f", "S16_LE"]),
        ("r44100_c1", ["-r", "44100", "-c", "1", "-f", "S16_LE"]),
    ]
    for dev in ("hw:0,0", "null", "pulse"):
        for label, extra in arec:
            p = os.path.join(TMP, f"arecf_{dev.replace(':', '').replace(',', '')}"
                                    f"_{label}.wav")
            leg = leg_file(f"arecord[{dev}]:{label}",
                           ["arecord", "-D", dev, "-d", "1"] + extra + [p], p)
            out["legs"][f"arecord[{dev}]|{label}"] = {
                "request": extra, "reported": describe(leg),
                "kind": out_kind(inspect(p)) if os.path.exists(p)
                else "missing", **leg}

    # ---- ffmpeg -f pulse input options ----------------------------------
    ffl = [
        ("baseline", []),
        ("sample_rate_44100", ["-sample_rate", "44100"]),
        ("sample_rate_96000", ["-sample_rate", "96000"]),
        ("channels_1", ["-channels", "1"]),
        ("channels_6", ["-channels", "6"]),
        ("sr44100_ch1", ["-sample_rate", "44100", "-channels", "1"]),
        ("sr8000", ["-sample_rate", "8000"]),
    ]
    for label, extra in ffl:
        p = os.path.join(TMP, f"ffp_{label}.wav")
        leg = leg_file(f"ffmpeg_pulse:{label}",
                       ["ffmpeg", "-nostdin", "-nostats", "-v", "error",
                        "-f", "pulse"] + extra + ["-i", LINE, "-t", "0.6",
                                                  "-y", p], p)
        out["legs"][f"ffmpeg_pulse|{label}"] = {
            "request": extra, "reported": describe(leg),
            "kind": out_kind(inspect(p)) if os.path.exists(p) else "missing",
            **leg}

    emit(out, "probe-format-axis-r77.json")
    print(out["probe"])


if __name__ == "__main__":
    main()
