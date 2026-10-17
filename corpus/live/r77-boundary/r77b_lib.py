"""r77-boundary probe library.

Seat-private. NEVER imports `corpus/fixtures` (that file is being edited live by
the author). Every leg is timeout-bounded and byte-capped; heavy scratch lives
on /dev/shm under a size watchdog, receipts live in corpus/live/r77-boundary/.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import signal
import struct
import subprocess
import sys
import threading
import time
from pathlib import Path

import numpy as np

ROOT = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
SEAT = ROOT / "corpus" / "live" / "r77-boundary"
SCRATCH = Path("/dev/shm/r77b")
TONE = SCRATCH / "tone1k_4s.wav"

DEFAULT_SINK = "alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink"
SPDIF_SINK = DEFAULT_SINK
SPEAKER_SINK = "alsa_output.usb-Generic_USB_Audio-00.HiFi__Speaker__sink"
HDMI_SINK = "alsa_output.pci-0000_01_00.1.hdmi-stereo"
LINE_SRC = "alsa_input.usb-Generic_USB_Audio-00.HiFi__Line__source"
MIC_SRC = "alsa_input.usb-Generic_USB_Audio-00.HiFi__Mic__source"

KILL = signal.SIGKILL


# ---------------------------------------------------------------- process glue


def sh(cmd, timeout=12.0, env=None, cwd=None, text=True, cap=16384):
    """Run a command with a hard timeout. Never floods memory: output is capped."""
    t0 = time.monotonic()
    e = dict(os.environ)
    if env:
        e.update(env)
    try:
        p = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
            timeout=timeout,
            env=e,
            cwd=str(cwd) if cwd else None,
        )
        rc, out, err, killed = p.returncode, p.stdout, p.stderr, False
    except subprocess.TimeoutExpired as exc:
        rc, out, err, killed = None, exc.stdout or b"", exc.stderr or b"", True
    wall = round(time.monotonic() - t0, 3)
    if text:
        out = out.decode("utf-8", "replace") if isinstance(out, bytes) else out
        err = err.decode("utf-8", "replace") if isinstance(err, bytes) else err
    return {
        "cmd": " ".join(cmd) if isinstance(cmd, (list, tuple)) else cmd,
        "rc": rc,
        "killed_by_timeout": killed,
        "wall_s": wall,
        "out": out[:cap] if isinstance(out, str) else out[:cap],
        "err": err[:cap] if isinstance(err, str) else err[:cap],
        "out_bytes": len(out),
        "err_bytes": len(err),
    }


def spawn(cmd, out_path=None, env=None):
    e = dict(os.environ)
    if env:
        e.update(env)
    fo = open(out_path, "wb") if out_path else subprocess.DEVNULL
    p = subprocess.Popen(
        cmd,
        stdout=fo,
        stderr=subprocess.PIPE,
        stdin=subprocess.DEVNULL,
        env=e,
    )
    p._out_file = fo  # keep the handle alive
    return p


def reap(p, timeout=8.0, sig=None):
    """Wait for p; on timeout send sig (default SIGKILL) and reap."""
    try:
        p.wait(timeout=timeout)
        killed = False
    except subprocess.TimeoutExpired:
        p.send_signal(sig or signal.SIGKILL)
        try:
            p.wait(timeout=3)
        except subprocess.TimeoutExpired:
            p.kill()
            p.wait(timeout=3)
        killed = True
    try:
        err = p.stderr.read() if p.stderr else b""
    except Exception:
        err = b""
    rc = p.returncode
    try:
        if getattr(p, "_out_file", None):
            p._out_file.close()
    except Exception:
        pass
    return {"rc": rc, "killed_by_us": killed, "err": err.decode("utf-8", "replace")[:4096]}


def sever(cmd, out_path, wall=1.2, sig=signal.SIGKILL, ready=0.35):
    """Start cmd, let it run `ready+wall` s, then hard-signal it. Bounded."""
    p = spawn(cmd, out_path)
    time.sleep(ready)
    t0 = time.monotonic()
    time.sleep(wall)
    p.send_signal(sig)
    r = reap(p, timeout=4)
    r["wall_before_signal_s"] = round(time.monotonic() - t0, 3)
    r["cmd"] = " ".join(cmd)
    return r


def size_watchdog(paths_fn, cap_bytes, stop_evt, interval=0.05):
    """Background truncator: keeps total bytes of all but the newest file under cap."""
    def run():
        while not stop_evt.is_set():
            try:
                files = [Path(p) for p in paths_fn()]
                files = [f for f in files if f.exists()]
                if len(files) > 1:
                    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
                    for f in files[1:]:
                        try:
                            if f.stat().st_size > 0:
                                with open(f, "r+b") as fh:
                                    fh.truncate(0)
                        except OSError:
                            pass
            except Exception:
                pass
            stop_evt.wait(interval)
    t = threading.Thread(target=run, daemon=True)
    t.start()
    return t


def tmpfs_free_gb():
    st = os.statvfs(str(SCRATCH))
    return round(st.f_bavail * st.f_frsize / 1e9, 2)


def wipe_scratch():
    if SCRATCH.exists():
        for child in SCRATCH.iterdir():
            try:
                if child.is_dir():
                    shutil.rmtree(child)
                else:
                    child.unlink()
            except OSError:
                pass
    SCRATCH.mkdir(parents=True, exist_ok=True)


def sha256(p, n=None):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        while True:
            b = fh.read(1 << 20)
            if not b:
                break
            h.update(b)
            if n and h.digest_size and False:
                break
    return h.hexdigest()


def make_tone(path=TONE, seconds=4.0, rate=48000, freq=1000, amp=16384):
    """Deterministic stereo 1 kHz s16 wav, written once."""
    if path.exists():
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    n = int(seconds * rate)
    t = np.arange(n) / rate
    s = (amp * np.sin(2 * np.pi * freq * t)).astype("<i2")
    inter = np.empty(n * 2, dtype="<i2")
    inter[0::2] = s
    inter[1::2] = s
    data = inter.tobytes()
    hdr = b"RIFF" + struct.pack("<I", 36 + len(data)) + b"WAVEfmt "
    hdr += struct.pack("<IHHIIHH", 16, 1, 2, rate, rate * 4, 4, 16)
    hdr += b"data" + struct.pack("<I", len(data))
    path.write_bytes(hdr + data)
    return path


# ------------------------------------------------------------------- wav parse


def chunk_walk(raw, want=b"data", max_chunks=64):
    """Return (found_offset_of_body, declared_size, fmt_dict, chunks_seen)."""
    chunks = []
    pos = 12
    fmt = {}
    body = None
    dsize = None
    n = 0
    while pos + 8 <= len(raw) and n < max_chunks:
        cid = raw[pos : pos + 4]
        csz = struct.unpack_from("<I", raw, pos + 4)[0]
        chunks.append((cid.decode("latin1"), csz))
        if cid == b"fmt " and len(raw) >= pos + 8 + 16:
            fmt = dict(
                tag=struct.unpack_from("<H", raw, pos + 8)[0],
                channels=struct.unpack_from("<H", raw, pos + 10)[0],
                rate=struct.unpack_from("<I", raw, pos + 12)[0],
                byte_rate=struct.unpack_from("<I", raw, pos + 16)[0],
                block_align=struct.unpack_from("<H", raw, pos + 20)[0],
                bits=struct.unpack_from("<H", raw, pos + 22)[0],
            )
            if fmt["tag"] == 0xFFFE and len(raw) >= pos + 8 + 40:
                fmt["sub_format"] = raw[pos + 8 + 24 : pos + 8 + 40].hex()
        if cid == want:
            body = pos + 8
            dsize = csz
            break
        pos += 8 + csz + (csz & 1)
        n += 1
    return body, dsize, fmt, chunks


def size_class(v, is_riff=False):
    if v is None:
        return "absent"
    if is_riff:
        if v == 0xFFFFFFFF:
            return "placeholder_ff"
        if v == 0x80000000:
            return "placeholder_80000000"
        if v == 8:
            return "placeholder_8"
        if v == 0:
            return "zero"
        return "finalized"
    if v == 0xFFFFFFFF:
        return "placeholder_ff"
    if v == 0x80000000:
        return "placeholder_80000000"
    if v == 0:
        return "zero"
    return "finalized"


def audio_stats(raw, body, dsize, fmt, segs=1):
    """Peak / nonzero-fraction / FFT peak freq, optionally per segment."""
    out = {}
    if body is None or not fmt:
        return {"data_absent": True}
    ch = fmt.get("channels") or 1
    bits = fmt.get("bits") or 16
    ba = fmt.get("block_align") or (ch * bits // 8)
    avail = min(dsize, len(raw) - body) if dsize is not None else len(raw) - body
    avail = max(0, avail)
    payload = raw[body : body + avail]
    out["payload_bytes_actual"] = len(payload)
    out["data_declared"] = dsize
    out["data_declared_field"] = size_class(dsize)
    if not payload or ba <= 0:
        out.update(peak=0, nonzero_frac=0.0, fft_peak_hz=None, frames=0)
        return out
    frames = len(payload) // ba
    out["frames"] = frames
    # decode to float per frame (first channel enough for a tone witness)
    if bits == 16:
        a = np.frombuffer(payload[: frames * ba], dtype="<i2").reshape(frames, ch).astype(np.float64)
    elif bits == 24:
        b = np.frombuffer(payload[: frames * ba], dtype=np.uint8).reshape(frames, ch * 3)
        # libsndfile may pad 24-bit samples into 3-byte or 4-byte containers;
        # block_align tells us which (ch*3 vs ch*4).
        per = ba // ch
        if per == 3:
            v = (
                b[:, 0::3].astype(np.int32)
                | (b[:, 1::3].astype(np.int32) << 8)
                | (b[:, 2::3].astype(np.int32) << 16)
            )
            v = np.where(v >= (1 << 23), v - (1 << 24), v)
        else:
            q = np.frombuffer(payload[: frames * ba], dtype="<i4").reshape(frames, ch)
            v = (q >> 8).astype(np.int64)
        a = v.astype(np.float64)
    elif bits == 32:
        if fmt.get("tag") in (3, 0xFFFE) and fmt.get("sub_format", "").startswith("03000000"):
            a = np.frombuffer(payload[: frames * ba], dtype="<f4").reshape(frames, ch).astype(np.float64)
        else:
            a = np.frombuffer(payload[: frames * ba], dtype="<i4").reshape(frames, ch).astype(np.float64)
    else:
        a = np.frombuffer(payload[: frames * ba], dtype=np.uint8).reshape(frames, ba).astype(np.float64)

    mono = a[:, 0]
    out["peak"] = float(np.abs(mono).max()) if mono.size else 0.0
    out["nonzero_frac"] = float((mono != 0).mean()) if mono.size else 0.0
    out["rms"] = float(np.sqrt((mono ** 2).mean())) if mono.size else 0.0
    rate = fmt.get("rate") or 48000
    if mono.size >= 256 and out["peak"] > 0:
        w = mono - mono.mean()
        win = np.hanning(w.size)
        sp = np.abs(np.fft.rfft(w * win))
        f = np.fft.rfftfreq(w.size, 1.0 / rate)
        out["fft_peak_hz"] = round(float(f[int(np.argmax(sp))]), 1)
    else:
        out["fft_peak_hz"] = None
    if segs > 1 and mono.size >= segs * 512:
        per = mono.size // segs
        seg_out = []
        for i in range(segs):
            s = mono[i * per : (i + 1) * per]
            d = dict(
                peak=float(np.abs(s).max()),
                nonzero_frac=float((s != 0).mean()),
                fft_peak_hz=None,
            )
            if s.size >= 256 and d["peak"] > 0:
                w = s - s.mean()
                sp = np.abs(np.fft.rfft(w * np.hanning(w.size)))
                f = np.fft.rfftfreq(w.size, 1.0 / rate)
                d["fft_peak_hz"] = round(float(f[int(np.argmax(sp))]), 1)
            seg_out.append(d)
        out["segments"] = seg_out
    return out


def inspect_wav(path, segs=1):
    p = Path(path)
    d = {"path": str(p), "exists": p.exists()}
    if not p.exists():
        return d
    raw = p.read_bytes()
    d["bytes"] = len(raw)
    d["sha256_16"] = hashlib.sha256(raw).hexdigest()[:16]
    if len(raw) < 12:
        d["riff_magic"] = raw[:4].decode("latin1")
        d["short"] = True
        return d
    d["riff_magic"] = raw[:4].decode("latin1")
    d["riff_size_field_raw"] = struct.unpack_from("<I", raw, 4)[0]
    d["riff_size_field"] = size_class(d["riff_size_field_raw"], is_riff=True)
    d["form_type"] = raw[8:12].decode("latin1")
    if d["riff_magic"] == "RF64":
        d["riff64"] = True
    body, dsize, fmt, chunks = chunk_walk(raw)
    d["chunks"] = chunks[:12]
    d["fmt"] = fmt
    d.update(audio_stats(raw, body, dsize, fmt, segs=segs))
    return d


# --------------------------------------------------------------- reader matrix


def readers(path):
    """Independent witnesses on one wound. Each bounded; mediainfo/soundfile are
    reported as unavailable rather than skipped silently."""
    p = str(path)
    r = {}
    r["soxi_s"] = sh(["soxi", "-s", p], timeout=15)
    r["soxi_D"] = sh(["soxi", "-D", p], timeout=15)
    r["sndfile_info"] = sh(["sndfile-info", p], timeout=15)
    r["ffprobe_dur"] = sh(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
        timeout=15,
    )
    try:
        import wave as wavemod

        with wavemod.open(p) as w:
            r["python_wave"] = {"rc": 0, "frames": w.getnframes(), "rate": w.getframerate()}
    except Exception as exc:  # noqa: BLE001
        r["python_wave"] = {"rc": 1, "error": f"{type(exc).__name__}: {exc}"[:200]}
    r["ffprobe_json"] = sh(
        ["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", p],
        timeout=15,
        cap=4096,
    )
    return r


def reader_digest(rd, path=None):
    def num(k, field="out"):
        v = rd.get(k, {}).get(field, "")
        return v.strip() if isinstance(v, str) else v

    snd = rd.get("sndfile_info", {}).get("out", "") or ""
    frames = re.search(r"Frames\s*:\s*(\d+)", snd)
    dur = re.search(r"Duration\s*:\s*([0-9:.]+)", snd)
    fp = num("ffprobe_dur")
    return {
        "soxi_s": num("soxi_s"),
        "soxi_D": num("soxi_D"),
        "sndfile_frames": frames.group(1) if frames else None,
        "sndfile_duration": dur.group(1) if dur else None,
        "sndfile_error": ("error" in snd.lower() and "no error" not in snd.lower()) or None,
        "ffprobe_duration": fp or None,
        "python_wave_frames": rd.get("python_wave", {}).get("frames"),
        "python_wave_error": rd.get("python_wave", {}).get("error"),
    }


def ffplay_wall(path, cap_s=8.0, extra=None):
    """Does a PLAYER trust the declared size or hit real EOF? Bounded."""
    cmd = ["ffplay", "-nodisp", "-autoexit", "-loglevel", "error", "-i", str(path)]
    if extra:
        cmd = ["ffplay", "-nodisp", "-autoexit", "-loglevel", "error"] + extra + ["-i", str(path)]
    t0 = time.monotonic()
    r = sh(cmd, timeout=cap_s, env={"SDL_AUDIODRIVER": "dummy", "SDL_VIDEODRIVER": "dummy"})
    r["wall_measured_s"] = round(time.monotonic() - t0, 3)
    r["hit_cap"] = r["killed_by_timeout"]
    return r


def ffmpeg_null_decode(path, cap_s=10.0):
    t0 = time.monotonic()
    r = sh(["ffmpeg", "-v", "error", "-i", str(path), "-f", "null", "-"], timeout=cap_s)
    r["wall_measured_s"] = round(time.monotonic() - t0, 3)
    return r


# ------------------------------------------------------------------- receipts


def save_receipt(name, obj):
    SEAT.mkdir(parents=True, exist_ok=True)
    p = SEAT / name
    p.write_text(json.dumps(obj, indent=1, default=str) + "\n")
    h = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
    print(f"[receipt] {p} sha256_16={h} bytes={p.stat().st_size}")
    return str(p), h


def brief(d, keys):
    return {k: d.get(k) for k in keys}
