#!/usr/bin/env python3
"""r94 scout library — bounded subprocess runner, own RIFF I/O, own metrics.

Leaf-seat discipline:
- every subprocess triple-bounded: wall cap + output-byte cap checked in the
  same loop that owns the process group (`start_new_session` + `os.killpg`),
  plus RLIMIT_CORE=0.
- own RIFF writer AND own RIFF reader: sox never sits in the measurement path
  of a sox output (no circular decode). One control leg cross-checks the own
  reader against `sox -t f32 -`.
- file-only: this seat never creates a PipeWire object, never plays/records.
"""
from __future__ import annotations

import hashlib
import json
import os
import resource
import signal
import struct
import subprocess
import time
from pathlib import Path

import numpy as np

ROOT = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
OUT = ROOT / "corpus/live/r94-scout"
SCRATCH = OUT / "scratch"
RECEIPTS = OUT / "receipts"
RUNS = OUT / "runs"
for _d in (SCRATCH, RECEIPTS, RUNS):
    _d.mkdir(parents=True, exist_ok=True)

SOX = "/usr/bin/sox"
FFMPEG = "/usr/bin/ffmpeg"

# ---------------------------------------------------------------- hashing ---

def sha256_file(p) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


# ------------------------------------------------------------- WAV writer ---

def _quantize_pcm16(x: np.ndarray) -> np.ndarray:
    # round-half-away-from-zero, clip to s16 range
    q = np.rint(x * 32768.0)
    return np.clip(q, -32768, 32767).astype("<i2")


def write_wav_pcm16(path, data_i16: np.ndarray, rate: int) -> None:
    """data_i16: (frames,) or (frames, channels) int16 array."""
    if data_i16.ndim == 1:
        data_i16 = data_i16[:, None]
    frames, channels = data_i16.shape
    body = data_i16.astype("<i2").tobytes()
    block = channels * 2
    fmt = struct.pack("<HHIIHH", 1, channels, rate, rate * block, block, 16)
    chunks = b"fmt " + struct.pack("<I", len(fmt)) + fmt
    chunks += b"data" + struct.pack("<I", len(body)) + body
    riff = b"WAVE" + chunks
    Path(path).write_bytes(b"RIFF" + struct.pack("<I", len(riff)) + riff)


def write_wav_f32(path, data_f: np.ndarray, rate: int) -> None:
    """IEEE float32 mono/stereo."""
    if data_f.ndim == 1:
        data_f = data_f[:, None]
    frames, channels = data_f.shape
    body = data_f.astype("<f4").tobytes()
    block = channels * 4
    fmt = struct.pack("<HHIIHH", 3, channels, rate, rate * block, block, 32)
    chunks = b"fmt " + struct.pack("<I", len(fmt)) + fmt
    chunks += b"fact" + struct.pack("<I", 4) + struct.pack("<I", frames)
    chunks += b"data" + struct.pack("<I", len(body)) + body
    riff = b"WAVE" + chunks
    Path(path).write_bytes(b"RIFF" + struct.pack("<I", len(riff)) + riff)


# ------------------------------------------------------------- WAV reader ---

