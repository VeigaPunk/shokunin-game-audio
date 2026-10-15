#!/usr/bin/env python3
"""r94b boundary library — bounded runner, own RIFF I/O, own metrics, own hogs.

Boundary-seat discipline (r94-boundary task, wave shokunin-train-20261015-w22):
- every subprocess triple-bounded: wall cap + output-byte cap checked in the same
  loop that owns the process group (`start_new_session` + `os.killpg`), plus
  RLIMIT_CORE=0.
- own RIFF writer AND own reader: sox never sits in the measurement path of a sox
  output (no circular decode).  Stimulus byte layout is replicated from the r94
  scout definition so that output shas are directly comparable across seats.
- file-only: no PipeWire object is ever created, no device is opened, no
  `pactl set-default-*`, no metadata write.  sox is never invoked with
  `-d`/`-p`/`play`/`rec`.
- hogs are own PIDs only, argv-marked `r94b_hog`; kill path re-verifies the
  marker and the recorded start-time before signalling.  No namespace-blind
  sweeps (r95 incident precedent: a preflight `sweep()` matched foreign
  `pw-record`/`pw-play` children by name).
"""
from __future__ import annotations

import hashlib
import json
import os
import resource
import signal
import struct
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
OUT = ROOT / "corpus/live/r94-boundary"
SCRATCH = OUT / "scratch"
RECEIPTS = OUT / "receipts"
RUNS = OUT / "runs"
SCOUT = ROOT / "corpus/live/r94-scout"
for _d in (SCRATCH, RECEIPTS, RUNS):
    _d.mkdir(parents=True, exist_ok=True)

SOX = "/usr/bin/sox"
FFMPEG = "/usr/bin/ffmpeg"
PACTL = "/usr/bin/pactl"
PWMETADATA = "/usr/bin/pw-metadata"

HOG_MARKER = "r94b_hog"
HOG_SCRIPT = str(Path(__file__).resolve().parent / "r94b_hog.py")


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
# byte layout replicated from corpus/live/r94-scout/probes/r94lib.py so the
# regenerated stimuli hash-compare against the scout's prep.json.

def write_wav_pcm16(path, data_i16: np.ndarray, rate: int) -> None:
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
    """Own RIFF parser -> (float64 (frames, ch) in [-1,1), meta)."""
    raw = Path(path).read_bytes()
    if raw[:4] != b"RIFF" or raw[8:12] != b"WAVE":
        raise ValueError(f"not RIFF/WAVE: {path}")
    pos = 12
    fmt = data = None
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
    tag, channels, rate, _br, block_align, bits = struct.unpack("<HHIIHH", fmt[:16])
    sub = None
    if tag == 0xFFFE and len(fmt) >= 26:
        sub = int.from_bytes(fmt[24:26], "little")
    eff = sub if sub is not None else tag
    n = len(data) // (block_align or 1)
    if eff == 1:
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
    elif eff == 3:
        if bits == 32:
            arr = np.frombuffer(data[: n * channels * 4], dtype="<f4").reshape(n, channels).astype(np.float64)
        elif bits == 64:
            arr = np.frombuffer(data[: n * channels * 8], dtype="<f8").reshape(n, channels)
        else:
            raise ValueError(f"unsupported float bits {bits}")
    else:
        raise ValueError(f"unsupported tag {eff}")
    return arr, {"tag": eff, "raw_tag": tag, "channels": channels, "rate": rate,
                 "bits": bits, "frames": n, "duration": n / rate, "bytes": len(data),
                 "fact_frames": extra.get("fact_frames")}


def i16(path):
    arr, meta = read_wav(path)
    return np.rint(arr * 32768.0).astype(np.int64), meta


# ---------------------------------------------------------------- metrics ---

def peak_db(x: np.ndarray) -> float:
    p = float(np.max(np.abs(x))) if x.size else 0.0
    return 20.0 * np.log10(p) if p > 0 else float("-inf")


def rms_db(x: np.ndarray) -> float:
    r = float(np.sqrt(np.mean(x.astype(np.float64) ** 2))) if x.size else 0.0
    return 20.0 * np.log10(r) if r > 0 else float("-inf")


