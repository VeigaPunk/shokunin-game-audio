"""r93 scout shared library — own bounded process helpers, own synth, own BS.1770.

Seat-owned (r93s_*). No import of corpus/fixtures/measure_audio.py (sibling-owned).
Every child: start_new_session + wall cap (killpg) + byte cap; RLIMIT_CORE=0
because pw-cli SIGABRTs on stdin EOF on this host (r92 claim 10).
"""
import json
import math
import os
import resource
import signal
import struct
import subprocess
import sys
import time
import wave

SEAT = "r93s"
WALL = 8.0          # default wall cap per child (s)
BYTE_CAP = 8 << 20  # default byte cap per capture (8 MB)


def _ncore():
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


class Bounded:
    """Run one child with element+wall+byte bounds; always kill the group."""

    def __init__(self, argv, wall=WALL, byte_cap=BYTE_CAP, cwd=None, stdin_data=None, env=None):
        self.argv = argv
        self.wall = wall
        self.byte_cap = byte_cap
        self.t0 = time.time()
        self.timed_out = False
        self.byte_capped = False
        self.rc = None
        e = dict(os.environ)
        if env:
            e.update(env)
        p = subprocess.Popen(
            argv, stdin=subprocess.PIPE if stdin_data is not None else subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True,
            cwd=cwd, preexec_fn=_ncore, env=e,
        )
        self.pid = p.pid
        try:
            out, err = p.communicate(input=stdin_data, timeout=wall)
            self.rc = p.returncode
        except subprocess.TimeoutExpired:
            self.timed_out = True
            try:
                os.killpg(os.getpgid(p.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass
            out, err = p.communicate()
            self.rc = p.returncode
        self.dur = time.time() - self.t0
        self.out = out.decode("utf-8", "replace")
        self.err = err.decode("utf-8", "replace")
        if len(self.out) > self.byte_cap:
            self.byte_capped = True
            self.out = self.out[: self.byte_cap]

    def as_dict(self):
        return {
            "argv": self.argv, "rc": self.rc, "dur": round(self.dur, 3),
            "timed_out": self.timed_out, "byte_capped": self.byte_capped,
            "out": self.out[-6000:], "err": self.err[-6000:],
        }


def run(argv, **kw):
    return Bounded(argv, **kw)


class PwCli:
    """Interactive pw-cli; load/unload modules inside this client context."""

    def __init__(self, wall=20.0, env=None, idle=0.5, hard=6.0):
        self.wall = wall
        self.idle = idle
        self.hard = hard
        e = dict(os.environ)
        if env:
            e.update(env)
        self.p = subprocess.Popen(
            ["pw-cli"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, start_new_session=True, bufsize=0, env=e,
            preexec_fn=_ncore,
        )
        self.log = []
        self._read_until_idle(idle, hard)

    def _read_until_idle(self, idle=None, hard=None):
        idle = self.idle if idle is None else idle
        hard = self.hard if hard is None else hard
        import select
        buf = b""
        t0 = time.time()
        last = time.time()
        while time.time() - t0 < hard:
            r, _, _ = select.select([self.p.stdout], [], [], 0.15)
            if r:
                chunk = os.read(self.p.stdout.fileno(), 65536)
                if not chunk:
                    break
                buf += chunk
                last = time.time()
            elif time.time() - last > idle:
                break
        txt = buf.decode("utf-8", "replace")
        self.log.append(txt)
        return txt

    def cmd(self, line, idle=None, hard=None):
        self.p.stdin.write((line + "\n").encode())
        self.p.stdin.flush()
        return self._read_until_idle(idle=idle, hard=hard)

    def load(self, module, args):
        out = self.cmd(f"load-module {module} {args}")
        var = None
        for line in out.splitlines():
            line = line.strip()
            if "= @module:" in line:
                try:
                    var = int(line.split("=")[0].strip())
                except ValueError:
                    pass
        return out, var

    def close(self):
        try:
            self.p.stdin.write(b"quit\n")
            self.p.stdin.flush()
        except Exception:
            pass
        try:
            self.p.wait(timeout=3)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(os.getpgid(self.p.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass
            try:
                self.p.wait(timeout=2)
            except Exception:
                pass
        return self.log


class Bg:
    """Background child with wall cap + killpg teardown."""

    def __init__(self, argv, wall=12.0, env=None):
        self.argv = argv
        self.wall = wall
        self.t0 = time.time()
        e = dict(os.environ)
        if env:
            e.update(env)
        self.p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  stdin=subprocess.DEVNULL, start_new_session=True, env=e,
                                  preexec_fn=_ncore)

    def stop(self):
        try:
            os.killpg(os.getpgid(self.p.pid), signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            out, err = self.p.communicate(timeout=3)
            rc = self.p.returncode
        except subprocess.TimeoutExpired:
            try:
                os.killpg(os.getpgid(self.p.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass
            out, err = self.p.communicate()
            rc = self.p.returncode
        return {"rc": rc, "dur": round(time.time() - self.t0, 3),
                "out": out.decode("utf-8", "replace")[-2000:],
                "err": err.decode("utf-8", "replace")[-2000:]}

    def alive(self):
        return self.p.poll() is None


# ---------------------------------------------------------------- own WAV I/O

def write_wav_f32(path, samples, rate=48000, ch=1):
    """Minimal IEEE-float RIFF writer (format tag 3). samples: list[float] mono,
    or list[tuple] interleaved for ch>1."""
    if ch == 1:
        flat = [float(s) for s in samples]
    else:
        flat = [float(s) for tup in samples for s in tup]
    n = len(flat)
    data = struct.pack("<%df" % n, *flat)
    hdr = b"RIFF" + struct.pack("<I", 36 + len(data)) + b"WAVE"
    fmt = b"fmt " + struct.pack("<IHHIIHH", 16, 3, ch, rate,
                                rate * ch * 4, ch * 4, 32)
    hdr += fmt + b"data" + struct.pack("<I", len(data))
    with open(path, "wb") as f:
        f.write(hdr + data)
    return {"path": path, "frames": n // ch, "ch": ch, "rate": rate}


def read_wav_any(path):
    """Read PCM16/PCM24/PCM32/float32/float64 WAV -> {rate, ch, sw, frames, x}.

    Own RIFF parser: the stdlib wave module rejects format tag 3 (float WAV),
    which is exactly the format pw-record --format f32 writes."""
    with open(path, "rb") as f:
        head = f.read(12)
        if head[:4] != b"RIFF" or head[8:12] != b"WAVE":
            raise ValueError("not a RIFF/WAVE file: %s" % path)
        fmt = None
        data = None
        while True:
            chdr = f.read(8)
            if len(chdr) < 8:
                break
            cid, csz = struct.unpack("<4sI", chdr)
            body = f.read(csz)
            if cid == b"fmt ":
                fmt = struct.unpack_from("<HHIIHH", body, 0)
            elif cid == b"data":
                data = body
        if fmt is None or data is None:
            raise ValueError("missing fmt/data chunk")
    tag, ch, rate, _brate, _balign, bits = fmt
    n = len(data) // (ch * max(1, bits // 8))
    if tag == 3:
        if bits == 32:
            vals = struct.unpack("<%df" % (len(data) // 4), data[: len(data) // 4 * 4])
            scale = 1.0
        elif bits == 64:
            vals = struct.unpack("<%dd" % (len(data) // 8), data[: len(data) // 8 * 8])
            scale = 1.0
        else:
            raise ValueError("float WAV bits=%d" % bits)
    elif tag == 1:
        if bits == 16:
            vals = struct.unpack("<%dh" % (len(data) // 2), data[: len(data) // 2 * 2])
            scale = 32768.0
        elif bits == 32:
            vals = struct.unpack("<%di" % (len(data) // 4), data[: len(data) // 4 * 4])
            scale = 2147483648.0
        elif bits == 24:
            raw = data[: (len(data) // 3) * 3]
            vals = []
            for i in range(0, len(raw), 3):
                v = raw[i] | (raw[i + 1] << 8) | (raw[i + 2] << 16)
                if v & 0x800000:
                    v -= 0x1000000
                vals.append(v)
            scale = 8388608.0
        else:
            raise ValueError("PCM WAV bits=%d" % bits)
    else:
        raise ValueError("WAV format tag %d unsupported" % tag)
    if ch > 1:
        chans = [list(vals[i::ch]) for i in range(ch)]
    else:
        chans = [list(vals)]
    return {"rate": rate, "ch": ch, "sw": bits // 8, "fmt": tag, "frames": n,
            "x": [[v / scale for v in c] for c in chans]}


def sine(f, dur, rate=48000, amp=0.5, phase=0.0):
    n = int(round(dur * rate))
    return [amp * math.sin(2 * math.pi * f * i / rate + phase) for i in range(n)]


# ------------------------------------------------------- own BS.1770 reference
# ITU-R BS.1770-4 K-weighting, 48 kHz coefficients (two-stage IIR).

K1_B = [1.53512485958697, -2.69169618940638, 1.19839281085285]
K1_A = [1.0, -1.69065929318241, 0.73248077421585]
K2_B = [1.0, -2.0, 1.0]
K2_A = [1.0, -1.99004745483398, 0.99007225036621]


def _biquad(x, b, a):
    y = [0.0] * len(x)
    x1 = x2 = y1 = y2 = 0.0
    for i, v in enumerate(x):
        yv = b[0] * v + b[1] * x1 + b[2] * x2 - a[1] * y1 - a[2] * y2
        x2, x1 = x1, v
        y2, y1 = y1, yv
        y[i] = yv
    return y


def k_weight(x):
    return _biquad(_biquad(x, K1_B, K1_A), K2_B, K2_A)


def _ms(x):
    return sum(v * v for v in x) / max(1, len(x))


def loudness_from_ms(sum_ms):
    """L = -0.691 + 10 log10(sum of channel-weighted mean squares)."""
    if sum_ms <= 0.0:
        return float("-inf")
    return -0.691 + 10.0 * math.log10(sum_ms)


def chans_ms(chans, weights):
    """chans: list of sample lists (already K-weighted); weights: per-channel."""
    tot = 0.0
    for c, wgt in zip(chans, weights):
        tot += wgt * _ms(c)
    return tot


def momentary_series(chans, weights, rate, win_s=0.4, step_s=0.1):
    """Sliding momentary loudness: mean over trailing win_s, stepped by step_s."""
    n = len(chans[0])
    win = int(round(win_s * rate))
    step = max(1, int(round(step_s * rate)))
    cum = []
    for c, wgt in zip(chans, weights):
        cc = [0.0] * (n + 1)
        for i, v in enumerate(c):
            cc[i + 1] = cc[i] + wgt * v * v
        cum.append(cc)
    out = []
    for end in range(win, n + 1, step):
        s = 0.0
        for cc in cum:
            s += (cc[end] - cc[end - win]) / win
        out.append((end, loudness_from_ms(s)))
    return out


def integrated_lufs(chans, weights, rate, block_s=0.4, overlap=0.75):
    """BS.1770-4 gated integrated loudness (absolute -70 LUFS, relative -10 LU)."""
    n = len(chans[0])
    win = int(round(block_s * rate))
    step = max(1, int(round(win * (1.0 - overlap))))
    cum = []
    for c, wgt in zip(chans, weights):
        cc = [0.0] * (n + 1)
        for i, v in enumerate(c):
            cc[i + 1] = cc[i] + wgt * v * v
        cum.append(cc)
    blocks = []
    for st in range(0, n - win + 1, step):
        en = st + win
        s = 0.0
        for cc in cum:
            s += (cc[en] - cc[st]) / win
        blocks.append(loudness_from_ms(s))
    if not blocks:
        return {"lufs": float("-inf"), "n_blocks": 0, "n_abs": 0, "n_rel": 0,
                "rel_thresh": None}
    above_abs = [b for b in blocks if b > -70.0]
    if not above_abs:
        return {"lufs": float("-inf"), "n_blocks": len(blocks), "n_abs": 0,
                "n_rel": 0, "rel_thresh": None}
    # relative threshold: loudness of the mean of blocks above absolute gate
    mean_abs = sum(10 ** ((b + 0.691) / 10.0) for b in above_abs) / len(above_abs)
    rel = -0.691 + 10.0 * math.log10(mean_abs) - 10.0
    above_rel = [b for b in above_abs if b > rel]
    mean_rel = sum(10 ** ((b + 0.691) / 10.0) for b in above_rel) / len(above_rel)
    return {"lufs": -0.691 + 10.0 * math.log10(mean_rel), "n_blocks": len(blocks),
            "n_abs": len(above_abs), "n_rel": len(above_rel), "rel_thresh": rel}


def jdump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, sort_keys=True)
    return path
