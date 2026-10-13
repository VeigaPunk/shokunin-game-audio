#!/usr/bin/env python3
"""r63 act-autodetect predicate sweep on the r61 pair (scratch, no repo writes).

Predicate under test (sox_ng-14.8.0.1 formats.c:93):
    CHECK(act, 0, 4, "RIFF", 256, 1, "\x84")
    => len>=257 && memcmp(data,"RIFF",4)==0 && data[256]==0x84  -> 'act' -> ffmpeg bridge
checked before CHECK(wav, 0,4,"RIFF", 8,4,"WAVE").

For every variant run `sox -V6 <f> -n stat`; parse detected format, (ffmpeg)
handler tag, samples read, exit code, FAIL line -> results.tsv (append mode per
batch).  Exhaustive batches stream through a temp file (no 23k files on disk).
"""
import concurrent.futures as cf
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]          # corpus/
LIVE = ROOT / "live"
SCRATCH = LIVE / "r63-author"
VARIANTS = SCRATCH / "variants"
TSV = SCRATCH / "results.tsv"

BASE_A = (LIVE / "round-61" / "pair_valid_17.wav").read_bytes()   # valid17, byte256=0x84
BASE_B = (LIVE / "round-61" / "pair_valid_16.wav").read_bytes()   # valid16, byte256=0x84

assert BASE_A[256] == 0x84 and BASE_B[256] == 0x84
assert BASE_A[:4] == b"RIFF" and BASE_B[:4] == b"RIFF"
assert len(BASE_A) == len(BASE_B) == 11588

DET_RE = re.compile(r"detected file format type `(\S+?)'")
SAMP_RE = re.compile(r"Samples read:\s+(\d+)")
FAIL_RE = re.compile(r"sox FAIL (\S+): (.*)")


def probe_bytes(buf, name, tmpdir):
    """Write buf to a temp .wav (unless name carries another ext), sox -V6 it, return TSV row."""
    ext = ".bin" if name.endswith(".bin") else ".wav"
    path = tmpdir / (name + ext)
    path.write_bytes(bytes(buf))
    return probe_file(path, name)


def probe_file(path, name=None):
    name = name or path.stem
    proc = subprocess.run(["sox", "-V6", str(path), "-n", "stat"],
                          capture_output=True, timeout=60)
    err = proc.stderr.decode(errors="replace")
    det = DET_RE.search(err)
    detected = det.group(1) if det else "NONE"
    route = "ffmpeg" if "(ffmpeg)" in err else ("native" if detected != "NONE" else "none")
    samp = SAMP_RE.search(err)
    samples = samp.group(1) if samp else "-"
    fail = FAIL_RE.search(err)
    failsig = (fail.group(1) + ":" + fail.group(2).strip()[:80]) if fail else "-"
    return f"{name}\t{detected}\t{route}\t{samples}\t{proc.returncode}\t{failsig}"


def emit(rows, fh):
    for r in rows:
        fh.write(r + "\n")
    fh.flush()


