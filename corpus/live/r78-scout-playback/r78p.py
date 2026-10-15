#!/usr/bin/env python3
"""R78 PLAYBACK-side scout harness (own).

Own harness, own classifiers — never imports corpus/fixtures (a sibling seat
is editing it concurrently).  Every leg is bounded three ways: consumer
duration flag, outer subprocess timeout, reader byte cap.  Every write stays
under corpus/live/r78-scout-playback/.

Playback has no output artifact, so the routing witness is a pair:
  (a) link topology   — pw-link -l consumers of the stream's output ports
  (b) content witness — concurrent pw-record captures of candidate sink
                        monitors; the monitor that carries the tone names the
                        sink that actually consumed the stream.
Tone is uniquely tagged per leg via node.name=r78p_<leg>.
"""
import json
import math
import os
import re
import signal
import struct
import subprocess
import time
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
SEAT = os.path.join(ROOT, "corpus", "live", "r78-scout-playback")
SCRATCH = os.path.join(SEAT, "scratch")
RAW = os.path.join(SEAT, "raw")
for d in (SEAT, SCRATCH, RAW):
    os.makedirs(d, exist_ok=True)

CAP_BYTES = 262144
DEFAULT_TIMEOUT = 15.0

S_SPDIF = "alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink"
S_SPK = "alsa_output.usb-Generic_USB_Audio-00.HiFi__Speaker__sink"
S_HP = "alsa_output.usb-Generic_USB_Audio-00.HiFi__Headphones__sink"
S_HDMI = "alsa_output.pci-0000_01_00.1.hdmi-stereo"
S_DS = ("alsa_output.usb-Sony_Interactive_Entertainment_DualSense_"
        "Wireless_Controller-00.Direct__Direct__sink")
LINE = "alsa_input.usb-Generic_USB_Audio-00.HiFi__Line__source"
MIC = "alsa_input.usb-Generic_USB_Audio-00.HiFi__Mic__source"
NS = "r78p_ns"
NS2 = "r78p_ns2"
# witness set: probe-owned null sinks + the three real outputs on card 0
WITNESS = [("ns", NS), ("ns2", NS2), ("spdif", S_SPDIF), ("spk", S_SPK),
           ("hdmi", S_HDMI)]
TONE = os.path.join(RAW, "tone_r78p.wav")


def sh(argv, timeout=DEFAULT_TIMEOUT, env=None):
    e = dict(os.environ)
    if env:
        e.update(env)
    t0 = time.monotonic()
    try:
        p = subprocess.run(argv, capture_output=True, timeout=timeout, env=e)
        return (p.returncode, p.stdout, p.stderr.decode(errors="replace"),
                round(time.monotonic() - t0, 3), False)
    except subprocess.TimeoutExpired as exc:
        return (None, (exc.stdout or b""),
                (exc.stderr or b"").decode(errors="replace"),
                round(time.monotonic() - t0, 3), True)
    except OSError as exc:
        return None, b"", f"spawn failed: {exc}", round(
            time.monotonic() - t0, 3), False


# ---------------------------------------------------------------- tone file

def make_tone(path=TONE, dur=2.0, freq=1000.0, amp=8192, rate=48000,
              ch=2):
    n = int(dur * rate)
    with wave.open(path, "wb") as w:
        w.setnchannels(ch)
        w.setsampwidth(2)
        w.setframerate(rate)
        buf = bytearray()
        for i in range(n):
            v = int(amp * math.sin(2 * math.pi * freq * i / rate))
            for c in range(ch):
                # left = freq, right = 1.5*freq so a channel swap is visible
                vv = v if c == 0 else int(amp * math.sin(
                    2 * math.pi * freq * 1.5 * i / rate))
                buf += struct.pack("<h", vv)
        w.writeframes(bytes(buf))
    return path


# ---------------------------------------------------------------- readers

def payload(path, cap=None):
    """Own RIFF payload extractor (no fixtures import).

    cap=None reads the whole file: an earlier 256 KiB default silently
    truncated every analysis to the first ~1.4 s of a capture, which is
    exactly where a late-pin tone is NOT.
    """
    try:
        b = open(path, "rb").read() if cap is None else open(
            path, "rb").read(cap * 4)
    except OSError:
        return b"", 0, {}
    if len(b) < 44:
        return b"", 0, {"bytes": len(b), "short": True}
    riff = b[0:4]
    i = b.find(b"data", 12)
    declared = None
    if i >= 0:
        declared = struct.unpack("<I", b[i + 4:i + 8])[0]
    meta = {"bytes": len(b), "riff": riff.decode(errors="replace"),
            "declared_data": declared}
    avail = len(b) - (i + 8) if i >= 0 else 0
    n = min(declared, avail) if declared is not None else avail
    if cap is not None:
        n = min(n, cap)
    body = b[i + 8:i + 8 + n] if i >= 0 else b""
    return body, len(body), meta


