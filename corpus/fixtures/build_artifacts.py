#!/usr/bin/env python3
"""Reproducibly synthesize five original, mono PCM16 audio fixtures."""
import argparse
import math
import struct
from pathlib import Path
import wave

import numpy as np

RATE = 48000
OUT = Path(__file__).resolve().parents[1] / "artifacts"


def save(name, samples, directory=OUT):
    directory.mkdir(parents=True, exist_ok=True)
    pcm = np.round(np.clip(samples, -1, 1) * 32767).astype("<i2")
    with wave.open(str(directory / f"{name}.wav"), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(RATE)
        wav.writeframes(pcm.tobytes())


def time(seconds):
    return np.arange(round(seconds * RATE)) / RATE


def build_invalid_probes():
    import struct

    out = OUT.parent / "live" / "round-6"
    out.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out / "short_sections.wav"), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(RATE)
        frames = (int(.2 * 32767 * math.sin(2*math.pi*180*i/RATE)) for i in range(3*RATE))
        wav.writeframes(b"".join(struct.pack("<h", sample) for sample in frames))
    (out / "corrupt.wav").write_bytes(bytes.fromhex("524946460000000057415645666d7420"))
    with wave.open(str(out / "wrong_format.wav"), "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(44100)
        frames = bytearray()
        for i in range(44100 * 4):
            t = i / 44100
            frames.extend(struct.pack("<hh", round(.30 * math.sin(2*math.pi*440*t)*32767),
                                      round(.25 * math.sin(2*math.pi*660*t)*32767)))
        wav.writeframes(frames)
    odd = OUT.parent / "live" / "round-7"
    odd.mkdir(parents=True, exist_ok=True)
    with wave.open(str(odd / "odd_sections.wav"), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(RATE)
        wav.writeframes(b"".join(struct.pack("<h", round(.2 * 32767 * math.sin(2*math.pi*180*i/RATE)))
                                 for i in range(101)))


def build_width_probes():
    out = OUT.parent / "live" / "round-22"
    out.mkdir(parents=True, exist_ok=True)
    samples = .2 * np.sin(2 * np.pi * 440 * time(4))
    save("native16_probe", samples, out)
    pcm24 = np.round(np.clip(samples, -1, 1) * 8388607).astype(np.int32)
    packed = np.stack((pcm24 & 255, (pcm24 >> 8) & 255, (pcm24 >> 16) & 255), axis=1).astype(np.uint8)
    with wave.open(str(out / "native24_probe.wav"), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(3)
        wav.setframerate(RATE)
        wav.writeframes(packed.tobytes())


def build_rate_channel_probes():
    out = OUT.parent / "live" / "round-25"
    out.mkdir(parents=True, exist_ok=True)
    for name, rate, channels in (("stereo48_probe", 48000, 2), ("mono441_probe", 44100, 1)):
        t = np.arange(4 * rate) / rate
        pcm = np.round(.2 * np.sin(2 * np.pi * 440 * t) * 32767).astype("<i2")
        if channels == 2:
            pcm = np.repeat(pcm[:, None], 2, axis=1)
        with wave.open(str(out / (name + ".wav")), "wb") as wav:
            wav.setnchannels(channels)
            wav.setsampwidth(2)
            wav.setframerate(rate)
            wav.writeframes(pcm.tobytes())


def build_ui_clone_probe():
    out = OUT.parent / "live" / "round-26"
    t = time(.12)
    samples = .30 * np.sin(2 * np.pi * 700 * t) * np.exp(-20 * t)
    for name in ("ui_clone", "ui_clone_alt"):
        save(name, samples, out)


def build_ui_duration_probe(frames, label):
    out = OUT.parent / "live" / "round-27"
    for name, count in ((f"ui_duration_{label}", 5760), (f"ui_duration_{label}_alt", frames)):
        t = np.arange(count) / RATE
        save(name, .38 * np.sin(2 * np.pi * (700*t + 800*t*t)) * np.exp(-30*t), out)


def build_ui_centroid_probe(multiplier, label):
    out = OUT.parent / "live" / "round-28"
    t = time(.12)
    for name, k in ((f"ui_centroid_{label}", 1.0),
                    (f"ui_centroid_{label}_alt", multiplier)):
        save(name, .38 * np.sin(2 * np.pi * (700*k*t + 800*k*t*t)) * np.exp(-30*t), out)


def build_ui_lower_centroid_probe(multiplier, label):
    out = OUT.parent / "live" / "round-29"
    t = time(.12)
    for name, k in ((f"ui_lower_centroid_{label}", 1.0),
                    (f"ui_lower_centroid_{label}_alt", multiplier)):
        save(name, .38 * np.sin(2 * np.pi * k * (700*t + 800*t*t)) * np.exp(-30*t), out)


def build_ui_orientation_probe(reverse):
    out = OUT.parent / "live" / "round-30"
    label = "reverse" if reverse else "forward"
    t = time(.12)
    for name, k in ((f"ui_orientation_{label}", .95 if reverse else 1.0),
                    (f"ui_orientation_{label}_alt", 1.0 if reverse else .95)):
        save(name, .38 * np.sin(2 * np.pi * k * (700*t + 800*t*t)) * np.exp(-30*t), out)


def build_ui_joint_below_probe():
    out = OUT.parent / "live" / "round-31"
    for name, count, k in (("ui_joint_below", 5760, 1.0),
                           ("ui_joint_below_alt", 6719, .88)):
        t = np.arange(count) / RATE
        save(name, .38 * np.sin(2 * np.pi * k * (700*t + 800*t*t)) * np.exp(-30*t), out)


def build_ui_mixed_pass_probe():
    out = OUT.parent / "live" / "round-32"
    for name, count, k in (("ui_mixed_pass", 5760, 1.0),
                           ("ui_mixed_pass_alt", 6719, 1.14)):
        t = np.arange(count) / RATE
        save(name, .38 * np.sin(2 * np.pi * k * (700*t + 800*t*t)) * np.exp(-30*t), out)


def build_ui_rate_probe():
    out = OUT.parent / "live" / "round-48"
    out.mkdir(parents=True, exist_ok=True)
    n = np.arange(5760)
    t = n / RATE
    samples = .28 * np.sin(2*np.pi*1000*t) * np.hanning(len(n))
    pcm = np.rint(np.clip(samples, -1, 1) * 32767).astype("<i2")
    for rate in (47999, 48000):
        with wave.open(str(out / f"ui-{rate}.wav"), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(rate)
            wav.writeframes(pcm.tobytes())


def build_ui_rate_above_probe():
    out = OUT.parent / "live" / "round-49"
    out.mkdir(parents=True, exist_ok=True)
    n = np.arange(5760)
    t = n / RATE
    samples = .28 * np.sin(2*np.pi*1000*t) * np.hanning(len(n))
    pcm = np.rint(np.clip(samples, -1, 1) * 32767).astype("<i2")
    for rate in (48001, 48000):
        with wave.open(str(out / f"ui-{rate}.wav"), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(rate)
            wav.writeframes(pcm.tobytes())


def build_ui_channel_probe():
    out = OUT.parent / "live" / "round-50"
    out.mkdir(parents=True, exist_ok=True)
    t = np.arange(5760) / RATE
    samples = (.18*np.sin(2*np.pi*440*t) + .10*np.sin(2*np.pi*1200*t+.2)
               + .06*np.sin(2*np.pi*2600*t+.7)) * np.exp(-8*t)
    pcm = np.round(np.clip(samples, -.95, .95)*32767).astype("<i2")
    for label, channels, data in (("mono", 1, pcm.tobytes()),
                                  ("stereo", 2, np.column_stack((pcm, pcm)).astype("<i2").tobytes())):
        with wave.open(str(out / f"{label}.wav"), "wb") as wav:
            wav.setnchannels(channels)
            wav.setsampwidth(2)
            wav.setframerate(RATE)
            wav.writeframes(data)


def build_ui_dec_preempt_r66_probe():
    out = OUT.parent / "live" / "round-66"
    out.mkdir(parents=True, exist_ok=True)
    # r65 measured the preemptor ordering gsrt < hcom < act < wav on
    # RIFF+0x84@256 files, with every collision member fail-side. r66's
    # sweep (corpus/live/r66-author/results.tsv) confirmed the ordering is
    # detect-only, not decode-only: a file matching hcom's CHECK conjuncts
    # can still satisfy the hcom reader's field walk and fully decode
    # (r65-critic's scratch D1 shape: 9 samples @22050 Hz). This pair is the
    # tracked equivalent — a fmt-16 PCM RIFF/WAVE skeleton whose data
    # payload (starts @44) carries both hcom conjuncts (FSSD@65-68,
    # HCOM@128-131) plus the reader's own field chain (huffcount@132=9 BE,
    # checksum@136, compresstype@140=0, divisor@144=1 -> 22050 Hz,
    # dictsize@148=2, two 4-byte dict entries, pad@158, first raw
    # sample@159, Huffman word@160-163 equal to the checksum word).
    # "hcom" keeps both conjuncts -> detected hcom, reader decodes.
    # "act" flips exactly one signature byte (@68 'D'->'E'), demoting
    # detection to act -> the ffmpeg bridge decodes the suppressed PCM16
    # wav. 0x84@256 is held on both members.
    buf = bytearray(b"\x00" * 600)
    buf[0:4] = b"RIFF"
    struct.pack_into("<I", buf, 4, 592)
    buf[8:12] = b"WAVE"
    buf[12:16] = b"fmt "
    struct.pack_into("<I", buf, 16, 16)
    struct.pack_into("<H", buf, 20, 1)
    struct.pack_into("<H", buf, 22, 1)
    struct.pack_into("<I", buf, 24, 8000)
    struct.pack_into("<I", buf, 28, 16000)
    struct.pack_into("<H", buf, 32, 2)
    struct.pack_into("<H", buf, 34, 16)
    buf[36:40] = b"data"
    struct.pack_into("<I", buf, 40, 556)
    for i in range(44, 600):
        buf[i] = (i * 7 + 3) & 0xFF          # deterministic ramp payload
    buf[65:69] = b"FSSD"
    buf[128:132] = b"HCOM"
    struct.pack_into(">I", buf, 132, 9)      # huffcount = 9 samples total
    struct.pack_into(">I", buf, 136, 0xA5A5A5A5)  # checksum = data word
    struct.pack_into(">I", buf, 140, 0)      # compresstype 0
    struct.pack_into(">I", buf, 144, 1)      # divisor 1 -> 22050 Hz
    struct.pack_into(">H", buf, 148, 2)      # dictsize 2
    struct.pack_into(">hh", buf, 150, 1, 1)  # dict[0] -> entry 1
    struct.pack_into(">hh", buf, 154, -1, 0) # dict[1] leaf, datum 0
    buf[158] = 0                             # pad byte before data
    buf[159] = 0x40                          # first raw sample
    struct.pack_into(">I", buf, 160, 0xA5A5A5A5)
    buf[256] = 0x84
    (out / "pair_dec_hcom.wav").write_bytes(buf)
    demoted = bytearray(buf)
    demoted[68] = ord("E")                   # 'D'->'E': FSSD conjunct broken
    (out / "pair_dec_act.wav").write_bytes(demoted)


def build_ui_lengate_r66_probe():
    out = OUT.parent / "live" / "round-66"
    out.mkdir(parents=True, exist_ok=True)
    # Every CHECK row gates on len >= p + l (the deeper signature field):
    # gsrt needs 16+9 = 25 bytes for "ring.bin\0"@16-24, hcom needs 128+4 =
    # 132 for "HCOM"@128-131. These four members straddle both gates
    # exactly: each below-gate member is the same RIFF/WAVE shell with the
    # signature's final byte truncated away by EOF, so detection falls
    # through to the wav row — the only row a short RIFF+WAVE file can
    # still satisfy. RIFF size fields stay self-consistent per member.
    def shell(n):
        buf = bytearray(b"\x00" * n)
        buf[0:4] = b"RIFF"
        struct.pack_into("<I", buf, 4, n - 8)
        buf[8:12] = b"WAVE"
        if n >= 44:
            buf[12:16] = b"fmt "
            struct.pack_into("<I", buf, 16, 16)
            struct.pack_into("<H", buf, 20, 1)
            struct.pack_into("<H", buf, 22, 1)
            struct.pack_into("<I", buf, 24, 8000)
            struct.pack_into("<I", buf, 28, 16000)
            struct.pack_into("<H", buf, 32, 2)
            struct.pack_into("<H", buf, 34, 16)
            buf[36:40] = b"data"
            struct.pack_into("<I", buf, 40, n - 44)
        for i in range(44, n):
            buf[i] = (i * 7 + 3) & 0xFF      # deterministic ramp payload
        return buf
    g = shell(25)
    g[16:25] = b"ring.bin\x00"               # full 9-byte literal fits: len 25
    (out / "pair_lengate_gsrt_25.wav").write_bytes(g)
    g = shell(24)
    g[16:24] = b"ring.bin"                   # NUL@24 truncated by EOF: len 24
    (out / "pair_lengate_gsrt_24.wav").write_bytes(g)
    h = shell(132)
    h[65:69] = b"FSSD"
    h[128:132] = b"HCOM"                     # 'M'@131 present: len 132
    (out / "pair_lengate_hcom_132.wav").write_bytes(h)
    h = shell(131)
    h[65:69] = b"FSSD"
    h[128:131] = b"HCO"                      # 'M'@131 truncated by EOF: len 131
    (out / "pair_lengate_hcom_131.wav").write_bytes(h)


def build_ui_preempt_r65_probe():
    out = OUT.parent / "live" / "round-65"
    out.mkdir(parents=True, exist_ok=True)
    # r63 pinned SoX_ng's act CHECK row (RIFF@0 AND file[256]==0x84) as one
    # first-match-wins table row. Two earlier rows can also hold on a RIFF
    # file: gsrt "ring.bin\0"@16 (the 9-byte C literal, NUL compared) and
    # hcom "FSSD"@65 AND "HCOM"@128. r65 measured the collision ordering
    # (corpus/live/r65-author/results.tsv): each preemptor claims the file
    # over act, and gsrt claims it over hcom when all signatures are
    # present. This family puts the same valid17 fixture behind each
    # signature: "act" is the uncollided control (byte-identical to
    # round-63/pair_route_84.wav), "gsrt"/"hcom" add exactly one signature,
    # "both" adds both. Every member keeps 0x84@256 — the only variable is
    # the signature span.
    values = [round(8191 * (.25*math.sin(2*math.pi*920*i/RATE) + .10*math.sin(2*math.pi*1380*i/RATE))) for i in range(5760)]
    data = struct.pack("<" + "h"*len(values), *values)
    guid = bytes.fromhex("0100000000001000800000aa00389b71")
    fmt = struct.pack("<HHIIHHHHI", 0xfffe, 1, RATE, RATE*2, 2, 16, 22, 17, 0x4) + guid
    riff = b"WAVEfmt " + struct.pack("<I", len(fmt)) + fmt + b"data" + struct.pack("<I", len(data)) + data
    blob = bytearray(b"RIFF" + struct.pack("<I", len(riff)) + riff)
    blob[256] = 0x84
    for name, edits in (("act", ()),
                        ("gsrt", ((16, b"ring.bin\x00"),)),
                        ("hcom", ((65, b"FSSD"), (128, b"HCOM"))),
                        ("both", ((16, b"ring.bin\x00"), (65, b"FSSD"), (128, b"HCOM")))):
        variant = bytearray(blob)
        for off, sig in edits:
            variant[off:off+len(sig)] = sig
        (out / f"pair_preempt_{name}.wav").write_bytes(variant)


def build_ui_validbits_steps_r64_probe():
    out = OUT.parent / "live" / "round-64"
    out.mkdir(parents=True, exist_ok=True)
    # r64's sweep pinned the wValidBitsPerSample -> codec step map under the
    # act-forced ffmpeg bridge (74 variants, corpus/live/r64-author/results.tsv):
    # nonzero valid V sets bits_per_coded_sample=V; ff_get_pcm_codec_id maps
    # w=(V+7)>>3 bytes -> pcm_u8(w1) | s16le(w2) | s24le(w3) | s32le(w4) |
    # none(w5..7) | s64le(w8); V>64 -> none. These three pairs straddle three
    # different step boundaries: {8,9} u8|s16le (the unsigned special case),
    # {24,25} s24le|s32le (tight straddle; r62's pair was the loose 24|32),
    # {56,57} none|s64le (the codec map's return after the dead band).
    # Byte 256 is pinned to 0x84 by assignment so every member keeps the
    # act-detected default route (r63 predicate: RIFF@0 AND file[256]==0x84).
    values = [round(8191 * (.25*math.sin(2*math.pi*920*i/RATE) + .10*math.sin(2*math.pi*1380*i/RATE))) for i in range(5760)]
    data = struct.pack("<" + "h"*len(values), *values)
    guid = bytes.fromhex("0100000000001000800000aa00389b71")
    for valid in (8, 9, 24, 25, 56, 57):
        fmt = struct.pack("<HHIIHHHHI", 0xfffe, 1, RATE, RATE*2, 2, 16, 22, valid, 0x4) + guid
        riff = b"WAVEfmt " + struct.pack("<I", len(fmt)) + fmt + b"data" + struct.pack("<I", len(data)) + data
        blob = bytearray(b"RIFF" + struct.pack("<I", len(riff)) + riff)
        blob[256] = 0x84
        (out / f"pair_valid_{valid}.wav").write_bytes(blob)


def build_ui_route_act_r63_probe():
    out = OUT.parent / "live" / "round-63"
    out.mkdir(parents=True, exist_ok=True)
    # r62 disclosed that SoX_ng's default loader probes ACT before WAV:
    # formats.c CHECK(act, 0, 4, "RIFF", 256, 1, "\x84") — file[0:4]=="RIFF"
    # and file[256]==0x84 selects the ffmpeg bridge; r63's sweep pinned that
    # byte exactly (all 256 values x all 11,588 positions on the r61 pair).
    # This pair keeps the r61 fragile header family (WAVE_FORMAT_EXTENSIBLE
    # valid17, which the native wav reader refuses outright) and differs ONLY
    # at file offset 256: 0x84 routes SoX to the ffmpeg bridge (which then
    # decodes via the valid17->pcm_s24le reclassification), 0x00 leaves the
    # native wav reader to reject the header. The payload byte is pinned by
    # assignment, not swept — the pair's purpose is the byte predicate, not
    # the signal.
    values = [round(8191 * (.25*math.sin(2*math.pi*920*i/RATE) + .10*math.sin(2*math.pi*1380*i/RATE))) for i in range(5760)]
    data = struct.pack("<" + "h"*len(values), *values)
    guid = bytes.fromhex("0100000000001000800000aa00389b71")
    fmt = struct.pack("<HHIIHHHHI", 0xfffe, 1, RATE, RATE*2, 2, 16, 22, 17, 0x4) + guid
    riff = b"WAVEfmt " + struct.pack("<I", len(fmt)) + fmt + b"data" + struct.pack("<I", len(data)) + data
    blob = bytearray(b"RIFF" + struct.pack("<I", len(riff)) + riff)
    for byte in (0x84, 0x00):
        variant = bytearray(blob)
        variant[256] = byte
        (out / f"pair_route_{byte:02x}.wav").write_bytes(variant)


def build_ui_extensible_valid24_probe():
    out = OUT.parent / "live" / "round-62"
    out.mkdir(parents=True, exist_ok=True)
    # Byte 256 of the finished file is the low byte of payload sample 94. The
    # r61 pair's payload accidentally carried 0x84 there, which routes SoX's
    # default loader through its ffmpeg bridge (formats.c probes ACT before
    # WAV on file[256]). Keep that property so this pair exercises the same
    # default path; sweep f2 deterministically until the byte matches.
    f2 = 1830
    while True:
        values = [round(8191 * (.26*math.sin(2*math.pi*940*i/RATE) + .11*math.sin(2*math.pi*f2*i/RATE))) for i in range(5760)]
        if values[94] & 0xff == 0x84:
            break
        f2 += 1
    data = struct.pack("<" + "h"*len(values), *values)
    guid = bytes.fromhex("0100000000001000800000aa00389b71")
    for valid in (24, 32):
        fmt = struct.pack("<HHIIHHHHI", 0xfffe, 1, RATE, RATE*2, 2, 16, 22, valid, 0x4) + guid
        riff = b"WAVEfmt " + struct.pack("<I", len(fmt)) + fmt + b"data" + struct.pack("<I", len(data)) + data
        (out / f"pair_valid_{valid}.wav").write_bytes(b"RIFF" + struct.pack("<I", len(riff)) + riff)


def build_ui_extensible_valid17_probe():
    out = OUT.parent / "live" / "round-61"
    out.mkdir(parents=True, exist_ok=True)
    values = [round(8191 * (.28*math.sin(2*math.pi*1050*i/RATE) + .10*math.sin(2*math.pi*1750*i/RATE))) for i in range(5760)]
    data = struct.pack("<" + "h"*len(values), *values)
    guid = bytes.fromhex("0100000000001000800000aa00389b71")
    for valid in (17, 16):
        fmt = struct.pack("<HHIIHHHHI", 0xfffe, 1, RATE, RATE*2, 2, 16, 22, valid, 0x4) + guid
        riff = b"WAVEfmt " + struct.pack("<I", len(fmt)) + fmt + b"data" + struct.pack("<I", len(data)) + data
        (out / f"pair_valid_{valid}.wav").write_bytes(b"RIFF" + struct.pack("<I", len(riff)) + riff)


def build_ui_extensible_valid0_probe():
    out = OUT.parent / "live" / "round-60"
    out.mkdir(parents=True, exist_ok=True)
    values = [round(8191 * (.24*math.sin(2*math.pi*997*i/RATE) + .09*math.sin(2*math.pi*1633*i/RATE))) for i in range(5760)]
    data = struct.pack("<" + "h"*len(values), *values)
    guid = bytes.fromhex("0100000000001000800000aa00389b71")
    for valid in (0, 16):
        fmt = struct.pack("<HHIIHHHHI", 0xfffe, 1, RATE, RATE*2, 2, 16, 22, valid, 0x4) + guid
        riff = b"WAVEfmt " + struct.pack("<I", len(fmt)) + fmt + b"data" + struct.pack("<I", len(data)) + data
        (out / f"pair_valid_{valid}.wav").write_bytes(b"RIFF" + struct.pack("<I", len(riff)) + riff)


def build_ui_extensible_valid13_probe():
    out = OUT.parent / "live" / "round-59"
    out.mkdir(parents=True, exist_ok=True)
    t = np.arange(5760, dtype=np.float64) / RATE
    values = np.rint(8191 * (.24*np.sin(2*np.pi*997*t) + .09*np.sin(2*np.pi*1633*t))).astype(np.int64)
    data = (values * 8).astype("<i2").tobytes()
    guid = bytes.fromhex("0100000000001000800000aa00389b71")
    for valid in (13, 16):
        fmt = struct.pack("<HHIIHHHHI", 0xfffe, 1, RATE, RATE*2, 2, 16, 22, valid, 0x4) + guid
        riff = b"WAVEfmt " + struct.pack("<I", len(fmt)) + fmt + b"data" + struct.pack("<I", len(data)) + data
        (out / f"pair_valid_{valid}.wav").write_bytes(b"RIFF" + struct.pack("<I", len(riff)) + riff)


def build_ui_extensible_valid14_probe():
    out = OUT.parent / "live" / "round-58"
    out.mkdir(parents=True, exist_ok=True)
    t = np.arange(5760, dtype=np.float64) / RATE
    values = np.rint((.25*np.sin(2*np.pi*1000*t) + .08*np.sin(2*np.pi*1500*t)) * 8191).astype(np.int64)
    data = (values * 4).astype("<i2").tobytes()
    guid = bytes.fromhex("0100000000001000800000aa00389b71")
    for valid in (14, 16):
        fmt = struct.pack("<HHIIHHHHI", 0xfffe, 1, RATE, RATE*2, 2, 16, 22, valid, 0x4) + guid
        riff = b"WAVEfmt " + struct.pack("<I", len(fmt)) + fmt + b"data" + struct.pack("<I", len(data)) + data
        (out / f"pair_valid_{valid}.wav").write_bytes(b"RIFF" + struct.pack("<I", len(riff)) + riff)


def build_ui_extensible_valid_bits_probe():
    out = OUT.parent / "live" / "round-57"
    out.mkdir(parents=True, exist_ok=True)
    samples = []
    for i in range(5760):
        t = i / RATE
        q = round(8191 * (.30*math.sin(2*math.pi*997*t) + .12*math.sin(2*math.pi*1733*t)))
        samples.append(max(-16384, min(16383, q)) * 2)
    data = struct.pack("<" + "h"*len(samples), *samples)
    guid = bytes.fromhex("0100000000001000800000aa00389b71")
    for valid in (15, 16):
        fmt = struct.pack("<HHIIHHHHI", 0xfffe, 1, RATE, RATE*2, 2, 16, 22, valid, 0x4) + guid
        riff = b"WAVEfmt " + struct.pack("<I", len(fmt)) + fmt + b"data" + struct.pack("<I", len(data)) + data
        (out / f"pair_valid_{valid}.wav").write_bytes(b"RIFF" + struct.pack("<I", len(riff)) + riff)


def build_ui_extensible_mask_probe():
    out = OUT.parent / "live" / "round-56"
    out.mkdir(parents=True, exist_ok=True)
    values = []
    for i in range(5760):
        t = i / RATE
        x = .25*math.sin(2*math.pi*1000*t) + .08*math.sin(2*math.pi*1500*t)
        values.append(max(-32768, min(32767, round(x*32767))))
    data = struct.pack("<" + "h"*len(values), *values)
    guid = bytes.fromhex("0100000000001000800000aa00389b71")
    for name, mask in (("zero", 0), ("center", 0x4)):
        fmt = struct.pack("<HHIIHHHHI", 0xfffe, 1, RATE, RATE*2, 2, 16, 22, 16, mask) + guid
        riff = b"WAVEfmt " + struct.pack("<I", len(fmt)) + fmt + b"data" + struct.pack("<I", len(data)) + data
        (out / f"pair_mask_{name}.wav").write_bytes(b"RIFF" + struct.pack("<I", len(riff)) + riff)


def build_ui_extensible_pcm16_probe():
    out = OUT.parent / "live" / "round-55"
    out.mkdir(parents=True, exist_ok=True)
    values = []
    for i in range(5760):
        t = i / RATE
        x = .25*math.sin(2*math.pi*1000*t) + .08*math.sin(2*math.pi*1500*t)
        values.append(max(-32768, min(32767, round(x*32767))))
    data = struct.pack("<" + "h"*len(values), *values)
    with wave.open(str(out / "pair_standard_pcm16.wav"), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(RATE)
        wav.writeframes(data)
    guid = bytes.fromhex("0100000000001000800000aa00389b71")
    fmt = struct.pack("<HHIIHHHHI", 0xfffe, 1, RATE, RATE*2, 2, 16, 22, 16, 0x4) + guid
    riff = b"WAVEfmt " + struct.pack("<I", len(fmt)) + fmt + b"data" + struct.pack("<I", len(data)) + data
    (out / "pair_extensible_pcm16.wav").write_bytes(b"RIFF" + struct.pack("<I", len(riff)) + riff)


def build_ui_pcm32_probe():
    out = OUT.parent / "live" / "round-54"
    out.mkdir(parents=True, exist_ok=True)
    values = []
    for i in range(5760):
        t = i / RATE
        x = .25*math.sin(2*math.pi*1000*t) + .08*math.sin(2*math.pi*1500*t)
        values.append(max(-32768, min(32767, round(x*32767))))
    with wave.open(str(out / "pair_pcm16.wav"), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(RATE)
        wav.writeframes(b"".join(struct.pack("<h", v) for v in values))
    data = b"".join(struct.pack("<i", v*65536) for v in values)
    header = (b"RIFF" + struct.pack("<I", 36+len(data)) + b"WAVEfmt "
              + struct.pack("<IHHIIHH", 16, 1, 1, RATE, RATE*4, 4, 32)
              + b"data" + struct.pack("<I", len(data)))
    (out / "pair_pcm32.wav").write_bytes(header + data)


def build_ui_float32_probe():
    out = OUT.parent / "live" / "round-53"
    out.mkdir(parents=True, exist_ok=True)
    n = np.arange(5760)
    samples = .25*np.sin(2*np.pi*1000*n/RATE) + .08*np.sin(2*np.pi*1500*n/RATE)
    pcm16 = np.rint(samples*32768).astype("<i2")
    with wave.open(str(out / "pair_pcm16.wav"), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(RATE)
        wav.writeframes(pcm16.tobytes())
    floats = (pcm16.astype("<f4")/32768).astype("<f4").tobytes()
    fmt = struct.pack("<HHIIHH", 3, 1, RATE, RATE*4, 4, 32)
    header = (b"RIFF" + struct.pack("<I", 4+8+len(fmt)+8+len(floats))
              + b"WAVEfmt " + struct.pack("<I", 16) + fmt
              + b"data" + struct.pack("<I", len(floats)))
    (out / "pair_float32.wav").write_bytes(header + floats)


def build_ui_pcm8_probe():
    out = OUT.parent / "live" / "round-52"
    out.mkdir(parents=True, exist_ok=True)
    n = np.arange(5760)
    samples = .25*np.sin(2*np.pi*1000*n/RATE) + .08*np.sin(2*np.pi*1500*n/RATE)
    pcm8 = np.clip(np.rint(samples*127+128), 0, 255).astype(np.uint8)
    pcm16 = (pcm8.astype(np.int16)-128)*256
    for name, width, data in (("pcm8", 1, pcm8.tobytes()),
                              ("pcm16", 2, pcm16.astype("<i2").tobytes())):
        with wave.open(str(out / f"pair_{name}.wav"), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(width)
            wav.setframerate(RATE)
            wav.writeframes(data)


def build_ui_pcm_depth_probe():
    out = OUT.parent / "live" / "round-51"
    out.mkdir(parents=True, exist_ok=True)
    n = np.arange(5760)
    samples = .25*np.sin(2*np.pi*1000*n/RATE) + .08*np.sin(2*np.pi*1500*n/RATE)
    pcm16 = np.rint(samples*32768).astype("<i2")
    with wave.open(str(out / "pair_pcm16.wav"), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(RATE)
        wav.writeframes(pcm16.tobytes())
    pcm24 = pcm16.astype(np.int32)*256
    with open(out / "pair_pcm24.wav", "wb") as wav:
        wav.write(b"RIFF" + struct.pack("<I", 36+len(pcm24)*3) + b"WAVEfmt "
                  + struct.pack("<IHHIIHH", 16, 1, 1, RATE, RATE*3, 3, 24)
                  + b"data" + struct.pack("<I", len(pcm24)*3))
        for value in pcm24:
            value = int(value) & 0xffffff
            wav.write(bytes((value & 255, (value >> 8) & 255, (value >> 16) & 255)))


def build_ui_upper_centroid_probe():
    out = OUT.parent / "live" / "round-47"
    out.mkdir(parents=True, exist_ok=True)
    n = np.arange(5760)
    t = n / RATE
    for label, frequency in (("below", 3983), ("above", 3984)):
        samples = .28 * np.sin(2*np.pi*frequency*t) * np.hanning(len(n))
        save(f"upper-{label}", samples, out)


def build_ui_absolute_centroid_probe():
    out = OUT.parent / "live" / "round-46"
    out.mkdir(parents=True, exist_ok=True)
    n = np.arange(5760)
    t = n / RATE
    for label, frequency in (("below", 225), ("above", 226)):
        samples = .28 * np.sin(2*np.pi*frequency*t) * np.hanning(len(n))
        save(f"centroid-{label}", samples, out)


def build_ui_lower_tolerance_probe():
    out = OUT.parent / "live" / "round-45"
    out.mkdir(parents=True, exist_ok=True)
    for frames in (5713, 5711):
        t = np.arange(frames) / RATE
        samples = .28 * np.sin(2*np.pi*(700*t + 700*t*t)) * np.exp(-5*t)
        save(f"duration-{frames}", samples, out)


def build_ui_tolerance_probe():
    out = OUT.parent / "live" / "round-44"
    out.mkdir(parents=True, exist_ok=True)
    for frames in (5807, 5809):
        t = np.arange(frames) / RATE
        samples = .28 * np.sin(2*np.pi*(700*t + 700*t*t)) * np.exp(-5*t)
        save(f"duration-{frames}", samples, out)


def build_ui_crest_probe():
    out = OUT.parent / "live" / "round-43"
    n = np.arange(5760)
    out.mkdir(parents=True, exist_ok=True)
    for counts in (46, 47):
        pcm = np.rint(counts * np.cos(2*np.pi*1000*n/RATE)).astype("<i2")
        with wave.open(str(out / f"crest-{counts}.wav"), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(RATE)
            wav.writeframes(pcm.tobytes())


def build_ui_peak_probe():
    out = OUT.parent / "live" / "round-42"
    n = np.arange(5760)
    out.mkdir(parents=True, exist_ok=True)
    for counts in (31129, 31130):
        pcm = np.rint(counts * np.cos(2*np.pi*1000*n/RATE)).astype("<i2")
        with wave.open(str(out / f"ui-peak-{counts}.wav"), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(RATE)
            wav.writeframes(pcm.tobytes())


def build_outer_slope_probe():
    out = OUT.parent / "live" / "round-41"
    n = np.arange(96000)
    pcm = np.rint(.15 * np.sin(2*np.pi*120*n/96000) * 32768).astype("<i2")
    out.mkdir(parents=True, exist_ok=True)
    for counts in (32, 33):
        probe = pcm.copy()
        probe[1] = 38 - counts
        with wave.open(str(out / f"slope-{counts}.wav"), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(RATE)
            wav.writeframes(probe.tobytes())


def build_outer_endpoint_probe():
    out = OUT.parent / "live" / "round-40"
    n = np.arange(96000)
    t = n / RATE
    base = .7 + .04*np.cos(2*np.pi*30*t)
    for counts in (983, 984):
        correction = counts/32768 - (base[-1] - base[0])
        pcm = np.rint((base + np.linspace(0, correction, len(n))) * 32768).astype("<i2")
        out.mkdir(parents=True, exist_ok=True)
        with wave.open(str(out / f"endpoint_{counts}.wav"), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(RATE)
            wav.writeframes(pcm.tobytes())


def build_ambience_orientation_probe():
    out = OUT.parent / "live" / "round-39"
    t = time(2.0)
    for name, frequency in (("orientation_low", 108), ("orientation_high", 114)):
        save(name, .22*np.sin(2*np.pi*frequency*t), out)


def build_ambience_centroid_above_probe():
    out = OUT.parent / "live" / "round-38"
    t = time(2.0)
    for name, frequency in (("ambience_above", 65), ("ambience_above_alt", 75)):
        save(name, .22*np.sin(2*np.pi*frequency*t), out)


def build_ambience_centroid_below_probe():
    out = OUT.parent / "live" / "round-37"
    t = time(2.0)
    for name, frequency in (("ambience_probe", 60), ("ambience_probe_alt", 64)):
        save(name, .22*np.sin(2*np.pi*frequency*t), out)


def main(broken=False, slope_probe=False, flat_probe=False, layer_flat_probe=False, join_probe=False, layer_slope_probe=False, layer_alt_flat_probe=False, layer_alt_join_probe=False, layer_alt_slope_probe=False, layer_alt_reverse_probe=False, layer_third_slope_probe=False, layer_third_slope_edge_pass=False, layer_third_slope_edge_fail=False, layer_third_join_probe=False, layer_third_join_edge_pass=False, layer_third_join_edge_fail=False):
    if slope_probe:
        t_probe = time(1)
        probe = .30 * np.sin(2*np.pi*220*t_probe)
        probe[0], probe[1], probe[-2], probe[-1] = 0., .45, .02, 0.
        save("slope_probe", probe, OUT.parent / "live" / "round-3")
    rng = np.random.default_rng(20261012)
    t = time(.12)
    save("ui", .38 * np.sin(2 * np.pi * (700*t + 800*t*t)) * np.exp(-30*t))
    t = time(.16)
    save("ui_alt", .32 * np.sin(2 * np.pi * (1200*t + 1200*t*t)) * np.exp(-18*t))
    t = time(.20)
    save("ui_third", .38 * np.sin(2 * np.pi * (700*t + 800*t*t)) * np.exp(-30*t))
    t = time(.32)
    noise = rng.standard_normal(len(t))
    save("impact", .40 * np.sin(2*np.pi*90*t) * np.exp(-16*t)
         + .23 * noise * np.exp(-65*t))
    save("impact_alt", .55*np.sin(2*np.pi*95*t)*np.exp(-14*t)
         + .25*np.sin(2*np.pi*340*t)*np.exp(-35*t)
         + .12*np.sin(2*np.pi*900*t)*np.exp(-50*t))
    t = time(.40)
    impact_noise = np.random.default_rng(3401).standard_normal(len(t))
    save("impact_third", .38*np.sin(2*np.pi*2200*t)*np.exp(-11*t)
         + .045*impact_noise*np.exp(-80*t))
    t = time(.24)
    noise = rng.standard_normal(len(t))
    # A short broadband step, with a rounded onset and decay.
    save("movement", .24 * noise * (1-np.exp(-250*t)) * np.exp(-22*t))
    t = time(.36)
    noise_alt = np.random.default_rng(20261013).standard_normal(len(t))
    save("movement_alt", .30 * noise_alt * (1-np.exp(-180*t)) * np.exp(-15*t))
    t = time(.30)
    movement_rng = np.random.default_rng(3501)
    movement_env = np.sin(np.pi*np.minimum(t/.012, 1)/2)**2 * np.exp(-t/.20)
    movement_third = .52*movement_env*np.sin(2*np.pi*1800*t)
    movement_attack = np.zeros(len(t))
    attack_count = round(.012*RATE)
    movement_attack[:attack_count] = movement_rng.normal(0, .07, attack_count) * np.exp(-np.arange(attack_count)/(RATE*.003))
    movement_third += movement_attack
    movement_third *= np.minimum(np.arange(len(t))/(RATE*.002), 1)
    save("movement_third", np.clip(movement_third, -.9, .9))
    t = time(2)
    ambience = .15*np.sin(2*np.pi*12*t) + .09*np.sin(2*np.pi*36*t)
    if broken:
        ambience[-round(.02*RATE):] += .5
    save("ambience", ambience)
    save("ambience_alt", .15*np.sin(2*np.pi*20*t) + .09*np.sin(2*np.pi*60*t)
         + .06*np.sin(2*np.pi*100*t))
    save("ambience_third", .20*np.sin(2*np.pi*90*t) + .025*np.sin(2*np.pi*130*t))
    t = time(2)
    save("stem", .23*np.sin(2*np.pi*220*t) + .11*np.sin(2*np.pi*330*t))
    t = time(4)
    common = .08*np.sin(2*np.pi*220*t) + .04*np.sin(2*np.pi*330*t)
    save("stem_sections", common + np.where(t < 2, .012, .060)*np.sin(2*np.pi*30*t))
    save("stem_layer", np.where(t < 2, .012, .060)*np.sin(2*np.pi*120*t))
    save("stem_layer_alt", np.where(t < 2, .015, .050)*np.sin(2*np.pi*180*t))
    save("stem_layer_third", np.where(t < 2, .015, .050)*np.sin(2*np.pi*200*t))
    if layer_third_slope_probe:
        with wave.open(str(OUT / "stem_layer_third.wav"), "rb") as wav:
            frames = np.frombuffer(wav.readframes(wav.getnframes()), dtype="<i2").copy()
        frames[96001] += 8
        out = OUT.parent / "live" / "round-18"
        out.mkdir(parents=True, exist_ok=True)
        with wave.open(str(out / "slope200_probe.wav"), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(RATE)
            wav.writeframes(frames.tobytes())
    for enabled, offset, filename in ((layer_third_slope_edge_pass, 2, "edgepass_probe.wav"),
                                      (layer_third_slope_edge_fail, 3, "edgefail_probe.wav")):
        if enabled:
            with wave.open(str(OUT / "stem_layer_third.wav"), "rb") as wav:
                frames = np.frombuffer(wav.readframes(wav.getnframes()), dtype="<i2").copy()
            frames[96001] += offset
            out = OUT.parent / "live" / "round-19"
            out.mkdir(parents=True, exist_ok=True)
            with wave.open(str(out / filename), "wb") as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(RATE)
                wav.writeframes(frames.tobytes())
    if layer_third_join_probe:
        # Canonical-copy two-sample step at 200 Hz throws the full-signal centroid
        # above the existing 2000 Hz band (measured 2195.8 Hz). Same pattern as the
        # 180 Hz join: keep the stepped 200 Hz layer and add the original 220/330 Hz
        # bed, then edit only the two join frames. Not a canonical rewrite.
        base = (np.where(t < 2, .015, .050)*np.sin(2*np.pi*200*t)
                + .08*np.sin(2*np.pi*220*t) + .04*np.sin(2*np.pi*330*t))
        frames = np.round(np.clip(base, -1, 1)*32767).astype("<i2")
        # s[95999] is -145; gap counts = target-(-145). .03*32768 = 983.04,
        # so target >= 839. 839 is the smallest integer that crosses .03 FS
        # while the preserved left step keeps side-slope at 0.
        frames[96000] = 839
        frames[96001] = frames[96000] + frames[95999] - frames[95998]
        out = OUT.parent / "live" / "round-20"
        out.mkdir(parents=True, exist_ok=True)
        with wave.open(str(out / "join200_probe.wav"), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(RATE)
            wav.writeframes(frames.tobytes())
    for enabled, gap_counts, name in ((layer_third_join_edge_pass, 983, "join200_edgepass_probe"),
                                      (layer_third_join_edge_fail, 984, "join200_edgefail_probe")):
        if enabled:
            base = (np.where(t < 2, .015, .050)*np.sin(2*np.pi*200*t)
                    + .08*np.sin(2*np.pi*220*t) + .04*np.sin(2*np.pi*330*t))
            frames = np.round(np.clip(base, -1, 1)*32767).astype("<i2")
            frames[96000] = frames[95999] + gap_counts
            frames[96001] = frames[96000] + frames[95999] - frames[95998]
            out = OUT.parent / "live" / "round-21"
            out.mkdir(parents=True, exist_ok=True)
            with wave.open(str(out / (name + ".wav")), "wb") as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(RATE)
                wav.writeframes(frames.tobytes())
    if layer_alt_reverse_probe:
        save("reverse180_probe", np.where(t < 2, .050, .015)*np.sin(2*np.pi*180*t),
             OUT.parent / "live" / "round-16")
    if layer_alt_slope_probe:
        with wave.open(str(OUT / "stem_layer_alt.wav"), "rb") as wav:
            frames = np.frombuffer(wav.readframes(wav.getnframes()), dtype="<i2").copy()
        frames[96001] += round(.0004*32767)
        out = OUT.parent / "live" / "round-15"
        out.mkdir(parents=True, exist_ok=True)
        with wave.open(str(out / "slope180_probe.wav"), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(RATE)
            wav.writeframes(frames.tobytes())
    if layer_alt_join_probe:
        base = (np.where(t < 2, .015, .050)*np.sin(2*np.pi*180*t)
                + .08*np.sin(2*np.pi*220*t) + .04*np.sin(2*np.pi*330*t))
        frames = np.round(np.clip(base, -1, 1)*32767).astype("<i2")
        frames[96000] = round(.040*32767)
        frames[96001] = frames[96000] + frames[95999] - frames[95998]
        out = OUT.parent / "live" / "round-14"
        out.mkdir(parents=True, exist_ok=True)
        with wave.open(str(out / "join180_probe.wav"), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(RATE)
            wav.writeframes(frames.tobytes())
    if join_probe:
        with wave.open(str(OUT / "stem_layer.wav"), "rb") as wav:
            source = np.frombuffer(wav.readframes(wav.getnframes()), dtype="<i2").astype(np.float64) / 32767
        frames = np.round(np.clip(source + .03*np.sin(2*np.pi*60*t), -1, 1)*32767).astype("<i2")
        frames[96000] = round(.0305*32767)
        out = OUT.parent / "live" / "round-10"
        out.mkdir(parents=True, exist_ok=True)
        with wave.open(str(out / "join_probe.wav"), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(RATE)
            wav.writeframes(frames.tobytes())
    if layer_slope_probe:
        with wave.open(str(OUT / "stem_layer.wav"), "rb") as wav:
            samples = np.frombuffer(wav.readframes(wav.getnframes()), dtype="<i2").copy()
        samples[96001] = round(samples[96001] + .0004*32767)
        out = OUT.parent / "live" / "round-11"
        out.mkdir(parents=True, exist_ok=True)
        with wave.open(str(out / "slope_probe.wav"), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(RATE)
            wav.writeframes(samples.tobytes())
    if layer_alt_flat_probe:
        save("flat180_probe", .036*np.sin(2*np.pi*180*t),
             OUT.parent / "live" / "round-13")
    if layer_flat_probe:
        save("flat120_probe", .036*np.sin(2*np.pi*120*t),
             OUT.parent / "live" / "round-8")
    if flat_probe:
        save("flat30_probe", common + .036*np.sin(2*np.pi*30*t),
             OUT.parent / "live" / "round-4")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--probe-failing", action="store_true")
    parser.add_argument("--probe-slope", action="store_true")
    parser.add_argument("--probe-flat", action="store_true")
    parser.add_argument("--probe-layer-flat", action="store_true")
    parser.add_argument("--probe-layer-join", action="store_true")
    parser.add_argument("--probe-layer-slope", action="store_true")
    parser.add_argument("--probe-layer-alt-flat", action="store_true")
    parser.add_argument("--probe-layer-alt-join", action="store_true")
    parser.add_argument("--probe-layer-alt-slope", action="store_true")
    parser.add_argument("--probe-layer-alt-reverse", action="store_true")
    parser.add_argument("--probe-layer-third-slope", action="store_true")
    parser.add_argument("--probe-layer-third-slope-edge-pass", action="store_true")
    parser.add_argument("--probe-layer-third-slope-edge-fail", action="store_true")
    parser.add_argument("--probe-layer-third-join", action="store_true")
    parser.add_argument("--probe-layer-third-join-edge-pass", action="store_true")
    parser.add_argument("--probe-layer-third-join-edge-fail", action="store_true")
    parser.add_argument("--probe-invalid", action="store_true")
    parser.add_argument("--probe-ui-clone", action="store_true")
    parser.add_argument("--probe-ui-duration-below", action="store_true")
    parser.add_argument("--probe-ui-duration-at", action="store_true")
    parser.add_argument("--probe-ui-centroid-below", action="store_true")
    parser.add_argument("--probe-ui-centroid-above", action="store_true")
    parser.add_argument("--probe-ui-lower-centroid-below", action="store_true")
    parser.add_argument("--probe-ui-lower-centroid-above", action="store_true")
    parser.add_argument("--probe-ui-orientation-forward", action="store_true")
    parser.add_argument("--probe-ui-orientation-reverse", action="store_true")
    parser.add_argument("--probe-ui-joint-below", action="store_true")
    parser.add_argument("--probe-ui-mixed-pass", action="store_true")
    parser.add_argument("--probe-ambience-centroid-below", action="store_true")
    parser.add_argument("--probe-ambience-centroid-above", action="store_true")
    parser.add_argument("--probe-ambience-orientation-forward", action="store_true")
    parser.add_argument("--probe-ambience-orientation-reverse", action="store_true")
    parser.add_argument("--probe-outer-endpoint-983", action="store_true")
    parser.add_argument("--probe-outer-endpoint-984", action="store_true")
    parser.add_argument("--probe-outer-slope-32", action="store_true")
    parser.add_argument("--probe-outer-slope-33", action="store_true")
    parser.add_argument("--probe-ui-peak-31129", action="store_true")
    parser.add_argument("--probe-ui-peak-31130", action="store_true")
    parser.add_argument("--probe-ui-crest-46", action="store_true")
    parser.add_argument("--probe-ui-crest-47", action="store_true")
    parser.add_argument("--probe-ui-tolerance-5807", action="store_true")
    parser.add_argument("--probe-ui-tolerance-5809", action="store_true")
    parser.add_argument("--probe-ui-lower-tolerance-5713", action="store_true")
    parser.add_argument("--probe-ui-lower-tolerance-5711", action="store_true")
    parser.add_argument("--probe-ui-absolute-centroid-below", action="store_true")
    parser.add_argument("--probe-ui-absolute-centroid-above", action="store_true")
    parser.add_argument("--probe-ui-upper-centroid-below", action="store_true")
    parser.add_argument("--probe-ui-upper-centroid-above", action="store_true")
    parser.add_argument("--probe-ui-rate-47999", action="store_true")
    parser.add_argument("--probe-ui-rate-48000", action="store_true")
    parser.add_argument("--probe-ui-rate-48001", action="store_true")
    parser.add_argument("--probe-ui-rate-48000-r49", action="store_true")
    parser.add_argument("--probe-ui-channel-stereo", action="store_true")
    parser.add_argument("--probe-ui-channel-mono", action="store_true")
    parser.add_argument("--probe-ui-pcm24", action="store_true")
    parser.add_argument("--probe-ui-pcm16", action="store_true")
    parser.add_argument("--probe-ui-pcm8", action="store_true")
    parser.add_argument("--probe-ui-pcm16-r52", action="store_true")
    parser.add_argument("--probe-ui-float32", action="store_true")
    parser.add_argument("--probe-ui-pcm16-r53", action="store_true")
    parser.add_argument("--probe-ui-pcm32", action="store_true")
    parser.add_argument("--probe-ui-pcm16-r54", action="store_true")
    parser.add_argument("--probe-ui-extensible-pcm16", action="store_true")
    parser.add_argument("--probe-ui-standard-pcm16-r55", action="store_true")
    parser.add_argument("--probe-ui-extensible-mask-zero", action="store_true")
    parser.add_argument("--probe-ui-extensible-mask-center", action="store_true")
    parser.add_argument("--probe-ui-extensible-valid-15", action="store_true")
    parser.add_argument("--probe-ui-extensible-valid-16", action="store_true")
    parser.add_argument("--probe-ui-extensible-valid-14-r58", action="store_true")
    parser.add_argument("--probe-ui-extensible-valid-16-r58", action="store_true")
    parser.add_argument("--probe-ui-extensible-valid-13-r59", action="store_true")
    parser.add_argument("--probe-ui-extensible-valid-16-r59", action="store_true")
    parser.add_argument("--probe-ui-extensible-valid-0-r60", action="store_true")
    parser.add_argument("--probe-ui-extensible-valid-16-r60", action="store_true")
    parser.add_argument("--probe-ui-extensible-valid-17-r61", action="store_true")
    parser.add_argument("--probe-ui-extensible-valid-16-r61", action="store_true")
    parser.add_argument("--probe-ui-extensible-valid-24-r62", action="store_true")
    parser.add_argument("--probe-ui-extensible-valid-32-r62", action="store_true")
    parser.add_argument("--probe-ui-route-act-84-r63", action="store_true")
    parser.add_argument("--probe-ui-route-act-00-r63", action="store_true")
    parser.add_argument("--probe-ui-extensible-valid-8-r64", action="store_true")
    parser.add_argument("--probe-ui-extensible-valid-9-r64", action="store_true")
    parser.add_argument("--probe-ui-extensible-valid-24-r64", action="store_true")
    parser.add_argument("--probe-ui-extensible-valid-25-r64", action="store_true")
    parser.add_argument("--probe-ui-extensible-valid-56-r64", action="store_true")
    parser.add_argument("--probe-ui-extensible-valid-57-r64", action="store_true")
    parser.add_argument("--probe-ui-preempt-act-r65", action="store_true")
    parser.add_argument("--probe-ui-preempt-gsrt-r65", action="store_true")
    parser.add_argument("--probe-ui-preempt-hcom-r65", action="store_true")
    parser.add_argument("--probe-ui-preempt-both-r65", action="store_true")
    parser.add_argument("--probe-ui-dec-hcom-r66", action="store_true")
    parser.add_argument("--probe-ui-dec-act-r66", action="store_true")
    parser.add_argument("--probe-ui-lengate-gsrt-24-r66", action="store_true")
    parser.add_argument("--probe-ui-lengate-gsrt-25-r66", action="store_true")
    parser.add_argument("--probe-ui-lengate-hcom-131-r66", action="store_true")
    parser.add_argument("--probe-ui-lengate-hcom-132-r66", action="store_true")
    args = parser.parse_args()
    if (args.probe_ui_dec_hcom_r66 or args.probe_ui_dec_act_r66
            or args.probe_ui_lengate_gsrt_24_r66 or args.probe_ui_lengate_gsrt_25_r66
            or args.probe_ui_lengate_hcom_131_r66 or args.probe_ui_lengate_hcom_132_r66):
        main()
        build_ui_dec_preempt_r66_probe()
        build_ui_lengate_r66_probe()
    elif (args.probe_ui_preempt_act_r65 or args.probe_ui_preempt_gsrt_r65
            or args.probe_ui_preempt_hcom_r65 or args.probe_ui_preempt_both_r65):
        main()
        build_ui_preempt_r65_probe()
    elif (args.probe_ui_extensible_valid_8_r64 or args.probe_ui_extensible_valid_9_r64
            or args.probe_ui_extensible_valid_24_r64 or args.probe_ui_extensible_valid_25_r64
            or args.probe_ui_extensible_valid_56_r64 or args.probe_ui_extensible_valid_57_r64):
        main()
        build_ui_validbits_steps_r64_probe()
    elif args.probe_ui_route_act_84_r63 or args.probe_ui_route_act_00_r63:
        main()
        build_ui_route_act_r63_probe()
    elif args.probe_ui_extensible_valid_24_r62 or args.probe_ui_extensible_valid_32_r62:
        main()
        build_ui_extensible_valid24_probe()
    elif args.probe_ui_extensible_valid_17_r61 or args.probe_ui_extensible_valid_16_r61:
        main()
        build_ui_extensible_valid17_probe()
    elif args.probe_ui_extensible_valid_0_r60 or args.probe_ui_extensible_valid_16_r60:
        main()
        build_ui_extensible_valid0_probe()
    elif args.probe_ui_extensible_valid_13_r59 or args.probe_ui_extensible_valid_16_r59:
        main()
        build_ui_extensible_valid13_probe()
    elif args.probe_ui_extensible_valid_14_r58 or args.probe_ui_extensible_valid_16_r58:
        main()
        build_ui_extensible_valid14_probe()
    elif args.probe_ui_extensible_valid_15 or args.probe_ui_extensible_valid_16:
        main()
        build_ui_extensible_valid_bits_probe()
    elif args.probe_ui_extensible_mask_zero or args.probe_ui_extensible_mask_center:
        main()
        build_ui_extensible_mask_probe()
    elif args.probe_ui_extensible_pcm16 or args.probe_ui_standard_pcm16_r55:
        main()
        build_ui_extensible_pcm16_probe()
    elif args.probe_ui_pcm32 or args.probe_ui_pcm16_r54:
        main()
        build_ui_pcm32_probe()
    elif args.probe_ui_float32 or args.probe_ui_pcm16_r53:
        main()
        build_ui_float32_probe()
    elif args.probe_ui_pcm8 or args.probe_ui_pcm16_r52:
        main()
        build_ui_pcm8_probe()
    elif args.probe_ui_pcm24 or args.probe_ui_pcm16:
        main()
        build_ui_pcm_depth_probe()
    elif args.probe_ui_channel_stereo or args.probe_ui_channel_mono:
        main()
        build_ui_channel_probe()
    elif args.probe_ui_rate_48001 or args.probe_ui_rate_48000_r49:
        main()
        build_ui_rate_above_probe()
    elif args.probe_ui_rate_47999 or args.probe_ui_rate_48000:
        main()
        build_ui_rate_probe()
    elif args.probe_ui_upper_centroid_below or args.probe_ui_upper_centroid_above:
        main()
        build_ui_upper_centroid_probe()
    elif args.probe_ui_absolute_centroid_below or args.probe_ui_absolute_centroid_above:
        main()
        build_ui_absolute_centroid_probe()
    elif args.probe_ui_lower_tolerance_5713 or args.probe_ui_lower_tolerance_5711:
        main()
        build_ui_lower_tolerance_probe()
    elif args.probe_ui_tolerance_5807 or args.probe_ui_tolerance_5809:
        main()
        build_ui_tolerance_probe()
    elif args.probe_ui_crest_46 or args.probe_ui_crest_47:
        main()
        build_ui_crest_probe()
    elif args.probe_ui_peak_31129 or args.probe_ui_peak_31130:
        main()
        build_ui_peak_probe()
    elif args.probe_outer_slope_32 or args.probe_outer_slope_33:
        main()
        build_outer_slope_probe()
    elif args.probe_outer_endpoint_983 or args.probe_outer_endpoint_984:
        main()
        build_outer_endpoint_probe()
    elif args.probe_ambience_orientation_forward or args.probe_ambience_orientation_reverse:
        main()
        build_ambience_orientation_probe()
    elif args.probe_ambience_centroid_above:
        main()
        build_ambience_centroid_above_probe()
    elif args.probe_ambience_centroid_below:
        main()
        build_ambience_centroid_below_probe()
    elif args.probe_ui_mixed_pass:
        main()
        build_ui_mixed_pass_probe()
    elif args.probe_ui_joint_below:
        main()
        build_ui_joint_below_probe()
    elif args.probe_ui_orientation_forward or args.probe_ui_orientation_reverse:
        main()
        build_ui_orientation_probe(args.probe_ui_orientation_reverse)
    elif args.probe_ui_lower_centroid_below or args.probe_ui_lower_centroid_above:
        main()
        build_ui_lower_centroid_probe(.95 if args.probe_ui_lower_centroid_below else .94,
                                      "below" if args.probe_ui_lower_centroid_below else "above")
    elif args.probe_ui_centroid_below or args.probe_ui_centroid_above:
        main()
        build_ui_centroid_probe(1.11 if args.probe_ui_centroid_below else 1.10,
                                "below" if args.probe_ui_centroid_below else "above")
    elif args.probe_ui_duration_below or args.probe_ui_duration_at:
        main()
        build_ui_duration_probe(6719 if args.probe_ui_duration_below else 6720,
                                "below" if args.probe_ui_duration_below else "at")
    elif args.probe_ui_clone:
        main()
        build_ui_clone_probe()
    elif args.probe_invalid:
        build_invalid_probes()
        build_width_probes()
        build_rate_channel_probes()
    else:
        main(args.probe_failing, args.probe_slope, args.probe_flat, args.probe_layer_flat, args.probe_layer_join, args.probe_layer_slope, args.probe_layer_alt_flat, args.probe_layer_alt_join, args.probe_layer_alt_slope, args.probe_layer_alt_reverse, args.probe_layer_third_slope, args.probe_layer_third_slope_edge_pass, args.probe_layer_third_slope_edge_fail, args.probe_layer_third_join, args.probe_layer_third_join_edge_pass, args.probe_layer_third_join_edge_fail)