def read_wav(path):
    """Own RIFF parser. Returns (float64 (frames, ch) in [-1,1), meta dict).

    Handles PCM u8/s16/s24/s32 and IEEE float32/64, plain and WAVE_FORMAT_EXTENSIBLE.
    """
    raw = Path(path).read_bytes()
    if raw[:4] != b"RIFF" or raw[8:12] != b"WAVE":
        raise ValueError(f"not RIFF/WAVE: {path}")
    pos = 12
    fmt = None
    data = None
    extra = {}
    while pos + 8 <= len(raw):
        cid = raw[pos:pos + 4]
        size = int.from_bytes(raw[pos + 4:pos + 8], "little")
        body = raw[pos + 8:pos + 8 + size]
        if cid == b"fmt ":
            fmt = body
        elif cid == b"data":
            data = body
        elif cid == b"fact":
            extra["fact_frames"] = int.from_bytes(body[:4], "little")
        pos += 8 + size + (size & 1)
    if fmt is None or data is None:
        raise ValueError(f"missing fmt/data: {path}")
    tag, channels, rate, _byterate, block_align, bits = struct.unpack("<HHIIHH", fmt[:16])
    sub = None
    if tag == 0xFFFE and len(fmt) >= 26:
        sub = int.from_bytes(fmt[24:26], "little")
    eff = sub if sub is not None else tag
    n = len(data) // (block_align or 1)
    if eff == 1:  # PCM int
        if bits == 16:
            arr = np.frombuffer(data[: n * channels * 2], dtype="<i2").reshape(n, channels) / 32768.0
        elif bits == 24:
            b = np.frombuffer(data[: n * channels * 3], dtype=np.uint8).reshape(n, channels, 3).astype(np.int32)
            v = (b[:, :, 0] | (b[:, :, 1] << 8) | (b[:, :, 2] << 16))
            v = np.where(v >= (1 << 23), v - (1 << 24), v)
            arr = v / 8388608.0
        elif bits == 32:
            arr = np.frombuffer(data[: n * channels * 4], dtype="<i4").reshape(n, channels) / 2147483648.0
        elif bits == 8:
            u = np.frombuffer(data[: n * channels], dtype=np.uint8).reshape(n, channels).astype(np.float64)
            arr = (u - 128.0) / 128.0
        else:
            raise ValueError(f"unsupported PCM bits {bits}")
    elif eff == 3:  # IEEE float
        if bits == 32:
            arr = np.frombuffer(data[: n * channels * 4], dtype="<f4").reshape(n, channels).astype(np.float64)
        elif bits == 64:
            arr = np.frombuffer(data[: n * channels * 8], dtype="<f8").reshape(n, channels)
        else:
            raise ValueError(f"unsupported float bits {bits}")
    else:
        raise ValueError(f"unsupported tag {eff}")
    meta = {
        "tag": eff, "raw_tag": tag, "channels": channels, "rate": rate,
        "bits": bits, "frames": n, "duration": n / rate,
        "bytes": len(data), "fact_frames": extra.get("fact_frames"),
    }
    return arr, meta


# ---------------------------------------------------------------- metrics ---

def peak_db(x: np.ndarray) -> float:
    p = float(np.max(np.abs(x))) if x.size else 0.0
    return 20.0 * np.log10(p) if p > 0 else float("-inf")


def rms_db(x: np.ndarray) -> float:
    r = float(np.sqrt(np.mean(x.astype(np.float64) ** 2))) if x.size else 0.0
    return 20.0 * np.log10(r) if r > 0 else float("-inf")


def tone_hz(x: np.ndarray, rate: int, lo=50.0, hi=None):
    """Parabolic-interpolated FFT peak of the strongest tone; (hz, amp_db)."""
    v = x[:, 0] if x.ndim > 1 else x
    if v.size < 64:
        return None, None
    hi = hi if hi is not None else rate / 2
    win = np.hanning(v.size)
    spec = np.abs(np.fft.rfft(v * win))
    freqs = np.fft.rfftfreq(v.size, 1.0 / rate)
    mask = (freqs >= lo) & (freqs <= hi)
    if not mask.any():
        return None, None
    idx = int(np.argmax(np.where(mask, spec, 0.0)))
    if 0 < idx < len(spec) - 1:
        a, b, c = spec[idx - 1], spec[idx], spec[idx + 1]
        denom = (a - 2 * b + c)
        delta = 0.5 * (a - c) / denom if denom != 0 else 0.0
    else:
        delta = 0.0
    f = freqs[idx] + delta * (freqs[1] - freqs[0])
    amp = 2.0 * spec[idx] / (win.sum() * 0.5)
    return float(f), float(20 * np.log10(amp)) if amp > 0 else None