def tone_hz(x: np.ndarray, rate: int, lo=50.0, hi=None):
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


def basic_metrics(path):
    arr, meta = read_wav(path)
    out = {"frames": meta["frames"], "channels": meta["channels"], "rate": meta["rate"],
           "duration_s": round(meta["duration"], 6), "bits": meta["bits"],
           "peak_db": [round(peak_db(arr[:, c]), 4) for c in range(arr.shape[1])],
           "rms_db": [round(rms_db(arr[:, c]), 4) for c in range(arr.shape[1])]}
    for c in range(arr.shape[1]):
        f, a = tone_hz(arr[:, c], meta["rate"], lo=100.0)
        out[f"tone{c}"] = {"hz": round(f, 3) if f else None,
                           "db": round(a, 3) if a is not None else None}
    return out


# -------------------------------------------------------- host witnesses ---

def _run_quiet(argv, timeout=5.0):
    try:
        p = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except Exception as e:  # noqa: BLE001
        return None, "", f"{type(e).__name__}: {e}"


def loadavg() -> str:
    try:
        return Path("/proc/loadavg").read_text().strip()
    except OSError:
        return ""


def loadavg1() -> float:
    try:
        return float(Path("/proc/loadavg").read_text().split()[0])
    except (OSError, ValueError, IndexError):
        return float("nan")


def default_node_witness():
    """Read-only witness: default sink/source + active stream counts."""
    w = {}
    rc, so, _ = _run_quiet([PACTL, "get-default-sink"])
    w["default_sink"] = so if rc == 0 else None
    rc, so, _ = _run_quiet([PACTL, "get-default-source"])
    w["default_source"] = so if rc == 0 else None
    rc, so, _ = _run_quiet([PACTL, "list", "short", "sink-inputs"])
    w["sink_inputs"] = len([l for l in so.splitlines() if l.strip()]) if rc == 0 else None
    rc, so, _ = _run_quiet([PACTL, "list", "short", "source-outputs"])
    w["source_outputs"] = len([l for l in so.splitlines() if l.strip()]) if rc == 0 else None
    return w


def settings_witness():
    """Read-only witness of the PipeWire clock settings metadata."""
    w = {}
    rc, so, _ = _run_quiet([PWMETADATA, "-n", "settings"], timeout=5.0)
    if rc == 0:
        for line in so.splitlines():
            if "key:" not in line:
                continue
            try:
                key = line.split("key:'", 1)[1].split("'", 1)[0]
                val = line.split("value:'", 1)[1].split("'", 1)[0]
            except IndexError:
                continue
            if key.startswith("clock."):
                w[key] = val
    return w


def host_context():
    return {"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "loadavg": loadavg(), "nproc": os.cpu_count(),
            "sox_version": _run_quiet([SOX, "--version"])[1],
            "sox_sha256": sha256_file(SOX)}


# ------------------------------------------------------------ hog manager ---

def proc_starttime(pid: int):
    try:
        st = Path(f"/proc/{pid}/stat").read_text()
        return int(st.rsplit(")", 1)[1].split()[19])
    except (OSError, IndexError, ValueError):
        return None


def proc_cmdline(pid: int) -> str:
    try:
        return Path(f"/proc/{pid}/cmdline").read_bytes().replace(b"\0", b" ").decode("utf-8", "replace")
    except OSError:
        return ""


def proc_cpu_seconds(pid: int):
    """utime+stime of pid in seconds, or None if gone."""
    try:
        st = Path(f"/proc/{pid}/stat").read_text()
        parts = st.rsplit(")", 1)[1].split()
        utime, stime = int(parts[11]), int(parts[12])
        return (utime + stime) / os.sysconf("SC_CLK_TCK")
    except (OSError, IndexError, ValueError):
        return None


