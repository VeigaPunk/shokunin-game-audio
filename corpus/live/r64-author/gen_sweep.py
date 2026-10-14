#!/usr/bin/env python3
"""r64 valid-bits -> codec reclassification sweep under the act-forced ffmpeg bridge.

Every variant is the SAME WAVE_FORMAT_EXTENSIBLE mono48k fmt40 header family as
r61/r62/r63 (tag 0xfffe, ch 1, rate 48000, byte_rate 96000, block_align 2,
bits_per_sample 16, cbSize 22, channel_mask 0x4, PCM GUID), over ONE shared
deterministic payload (5760 x int16 = 11,520 data bytes), with file[256] pinned
to 0x84 so SoX_ng autodetect selects `act` -> the ffmpeg bridge (r63 predicate).
Variants differ ONLY at bytes 38-39 (wValidBitsPerSample, u16 LE).

Per variant three probes are recorded:
  (a) ffprobe negotiated codec_name/bits_per_sample + format.duration
  (b) default-route `sox -V6 <f> -n stat`: detected format, (ffmpeg) route tag,
      Samples read, exit, stderr tail   -> the ffmpeg-bridge leg
  (c) forced native `sox -t wav <f> -n stat`: exit / Samples read / stderr tail
  (d) forced `sox -t ffmpeg <f> -n stat`: separates autodetect from handler

Prediction under test (r62 law): nonzero valid V sets bits_per_coded_sample=V;
ff_get_pcm_codec_id maps w=(V+7)>>3 bytes -> pcm_u8(w1)/s16le(w2)/s24le(w3)/
s32le(w4)/none(w5,6,7)/s64le(w8); V>64 -> none. Samples = sum floor(pkt_i/w)
with packets from min(mp, remaining), mp = ba*2^floor(log2(bitrate/80/ba)).
"""
import json
import math
import re
import struct
import subprocess
import sys
from pathlib import Path

RATE = 48000
HERE = Path(__file__).resolve().parent
SWEEP = HERE / "sweep"
TSV = HERE / "results.tsv"

# exhaustive low range 0..66 + far tail probes of the u16 field
VALUES = list(range(0, 67)) + [72, 96, 128, 255, 1024, 32768, 65535]
GUID = bytes.fromhex("0100000000001000800000aa00389b71")


def base_blob():
    # deterministic payload; byte 256 (data[188], sample 94 low byte) pinned
    # to 0x84 by assignment afterwards (r63 convention).
    values = [round(8191 * (.25 * math.sin(2 * math.pi * 920 * i / RATE)
                            + .10 * math.sin(2 * math.pi * 1380 * i / RATE)))
              for i in range(5760)]
    data = struct.pack("<" + "h" * len(values), *values)
    fmt = struct.pack("<HHIIHHHHI", 0xfffe, 1, RATE, RATE * 2, 2, 16, 22, 0, 0x4) + GUID
    riff = b"WAVEfmt " + struct.pack("<I", len(fmt)) + fmt \
        + b"data" + struct.pack("<I", len(data)) + data
    blob = bytearray(b"RIFF" + struct.pack("<I", len(riff)) + riff)
    blob[256] = 0x84
    return blob


def write_variant(blob, valid):
    v = bytearray(blob)
    struct.pack_into("<H", v, 38, valid)
    path = SWEEP / f"sweep_valid_{valid}.wav"
    path.write_bytes(v)
    return path


def run(args):
    return subprocess.run(args, capture_output=True, text=False)


def ffprobe_info(path):
    p = run(["ffprobe", "-v", "error", "-show_entries",
             "stream=codec_name,bits_per_sample,bits_per_raw_sample:format=duration",
             "-of", "json", str(path)])
    if p.returncode != 0:
        return {"ffprobe_exit": p.returncode,
                "ffprobe_err": p.stderr.decode(errors="replace").strip()[-160:]}
    try:
        probe = json.loads(p.stdout)
    except Exception:
        return {"ffprobe_exit": 0, "codec": "UNPARSED"}
    streams = probe.get("streams") or []
    info = {"ffprobe_exit": 0, "n_streams": len(streams),
            "duration": (probe.get("format") or {}).get("duration")}
    if streams:
        s = streams[0]
        info["codec"] = s.get("codec_name")
        info["bps"] = s.get("bits_per_sample")
        info["bprs"] = s.get("bits_per_raw_sample")
    return info