def peaks(path):
    """Per-channel peak + nonzero fraction of an s16le/2ch capture."""
    body, n, meta = payload(path)
    n = n - (n % 4)
    if n == 0:
        return {"peak_L": 0, "peak_R": 0, "peak": 0, "frames": 0,
                "payload": 0, "nonzero_frac": 0.0, "meta": meta}
    a = np.frombuffer(body[:n], dtype="<i2").reshape(-1, 2)
    lmax = int(np.abs(a[:, 0]).max())
    rmax = int(np.abs(a[:, 1]).max())
    nz = int(np.count_nonzero(np.abs(a).max(axis=1)))
    frames = n // 4
    return {"peak_L": lmax, "peak_R": rmax, "peak": max(lmax, rmax),
            "frames": frames, "payload": n,
            "nonzero_frac": round(nz / frames, 4) if frames else 0.0,
            "meta": meta}


def analyze_capture(path, floor=512):
    p = peaks(path)
    p["tone"] = bool(p["peak"] >= floor and p["nonzero_frac"] > 0.5)
    return p


# ---- frequency-strict classification -------------------------------------
# The default-sink monitor is NOT a clean floor: a concurrent lane's probe
# tone (amp ~4096) aliases it.  So a witness only counts as MINE when both
# channels' dominant frequencies match this seat's tag tone (L 1 kHz,
# R 1.5 kHz) and the amplitude is in range.  Everything else is FOREIGN.

TONE_F_L = 1000.0
TONE_F_R = 1500.0
TONE_AMP = 8192.0
RATE = 48000


def _seg_stats(seg):
    """(peak_L, peak_R, f_L, f_R, frames) — FFT over the ACTIVE span.

    Zero-crossing counting over a whole window is wrong for a partial-coverage
    window (tone present 0.2 s of 0.5 s reads as 400 Hz).  So: locate the
    active span (|sample| >= 64 on either channel) and FFT that span only.
    """
    n = len(seg) - (len(seg) % 4)
    if n < 8:
        return 0, 0, 0.0, 0.0, 0
    a = np.frombuffer(seg[:n], dtype="<i2").reshape(-1, 2).astype(np.float64)
    L, R = a[:, 0], a[:, 1]
    pl, pr = float(np.abs(L).max()), float(np.abs(R).max())
    act = np.nonzero(np.abs(a).max(axis=1) >= 64)[0]
    if len(act) < 480:                      # <10 ms of signal
        return pl, pr, 0.0, 0.0, len(L)

    def domf(x):
        x = x - x.mean()
        w = np.hanning(len(x))
        sp = np.abs(np.fft.rfft(x * w))
        return float(int(np.argmax(sp)) * RATE / len(x))

    s, e = int(act[0]), int(act[-1]) + 1
    return pl, pr, domf(L[s:e]), domf(R[s:e]), len(L)


def windows(path, win=0.5, cap=None):
    """Per-window peak + zero-crossing frequency, in capture-file order."""
    body, n, meta = payload(path, cap=cap)
    step = int(win * RATE) * 4
    out = []
    for k, s in enumerate(range(0, n, step)):
        pl, pr, fl, fr, fr_n = _seg_stats(body[s:s + step])
        out.append({"t0": round(k * win, 3), "peak_L": pl, "peak_R": pr,
                    "f_L": round(fl, 1), "f_R": round(fr, 1),
                    "frames": fr_n})
    return {"meta": meta, "windows": out}


def is_mine(w, amp=TONE_AMP, tol=0.06):
    """Strict: BOTH channels carry this seat's tag tone."""
    if w["peak_L"] < amp * 0.5 or w["peak_R"] < amp * 0.4:
        return False
    if abs(w["f_L"] - TONE_F_L) > TONE_F_L * tol:
        return False
    if abs(w["f_R"] - TONE_F_R) > TONE_F_R * tol:
        return False
    return True


