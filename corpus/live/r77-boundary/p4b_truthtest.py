"""r77 BOUNDARY probe 4b — format truth, done phase-independently.

p4's s24 "roundtrip delta" was dominated by capture-to-capture PHASE offset, not
quantisation: the tone restarts each leg, so sample-wise comparison is
meaningless without alignment. This probe replaces it with phase-independent
tests:
  * s24 samples must be an exact left shift of the s16 source (all % 256 == 0),
    s32 all % 65536 == 0;
  * f32 peak in float units (p4 decoded tag-3 data as int32 by mistake);
  * aligned cross-correlation residual for the s24 leg;
  * the 4 GiB WAV boundary on the pw-record/libsndfile side (arecord's sentinel
    has no counterpart here, and pw-record's own rf64/w64 containers fail).
"""

from __future__ import annotations

import json
import shutil
import sys
import threading
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from r77b_lib import (  # noqa: E402
    SPDIF_SINK,
    SCRATCH,
    TONE,
    chunk_walk,
    inspect_wav,
    make_tone,
    reap,
    save_receipt,
    sh,
    spawn,
    wipe_scratch,
)

PROP = ["-P", "stream.capture.sink=true"]


def cap(tag, flags, seconds=2.0, rate=48000, timeout=20.0):
    out = SCRATCH / f"g_{tag}.wav"
    cmd = ["pw-record"] + PROP + ["--target", SPDIF_SINK] + flags + ["-n", str(int(seconds * rate)), str(out)]
    p = spawn(cmd)
    time.sleep(0.35)
    pl = spawn(["pw-cat", "-p", "--target", SPDIF_SINK, str(TONE)])
    t0 = time.monotonic()
    r = reap(p, timeout=timeout)
    wall = round(time.monotonic() - t0, 3)
    reap(pl, timeout=6)
    insp = inspect_wav(out)
    return {"tag": tag, "cmd": " ".join(cmd), "rc": r["rc"], "wall": wall, "err": r["err"].strip()[:160],
            "out": str(out), "bytes": insp.get("bytes"), "fmt": insp.get("fmt"),
            "frames": insp.get("frames"), "peak": insp.get("peak"), "nz": round(insp.get("nonzero_frac") or 0, 4),
            "fft_hz": insp.get("fft_peak_hz"), "data": insp.get("data_declared_field")}


def payload(path):
    raw = Path(path).read_bytes()
    body, dsize, fmt, _ = chunk_walk(raw)
    if body is None:
        return None, None, None
    n = min(dsize, len(raw) - body)
    return raw[body : body + n], fmt, n


def decode_s16(path):
    p, fmt, _ = payload(path)
    if p is None or fmt.get("bits") != 16:
        return None
    ch, ba = fmt["channels"], fmt["block_align"]
    f = len(p) // ba
    return np.frombuffer(p[: f * ba], dtype="<i2").reshape(f, ch)[:, 0].astype(np.int64)


def decode_s24_packed(path):
    p, fmt, _ = payload(path)
    if p is None:
        return None, fmt
    ch, ba = fmt["channels"], fmt["block_align"]
    per = ba // ch
    f = len(p) // ba
    if per == 3:
        b = np.frombuffer(p[: f * ba], dtype=np.uint8).reshape(f, ch, 3)
        v = (b[:, :, 0].astype(np.int64) | (b[:, :, 1].astype(np.int64) << 8)
             | (b[:, :, 2].astype(np.int64) << 16))
        v = np.where(v >= (1 << 23), v - (1 << 24), v)
        return v[:, 0], fmt
    q = np.frombuffer(p[: f * ba], dtype="<i4").reshape(f, ch)[:, 0].astype(np.int64)
    return q >> 8, fmt


def decode_s32(path):
    p, fmt, _ = payload(path)
    if p is None:
        return None, fmt
    ch, ba = fmt["channels"], fmt["block_align"]
    f = len(p) // ba
    return np.frombuffer(p[: f * ba], dtype="<i4").reshape(f, ch)[:, 0].astype(np.int64), fmt


def decode_f32(path):
    p, fmt, _ = payload(path)
    if p is None:
        return None, fmt
    ch, ba = fmt["channels"], fmt["block_align"]
    f = len(p) // ba
    return np.frombuffer(p[: f * ba], dtype="<f4").reshape(f, ch)[:, 0].astype(np.float64), fmt