SAMPLES_RE = re.compile(r"Samples read:\s*(\d+)")
DETECT_RE = re.compile(r"detected file format type `(\S+?)'")


def sox_probe(args):
    p = run(args)
    err = p.stderr.decode(errors="replace")
    m = SAMPLES_RE.search(err)
    return {"exit": p.returncode,
            "samples": int(m.group(1)) if m else None,
            "detected": (DETECT_RE.search(err) or [None, None])[1],
            "ffmpeg_tag": "(ffmpeg)" in err,
            "err_tail": err.strip().splitlines()[-1][-160:] if p.returncode else ""}


def predicted(valid):
    if valid == 0:
        return 2, "pcm_s16le", 5760            # no reclassification
    if valid > 64:
        return None, "NONE", None
    w = (valid + 7) >> 3
    codec = {1: "pcm_u8", 2: "pcm_s16le", 3: "pcm_s24le",
             4: "pcm_s32le", 8: "pcm_s64le"}.get(w, "NONE")
    if codec == "NONE":
        return w, codec, None
    bitrate = w * 8 * RATE
    ba = 2
    mp = ba * (1 << int(math.log2(bitrate / 80 / ba)))
    remaining = 11520
    total = 0
    while remaining > 0:
        pkt = min(mp, remaining)
        pkt -= pkt % ba                          # wavdec floors to block_align
        if pkt < w:
            break                                # pcmdec rejects sub-width packet
        total += pkt // w                        # floor drop of the tail residue
        remaining -= pkt
    return w, codec, total


def main():
    SWEEP.mkdir(parents=True, exist_ok=True)
    blob = base_blob()
    assert blob[256] == 0x84 and len(blob) == 11588
    rows = []
    for v in VALUES:
        path = write_variant(blob, v)
        assert path.read_bytes()[256] == 0x84
        fp = ffprobe_info(path)
        bridge = sox_probe(["sox", "-V6", str(path), "-n", "stat"])
        forced = sox_probe(["sox", "-t", "ffmpeg", str(path), "-n", "stat"])
        native = sox_probe(["sox", "-t", "wav", str(path), "-n", "stat"])
        w, pc, ps = predicted(v)
        rows.append({"valid": v, "pred_w": w, "pred_codec": pc, "pred_samples": ps,
                     "fp": fp, "bridge": bridge, "forced": forced, "native": native})
    (HERE / "results.json").write_text(json.dumps(rows, indent=1))
    with TSV.open("w") as fh:
        fh.write("valid\tpred_w\tpred_codec\tpred_n\tfp_codec\tfp_bps\tfp_dur"
                 "\tdetected\troute\tbr_exit\tbr_n\tff_exit\tff_n"
                 "\tnat_exit\tnat_n\tnat_err\tmatch\n")
        for r in rows:
            fp, br, ff, nat = r["fp"], r["bridge"], r["forced"], r["native"]
            got_codec = fp.get("codec") or "NONE"
            match = (got_codec == r["pred_codec"]
                     and br["samples"] == r["pred_samples"])
            fh.write("\t".join(str(x) for x in (
                r["valid"], r["pred_w"], r["pred_codec"], r["pred_samples"],
                got_codec, fp.get("bps"), fp.get("duration"),
                br["detected"], "ffmpeg" if br["ffmpeg_tag"] else "?",
                br["exit"], br["samples"], ff["exit"], ff["samples"],
                nat["exit"], nat["samples"],
                nat["err_tail"][-60:].replace("\t", " "),
                "OK" if match else "MISMATCH")) + "\n")
    mism = [r["valid"] for r in rows
            if ((r["fp"].get("codec") or "NONE") != r["pred_codec"]
                or r["bridge"]["samples"] != r["pred_samples"])]
    print(f"{len(rows)} variants; mismatches vs predicted law: {mism or 'none'}")


if __name__ == "__main__":
    sys.exit(main())