def main(which):
    VARIANTS.mkdir(parents=True, exist_ok=True)
    tmpdir = SCRATCH / "tmp"
    tmpdir.mkdir(parents=True, exist_ok=True)
    fh = TSV.open("a")
    if TSV.stat().st_size == 0:
        fh.write("variant\tdetected\troute\tsamples\texit\tfail\n")

    if which in ("all", "targeted"):
        rows = []
        # 1) targeted value sweep @256 (brief's set) on both bases
        for tag, base in (("v17", BASE_A), ("v16", BASE_B)):
            for v in (0x00, 0x01, 0x7F, 0x80, 0x83, 0x84, 0x85, 0xFF):
                buf = bytearray(base); buf[256] = v
                rows.append(probe_bytes(buf, f"{tag}_val_{v:02x}", VARIANTS))
        # 2) 0x84 position sweep (brief's set + near-field) on both bases
        for tag, base in (("v17", BASE_A), ("v16", BASE_B)):
            for pos in (255, 256, 257, 258, 511, 512, 1024):
                buf = bytearray(base); buf[256] = 0x00; buf[pos] = 0x84
                rows.append(probe_bytes(buf, f"{tag}_pos_{pos}", VARIANTS))
        # 3) conjunction / window / boundary controls
        # 3a) RIFF@0 destroyed, 0x84@256 kept -> act must NOT fire (RIFF conjunct)
        for tag, base in (("v17", BASE_A), ("v16", BASE_B)):
            for off, val, lbl in ((0, 0x58, "riff0"), (3, 0x58, "riff3")):
                buf = bytearray(base); buf[off] = val
                rows.append(probe_bytes(buf, f"{tag}_c_{lbl}", VARIANTS))
        # 3b) WAVE@8 destroyed, 0x84@256 kept -> act still fires if it ignores WAVE
        for tag, base in (("v17", BASE_A), ("v16", BASE_B)):
            buf = bytearray(base); buf[8] = 0x58      # 'W'->'X'
            rows.append(probe_bytes(buf, f"{tag}_c_wave8", VARIANTS))
        # 3c) neighbors of 256 mutated, 0x84@256 kept -> act still fires (len-1 memcmp)
        for tag, base in (("v17", BASE_A), ("v16", BASE_B)):
            for off, val in ((255, 0x00), (255, 0xFF), (257, 0x00), (257, 0xFF)):
                buf = bytearray(base); buf[off] = val
                rows.append(probe_bytes(buf, f"{tag}_c_n{off}_{val:02x}", VARIANTS))
        # 3d) length boundary: AUTO_DETECT_SIZE=257 buffer
        buf = bytearray(BASE_B[:257])                                   # len=257, keeps 0x84@256
        rows.append(probe_bytes(buf, "v16_c_len257_keep84", VARIANTS))
        buf = bytearray(BASE_B[:257]); buf[256] = 0x00                  # len=257, no trigger
        rows.append(probe_bytes(buf, "v16_c_len257_zero84", VARIANTS))
        buf = bytearray(BASE_B[:256]); buf[255] = 0x84                  # len=256, byte256 absent
        rows.append(probe_bytes(buf, "v16_c_len256_84at255", VARIANTS))
        buf = bytearray(BASE_B[:258])                                   # len=258 > buffer, keeps 0x84@256
        rows.append(probe_bytes(buf, "v16_c_len258_keep84", VARIANTS))
        # 3e) extension independence: same bytes, real .bin name (autodetect is
        # content-first; ext is only the NULL-detect fallback)
        p = VARIANTS / "v17_c_ext.bin"; p.write_bytes(bytes(BASE_A))
        rows.append(probe_file(p, "v17_c_ext.bin"))
        p = VARIANTS / "v16_c_noriff.bin"; buf = bytearray(BASE_B); buf[0] = 0x58
        p.write_bytes(bytes(buf))
        rows.append(probe_file(p, "v16_c_noriff.bin"))
        emit(rows, fh)
        print(f"targeted: {len(rows)} rows")

    if which in ("all", "fullval"):
        # 4) EXHAUSTIVE value domain at offset 256, both bases (512 probes)
        rows = []
        def valjob(arg):
            tag, base, v = arg
            buf = bytearray(base); buf[256] = v
            p = tmpdir / f"val_{tag}_{v:02x}.wav"
            p.write_bytes(bytes(buf))
            r = probe_file(p, f"{tag}_fullval_{v:02x}")
            p.unlink()
            return r
        jobs = [(t, b, v) for t, b in (("v17", BASE_A), ("v16", BASE_B)) for v in range(256)]
        with cf.ThreadPoolExecutor(16) as ex:
            rows = list(ex.map(valjob, jobs))
        emit(rows, fh)
        print(f"fullval: {len(rows)} rows")

    if which in ("all", "fullpos"):
        # 5) EXHAUSTIVE position sweep: 0x84@X with byte256 forced 0x00, both bases
        def posjob(arg):
            tag, base, pos = arg
            buf = bytearray(base); buf[256] = 0x00; buf[pos] = 0x84
            p = tmpdir / f"pos_{tag}_{pos}.wav"
            p.write_bytes(bytes(buf))
            r = probe_file(p, f"{tag}_fullpos_{pos}")
            p.unlink()
            return r
        jobs = [(t, b, pos) for t, b in (("v17", BASE_A), ("v16", BASE_B))
                for pos in range(len(b))]
        done = 0
        with cf.ThreadPoolExecutor(16) as ex:
            for chunk_start in range(0, len(jobs), 2048):
                chunk = jobs[chunk_start:chunk_start + 2048]
                emit(list(ex.map(posjob, chunk)), fh)
                done += len(chunk)
                print(f"fullpos progress {done}/{len(jobs)}", file=sys.stderr)
        print(f"fullpos: {len(jobs)} rows")

    fh.close()


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "all")