class HogSet:
    """Own-PID-only CPU load.  Never matches processes by name for killing."""

    def __init__(self, n: int):
        self.n = n
        self.pids = []
        self.starttimes = {}
        self.procs = []
        self.started_utc = None
        self.stopped_utc = None
        self.loadavg_before = None
        self.loadavg_after = None
        self.kill_log = []

    def start(self):
        self.loadavg_before = loadavg()
        self.started_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        env = dict(os.environ)
        env["LC_ALL"] = "C"
        for _ in range(self.n):
            p = subprocess.Popen([sys.executable, HOG_SCRIPT], stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL,
                                 start_new_session=True, env=env)
            self.pids.append(p.pid)
            self.procs.append(p)
        # verify every spawned pid is really ours and carries the marker
        for pid in self.pids:
            cl = proc_cmdline(pid)
            ok = HOG_MARKER in cl
            self.starttimes[pid] = proc_starttime(pid)
            self.kill_log.append({"pid": pid, "marker_ok": ok, "cmdline": cl[:120],
                                  "starttime": self.starttimes[pid]})
        time.sleep(1.0)
        return self

    def alive(self):
        return [pid for pid in self.pids if Path(f"/proc/{pid}").exists()]

    def cpu_seconds(self):
        tot = 0.0
        n = 0
        for pid in self.pids:
            c = proc_cpu_seconds(pid)
            if c is not None:
                tot += c
                n += 1
        return {"cpu_seconds_total": round(tot, 3), "procs_counted": n,
                "cpu_seconds_per_proc": round(tot / n, 3) if n else None,
                "nproc": os.cpu_count()}

    def warmup(self, seconds: float):
        """Hold the hogs long enough for the 1-min loadavg to reflect them."""
        t0 = time.time()
        while time.time() - t0 < seconds:
            time.sleep(0.5)
        self.loadavg_after_warmup = loadavg()
        return self

    def stop(self):
        self.loadavg_after = loadavg()
        self.cpu_at_stop = self.cpu_seconds()
        for pid in self.pids:
            entry = {"pid": pid}
            # re-verify: marker in cmdline AND starttime unchanged
            cl = proc_cmdline(pid)
            st = proc_starttime(pid)
            if not cl:
                entry["skip"] = "gone"
                self.kill_log.append(entry)
                continue
            if HOG_MARKER not in cl:
                entry["skip"] = "marker-mismatch"
                self.kill_log.append(entry)
                continue
            if self.starttimes.get(pid) is not None and st != self.starttimes.get(pid):
                entry["skip"] = "starttime-mismatch"
                self.kill_log.append(entry)
                continue
            try:
                os.kill(pid, signal.SIGTERM)
                entry["sigterm"] = True
            except ProcessLookupError:
                entry["sigterm"] = "gone"
            self.kill_log.append(entry)
        deadline = time.time() + 5.0
        while time.time() < deadline and self.alive():
            time.sleep(0.1)
        for pid in self.alive():
            cl = proc_cmdline(pid)
            if HOG_MARKER in cl and proc_starttime(pid) == self.starttimes.get(pid):
                try:
                    os.kill(pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
        for p in self.procs:
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass
        self.stopped_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self.kill_log.append({"final_alive": self.alive()})
        return self

    def receipt(self):
        return {"count": self.n, "pids": self.pids, "started_utc": self.started_utc,
                "stopped_utc": self.stopped_utc, "loadavg_before": self.loadavg_before,
                "loadavg_after_warmup": getattr(self, "loadavg_after_warmup", None),
                "loadavg_after": self.loadavg_after,
                "cpu_at_stop": getattr(self, "cpu_at_stop", None),
                "kill_log": self.kill_log}


# -------------------------------------------------------- bounded runner ---

def run_bounded(argv, leg_dir, wall=10.0, out_path=None, out_cap=64 << 20,
                extra_env=None, cwd=None, want_stdout=False):
    """Run argv under triple bounds.  Writes cmd/stdout/stderr/meta into leg_dir."""
    leg_dir = Path(leg_dir)
    leg_dir.mkdir(parents=True, exist_ok=True)
    (leg_dir / "cmd").write_text(json.dumps(argv))
    env = dict(os.environ)
    env["LC_ALL"] = "C"
    if extra_env:
        env.update(extra_env)

    def _preexec():
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))

    la_before = loadavg1()
    out_f = open(leg_dir / "stdout", "wb")
    err_f = open(leg_dir / "stderr", "wb")
    t0 = time.monotonic()
    p = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=out_f, stderr=err_f,
                         start_new_session=True, cwd=cwd, env=env, preexec_fn=_preexec)
    killed = None
    while True:
        rc = p.poll()
        if rc is not None:
            break
        if time.monotonic() - t0 > wall:
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
    la_after = loadavg1()
    out_f.close()
    err_f.close()
    stdout = (leg_dir / "stdout").read_bytes()
    stderr = (leg_dir / "stderr").read_bytes()
    meta = {"argv": argv, "rc": rc, "wall_s": round(wall_s, 4), "killed": killed,
            "stdout_bytes": len(stdout), "stderr_bytes": len(stderr),
            "stderr_head": stderr[:400].decode("utf-8", "replace"),
            "loadavg1_before": la_before, "loadavg1_after": la_after}
    if out_path is not None and Path(out_path).exists():
        meta["out_bytes"] = Path(out_path).stat().st_size
        meta["out_sha256"] = sha256_file(out_path)
    else:
        meta["out_bytes"] = None
        meta["out_sha256"] = None
    if want_stdout:
        meta["stdout_sha256"] = sha256_bytes(stdout)
    (leg_dir / "meta.json").write_text(json.dumps(meta, indent=1))
    return meta