def aligned_residual(a, b):
    """Best-lag alignment by FFT cross-correlation, then residual stats."""
    n = min(a.size, b.size)
    x, y = a[:n].astype(np.float64), b[:n].astype(np.float64)
    X = np.fft.rfft(x - x.mean(), 2 * n)
    Y = np.fft.rfft(y - y.mean(), 2 * n)
    cc = np.fft.irfft(X * np.conj(Y))
    lag = int(np.argmax(cc))
    if lag > n:
        lag -= 2 * n
    ys = np.roll(y, -lag)
    d = ys - x
    # ignore the wrap seam
    lo, hi = 64, n - 64
    d = d[lo:hi]
    return {"lag_samples": lag, "max_abs_residual": float(np.abs(d).max()),
            "rms_residual": float(np.sqrt((d ** 2).mean())),
            "in_s16_lsb": {"max": round(float(np.abs(d).max()) / 256, 4),
                           "rms": round(float(np.sqrt((d ** 2).mean())) / 256, 5)}}


class SizeMon(threading.Thread):
    def __init__(self, path, stop_evt, interval=0.25, cap_bytes=5.6e9, min_free=3.0e9):
        super().__init__(daemon=True)
        self.path, self.stop, self.interval = path, stop_evt, interval
        self.cap, self.min_free, self.samples, self.tripped = cap_bytes, min_free, [], None

    def run(self):
        t0 = time.monotonic()
        while not self.stop.is_set():
            try:
                sz = self.path.stat().st_size if self.path.exists() else None
            except OSError:
                sz = None
            free = shutil.disk_usage("/dev/shm").free
            self.samples.append((round(time.monotonic() - t0, 2), sz, round(free / 1e9, 2)))
            if sz and sz > self.cap:
                self.tripped = "cap_bytes"
                self.stop.set()
            if free < self.min_free:
                self.tripped = "min_free"
                self.stop.set()
            self.stop.wait(self.interval)


def four_gig_boundary():
    rec = {"free_gb_before": round(shutil.disk_usage("/dev/shm").free / 1e9, 2)}
    if rec["free_gb_before"] < 8.0:
        rec["skipped"] = "not enough tmpfs"
        return rec
    # fastest legal data rate: probe legality of a 64-channel leg first
    legal = sh(["pw-record"] + PROP + ["--target", SPDIF_SINK, "--rate", "768000", "--channels", "64",
                                       "--format", "f64", "-n", "1000", str(SCRATCH / "legal64.wav")], timeout=15)
    rec["legality_64ch"] = {"rc": legal["rc"], "bytes": (SCRATCH / "legal64.wav").stat().st_size
                            if (SCRATCH / "legal64.wav").exists() else None}
    ch = "64" if rec["legality_64ch"]["bytes"] and rec["legality_64ch"]["bytes"] > 1000 else "32"
    rec["channels_used"] = ch
    out = SCRATCH / "big.wav"
    cmd = ["pw-record"] + PROP + ["--target", SPDIF_SINK, "--rate", "768000", "--channels", ch,
                                  "--format", "f64", str(out)]
    stop = threading.Event()
    mon = SizeMon(out, stop)
    mon.start()
    p = spawn(cmd)
    t0 = time.monotonic()
    # let it run until the monitor trips or 100 s
    while not stop.is_set() and time.monotonic() - t0 < 100:
        time.sleep(0.2)
        if p.poll() is not None:
            break
    exited_on_its_own = p.poll() is not None
    if not exited_on_its_own:
        p.send_signal(9)
    r = reap(p, timeout=8)
    stop.set()
    mon.join(timeout=3)
    rec.update({
        "cmd": " ".join(cmd), "exited_on_its_own": exited_on_its_own, "rc": r["rc"],
        "err": r["err"].strip()[:400], "wall_s": round(time.monotonic() - t0, 2),
        "monitor_tripped": mon.tripped,
        "final_size": out.stat().st_size if out.exists() else None,
        "final_size_minus_4GiB": (out.stat().st_size - 2**32) if out.exists() else None,
        "size_samples_head": mon.samples[:6], "size_samples_tail": mon.samples[-6:],
        "free_gb_after": round(shutil.disk_usage("/dev/shm").free / 1e9, 2),
    })
    if out.exists():
        raw = out.read_bytes()[:64]
        rec["header_head_hex"] = raw[:48].hex()
        rec["riff_size_field"] = int.from_bytes(raw[4:8], "little") if len(raw) >= 8 else None
        rec["riff_size_field_hex"] = raw[4:8].hex()
    out.unlink(missing_ok=True)
    rec["free_gb_after_cleanup"] = round(shutil.disk_usage("/dev/shm").free / 1e9, 2)
    return rec


