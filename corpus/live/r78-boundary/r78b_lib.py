#!/usr/bin/env python3
"""R78 BOUNDARY harness (own) — adversarial playback-lattice probes.

Own harness, own classifiers; does not import corpus/fixtures or the
r78-scout-playback harness.  All writes stay under corpus/live/r78-boundary/.

Tag tone is UNIQUE to this seat: L 1100 Hz / R 1750 Hz, amp 12000, s16/48k.
(Scout used 1000/1500 @ 8192; a foreign lane runs ~1000 Hz stereo @ ~4096.)

Playback has no output artifact, so routing evidence = pair of witnesses:
  (a) topology — pw-link -l consumers of the stream's output_* ports
  (b) content  — concurrent pw-record captures of candidate sink monitors,
                 classified frequency-strict per 0.25/0.5 s window.
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
SEAT = os.path.join(ROOT, "corpus", "live", "r78-boundary")
RAW = os.path.join(SEAT, "raw")
for d in (SEAT, RAW):
    os.makedirs(d, exist_ok=True)

DEFAULT_TIMEOUT = 15.0

S_SPDIF = "alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink"
S_SPK = "alsa_output.usb-Generic_USB_Audio-00.HiFi__Speaker__sink"
S_HP = "alsa_output.usb-Generic_USB_Audio-00.HiFi__Headphones__sink"
S_HDMI = "alsa_output.pci-0000_01_00.1.hdmi-stereo"
S_DS = ("alsa_output.usb-Sony_Interactive_Entertainment_DualSense_"
        "Wireless_Controller-00.Direct__Direct__sink")
LINE = "alsa_input.usb-Generic_USB_Audio-00.HiFi__Line__source"
MIC = "alsa_input.usb-Generic_USB_Audio-00.HiFi__Mic__source"
DSSRC = ("alsa_input.usb-Sony_Interactive_Entertainment_DualSense_"
         "Wireless_Controller-00.Direct__Direct__source")
NS = "r78b_ns"
NS2 = "r78b_ns2"
WITNESS = [("ns", NS), ("ns2", NS2), ("spdif", S_SPDIF), ("spk", S_SPK)]
TONE = os.path.join(RAW, "tone_r78b.wav")
TONE2 = os.path.join(RAW, "tone2_r78b.wav")

TONE_F_L = 1100.0
TONE_F_R = 1750.0
TONE_AMP = 12000.0
TONE2_F_L = 800.0
TONE2_F_R = 2100.0
RATE = 48000


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


def make_tone(path=TONE, dur=2.0, fl=TONE_F_L, fr=TONE_F_R, amp=TONE_AMP,
              rate=RATE, ch=2):
    n = int(dur * rate)
    with wave.open(path, "wb") as w:
        w.setnchannels(ch)
        w.setsampwidth(2)
        w.setframerate(rate)
        buf = bytearray()
        for i in range(n):
            vl = int(amp * math.sin(2 * math.pi * fl * i / rate))
            vr = int(amp * math.sin(2 * math.pi * fr * i / rate))
            if ch == 1:
                buf += struct.pack("<h", vl)
            else:
                buf += struct.pack("<h", vl)
                buf += struct.pack("<h", vr)
                for c in range(2, ch):
                    buf += struct.pack("<h", 0)
        w.writeframes(bytes(buf))
    return path


def make_pcm16(path, dur, rate, ch, amp=TONE_AMP, fl=TONE_F_L):
    """Raw s16 mono/stereo/n-ch buffer writer (helper for odd wavs)."""
    n = int(dur * rate)
    buf = bytearray()
    for i in range(n):
        v = int(amp * math.sin(2 * math.pi * fl * i / rate))
        for c in range(ch):
            buf += struct.pack("<h", v if c == 0 else 0)
    return bytes(buf)


# ---------------------------------------------------------------- readers

def payload(path, cap=None):
    try:
        b = open(path, "rb").read() if cap is None else open(
            path, "rb").read(cap * 4)
    except OSError:
        return b"", 0, {}
    if len(b) < 44:
        return b"", 0, {"bytes": len(b), "short": True}
    i = b.find(b"data", 12)
    declared = None
    if i >= 0:
        declared = struct.unpack("<I", b[i + 4:i + 8])[0]
    meta = {"bytes": len(b), "declared_data": declared}
    avail = len(b) - (i + 8) if i >= 0 else 0
    n = min(declared, avail) if declared is not None else avail
    if cap is not None:
        n = min(n, cap)
    body = b[i + 8:i + 8 + n] if i >= 0 else b""
    return body, len(body), meta


def _seg_stats(seg):
    """(peak_L, peak_R, f_L, f_R, frames) over the ACTIVE span."""
    n = len(seg) - (len(seg) % 4)
    if n < 8:
        return 0, 0, 0.0, 0.0, 0
    a = np.frombuffer(seg[:n], dtype="<i2").reshape(-1, 2).astype(np.float64)
    L, R = a[:, 0], a[:, 1]
    pl, pr = float(np.abs(L).max()), float(np.abs(R).max())
    act = np.nonzero(np.abs(a).max(axis=1) >= 64)[0]
    if len(act) < 480:
        return pl, pr, 0.0, 0.0, len(L)

    def domf(x):
        x = x - x.mean()
        w = np.hanning(len(x))
        sp = np.abs(np.fft.rfft(x * w))
        return float(int(np.argmax(sp)) * RATE / len(x))

    s, e = int(act[0]), int(act[-1]) + 1
    return pl, pr, domf(L[s:e]), domf(R[s:e]), len(L)


def windows(path, win=0.5, cap=None):
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
    if w["peak_L"] < amp * 0.5 or w["peak_R"] < amp * 0.4:
        return False
    if abs(w["f_L"] - TONE_F_L) > TONE_F_L * tol:
        return False
    if abs(w["f_R"] - TONE_F_R) > TONE_F_R * tol:
        return False
    return True


def is_mine_r_tag(w, amp=TONE_AMP, tol=0.06):
    return (w["peak_R"] >= amp * 0.4
            and abs(w["f_R"] - TONE_F_R) <= TONE_F_R * tol)


def is_mine2(w, tol=0.06):
    """Second tag tone (800/2100) — for the two-tone mix leg."""
    if w["peak_L"] < TONE_AMP * 0.35 or w["peak_R"] < TONE_AMP * 0.3:
        return False
    if abs(w["f_L"] - TONE2_F_L) > TONE2_F_L * tol:
        return False
    if abs(w["f_R"] - TONE2_F_R) > TONE2_F_R * tol:
        return False
    return True


def classify(path, win=0.5, cap=None):
    w = windows(path, win=win, cap=cap)
    mine = [x["t0"] for x in w["windows"] if is_mine(x)]
    rtag = [x["t0"] for x in w["windows"] if is_mine_r_tag(x)]
    mine2 = [x["t0"] for x in w["windows"] if is_mine2(x)]
    foreign = [x["t0"] for x in w["windows"]
               if x["peak_L"] >= 512 and not is_mine(x) and not is_mine2(x)]
    return {"meta": w["meta"], "n_windows": len(w["windows"]),
            "mine": mine, "mine_r_tag": rtag, "mine2": mine2,
            "foreign": foreign,
            "silent_n": len([x for x in w["windows"] if x["peak_L"] < 512]),
            "windows": w["windows"],
            "verdict": ("mine" if mine else
                        "mine_r_tag" if rtag else
                        "mine2" if mine2 else
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
    out = {}
    for port, peers in links.items():
        if port.startswith(tag + ":") and "output" in port:
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
        nodes.setdefault(p.get("node.name", f"id{o['id']}"), p)
    return nodes


def pw_objects_by_name(name):
    """All pw-dump objects (any type) whose props carry node.name==name."""
    rc, out, err, _, _ = sh(["pw-dump"], timeout=10)
    hits = []
    try:
        d = json.loads(out.decode(errors="replace"))
    except Exception:
        return hits
    for o in d:
        p = o.get("info", {}).get("props", {}) or {}
        if p.get("node.name") == name:
            hits.append({"id": o["id"], "type": o.get("type"),
                         "state": o.get("info", {}).get("state"),
                         "object.serial": p.get("object.serial"),
                         "media.class": p.get("media.class")})
    return hits


def serial_of(node_name, want_type=None):
    rc, out, err, _, _ = sh(["pw-dump"], timeout=10)
    try:
        d = json.loads(out.decode(errors="replace"))
    except Exception:
        return None
    for o in d:
        if o.get("type") != "PipeWire:Interface:Node":
            continue
        p = o.get("info", {}).get("props", {}) or {}
        if p.get("node.name") == node_name:
            return p.get("object.serial")
    return None


def port_serial(port_name):
    """object.serial of a Port whose port.name == port_name."""
    rc, out, err, _, _ = sh(["pw-dump"], timeout=10)
    try:
        d = json.loads(out.decode(errors="replace"))
    except Exception:
        return None
    for o in d:
        if o.get("type") != "PipeWire:Interface:Port":
            continue
        p = o.get("info", {}).get("props", {}) or {}
        if p.get("port.name") == port_name:
            return p.get("object.serial")
    return None


PROP_KEYS = ("node.name", "media.class", "media.role", "media.category",
             "target.object", "node.target", "node.autoconnect",
             "stream.capture.sink", "stream.monitor", "stream.is-live",
             "application.name", "client.api", "node.virtual",
             "audio.channels", "audio.rate", "node.state")


def prop_slice(props):
    return {k: props[k] for k in PROP_KEYS if k in props}


def pactl(*args, timeout=8):
    return sh(["pactl", *args], timeout=timeout)


def pactl_json(*args):
    rc, out, err, w, to = sh(["pactl", "--format=json", *args], timeout=8)
    try:
        return json.loads(out.decode(errors="replace")), rc, err
    except Exception:
        return None, rc, err


def sink_input_index(node_name):
    """pactl sink-input index whose props node.name == node_name (else None)."""
    d, rc, err = pactl_json("list", "sink-inputs")
    if isinstance(d, list):
        for it in d:
            props = it.get("properties", {})
            if props.get("node.name") == node_name:
                return it.get("index")
    return None


def foreign_sink_inputs():
    """sink-inputs not owned by this seat (foreign playback streams)."""
    d, rc, err = pactl_json("list", "sink-inputs")
    out = []
    if isinstance(d, list):
        for it in d:
            props = it.get("properties", {})
            nm = props.get("node.name", "")
            out.append({"index": it.get("index"), "node.name": nm,
                        "sink": it.get("sink"),
                        "mine": nm.startswith("r78b")})
    return out


def load_null(name, desc="r78b probe null"):
    rc, out, err, _, _ = pactl("load-module", "module-null-sink",
                               f"sink_name={name}",
                               f"sink_properties=device.description={desc}")
    return (out.decode().strip() if rc == 0 else None), rc, err


def unload(mid):
    return pactl("unload-module", str(mid))


def unload_all_mine(prefix="r78b"):
    rc, out, err, _, _ = sh(["pactl", "list", "modules", "short"], timeout=8)
    ids = [l.split()[0] for l in out.decode(errors="replace").splitlines()
           if f"sink_name={prefix}" in l]
    res = [[i, unload(i)[0]] for i in ids]
    return {"unloaded": res, "count": len(res)}


def get_default_sink():
    rc, out, err, _, _ = pactl("get-default-sink")
    return out.decode().strip(), rc, err.strip()


def metadata_default():
    rc, out, err, _, _ = sh(["pw-metadata", "-n", "default"], timeout=8)
    txt = out.decode(errors="replace")
    cur = {}
    for m in re.finditer(r"key:'([^']+)' value:'([^']*)'", txt):
        cur[m.group(1)] = m.group(2)
    return cur, txt


def set_default_sink_meta(name_or_json):
    """pw-metadata -n default 0 default.audio.sink <json-string>."""
    return sh(["pw-metadata", "-n", "default", "0", "default.audio.sink",
               name_or_json], timeout=8)


SPDIF_META_JSON = '{"name":"%s"}' % S_SPDIF


def node_state(name):
    n = pw_nodes().get(name)
    return n.get("_state") if n else None


# ---------------------------------------------------------------- monitors

class Monitors:
    """Concurrent pw-record captures of candidate sink monitors.

    `sinks` = list of (label, target) where target is a node.name or an
    object.serial-as-string (pw-record resolves both under
    stream.capture.sink=true).
    """

    def __init__(self, sinks=None, tag="r78bmon", rate=48000, ch=2,
                 win=0.5):
        self.sinks = sinks if sinks is not None else WITNESS
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
                 "--target", str(sink), "--format", "s16", "--rate",
                 "48000", "--channels", "2", path],
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
            c["bytes"] = c["meta"].get("bytes")
            c["sha256"] = sha256(self.paths[label])
            out[label] = c
        return out


def play_leg(argv, tag, monitors=None, probe_at=1.0, timeout=12.0,
             env=None, timeline_every=0.0, tail=0.6, actions=None):
    """Spawn `argv` while `monitors` runs; sample topology mid-stream.

    actions: list of (t_offset, callable) fired while the consumer is alive.
    Returns a per-leg dict with rc/wall/stderr/props/consumers/captures.
    """
    if monitors is None:
        monitors = Monitors(tag=f"{tag}m")
    monitors.start()
    t0 = time.monotonic()
    deadline = t0 + timeout
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            env={**os.environ, **(env or {})})
    mid = {}
    timeline = []
    fired = []
    acts = sorted(actions or [])
    try:
        time.sleep(probe_at)
        mid["links"] = consumers_of(pwlink(), tag)
        mid["props"] = prop_slice(pw_nodes().get(tag, {}))
        mid["node_state"] = node_state(tag)
        mid["alive"] = proc.poll() is None
        while proc.poll() is None and time.monotonic() < deadline:
            now = time.monotonic() - t0
            while acts and now >= acts[0][0]:
                t, fn = acts.pop(0)
                try:
                    fired.append([t, fn()])
                except Exception as exc:
                    fired.append([t, f"ACTION-ERR {exc!r}"])
            if timeline_every > 0:
                timeline.append([round(now, 2),
                                 consumers_of(pwlink(), tag)])
                time.sleep(timeline_every)
            else:
                time.sleep(0.05)
    except Exception as exc:  # pragma: no cover
        mid["error"] = repr(exc)
    # fire remaining actions even if proc exited (e.g. post-exit checks)
    while acts:
        t, fn = acts.pop(0)
        try:
            fired.append([t, fn()])
        except Exception as exc:
            fired.append([t, f"ACTION-ERR {exc!r}"])
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
    caps = monitors.stop()
    return {"argv": argv, "rc": rc, "stderr": err.strip()[:400],
            "stdout": (so or b"").decode(errors="replace").strip()[:200],
            "wall_s": wall, "timed_out": timed_out, "mid": mid,
            "timeline": timeline, "actions": fired, "caps": caps,
            "carried": [k for k, v in caps.items()
                        if v["verdict"] in ("mine", "mine_r_tag")],
            "foreign": [k for k, v in caps.items() if v["foreign"]]}


def pwplay(tag, extra_args, timeout=12.0, **kw):
    argv = ["pw-play", "-P", f"node.name={tag}", *extra_args]
    return play_leg(argv, tag, timeout=timeout, **kw)


def save(name, obj):
    path = os.path.join(SEAT, name)
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, default=str)
    print("wrote", path)
    return path


def foreign_note():
    return {"sink_inputs": foreign_sink_inputs(),
            "procs": [l for l in sh(
                ["ps", "-eo", "pid,comm,args"], timeout=6)[1].decode(
                    errors="replace").splitlines()
                if re.search(r"pw-(play|cat|record)|parec|paplay|pacat|"
                             r"aplay|arecord|ffmpeg|love", l)
                and "grep" not in l][:30]}