def write_receipt(stage: str, payload: dict) -> Path:
    payload = {"stage": stage, **payload}
    p = RECEIPTS / f"{stage}.json"
    p.write_text(json.dumps(payload, indent=1))
    return p


# ----------------------------------------------------------- stimuli defs ---
# byte-for-byte the r94 scout stimulus definitions (rate 48000 unless noted)

def build_stimuli():
    rate = 48000
    stim = {}
    t_a = np.arange(48000) / rate
    a = np.column_stack([np.rint(16384.0 * np.sin(2 * np.pi * 1000.0 * t_a)),
                         np.rint(8192.0 * np.sin(2 * np.pi * 1500.0 * t_a))]).astype("<i2")
    write_wav_pcm16(SCRATCH / "r94b_stim_a.wav", a, rate)

    t_b = np.arange(12000) / rate
    b = np.rint(16384.0 * np.sin(2 * np.pi * 997.0 * t_b)).astype("<i2")
    write_wav_pcm16(SCRATCH / "r94b_stim_b.wav", b, rate)

    c = np.zeros(19200, dtype="<i2")
    t_c = np.arange(9600) / rate
    c[4800:14400] = np.rint(16384.0 * np.sin(2 * np.pi * 997.0 * t_c)).astype("<i2")
    write_wav_pcm16(SCRATCH / "r94b_stim_c.wav", c, rate)

    f = (0.5 * np.sin(2 * np.pi * 997.0 * t_b)).astype("<f4")
    write_wav_f32(SCRATCH / "r94b_stim_f.wav", f, rate)

    h = np.rint(16384.0 * np.sin(2 * np.pi * 20000.0 * t_b)).astype("<i2")
    write_wav_pcm16(SCRATCH / "r94b_stim_h.wav", h, rate)

    i = np.rint(16384.0 * np.sin(2 * np.pi * 997.0 * np.arange(12001) / rate)).astype("<i2")
    write_wav_pcm16(SCRATCH / "r94b_stim_i.wav", i, rate)

    j = np.rint(16384.0 * np.sin(2 * np.pi * 23000.0 * t_b)).astype("<i2")
    write_wav_pcm16(SCRATCH / "r94b_stim_j.wav", j, rate)

    rng = np.random.default_rng(94)
    r = rng.integers(-32768, 32768, size=4800, dtype=np.int64).astype("<i2")
    write_wav_pcm16(SCRATCH / "r94b_stim_r.wav", r, rate)

    c2 = np.zeros(21600, dtype="<i2")
    t_c2 = np.arange(9600) / rate
    c2[4800:14400] = np.rint(16384.0 * np.sin(2 * np.pi * 997.0 * t_c2)).astype("<i2")
    write_wav_pcm16(SCRATCH / "r94b_stim_c2.wav", c2, rate)

    for p in sorted(SCRATCH.glob("r94b_stim_*.wav")):
        stim[p.name] = sha256_file(p)
    return stim