def main():
    wipe_scratch()
    make_tone()
    rec = {"probe": "r77-boundary/p4b-format-truth", "t0": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    # silence gate: a non-zero baseline means another client is feeding the sink
    base = cap("silence_baseline", [], seconds=1.5)
    rec["silence_baseline"] = {"peak": base["peak"], "nz": base["nz"], "confounded": bool((base["peak"] or 0) > 0)}

    legs = {}
    legs["s16_48k_2ch"] = cap("s16", [])
    legs["s24_48k_2ch"] = cap("s24", ["--format", "s24"])
    legs["s32_48k_2ch"] = cap("s32", ["--format", "s32"])
    legs["f32_48k_2ch"] = cap("f32", ["--format", "f32"])
    legs["r8000_c1"] = cap("r8000c1", ["--rate", "8000", "--channels", "1"], rate=8000)
    legs["r8000_c1_q15"] = cap("r8000c1q15", ["--rate", "8000", "--channels", "1", "--quality", "15"], rate=8000)
    legs["r44100_c2"] = cap("r44100c2", ["--rate", "44100", "--channels", "2"], rate=44100)
    rec["legs"] = legs

    truth = {}
    s16 = decode_s16(legs["s16_48k_2ch"]["out"])
    s24, f24 = decode_s24_packed(legs["s24_48k_2ch"]["out"])
    s32, f32meta = decode_s32(legs["s32_48k_2ch"]["out"])
    flt, _ = decode_f32(legs["f32_48k_2ch"]["out"])
    if s24 is not None:
        truth["s24_mod256_zero"] = bool(np.all(s24 % 256 == 0))
        truth["s24_distinct_mod256"] = sorted(set(np.unique(s24 % 256).tolist()))[:8]
        truth["s24_peak"] = int(np.abs(s24).max())
        truth["s24_peak_over_s16_peak"] = int(np.abs(s24).max()) / max(int(np.abs(s16).max()), 1)
    if s32 is not None:
        truth["s32_mod65536_zero"] = bool(np.all(s32 % 65536 == 0))
        truth["s32_peak"] = int(np.abs(s32).max())
        truth["s32_peak_over_s16_peak"] = int(np.abs(s32).max()) / max(int(np.abs(s16).max()), 1)
    if flt is not None:
        truth["f32_peak_float"] = round(float(np.abs(flt).max()), 6)
        truth["f32_expected_s16_over_32768"] = round(float(np.abs(s16).max()) / 32768.0, 6)
        truth["f32_ratio"] = round(float(np.abs(flt).max()) / max(float(np.abs(s16).max()) / 32768.0, 1e-12), 6)
    if s16 is not None and s24 is not None:
        truth["s24_aligned_residual"] = aligned_residual(s24, s16 * 256)
    if s16 is not None and s32 is not None:
        truth["s32_aligned_residual"] = aligned_residual(s32, s16 * 65536)
    rec["format_truth"] = truth

    rec["four_gig_boundary"] = four_gig_boundary()
    save_receipt("probe-p4b-format-truth.json", rec)

    print("silence gate:", rec["silence_baseline"])
    for k, v in legs.items():
        f = v.get("fmt") or {}
        print(f"{k:16s} rc={v['rc']} bytes={v['bytes']} tag={f.get('tag')} ch={f.get('channels')} "
              f"rate={f.get('rate')} bits={f.get('bits')} ba={f.get('block_align')} peak={v['peak']} "
              f"fft={v['fft_hz']} nz={v['nz']}")
    print("format truth:", json.dumps(truth, indent=1))
    print("4GiB boundary:", json.dumps(rec["four_gig_boundary"], indent=1))


if __name__ == "__main__":
    main()
