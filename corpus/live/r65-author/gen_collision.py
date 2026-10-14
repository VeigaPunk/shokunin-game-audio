#!/usr/bin/env python3
"""r65 collision matrix: RIFF+0x84@256 files that also match each preemptor
CHECK row (gsrt 'ring.bin\\0'@16, hcom 'FSSD'@65 AND 'HCOM'@128).

Two bases:
  B = r61-family 11,588-B WAVE_FORMAT_EXTENSIBLE valid17 fixture (shared
      deterministic payload, byte 256 pinned by assignment — r63 convention)
  M = minimal 257-B RIFF/WAVE shell (autodetect window exactly)

Probes per variant: default sox -V6 stat (detected/samples/exit), sox --i,
raw f32 decode, forced -t legs (act/gsrt/hcom/wav), ffprobe codec/duration.
Writes variants/*.wav + results.tsv (one row per variant).
"""
import math
import re
import struct
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
VAR = HERE / "variants"
RATE = 48000


def family_blob():
    """r61-family valid17 extensible fixture, shared r63/r64 payload."""
    values = [round(8191 * (.25*math.sin(2*math.pi*920*i/RATE) + .10*math.sin(2*math.pi*1380*i/RATE)))
              for i in range(5760)]
    data = struct.pack("<" + "h"*len(values), *values)
    guid = bytes.fromhex("0100000000001000800000aa00389b71")
    fmt = struct.pack("<HHIIHHHHI", 0xfffe, 1, RATE, RATE*2, 2, 16, 22, 17, 0x4) + guid
    riff = b"WAVEfmt " + struct.pack("<I", len(fmt)) + fmt + b"data" + struct.pack("<I", len(data)) + data
    blob = bytearray(b"RIFF" + struct.pack("<I", len(riff)) + riff)
    blob[256] = 0x84
    return blob


def minimal_blob():
    """257-byte RIFF/WAVE shell: RIFF@0, WAVE@8, 0x84@256, zeros elsewhere."""
    blob = bytearray(257)
    blob[0:4] = b"RIFF"
    struct.pack_into("<I", blob, 4, 249)
    blob[8:12] = b"WAVE"
    blob[256] = 0x84
    return blob


GSRT = b"ring.bin\x00"          # @16..24 (9 B, C literal includes the NUL)
def build():
    VAR.mkdir(exist_ok=True)
    B, M = family_blob(), minimal_blob()
    specs = []
    def add(name, base, edits, b256=0x84):
        v = bytearray(base)
        for off, data in edits:
            v[off:off+len(data)] = data
        if len(v) > 256:
            v[256] = b256
        specs.append((name, v))
    # ---- family-B variants (r61 fixture shape) ----
    add("b_base84", B, [])
    add("b_base00", B, [], b256=0x00)
    add("b_gsrt", B, [(16, GSRT)])
    add("b_gsrt_m23", B, [(16, b"ring.bim\x00")])          # 1 byte off: 'n'->'m' @23
    add("b_gsrt_x24", B, [(16, b"ring.binX")])             # NUL terminator broken @24
    add("b_gsrt_no84", B, [(16, GSRT)], b256=0x00)
    add("b_hcom", B, [(65, b"FSSD"), (128, b"HCOM")])
    add("b_hcom_x131", B, [(65, b"FSSD"), (128, b"HCOX")]) # 1 byte off: 'M'->'X' @131
    add("b_hcom_fssd_only", B, [(65, b"FSSD")])
    add("b_hcom_hcom_only", B, [(128, b"HCOM")])
    add("b_hcom_x65", B, [(65, b"XSSD"), (128, b"HCOM")])  # FSSD broken @65
    add("b_hcom_no84", B, [(65, b"FSSD"), (128, b"HCOM")], b256=0x00)
    add("b_both", B, [(16, GSRT), (65, b"FSSD"), (128, b"HCOM")])
    add("b_both_no84", B, [(16, GSRT), (65, b"FSSD"), (128, b"HCOM")], b256=0x00)
    # ---- minimal-M variants (257-B shell) ----
    add("m_base84", M, [])
    add("m_gsrt", M, [(16, GSRT)])
    add("m_hcom", M, [(65, b"FSSD"), (128, b"HCOM")])
    add("m_both", M, [(16, GSRT), (65, b"FSSD"), (128, b"HCOM")])
    add("m_gsrt25", bytearray(25), [(16, GSRT)], b256=0x00)  # 25-B file, no RIFF at all
    for name, blob in specs:
        (VAR / f"{name}.wav").write_bytes(blob)
    return [n for n, _ in specs]


DET = re.compile(r"detected file format type `(\S+?)'")
SAMPLES = re.compile(r"Samples read:\s*(\d+)")


def run(*args):
    p = subprocess.run(args, capture_output=True)
    return p.returncode, p.stdout, p.stderr


def tail(b, n=140):
    lines = b.decode(errors="replace").strip().splitlines()
    return lines[-1][-n:] if lines else ""


def probe(name):
    f = str(VAR / f"{name}.wav")
    row = {"name": name}
    rc, out, err = run("sox", "-V6", f, "-n", "stat")
    det = DET.search(err.decode(errors="replace"))
    smp = SAMPLES.search(err.decode(errors="replace"))
    row["detected"] = det.group(1) if det else "NONE"
    row["stat_rc"] = rc
    row["stat_samples"] = smp.group(1) if smp else "-"
    row["stat_tail"] = tail(err)
    rc, out, err = run("sox", "--i", f)
    info = out.decode(errors="replace")
    row["i_rc"] = rc
    row["i_ffmpeg"] = "ffmpeg" if "(ffmpeg)" in info else "-"
    row["i_duration"] = "Duration" if "Duration" in info else "-"
    row["i_tail"] = tail(err or out)
    rc, out, err = run("sox", f, "-t", "f32", "-e", "floating-point", "-")
    row["dec_rc"] = rc
    row["dec_samples"] = len(out)//4
    for t in ("act", "gsrt", "hcom", "wav"):
        rc, out, err = run("sox", "-t", t, f, "-n", "stat")
        smp = SAMPLES.search(err.decode(errors="replace"))
        row[f"t_{t}_rc"] = rc
        row[f"t_{t}_smp"] = smp.group(1) if smp else "-"
    rc, out, err = run("ffprobe", "-v", "error", "-show_entries",
                       "stream=codec_name,bits_per_sample:format=duration",
                       "-of", "json", f)
    row["fp_rc"] = rc
    row["fp"] = (out.decode(errors="replace").replace("\n", " ")[:160] if rc == 0
                 else "ERR:" + tail(err))
    return row


def main():
    names = build()
    cols = ["name", "detected", "stat_rc", "stat_samples", "i_rc", "i_ffmpeg",
            "i_duration", "dec_rc", "dec_samples", "t_act_rc", "t_act_smp",
            "t_gsrt_rc", "t_gsrt_smp", "t_hcom_rc", "t_hcom_smp", "t_wav_rc",
            "t_wav_smp", "fp_rc", "stat_tail", "i_tail", "fp"]
    with (HERE / "results.tsv").open("w") as fh:
        fh.write("\t".join(cols) + "\n")
        for n in names:
            row = probe(n)
            fh.write("\t".join(str(row.get(c, "")) for c in cols) + "\n")
            fh.flush()
            print(n, row["detected"], row["stat_rc"], row["stat_samples"], file=__import__("sys").stderr)


if __name__ == "__main__":
    main()
