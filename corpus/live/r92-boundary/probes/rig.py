"""r92b boundary rig — an INDEPENDENT falsification instrument for the r92 scout.

Seat-owned (`r92b_*`). No import of the scout's modules, no import of
corpus/fixtures/measure_audio.py. Own WAV I/O (s16/s24/f32), own numpy DFT,
own analytic RBJ reference (complex response, not impulse simulation).

Topology (identical in shape to the scout's proven v2 rig, so the pins are
replayable; every stream has node.autoconnect=false):

    pw-play r92b_play -> r92b_in null sink (driver, mono)
    r92b_in:monitor_MONO -> r92b_fc_in:playback_MONO   (filter-chain input)
    r92b_in:monitor_MONO -> r92b_ref:input_MONO        (PRE tap)
    r92b_fc_out:output_MONO -> r92b_rec:input_MONO     (POST tap)

Transfer function = post-bin / pre-bin (route gain cancels).

Bounds: every child is start_new_session + wall cap + killpg; captures are
wall-bounded; RLIMIT_CORE=0 (pw-cli aborts on stdin EOF on this host).
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

import numpy as np

SEAT = "r92b"
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNS = os.path.join(HERE, "runs")
SCRATCH = os.path.join(HERE, "scratch")
REC = os.path.join(HERE, "receipts")
for _d in (RUNS, SCRATCH, REC):
    os.makedirs(_d, exist_ok=True)

RATE = 48000
FREQS = [200, 1000, 4000, 12000, 20000]   # 20000 added: Freq-edge discrimination
WIN = 24000                                # 0.5 s; all FREQS have integer cycles
NS = "r92b_in"
FC_IN, FC_OUT = "r92b_fc_in", "r92b_fc_out"
PLAY, REF, RECN = "r92b_play", "r92b_ref", "r92b_rec"
LOAD_SINK = "r92b_load"
AUDIO_TOOLS = ("pw-record", "pw-play", "pw-cli", "pw-cat", "pw-dump", "pw-link",
               "pw-mididump", "wpexec", "pipewire")


def ncore():
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


# --------------------------------------------------------------- bounded child

class Bounded:
    def __init__(self, argv, wall=8.0, byte_cap=1 << 20, stdin_data=None, env=None, cwd=None):
        self.argv, self.wall, self.byte_cap = argv, wall, byte_cap
        self.t0 = time.time()
        self.timed_out = False
        e = dict(os.environ)
        if env:
            e.update(env)
        p = subprocess.Popen(argv, stdin=subprocess.PIPE if stdin_data is not None else subprocess.DEVNULL,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             start_new_session=True, preexec_fn=ncore, env=e, cwd=cwd)
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
        self.dur = round(time.time() - self.t0, 3)
        self.out = out.decode("utf-8", "replace")[:self.byte_cap]
        self.err = err.decode("utf-8", "replace")[:self.byte_cap]
        self.out_bytes = len(out)
        self.err_bytes = len(err)

    def d(self):
        return {"argv": self.argv, "rc": self.rc, "dur": self.dur, "timed_out": self.timed_out,
                "out_bytes": self.out_bytes, "out": self.out[-3000:], "err": self.err[-3000:]}


def run(argv, **kw):
    return Bounded(argv, **kw)


class Bg:
    """Background child with wall cap + killpg."""

    def __init__(self, argv, wall=14.0, env=None):
        self.argv, self.wall, self.t0 = argv, wall, time.time()
        e = dict(os.environ)
        if env:
            e.update(env)
        self.p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  stdin=subprocess.DEVNULL, start_new_session=True, env=e,
                                  preexec_fn=ncore)

    def alive(self):
        return self.p.poll() is None

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
                "out": out.decode("utf-8", "replace")[-800:],
                "err": err.decode("utf-8", "replace")[-800:]}


class PwCli:
    """Interactive pw-cli; a module loaded here dies with this process."""

    def __init__(self, wall=20.0, idle=0.35, hard=2.5, env=None):
        e = dict(os.environ)
        if env:
            e.update(env)
        self.p = subprocess.Popen(["pw-cli"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT, start_new_session=True, bufsize=0,
                                  env=e, preexec_fn=ncore)
        self.log = []
        self._idle(idle, hard)

    def _idle(self, idle, hard):
        import select
        buf, t0, last = b"", time.time(), time.time()
        while time.time() - t0 < hard:
            r, _, _ = select.select([self.p.stdout], [], [], 0.15)
            if r:
                ch = os.read(self.p.stdout.fileno(), 65536)
                if not ch:
                    break
                buf += ch
                last = time.time()
            elif time.time() - last > idle:
                break
        txt = buf.decode("utf-8", "replace")
        self.log.append(txt)
        return txt

    def cmd(self, line, idle=None, hard=None):
        try:
            self.p.stdin.write((line + "\n").encode())
            self.p.stdin.flush()
        except Exception as e:
            return "<<write failed: %r>>" % (e,)
        return self._idle(idle or 0.35, hard or 2.5)

    def load(self, module, args):
        out = self.cmd("load-module %s %s" % (module, args), idle=0.6, hard=4.0)
        var = None
        for ln in out.splitlines():
            if "= @module:" in ln:
                try:
                    var = int(ln.split("=")[0].strip())
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

    def text(self):
        return "".join(self.log)


# ------------------------------------------------------------------ WAV I/O

def wav_write(path, x, rate=RATE, fmt="s16", ch=1):
    """x: 1-D (interleaved) float array in [-1,1]. fmt: s16 | s24 | f32."""
    x = np.asarray(x, dtype=np.float64)
    if fmt == "s16":
        data = np.clip(np.rint(x * 32767.0), -32768, 32767).astype("<i2").tobytes()
        bits, tag, block = 16, 1, 2
    elif fmt == "s24":
        v = np.clip(np.rint(x * 8388607.0), -8388608, 8388607).astype("<i4")
        raw = v.astype("<u4").view(np.uint8).reshape(-1, 4)[:, :3]
        data = raw.tobytes()
        bits, tag, block = 24, 1, 3
    elif fmt == "f32":
        data = x.astype("<f4").tobytes()
        bits, tag, block = 32, 3, 4
    else:
        raise ValueError(fmt)
    n = len(x) // ch
    hdr = b"RIFF" + struct.pack("<I", 36 + len(data)) + b"WAVE"
    hdr += b"fmt " + struct.pack("<IHHIIHH", 16, tag, ch, rate, rate * block * ch, block * ch, bits)
    hdr += b"data" + struct.pack("<I", len(data))
    with open(path, "wb") as f:
        f.write(hdr + data)
    return {"path": path, "frames": n, "bytes": 44 + len(data), "fmt": fmt, "rate": rate}


def wav_read(path):
    """Minimal RIFF reader: PCM s16/s24/s32 and IEEE float32."""
    with open(path, "rb") as f:
        b = f.read()
    if b[:4] != b"RIFF" or b[8:12] != b"WAVE":
        raise ValueError("not a RIFF/WAVE file: %s" % path)
    pos, fmt, data = 12, None, None
    while pos + 8 <= len(b):
        cid, sz = b[pos:pos + 4], struct.unpack("<I", b[pos + 4:pos + 8])[0]
        body = b[pos + 8:pos + 8 + sz]
        if cid == b"fmt ":
            tag, ch, rate, _, _, bits = struct.unpack("<HHIIHH", body[:16])
            fmt = {"tag": tag, "ch": ch, "rate": rate, "bits": bits}
            if tag == 0xFFFE and len(body) >= 40:      # WAVE_FORMAT_EXTENSIBLE
                fmt["tag"] = struct.unpack("<H", body[24:26])[0]
        elif cid == b"data":
            data = body
        pos += 8 + sz + (sz & 1)
    if fmt is None or data is None:
        raise ValueError("no fmt/data chunk: %s" % path)
    tag, bits, ch = fmt["tag"], fmt["bits"], fmt["ch"]
    if tag == 1 and bits == 16:
        x = np.frombuffer(data, "<i2").astype(np.float64) / 32768.0
    elif tag == 1 and bits == 24:
        u = np.frombuffer(data, np.uint8).reshape(-1, 3).astype(np.uint32)
        v = (u[:, 0] | (u[:, 1] << 8) | (u[:, 2] << 16)).astype(np.int32)
        v = np.where(v & 0x800000, v - 0x1000000, v)
        x = v.astype(np.float64) / 8388608.0
    elif tag == 1 and bits == 32:
        x = np.frombuffer(data, "<i4").astype(np.float64) / 2147483648.0
    elif tag == 3 and bits == 32:
        x = np.frombuffer(data, "<f4").astype(np.float64)
    else:
        raise ValueError("unsupported wav tag=%s bits=%s" % (tag, bits))
    if ch > 1:
        x = x.reshape(-1, ch)
    return {"rate": fmt["rate"], "ch": ch, "bits": bits, "tag": tag, "frames": len(x),
            "x": x, "bytes": len(b)}


def sha16(path):
    import hashlib
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


# ------------------------------------------------------------------- synth

def multitone(freqs, dur, rate=RATE, amp=0.2):
    n = int(dur * rate)
    t = np.arange(n) / rate
    x = np.zeros(n)
    for f in freqs:
        x += amp * np.sin(2 * np.pi * f * t)
    return x / max(1, len(freqs))


def single_tone(f, dur, rate=RATE, amp=0.5):
    n = int(dur * rate)
    return amp * np.sin(2 * np.pi * f * np.arange(n) / rate)


def ir_wav(path, taps, n=8192, rate=RATE, fmt="s16"):
    buf = np.zeros(n)
    for off, g in taps:
        if 0 <= off < n:
            buf[off] += g
    return wav_write(path, buf, rate=rate, fmt=fmt)


def decay_ir(path, taps_n=512, decay=0.99, n=8192, rate=RATE):
    """Long exponentially-decaying IR: sample-exactness at scale."""
    buf = np.zeros(n)
    for i in range(taps_n):
        buf[i] = decay ** i
    return wav_write(path, buf, rate=rate)


# ------------------------------------------------------------------ analysis

def dft_mags(x, freqs, rate=RATE):
    """Vectorised single-bin DFT magnitude (same estimator class as the scout's
    Goertzel, independent implementation)."""
    x = np.asarray(x, dtype=np.float64)
    n = len(x)
    t = np.arange(n)
    out = {}
    for f in freqs:
        w = 2 * np.pi * f / rate
        re = float(np.dot(x, np.cos(w * t)))
        im = -float(np.dot(x, np.sin(w * t)))
        out[int(f)] = 2.0 * math.hypot(re, im) / n
    return out


def best_window(x, win=WIN, step=2400):
    if len(x) <= win:
        return np.asarray(x), 0
    best, bi = -1.0, 0
    for i in range(0, len(x) - win + 1, step):
        seg = x[i:i + win]
        r = float(np.dot(seg, seg))
        if r > best:
            best, bi = r, i
    return np.asarray(x[bi:bi + win]), bi


def db(a, b, floor=1e-15):
    return round(20 * math.log10(max(floor, a) / max(floor, b)), 3)


def sig_stats(x):
    x = np.asarray(x)
    return {"n": int(len(x)), "nz_exact": int(np.count_nonzero(x)), "max_abs": float(np.max(np.abs(x))) if len(x) else 0.0,
            "rms": float(np.sqrt(np.mean(x * x))) if len(x) else 0.0}


# ------------------------------------------------------- analytic RBJ reference

def rbj(label, f0, q, gain_db=0.0, rate=RATE, slope=None):
    """RBJ cookbook coefficients (analytic, float64). Returns (b, a) normalised.
    label: lp hp pk ls hs nt ap bp. slope: shelf S (overrides q when set)."""
    if q == 0:
        q = 0.707
    A = 10.0 ** (gain_db / 40.0)
    w0 = 2 * math.pi * f0 / rate
    cw, sw = math.cos(w0), math.sin(w0)
    al = sw / 2 * math.sqrt((A + 1 / A) * (1 / slope - 1) + 2) if slope else sw / (2 * q)
    if label == "lp":
        b, a = [(1 - cw) / 2, 1 - cw, (1 - cw) / 2], [1 + al, -2 * cw, 1 - al]
    elif label == "hp":
        b, a = [(1 + cw) / 2, -(1 + cw), (1 + cw) / 2], [1 + al, -2 * cw, 1 - al]
    elif label == "pk":
        b, a = [1 + al * A, -2 * cw, 1 - al * A], [1 + al / A, -2 * cw, 1 - al / A]
    elif label == "ls":
        s = 2 * math.sqrt(A) * al
        b = [A * ((A + 1) - (A - 1) * cw + s), 2 * A * ((A - 1) - (A + 1) * cw), A * ((A + 1) - (A - 1) * cw - s)]
        a = [(A + 1) + (A - 1) * cw + s, -2 * ((A - 1) + (A + 1) * cw), (A + 1) + (A - 1) * cw - s]
    elif label == "hs":
        s = 2 * math.sqrt(A) * al
        b = [A * ((A + 1) + (A - 1) * cw + s), -2 * A * ((A - 1) + (A + 1) * cw), A * ((A + 1) + (A - 1) * cw - s)]
        a = [(A + 1) - (A - 1) * cw + s, 2 * ((A - 1) - (A + 1) * cw), (A + 1) - (A - 1) * cw - s]
    elif label == "nt":
        b, a = [1, -2 * cw, 1], [1 + al, -2 * cw, 1 - al]
    elif label == "ap":
        b, a = [1 - al, -2 * cw, 1 + al], [1 + al, -2 * cw, 1 - al]
    elif label == "bp":
        b, a = [al, 0.0, -al], [1 + al, -2 * cw, 1 - al]
    else:
        raise ValueError(label)
    b = np.array(b, dtype=np.float64) / a[0]
    a = np.array(a, dtype=np.float64) / a[0]
    return b, a


def rbj_gains(label, f0, q, gain_db=0.0, freqs=None, rate=RATE, slope=None):
    b, a = rbj(label, f0, q, gain_db, rate=rate, slope=slope)
    out = {}
    for f in (freqs or FREQS):
        z = np.exp(-2j * np.pi * f / rate)
        H = (b[0] + b[1] * z + b[2] * z * z) / (a[0] + a[1] * z + a[2] * z * z)
        out[int(f)] = round(20 * math.log10(abs(H)), 3)
    return out


# ------------------------------------------------------------ host census/sweep

def live_r92b():
    d = run(["pw-dump"], wall=8.0)
    try:
        objs = json.loads(d.out)
    except Exception:
        objs = []
    nodes = []
    for o in objs:
        if o.get("type") != "PipeWire:Interface:Node":
            continue
        p = o.get("info", {}).get("props", {})
        nm = p.get("node.name", "")
        if nm.startswith(SEAT):
            nodes.append(nm)
    mods = [l.split()[0] for l in run(["pactl", "list", "modules", "short"], wall=6.0).out.splitlines()
            if SEAT in l]
    return {"nodes": sorted(nodes), "modules": mods, "procs": stray_procs()}


def stray_procs():
    out = run(["ps", "-eo", "pid,cmd"], wall=6.0).out
    keep = []
    for l in out.splitlines():
        parts = l.strip().split(None, 1)
        if len(parts) != 2:
            continue
        pid, cmd = parts
        if not cmd.startswith(AUDIO_TOOLS) and "r92b_burn" not in cmd:
            continue
        if SEAT in cmd:
            keep.append(l.strip()[:160])
    return keep


def kill_stray():
    killed = []
    for l in stray_procs():
        pid = int(l.split()[0])
        try:
            os.kill(pid, signal.SIGKILL)
            killed.append(pid)
        except Exception:
            pass
    return killed


def sink_load(name, channels=1):
    o = run(["pactl", "load-module", "module-null-sink", "sink_name=%s" % name,
             "channels=%d" % channels], wall=6.0)
    mid = None
    try:
        mid = int(o.out.strip().split()[-1])
    except Exception:
        pass
    return {"rc": o.rc, "id": mid, "out": o.out.strip(), "err": o.err.strip()}


def sink_unload(name, expect_id):
    """Namespace-guarded: the module's own args must carry this seat's name."""
    lst = run(["pactl", "list", "modules", "short"], wall=6.0).out
    cand = []
    for line in lst.splitlines():
        if "module-null-sink" in line and ("sink_name=%s" % name) in line and SEAT in line:
            cand.append(int(line.split()[0]))
    verified = expect_id in cand
    o = run(["pactl", "unload-module", str(expect_id)], wall=6.0) if verified else None
    return {"name": name, "expected": expect_id, "candidates": cand, "verified": verified,
            "rc": o.rc if o else None, "err": o.err.strip() if o else None}


def census():
    d = run(["pw-dump"], wall=8.0)
    try:
        objs = json.loads(d.out)
    except Exception:
        objs = []
    nodes = []
    for o in objs:
        if o.get("type") != "PipeWire:Interface:Node":
            continue
        p = o.get("info", {}).get("props", {})
        nm = p.get("node.name", "")
        if not (nm.startswith(SEAT) or p.get("node.description") == "r92b_fc"):
            continue
        ports = sorted(q["info"]["props"].get("port.name")
                       for q in objs if q.get("type") == "PipeWire:Interface:Port"
                       and q.get("info", {}).get("props", {}).get("node.id") == o["id"])
        nodes.append({"id": o["id"], "name": nm, "class": p.get("media.class"),
                      "state": o.get("info", {}).get("state"), "ports": ports,
                      "channels": p.get("audio.channels"), "rate": p.get("node.rate") or p.get("audio.rate")})
    lk = run(["pw-link", "-l"], wall=6.0).out
    return {"nodes": nodes,
            "r92b_links": [l.strip() for l in lk.splitlines() if SEAT in l],
            "spdif_links": [l.strip() for l in lk.splitlines() if "SPDIF" in l]}


def preflight():
    before = live_r92b()
    killed = kill_stray()
    for m in before["modules"]:
        run(["pactl", "unload-module", m], wall=6.0)
    time.sleep(0.4)
    after = live_r92b()
    return {"before": before, "killed": killed, "after": after,
            "was_clean": not (before["nodes"] or before["modules"] or before["procs"])}


def sweep():
    before = live_r92b()
    for m in before["modules"]:
        run(["pactl", "unload-module", m], wall=6.0)
    time.sleep(0.4)
    after = live_r92b()
    return {"before": before, "after": after,
            "clean": not (after["nodes"] or after["modules"] or after["procs"])}


# ---------------------------------------------------------------------- rig

def fc_args(nodes, links=None, channels=1, rate=None, extra=""):
    g = "filter.graph={nodes=[%s]" % ",".join(nodes)
    if links:
        g += ",links=[%s]" % ",".join(links)
    g += "}"
    parts = ["node.description=r92b_fc", g,
             "audio.channels=%d" % channels,
             "audio.position=[MONO]" if channels == 1 else "audio.position=[FL,FR]"]
    if rate:
        parts.append("audio.rate=%d" % rate)
    parts.append("capture.props={node.name=%s,node.autoconnect=false,media.class=Audio/Sink}" % FC_IN)
    parts.append("playback.props={node.name=%s,node.autoconnect=false}" % FC_OUT)
    if extra:
        parts.append(extra)
    return ",".join(parts)


def NODE(label, name="f1", **ctl):
    return "{%s}" % ("type=builtin,name=%s,label=%s" % (name, label)
                     + (",control={%s}" % ",".join("%s=%s" % kv for kv in ctl.items()) if ctl else ""))


class Rig:
    def __init__(self, tag, args, debug="3", idle=0.35, hard=2.5, settle=0.6):
        self.tag, self.args, self.debug = tag, args, debug
        self.idle, self.hard, self.settle = idle, hard, settle
        self.link_log = []

    def arm(self):
        self.sink = sink_load(NS)
        self.cli = PwCli(env={"PIPEWIRE_DEBUG": self.debug}, idle=self.idle, hard=self.hard)
        out, var = self.cli.load("libpipewire-module-filter-chain", self.args)
        self.load_out, self.fc_var = out, var
        time.sleep(self.settle)
        self._link("feed", "%s:monitor_MONO" % NS, "%s:playback_MONO" % FC_IN)
        return self

    def _link(self, tag, a, b, tries=10):
        last = None
        for i in range(tries):
            r = run(["pw-link", a, b], wall=5.0)
            last = r
            if r.rc == 0:
                self.link_log.append({"tag": tag, "a": a, "b": b, "rc": 0, "tries": i + 1})
                return 0
            if "File exists" in r.err:
                self.link_log.append({"tag": tag, "a": a, "b": b, "rc": 0, "tries": i + 1, "note": "exists"})
                return 0
            time.sleep(0.25)
        self.link_log.append({"tag": tag, "a": a, "b": b, "rc": last.rc, "err": last.err.strip()[:200], "tries": tries})
        return last.rc

    def start_captures(self, ref_path, out_path, fmt="s16", wall=14.0):
        for p in (ref_path, out_path):
            if os.path.exists(p):
                os.unlink(p)
        extra = [] if fmt == "s16" else ["--format", fmt]
        self.ref = Bg(["pw-record", "--channels", "1"] + extra +
                      ["-P", "node.name=%s" % REF, "-P", "node.autoconnect=false", ref_path], wall=wall)
        self.rec = Bg(["pw-record", "--channels", "1"] + extra +
                      ["-P", "node.name=%s" % RECN, "-P", "node.autoconnect=false", out_path], wall=wall)
        time.sleep(0.6)
        self.ok_ref = self._link("ref-tap", "%s:monitor_MONO" % NS, "%s:input_MONO" % REF) == 0
        self.ok_rec = self._link("post-tap", "%s:output_MONO" % FC_OUT, "%s:input_MONO" % RECN) == 0
        time.sleep(0.2)

    def play(self, wav, wall=8.0):
        p = Bg(["pw-play", "--target", NS, "-P", "node.name=%s" % PLAY, wav], wall=wall)
        time.sleep(0.8)
        got = [l for l in self.links_now() if PLAY in l]
        if not got:
            self._link("stimulus", "%s:output_MONO" % PLAY, "%s:playback_MONO" % NS)
        else:
            self.link_log.append({"tag": "stimulus-wp", "a": PLAY, "b": NS, "rc": 0, "tries": 1})
        t0 = time.time()
        while p.alive() and time.time() - t0 < wall:
            time.sleep(0.1)
        st = p.stop()
        time.sleep(0.3)
        return st

    def links_now(self):
        return [l.strip() for l in run(["pw-link", "-l"], wall=6.0).out.splitlines() if SEAT in l]

    def stop(self):
        out = {}
        for nm, obj in (("ref", getattr(self, "ref", None)), ("rec", getattr(self, "rec", None))):
            if obj is not None:
                out[nm] = obj.stop()
        time.sleep(0.3)
        return out

    def keep_lines(self):
        txt = self.cli.text() if getattr(self, "cli", None) else ""
        keep = [l.strip()[:300] for l in txt.splitlines()
                if "[E]" in l or "[W]" in l or "using port" in l or "loaded n_" in l]
        return keep[-70:]

    def disarm(self):
        txt = self.cli.text() if getattr(self, "cli", None) else ""
        stats = {"lines": len(txt.splitlines()), "E": txt.count("[E]"), "W": txt.count("[W]"),
                 "I": txt.count("[I]"), "debug": self.debug}
        res = {"tag": self.tag, "sink": self.sink, "links": self.link_log,
               "load_out": (self.load_out or "")[-500:], "fc_var": getattr(self, "fc_var", None),
               "log_stats": stats, "fc_log": self.keep_lines()}
        try:
            if getattr(self, "fc_var", None) is not None:
                res["unload"] = self.cli.cmd("unload-module %d" % self.fc_var, idle=0.5, hard=2.5)[-300:]
        except Exception as e:
            res["cli_error"] = repr(e)
        try:
            self.cli.close()
        except Exception:
            pass
        time.sleep(0.4)
        res["sink_unload"] = sink_unload(NS, self.sink["id"]) if self.sink.get("id") else None
        time.sleep(0.3)
        res["live"] = live_r92b()
        return res


# ------------------------------------------------------------------ leg runner

def analyze_pair(ref_path, out_path):
    if not (os.path.exists(ref_path) and os.path.exists(out_path)):
        return {"ref_bytes": 0, "out_bytes": 0}
    rb, ob = os.path.getsize(ref_path), os.path.getsize(out_path)
    r = {"ref_bytes": rb, "out_bytes": ob, "ref_sha16": sha16(ref_path), "out_sha16": sha16(out_path)}
    if rb < 1000 or ob < 1000:
        return r
    wr, wo = wav_read(ref_path), wav_read(out_path)
    xr, xo = wr["x"], wo["x"]
    r["ref_fmt"], r["out_fmt"] = [wr["tag"], wr["bits"]], [wo["tag"], wo["bits"]]
    r["ref_frames"], r["out_frames"] = wr["frames"], wo["frames"]
    sr, offr = best_window(xr)
    so, offo = best_window(xo)
    r["win_offsets"] = [offr, offo]
    r["ref_stats"], r["out_stats"] = sig_stats(sr), sig_stats(so)
    mr, mo = dft_mags(sr, FREQS), dft_mags(so, FREQS)
    r["ref_mags"], r["out_mags"] = mr, mo
    r["gain_db"] = {str(f): db(mo[f], mr[f]) for f in FREQS}
    r["peak"] = [round(float(np.max(np.abs(sr))), 6), round(float(np.max(np.abs(so))), 6)]
    return r


def analyze_ir(ref_path, out_path, thresh=1e-4):
    if not (os.path.exists(ref_path) and os.path.exists(out_path)):
        return {}
    r = {"ref_bytes": os.path.getsize(ref_path), "out_bytes": os.path.getsize(out_path),
         "ref_sha16": sha16(ref_path), "out_sha16": sha16(out_path)}
    if r["ref_bytes"] < 1000 or r["out_bytes"] < 1000:
        return r
    wr, wo = wav_read(ref_path), wav_read(out_path)
    xr, xo = wr["x"], wo["x"]
    r["ref_stats"], r["out_stats"] = sig_stats(xr), sig_stats(xo)
    for tag, x in (("ref", xr), ("out", xo)):
        idx = np.nonzero(np.abs(x) > thresh)[0]
        r["%s_n_gt" % tag] = int(len(idx))
        r["%s_first" % tag] = [int(idx[0]), round(float(x[idx[0]]), 7)] if len(idx) else None
        if len(idx):
            order = idx[np.argsort(-np.abs(x[idx]))]
            pk = [(int(i), round(float(x[i]), 7)) for i in order[:6]]
            r["%s_top" % tag] = pk
            r["%s_span" % tag] = [int(idx[0]), int(idx[-1])]
    if r.get("out_first") and r.get("ref_first"):
        r["delta_samples"] = r["out_first"][0] - r["ref_first"][0]
    if r.get("out_top") and len(r["out_top"]) >= 2:
        (i0, a0), (i1, a1) = r["out_top"][0], r["out_top"][1]
        r["peak_gap"] = i1 - i0
        r["peak_ratio_signed"] = round(a1 / a0, 6) if a0 else None
    return r


def run_leg(tag, args, kind, rep, stim, attempt_max=2, fmt="s16", debug="3"):
    row = None
    for attempt in range(attempt_max):
        rp = os.path.join(SCRATCH, "%s_ref_%s_%d_%d.wav" % (tag, tag, rep, attempt))
        op = os.path.join(SCRATCH, "%s_out_%s_%d_%d.wav" % (tag, tag, rep, attempt))
        rig = Rig(tag, args, debug=debug).arm()
        rig.start_captures(rp, op, fmt=fmt)
        play = rig.play(os.path.join(SCRATCH, stim))
        stops = rig.stop()
        an = analyze_ir(rp, op) if kind == "ir" else analyze_pair(rp, op)
        d = rig.disarm()
        row = {"rep": rep, "attempt": attempt, "args": args, "analysis": an, "play": play,
               "stops": stops, "links": d["links"], "fc_log": d["fc_log"], "live": d["live"],
               "log_stats": d.get("log_stats"), "sink_unload": d["sink_unload"],
               "load_out": d["load_out"]}
        if kind == "ir":
            ok = an.get("out_bytes", 0) > 1000 and (an.get("out_n_gt", 0) or 0) > 0
        else:
            ok = (an.get("ref_bytes", 0) > 1000 and an.get("out_bytes", 0) > 1000
                  and max(an.get("ref_mags", {}).values() or [0]) > 1e-6
                  and max(an.get("out_mags", {}).values() or [0]) > 1e-6)
        row["valid"] = bool(ok)
        if ok:
            return row
        time.sleep(0.4)
    return row


# ------------------------------------------------------------------- load gen

class LoadGen:
    """Own CPU burners (bounded, killpg) — 'under load' = the same pins, re-armed
    while the host is busy. Optionally a second seat sink fed by a long tone."""

    def __init__(self, n=6):
        self.n = n
        self.procs = []

    def start(self):
        for i in range(self.n):
            self.procs.append(Bg(["python3", "-c",
                                  "x=0\nwhile True: x=(x*1103515245+12345)&0x7fffffff"],
                                 wall=600.0))
        return self

    def stop(self):
        rcs = []
        for p in self.procs:
            rcs.append(p.stop()["rc"])
        return rcs


def jdump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, sort_keys=True, default=str)
    return path
