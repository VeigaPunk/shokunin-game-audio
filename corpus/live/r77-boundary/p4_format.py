"""r77 BOUNDARY probe 4 — format-axis edges + 24-bit roundtrip truth.

Tone-anchored: every leg captures the default sink's monitor while a 1 kHz tone
plays into that sink, so "did the conversion keep the signal" is measurable
(FFT peak frequency + level), not assumed.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from r77b_lib import (  # noqa: E402
    SCRATCH,
    SPDIF_SINK,
    TONE,
    inspect_wav,
    make_tone,
    reap,
    save_receipt,
    spawn,
    wipe_scratch,
)


def cap(tag, flags, seconds=2.0, rate=48000, timeout=20.0):
    out = SCRATCH / f"f_{tag}.wav"
    n = int(seconds * rate)
    cmd = ["pw-record", "-P", "stream.capture.sink=true", "--target", SPDIF_SINK]
    cmd += flags + ["-n", str(n), str(out)]
    p = spawn(cmd)
    time.sleep(0.35)
    pl = spawn(["pw-cat", "-p", "--target", SPDIF_SINK, str(TONE)])
    t0 = time.monotonic()
    r = reap(p, timeout=timeout)
    wall = round(time.monotonic() - t0, 3)
    reap(pl, timeout=6)
    insp = inspect_wav(out)
    keep = ("bytes", "riff_size_field", "data_declared", "data_declared_field", "frames", "fmt",
            "peak", "nonzero_frac", "fft_peak_hz", "payload_bytes_actual", "chunks")
    d = {k: insp.get(k) for k in keep}
    d.update(tag=tag, cmd=" ".join(cmd), rc=r["rc"], killed=r["killed_by_us"],
             err=r["err"].strip()[:200], wall=wall, out=str(out))
    return d


def channel_peaks(path):
    """Per-channel peak for a multichannel capture (which channels carry the tone?)."""
    from r77b_lib import chunk_walk

    raw = Path(path).read_bytes()
    body, dsize, fmt, _ = chunk_walk(raw)
    if body is None or not fmt:
        return None
    ch = fmt["channels"]
    bits = fmt["bits"]
    ba = fmt["block_align"]
    frames = min(dsize, len(raw) - body) // ba
    if bits != 16:
        return {"note": f"channel split only implemented for s16 (bits={bits})", "channels": ch}
    a = np.frombuffer(raw[body : body + frames * ba], dtype="<i2").reshape(frames, ch)
    return {"channels": ch, "per_channel_peak": [int(np.abs(a[:, c]).max()) for c in range(ch)],
            "per_channel_rms": [round(float(np.sqrt((a[:, c].astype(float) ** 2).mean())), 1) for c in range(ch)]}


def s16_mono(path):
    from r77b_lib import chunk_walk

    raw = Path(path).read_bytes()
    body, dsize, fmt, _ = chunk_walk(raw)
    if body is None or fmt.get("bits") != 16:
        return None
    ch, ba = fmt["channels"], fmt["block_align"]
    frames = min(dsize, len(raw) - body) // ba
    a = np.frombuffer(raw[body : body + frames * ba], dtype="<i2").reshape(frames, ch)
    return a[:, 0].astype(np.float64) / 32768.0


def s24_mono(path):
    """Decode a 24-bit capture to normalized float, honouring block_align."""
    from r77b_lib import chunk_walk

    raw = Path(path).read_bytes()
    body, dsize, fmt, _ = chunk_walk(raw)
    if body is None:
        return None, None
    ch, ba, bits = fmt["channels"], fmt["block_align"], fmt["bits"]
    frames = min(dsize, len(raw) - body) // ba
    payload = raw[body : body + frames * ba]
    per = ba // ch
    if per == 3:
        b = np.frombuffer(payload, dtype=np.uint8).reshape(frames, ch, 3)
        v = (b[:, :, 0].astype(np.int32) | (b[:, :, 1].astype(np.int32) << 8)
             | (b[:, :, 2].astype(np.int32) << 16))
        v = np.where(v >= (1 << 23), v - (1 << 24), v).astype(np.int64)
        scale = float(1 << 23)
    else:
        q = np.frombuffer(payload, dtype="<i4").reshape(frames, ch).astype(np.int64)
        v = q >> 8
        scale = float(1 << 23)
    return (v[:, 0].astype(np.float64) / scale), {"block_align": ba, "per_sample_bytes": per,
                                                  "bits_field": bits, "channels": ch,
                                                  "container": "packed3" if per == 3 else "padded4"}


def main():
    wipe_scratch()
    make_tone()
    rec = {"probe": "r77-boundary/p4-format", "t0": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

    legs = {}
    legs["baseline_s16_2ch_48k"] = cap("baseline", [])
    legs["rate8000_ch1"] = cap("r8000c1", ["--rate", "8000", "--channels", "1"], rate=8000)
    legs["rate96000_ch1"] = cap("r96c1", ["--rate", "96000", "--channels", "1"], rate=96000)
    legs["rate8000_ch2"] = cap("r8000c2", ["--rate", "8000", "--channels", "2"], rate=8000)
    legs["rate44100_ch1"] = cap("r44100c1", ["--rate", "44100", "--channels", "1"], rate=44100)
    legs["rate11025_ch2"] = cap("r11025c2", ["--rate", "11025", "--channels", "2"], rate=11025)
    legs["rate192000_ch2"] = cap("r192c2", ["--rate", "192000", "--channels", "2"], rate=192000)
    legs["fmt_s24"] = cap("s24", ["--format", "s24"])
    legs["fmt_s24_r8000_c1"] = cap("s24r8c1", ["--format", "s24", "--rate", "8000", "--channels", "1"], rate=8000)
    legs["fmt_s32"] = cap("s32", ["--format", "s32"])
    legs["fmt_f32"] = cap("f32", ["--format", "f32"])
    legs["fmt_u8"] = cap("u8", ["--format", "u8"])
    legs["ch6_upmix"] = cap("ch6", ["--channels", "6"])
    legs["ch1_map_FL"] = cap("ch1FL", ["--channels", "1", "--channel-map", "FL"])
    legs["q0"] = cap("q0", ["--quality", "0"])
    legs["q15"] = cap("q15", ["--quality", "15"])
    legs["q15_r8000_c1"] = cap("q15r8c1", ["--quality", "15", "--rate", "8000", "--channels", "1"], rate=8000)
    # container axis: is the advertised 64-bit container actually usable?
    legs["container_rf64"] = cap("rf64", ["--container", "rf64"])
    legs["container_w64"] = cap("w64", ["--container", "w64"])
    legs["container_caf"] = cap("caf", ["--container", "caf"])
    legs["container_raw"] = cap("raw", ["--container", "raw"])
    legs["container_wav_explicit"] = cap("wavx", ["--container", "wav"])
    rec["legs"] = legs

    # multichannel content map
    rec["ch6_channels"] = channel_peaks(legs["ch6_upmix"]["out"])

    # 24-bit roundtrip truth: compare normalized waveform against the s16 baseline
    base = s16_mono(legs["baseline_s16_2ch_48k"]["out"])
    s24, meta = s24_mono(legs["fmt_s24"]["out"])
    rt = {"s24_meta": meta}
    if base is not None and s24 is not None:
        m = min(base.size, s24.size)
        b, s = base[:m], s24[:m]
        d = s - b
        rt.update(
            compared_frames=m,
            base_rms=round(float(np.sqrt((b ** 2).mean())), 8),
            s24_rms=round(float(np.sqrt((s ** 2).mean())), 8),
            rms_ratio=round(float(np.sqrt((s ** 2).mean()) / max(np.sqrt((b ** 2).mean()), 1e-12)), 6),
            max_abs_delta_lsb_s16=round(float(np.abs(d).max() * 32768), 3),
            rms_delta_lsb_s16=round(float(np.sqrt((d ** 2).mean()) * 32768), 4),
            s24_quantisation_floor_lsb_s16=round(1 / 256, 6),
        )
    rec["s24_roundtrip"] = rt

    save_receipt("probe-p4-format.json", rec)
    print("== format legs ==")
    for k, d in legs.items():
        f = d.get("fmt") or {}
        print(f"{k:22s} rc={d['rc']:>3} bytes={str(d['bytes']):>8} fmt=tag{f.get('tag')}/{f.get('channels')}ch/"
              f"{f.get('rate')}Hz/{f.get('bits')}b ba={f.get('block_align')} frames={d.get('frames')} "
              f"peak={d.get('peak')} fft={d.get('fft_peak_hz')} data={d.get('data_declared_field')} err={d['err'][:40]}")
    print("== ch6 channel map ==", rec["ch6_channels"])
    print("== s24 roundtrip ==", rec["s24_roundtrip"])


if __name__ == "__main__":
    main()
