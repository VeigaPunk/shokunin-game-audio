#!/usr/bin/env python3
"""r62 critic: discriminating WAV variants for the SoX/ffmpeg 3839-frame UNKNOWN.

All files are WAVE_FORMAT_EXTENSIBLE fmt40/cbSize22/mask0x4/PCM-GUID mono 48000
16-bit container unless overridden, byte-compatible with the r61 pair except for
the named varied parameter(s). Payload = prefix of the canonical r61 payload
(zeros past its end) so byte-content comparisons stay controlled.
"""
import struct, sys, os

PCM_GUID = bytes.fromhex("0100000000001000800000aa00389b71")
ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "..", "round-61", "pair_valid_16.wav")


def base_payload():
    with open(SRC, "rb") as f:
        b = f.read()
    idx = b.find(b"data")
    n = struct.unpack_from("<I", b, idx + 4)[0]
    return b[idx + 8 : idx + 8 + n]


BASE = base_payload()


def payload(n):
    if n <= len(BASE):
        return BASE[:n]
    return BASE + b"\x00" * (n - len(BASE))


def riff(chunks):
    body = b""
    for tag, d in chunks:
        body += tag + struct.pack("<I", len(d)) + d
        if len(d) % 2:
            body += b"\x00"
    return b"RIFF" + struct.pack("<I", 4 + len(body)) + b"WAVE" + body


def ext(path, valid, n=11520, container_bits=16, block_align=None,
        byte_rate=None, mask=4, ch=1, rate=48000, fact=None, pad=True):
    ba = block_align if block_align is not None else ch * container_bits // 8
    br = byte_rate if byte_rate is not None else rate * ba
    fmt = struct.pack("<HHIIHH", 0xFFFE, ch, rate, br, ba, container_bits)
    fmt += struct.pack("<H", 22) + struct.pack("<H", valid)
    fmt += struct.pack("<I", mask) + PCM_GUID
    chunks = [(b"fmt ", fmt)]
    if fact is not None:
        chunks.append((b"fact", struct.pack("<I", fact)))
    d = payload(n)
    chunks.append((b"data", d))
    out = riff(chunks) if pad else _riff_nopad(chunks)
    with open(path, "wb") as f:
        f.write(out)


def _riff_nopad(chunks):
    body = b""
    for tag, d in chunks:
        body += tag + struct.pack("<I", len(d)) + d
    return b"RIFF" + struct.pack("<I", 4 + len(body)) + b"WAVE" + body


def pcm(path, bits, n, ch=1, rate=48000):
    ba = ch * bits // 8
    br = rate * ba
    fmt = struct.pack("<HHIIHH", 1, ch, rate, br, ba, bits)
    with open(path, "wb") as f:
        f.write(riff([(b"fmt ", fmt), (b"data", payload(n))]))


def main():
    out = os.path.join(ROOT, "var")
    os.makedirs(out, exist_ok=True)
    made = []

    # Sweep A: valid-bits value, fixed 11520 payload, 16-bit container.
    for v in [8, 15, 16, 17, 18, 20, 23, 24, 25, 31, 32, 33, 40, 255]:
        p = os.path.join(out, f"ext_v{v}_n11520.wav")
        ext(p, v)
        made.append(p)

    # Sweep B/C: data-size sweep under valid17 (s24 path), valid24 (s24),
    # valid32 (s32 candidate).
    sizes = [96, 1152, 2046, 2047, 4094, 4095, 4096, 4097, 4098, 4100,
             7678, 7680, 8190, 8191, 8192, 8193, 8194, 8195, 8196,
             11514, 11515, 11516, 11517, 11518, 11519, 11520, 11521,
             11522, 11523, 11524, 11526, 12288, 23040, 24576]
    for v in [17, 24, 32]:
        for n in sizes:
            p = os.path.join(out, f"ext_v{v}_n{n}.wav")
            ext(p, v, n=n)
            made.append(p)

    # Sweep D: non-extensible PCM controls (tag 0x0001).
    for bits in [16, 24, 32]:
        for n in [7678, 7680, 11517, 11518, 11520, 11522, 23040]:
            if n % (bits // 8) != 0 and bits != 24:
                pass  # keep odd sizes too; pcm() writes them raw
            p = os.path.join(out, f"pcm{bits}_n{n}.wav")
            pcm(p, bits, n)
            made.append(p)

    # Sweep E: block-align field perturbation under valid17, n=11520.
    for ba in [1, 2, 3, 4, 5, 6, 7, 8, 10]:
        p = os.path.join(out, f"ext_v17_n11520_ba{ba}.wav")
        ext(p, 17, n=11520, block_align=ba)
        made.append(p)

    # Sweep F: fact chunk (declared sample count) under valid17 and valid16.
    for v in [16, 17]:
        for fc in [1, 3839, 3840, 5760]:
            p = os.path.join(out, f"ext_v{v}_n11520_fact{fc}.wav")
            ext(p, v, n=11520, fact=fc)
            made.append(p)

    # Sweep G: odd data size written WITHOUT the RIFF pad byte (malformed).
    for n in [11517, 11519, 11521]:
        p = os.path.join(out, f"ext_v17_n{n}_nopad.wav")
        ext(p, 17, n=n, pad=False)
        made.append(p)

    # Sweep H: 24-bit container variants (blockAlign 3 real path).
    for v, n in [(24, 11520), (17, 11520), (16, 11520), (24, 11517)]:
        p = os.path.join(out, f"ext24_v{v}_n{n}.wav")
        ext(p, v, n=n, container_bits=24)
        made.append(p)

    # Sweep I: stereo-doubled frame test — 2ch with same total bytes? No:
    # keep mono-only to avoid extra variables. Instead mask perturbation
    # (mask is the other field near offset 38's neighborhood).
    p = os.path.join(out, "ext_v17_n11520_mask0.wav")
    ext(p, 17, n=11520, mask=0)
    made.append(p)

    # Reference: exact rebuild of r61 pair (sanity SHA check).
    ext(os.path.join(out, "rebuild_v17.wav"), 17)
    ext(os.path.join(out, "rebuild_v16.wav"), 16)

    print(f"made {len(made)} variants in {out}")


if __name__ == "__main__":
    main()
