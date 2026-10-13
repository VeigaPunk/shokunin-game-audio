#!/usr/bin/env python3
"""r62-boundary: generate single-field WAV variants of round-61 pair_valid_17.wav.
Base layout (mono 48000 Hz WAVE_FORMAT_EXTENSIBLE, fmt=40, cbSize=22,
mask=0x4, PCM subtype GUID, 16-bit container, 11520-byte signed16 payload).
Each variant changes exactly ONE declared field unless noted.
"""
import struct, os, sys

BASE = "/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/round-61/pair_valid_17.wav"
OUT = "/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r62-boundary/variants"

PCM_GUID_TAIL = bytes.fromhex("00001000800000aa00389b71")  # 12-byte tail after DWORD subtype id
FLOAT_TAG = 3

def build(valid=17, bits=16, rate=48000, ch=1, tag=0xFFFE, fmt_size=40,
          cbsize=22, mask=0x4, subtype_id=1, data_bytes=None, data_size=None,
          n_avg=None, block_align=None, riff_delta=0, payload=None):
    """data_bytes: actual payload length; data_size: declared 'data' chunk size.
    payload: explicit bytes (default: reuse base payload truncated/padded)."""
    if block_align is None:
        block_align = ch * ((bits + 7) // 8)
    if n_avg is None:
        n_avg = rate * block_align
    base = open(BASE, 'rb').read()
    base_payload = base[68:]
    if payload is None:
        n = data_bytes if data_bytes is not None else 11520
        payload = base_payload[:n] if n <= len(base_payload) else base_payload + bytes(n - len(base_payload))
    if data_bytes is None:
        data_bytes = len(payload)
    if data_size is None:
        data_size = data_bytes

    fmt_body = struct.pack("<HHIIHH", tag, ch, rate, n_avg, block_align, bits)
    if fmt_size >= 18:
        fmt_body += struct.pack("<H", cbsize)
        ext = b""
        if cbsize >= 22:
            guid = struct.pack("<I", subtype_id) + PCM_GUID_TAIL
            ext = struct.pack("<HI", valid, mask) + guid
        elif cbsize > 0:
            ext = bytes(cbsize)
        fmt_body += ext
    # fmt_size is the declared chunk size; pad/truncate body to match
    body = fmt_body[:fmt_size]
    if len(body) < fmt_size:
        body += bytes(fmt_size - len(body))

    data_chunk = b"data" + struct.pack("<I", data_size) + payload
    if data_size > data_bytes:
        pass  # declared > actual: reader hits EOF
    if data_bytes & 1:
        data_chunk += b"\x00"  # RIFF pad byte
    riff_size = 4 + (8 + fmt_size) + len(data_chunk) + riff_delta
    return b"RIFF" + struct.pack("<I", riff_size & 0xFFFFFFFF) + b"WAVE" + \
           b"fmt " + struct.pack("<I", fmt_size) + body + data_chunk

def w(name, blob):
    p = os.path.join(OUT, name)
    open(p, 'wb').write(blob)
    return p

def main():
    os.makedirs(OUT, exist_ok=True)
    names = []
    # A: wValidBitsPerSample sweep (all else identical to pair_valid_17)
    for vb in [0, 1, 7, 8, 9, 15, 16, 17, 23, 24, 25, 31, 32, 33, 40, 63, 64, 65, 255]:
        names.append(w(f"a_valid_{vb:03d}.wav", build(valid=vb)))
    # B: sample-rate sweep at valid=17 (changes max_size via bitrate)
    for r in [8000, 12000, 24000, 44100, 48000, 96000]:
        names.append(w(f"b_rate_{r}.wav", build(valid=17, rate=r)))
    # C: data-size sweep at valid=17
    for dsz in [8190, 8193, 11520, 11523, 16380, 24576]:
        names.append(w(f"c_data_{dsz}.wav", build(valid=17, data_bytes=dsz)))
    # D: structure controls
    names.append(w("d_fmt18_tagfffe.wav", build(valid=17, fmt_size=18, cbsize=22)))
    names.append(w("d_fmt40_cb0.wav",     build(valid=17, fmt_size=40, cbsize=0)))
    names.append(w("d_fmt40_cb20.wav",    build(valid=17, fmt_size=40, cbsize=20)))
    names.append(w("d_plain_tag0001.wav", build(valid=17, tag=0x0001)))
    names.append(w("d_subtype_float.wav", build(valid=17, subtype_id=FLOAT_TAG)))
    # declared data size vs actual mismatch
    names.append(w("e_decl_bigger.wav",   build(valid=17, data_bytes=11520, data_size=11523)))
    names.append(w("e_decl_smaller.wav",  build(valid=17, data_bytes=11520, data_size=11517)))
    # 24-bit container control: valid=17 inside a true 24-bit file (block_align=3)
    payload24 = bytearray()
    base_payload = open(BASE,'rb').read()[68:]
    for i in range(0, 11520, 2):
        payload24 += base_payload[i:i+2] + b"\x00"  # 16-bit samples -> low 3-byte? arbitrary
    names.append(w("f_bits24_valid17.wav", build(valid=17, bits=24, payload=bytes(payload24))))
    names.append(w("f_bits24_valid24.wav", build(valid=24, bits=24, payload=bytes(payload24))))
    for n in names:
        print(n)
if __name__ == "__main__":
    main()