def band_level_db(x: np.ndarray, rate: int, f0: float, half=40.0) -> float:
    """Level (dB FS) in a band around f0 via windowed DFT (own reference)."""
    v = x[:, 0] if x.ndim > 1 else x
    if v.size < 64:
        return float("-inf")
    win = np.hanning(v.size)
    spec = np.abs(np.fft.rfft(v * win))
    freqs = np.fft.rfftfreq(v.size, 1.0 / rate)
    band = (freqs >= f0 - half) & (freqs <= f0 + half)
    if not band.any():
        return float("-inf")
    peak = float(spec[band].max()) * 2.0 / (win.sum() * 0.5)
    return float(20 * np.log10(peak)) if peak > 0 else float("-inf")


def env_at(x: np.ndarray, idx: int) -> float:
    v = x[:, 0] if x.ndim > 1 else x
    if idx < 0 or idx >= v.size:
        return float("nan")
    return float(v[idx])


# -------------------------------------------------------- bounded runner ---

def run_bounded(argv, leg_dir, wall=10.0, out_path=None, out_cap=64 << 20,
                stdin_bytes=None, extra_env=None, cwd=None):
    """Run argv under triple bounds. Writes cmd/stdout/stderr/meta into leg_dir."""
    leg_dir = Path(leg_dir)
    leg_dir.mkdir(parents=True, exist_ok=True)
    (leg_dir / "cmd").write_text(json.dumps(argv))
    env = dict(os.environ)
    env["LC_ALL"] = "C"
    if extra_env:
        env.update(extra_env)

    def _preexec():
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))

    out_f = open(leg_dir / "stdout", "wb")
    err_f = open(leg_dir / "stderr", "wb")
    t0 = time.monotonic()
    p = subprocess.Popen(
        argv, stdin=subprocess.PIPE if stdin_bytes is not None else subprocess.DEVNULL,
        stdout=out_f, stderr=err_f, start_new_session=True, cwd=cwd,
        env=env, preexec_fn=_preexec,
    )
    if stdin_bytes is not None:
        try:
            p.stdin.write(stdin_bytes)
            p.stdin.close()
        except (BrokenPipeError, OSError):
            pass
    killed = None
    while True:
        rc = p.poll()
        if rc is not None:
            break
        el = time.monotonic() - t0
        if el > wall:
            killed = f"wall>{wall:g}s"
            break
        if out_path is not None:
            op = Path(out_path)
            try:
                if op.exists() and op.stat().st_size > out_cap:
                    killed = f"out>{out_cap}B"
                    break
            except OSError:
                pass
        time.sleep(0.02)
    if killed:
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
        try:
            p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pass
    try:
        rc = p.wait(timeout=5)
    except subprocess.TimeoutExpired:
        rc = None
    wall_s = time.monotonic() - t0
    out_f.close()
    err_f.close()
    stdout = (leg_dir / "stdout").read_bytes()
    stderr = (leg_dir / "stderr").read_bytes()
    meta = {
        "argv": argv, "rc": rc, "wall_s": round(wall_s, 4), "killed": killed,
        "stdout_bytes": len(stdout), "stderr_bytes": len(stderr),
        "stderr_head": stderr[:400].decode("utf-8", "replace"),
        "stdout_head": stdout[:400].decode("utf-8", "replace"),
    }
    if out_path is not None and Path(out_path).exists():
        meta["out_bytes"] = Path(out_path).stat().st_size
        meta["out_sha256"] = sha256_file(out_path)
    else:
        meta["out_bytes"] = None
        meta["out_sha256"] = None
    (leg_dir / "meta.json").write_text(json.dumps(meta, indent=1))
    return meta


# ------------------------------------------------------------ host context ---

def host_context() -> dict:
    return {
        "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "loadavg": Path("/proc/loadavg").read_text().strip(),
        "nproc": os.cpu_count(),
        "sox_version": subprocess.run([SOX, "--version"], capture_output=True,
                                      text=True).stdout.strip(),
        "sox_sha256": sha256_file(SOX),
    }


def write_receipt(stage: str, payload: dict) -> Path:
    payload = {"stage": stage, **payload}
    p = RECEIPTS / f"{stage}.json"
    p.write_text(json.dumps(payload, indent=1))
    return p