def is_mine_r_tag(w, amp=TONE_AMP, tol=0.06):
    """Loose: the 1.5 kHz RIGHT channel alone names the tone.

    Survives a concurrent 1 kHz-stereo probe tone summing on the left.
    """
    return (w["peak_R"] >= amp * 0.4
            and abs(w["f_R"] - TONE_F_R) <= TONE_F_R * tol)


def classify(path, win=0.5, cap=None):
    """mine / foreign / silent per window for one capture file."""
    w = windows(path, win=win, cap=cap)
    mine = [x["t0"] for x in w["windows"] if is_mine(x)]
    rtag = [x["t0"] for x in w["windows"] if is_mine_r_tag(x)]
    foreign = [x["t0"] for x in w["windows"]
               if x["peak_L"] >= 512 and not is_mine(x)]
    silent = [x["t0"] for x in w["windows"] if x["peak_L"] < 512]
    return {"meta": w["meta"], "n_windows": len(w["windows"]),
            "mine": mine, "mine_r_tag": rtag, "foreign": foreign,
            "silent": silent, "windows": w["windows"],
            "verdict": ("mine" if mine else
                        "mine_r_tag" if rtag else
                        "foreign" if foreign else "silent")}


def sha256(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()[:16]


# ---------------------------------------------------------------- pipewire

def pwlink():
    rc, out, err, _, _ = sh(["pw-link", "-l"], timeout=6)
    txt = out.decode(errors="replace")
    links = {}
    cur = None
    for line in txt.splitlines():
        if not line.strip():
            continue
        if line.lstrip().startswith("|->"):
            if cur:
                links.setdefault(cur, []).append(line.split("|->")[1].strip())
        elif line.lstrip().startswith("<-|"):
            if cur:
                links.setdefault(line.split("<-|")[1].strip(),
                                 []).append(cur)
        else:
            cur = line.strip()
            links.setdefault(cur, [])
    return links


def consumers_of(links, tag):
    """Downstream peers of <tag>:output_* (playback destination ports)."""
    out = {}
    for port, peers in links.items():
        if port.startswith(tag + ":") and "output" in port:
            out[port] = peers
    return out


def producers_of(links, tag):
    out = {}
    for port, peers in links.items():
        if port.startswith(tag + ":") and "input" in port:
            out[port] = peers
    return out


def pw_nodes():
    rc, out, err, _, _ = sh(["pw-dump"], timeout=10)
    nodes = {}
    try:
        d = json.loads(out.decode(errors="replace"))
    except Exception:
        return nodes
    for o in d:
        if o.get("type") != "PipeWire:Interface:Node":
            continue
        p = dict(o.get("info", {}).get("props", {}))
        p["_id"] = o["id"]
        p["_state"] = o.get("info", {}).get("state")
        nodes[p.get("node.name", f"id{o['id']}")] = p
    return nodes


PROP_KEYS = ("node.name", "media.class", "media.role", "media.category",
             "target.object", "node.target", "node.autoconnect",
             "stream.capture.sink", "stream.monitor", "stream.is-live",
             "application.name", "client.api", "node.virtual",
             "audio.channels", "audio.rate", "resample.quality")


def prop_slice(props):
    return {k: props[k] for k in PROP_KEYS if k in props}


def pactl(*args, timeout=8):
    return sh(["pactl", *args], timeout=timeout)


def load_null(name, desc="r78p probe null"):
    rc, out, err, _, _ = pactl("load-module", "module-null-sink",
                               f"sink_name={name}",
                               f"sink_properties=device.description={desc}")
    return out.decode().strip() if rc == 0 else None, rc, err


def unload(mid):
    return pactl("unload-module", str(mid))


def unload_all_mine(prefix="r78p"):
    """Unload every probe-owned null sink (leak hygiene).

    A leaked duplicate sink NAME is a measurement trap: a name-targeted
    stream and a name-targeted monitor witness can resolve to DIFFERENT
    same-named nodes, which reads as 'linked but silent'.
    """
    rc, out, err, _, _ = sh(["pactl", "list", "modules", "short"], timeout=8)
    ids = [l.split()[0] for l in out.decode(errors="replace").splitlines()
           if f"sink_name={prefix}" in l]
    res = [[i, unload(i)[0]] for i in ids]
    return {"unloaded": res, "count": len(res)}


# ---------------------------------------------------------------- monitors

class Monitors:
    """Concurrent pw-record captures of candidate sink monitors."""

    def __init__(self, sinks=None, tag="r78pmon", rate=48000, ch=2, win=0.5):
        self.sinks = sinks or WITNESS
        self.tag = tag
        self.win = win
        self.procs = {}
        self.paths = {}

    def start(self):
        for label, sink in self.sinks:
            path = os.path.join(RAW, f"{self.tag}_{label}.wav")
            self.paths[label] = path
            if os.path.exists(path):
                os.unlink(path)
            p = subprocess.Popen(
                ["pw-record", "-P", f"node.name={self.tag}_{label}",
                 "-P", "stream.capture.sink=true",
                 "--target", sink, "--format", "s16", "--rate", "48000",
                 "--channels", "2", path],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.procs[label] = p
        time.sleep(0.35)

    def stop(self):
        for p in self.procs.values():
            if p.poll() is None:
                p.send_signal(signal.SIGTERM)
        for p in self.procs.values():
            try:
                p.wait(timeout=4)
            except subprocess.TimeoutExpired:
                p.kill()
                p.wait(timeout=2)
        return self.result()

    def result(self):
        out = {}
        for label, _ in self.sinks:
            c = classify(self.paths[label], win=self.win)
            c["peak"] = peaks(self.paths[label])["peak"]
            c["sha256"] = sha256(self.paths[label])
            out[label] = c
        return out

    def mine_labels(self):
        r = self.result()
        return [lab for lab in r if r[lab]["verdict"] in ("mine",
                                                          "mine+foreign")]


def play(args, tag, timeout=12.0, env=None, extra=None):
    """Run pw-play/pw-cat -p bounded; return (rc, err, wall, timed_out)."""
    argv = ["pw-play", "-P", f"node.name={tag}", *args]
    if extra:
        argv += extra
    return sh(argv, timeout=timeout, env=env)


def one_leg(mon, argv, tag, probe_at=1.0, timeout=12.0, env=None,
            sample_every=0.0, tail=0.6):
    """Play `argv` while monitors run; sample topology/props mid-stream.

    sample_every > 0 records a topology timeline (t, consumers) so a late
    link (or a late loss) is visible rather than inferred from one sample.
    `tail` keeps the witnesses recording after the consumer exits, so a
    FOREIGN (concurrent-lane) tone is separable from this leg's tone.
    """
    mon.start()
    t0 = time.monotonic()
    deadline = t0 + timeout
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env={**os.environ,
                                                         **(env or {})})
    mid = {}
    timeline = []
    try:
        time.sleep(probe_at)
        mid["links"] = consumers_of(pwlink(), tag)
        mid["props"] = prop_slice(pw_nodes().get(tag, {}))
        mid["alive"] = proc.poll() is None
        if sample_every > 0:
            while proc.poll() is None and time.monotonic() < deadline:
                timeline.append([round(time.monotonic() - t0, 2),
                                 consumers_of(pwlink(), tag)])
                time.sleep(sample_every)
    except Exception as exc:  # pragma: no cover
        mid["error"] = repr(exc)
    try:
        so, se = proc.communicate(timeout=max(0.3, deadline -
                                              time.monotonic()))
        rc = proc.returncode
        err = se.decode(errors="replace")
        timed_out = False
    except subprocess.TimeoutExpired:
        proc.kill()
        so, se = proc.communicate()
        rc, err, timed_out = None, se.decode(errors="replace"), True
    time.sleep(tail)
    wall = round(time.monotonic() - t0, 3)
    caps = mon.stop()
    return {"argv": argv, "rc": rc, "stderr": err.strip()[:400],
            "wall_s": wall, "timed_out": timed_out, "mid": mid,
            "timeline": timeline, "caps": caps,
            "carried": [k for k, v in caps.items()
                        if v["verdict"] in ("mine", "mine_r_tag")],
            "foreign": [k for k, v in caps.items() if v["foreign"]]}


def save(name, obj):
    path = os.path.join(SEAT, name)
    with open(path, "w") as f:
        json.dump(obj, f, indent=1)
    print("wrote", path)
    return path


def toolchain():
    t = {}
    for k, argv in (("pw-cat", ["pw-cat", "--version"]),
                    ("pactl", ["pactl", "--version"]),
                    ("aplay", ["aplay", "--version"]),
                    ("arecord", ["arecord", "--version"]),
                    ("ffmpeg", ["ffmpeg", "-version"]),
                    ("python", ["python3", "-V"]),
                    ("uname", ["uname", "-r"])):
        rc, out, err, _, _ = sh(argv, timeout=8)
        t[k] = (out.decode(errors="replace") + err).strip().splitlines()[0:2]
    return t
