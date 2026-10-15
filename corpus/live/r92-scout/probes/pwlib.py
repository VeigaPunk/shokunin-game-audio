"""r92 scout shared library — own bounded process helpers, own synth, own DSP analysis.

Seat-owned. No import of corpus/fixtures/measure_audio.py (sibling-owned, dirty).
Every child runs in its own session (start_new_session) and is killed by process
group on wall-cap; captures are additionally byte-capped.
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

SEAT = "r92s"
WALL = 6.0          # default wall cap per child (s)
BYTE_CAP = 8 << 20  # default byte cap per capture (8 MB)


def _ncore():
    """pw-cli aborts (SIGABRT) on stdin EOF on this host -> no core files."""
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
        if len(out) > self.byte_cap:
            self.byte_capped = True
            self.out = self.out[: self.byte_cap]

    def as_dict(self):
        return {
            "argv": self.argv, "rc": self.rc, "dur": round(self.dur, 3),
            "timed_out": self.timed_out, "byte_capped": self.byte_capped,
            "out": self.out[-4000:], "err": self.err[-4000:],
        }


def run(argv, **kw):
    return Bounded(argv, **kw)


class PwCli:
    """Interactive pw-cli driven through a pipe; load/unload modules in-process.

    A module loaded by pw-cli lives in the pw-cli client context: the module var
    is only addressable from this session, and the objects die with the process.
    """

    def __init__(self, wall=20.0, env=None, idle=0.8, hard=8.0):
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
        """Returns (out_text, module_var). pw-cli prints '<var> = @module:<id>'."""
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


# ---------------------------------------------------------------- own synth

def write_wav(path, samples, rate=48000, ch=1):
    """samples: list of floats (mono) or list of tuples (interleaved)."""
    with wave.open(path, "wb") as w:
        w.setnchannels(ch)
        w.setsampwidth(2)
        w.setframerate(rate)
        frames = bytearray()
        if ch == 1:
            for s in samples:
                v = int(max(-1.0, min(1.0, s)) * 32767)
                frames += struct.pack("<h", v)
        else:
            for tup in samples:
                for s in tup:
                    v = int(max(-1.0, min(1.0, s)) * 32767)
                    frames += struct.pack("<h", v)
        w.writeframes(bytes(frames))


def read_wav(path):
    with wave.open(path, "rb") as w:
        rate = w.getframerate()
        ch = w.getnchannels()
        sw = w.getsampwidth()
        n = w.getnframes()
        raw = w.readframes(n)
    if sw == 2:
        vals = struct.unpack("<%dh" % (len(raw) // 2), raw)
    elif sw == 4:
        vals = struct.unpack("<%di" % (len(raw) // 4), raw)
    else:
        raise ValueError("sampwidth %d" % sw)
    scale = 32768.0 if sw == 2 else 2147483648.0
    if ch > 1:
        vals = [vals[i::ch] for i in range(ch)]
    else:
        vals = [list(vals)]
    return {"rate": rate, "ch": ch, "sw": sw, "frames": n,
            "x": [[v / scale for v in c] for c in vals]}


def sine(f, dur, rate=48000, amp=0.5, phase=0.0):
    n = int(dur * rate)
    return [amp * math.sin(2 * math.pi * f * i / rate + phase) for i in range(n)]


def multitone(freqs, dur, rate=48000, amp=0.4):
    """Sum of sines; each freq chosen to be an integer number of cycles in dur."""
    n = int(dur * rate)
    out = []
    for i in range(n):
        s = 0.0
        for f in freqs:
            s += amp * math.sin(2 * math.pi * f * i / rate)
        out.append(s / max(1, len(freqs)))
    return out


def delta_wav(path, delay_samples=0, taps=None, rate=48000, n=4096):
    """taps: list of (offset, gain). Default: single impulse at delay_samples."""
    if taps is None:
        taps = [(delay_samples, 1.0)]
    buf = [0.0] * n
    for off, g in taps:
        if 0 <= off < n:
            buf[off] = g
    write_wav(path, buf, rate=rate, ch=1)
    return buf


# ------------------------------------------------------- own DSP analysis

def dft_mag(x, f, rate):
    """Single-bin DFT magnitude (Goertzel-style) at frequency f."""
    n = len(x)
    re = im = 0.0
    w = 2 * math.pi * f / rate
    for i, v in enumerate(x):
        re += v * math.cos(w * i)
        im -= v * math.sin(w * i)
    return 2.0 * math.hypot(re, im) / n


def dft_mags(x, freqs, rate):
    return {f: round(dft_mag(x, f, rate), 6) for f in freqs}


def peak_index(x, thresh=0.02):
    """Index of the largest absolute sample (impulse peak)."""
    best, bi = 0.0, -1
    for i, v in enumerate(x):
        if abs(v) > best:
            best, bi = abs(v), i
    return (bi, round(best, 6)) if best > thresh else (-1, round(best, 6))


def xcorr_lag(a, b, maxlag=4096):
    """Lag (in samples) of the best positive-lag match of b against a."""
    best, bl = -1e18, 0
    n = min(len(a), len(b))
    for lag in range(0, min(maxlag, n)):
        s = 0.0
        for i in range(0, n - lag, 8):
            s += a[i] * b[i + lag]
        if s > best:
            best, bl = s, lag
    return bl


def biquad_ir(label, freq, q, gain_db, rate=48000, n=4096):
    """Reference biquad impulse response (RBJ cookbook) for cross-check."""
    A = 10 ** (gain_db / 40.0)
    w0 = 2 * math.pi * freq / rate
    cw, sw = math.cos(w0), math.sin(w0)
    alpha = sw / (2 * q)
    if label == "bq_lowpass":
        b0, b1, b2 = (1 - cw) / 2, 1 - cw, (1 - cw) / 2
        a0, a1, a2 = 1 + alpha, -2 * cw, 1 - alpha
    elif label == "bq_highpass":
        b0, b1, b2 = (1 + cw) / 2, -(1 + cw), (1 + cw) / 2
        a0, a1, a2 = 1 + alpha, -2 * cw, 1 - alpha
    elif label == "bq_peaking":
        b0, b1, b2 = 1 + alpha * A, -2 * cw, 1 - alpha * A
        a0, a1, a2 = 1 + alpha / A, -2 * cw, 1 - alpha / A
    elif label == "bq_lowshelf":
        s = 2 * math.sqrt(A) * alpha
        b0 = A * ((A + 1) - (A - 1) * cw + s)
        b1 = 2 * A * ((A - 1) - (A + 1) * cw)
        b2 = A * ((A + 1) - (A - 1) * cw - s)
        a0 = (A + 1) + (A - 1) * cw + s
        a1 = -2 * ((A - 1) + (A + 1) * cw)
        a2 = (A + 1) + (A - 1) * cw - s
    elif label == "bq_highshelf":
        s = 2 * math.sqrt(A) * alpha
        b0 = A * ((A + 1) + (A - 1) * cw + s)
        b1 = -2 * A * ((A - 1) + (A + 1) * cw)
        b2 = A * ((A + 1) + (A - 1) * cw - s)
        a0 = (A + 1) - (A - 1) * cw + s
        a1 = 2 * ((A - 1) - (A + 1) * cw)
        a2 = (A + 1) - (A - 1) * cw - s
    elif label == "bq_notch":
        b0, b1, b2 = 1, -2 * cw, 1
        a0, a1, a2 = 1 + alpha, -2 * cw, 1 - alpha
    elif label == "bq_allpass":
        b0, b1, b2 = 1 - alpha, -2 * cw, 1 + alpha
        a0, a1, a2 = 1 + alpha, -2 * cw, 1 - alpha
    else:
        raise ValueError(label)
    b = [b0 / a0, b1 / a0, b2 / a0]
    a = [1.0, a1 / a0, a2 / a0]
    y = [0.0] * n
    x = [0.0] * n
    x[0] = 1.0
    for i in range(n):
        acc = b[0] * x[i]
        if i >= 1:
            acc += b[1] * x[i - 1] - a[1] * y[i - 1]
        if i >= 2:
            acc += b[2] * x[i - 2] - a[2] * y[i - 2]
        y[i] = acc
    return y


def jdump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, sort_keys=True)
    return path
