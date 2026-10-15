#!/usr/bin/env python3
"""R78 scout pre-measurement harness — stream-props / link / midi frontier.

Own harness, own classifiers (never imports corpus/fixtures — the r77 author
is editing it concurrently). Every leg is triple-bounded: consumer duration
flag, outer subprocess timeout, reader byte cap. All artifacts stay under
corpus/live/r78-scout/. A probe-owned null sink (r78_ns) is the ONLY tone
target so a concurrent seat's Speaker/SPDIF traffic can never alias my
anchors.
"""
import json
import math
import os
import re
import signal
import struct
import subprocess
import sys
import tempfile
import time
import wave

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))  # repo root
SEAT = os.path.join(ROOT, "corpus", "live", "r78-scout")
SCRATCH = os.path.join(SEAT, "scratch")
RAW = os.path.join(SEAT, "raw")

CAP_BYTES = 262144          # 256 KiB hard per-leg cap
DEFAULT_TIMEOUT = 12.0

LINE = "alsa_input.usb-Generic_USB_Audio-00.HiFi__Line__source"
MIC = "alsa_input.usb-Generic_USB_Audio-00.HiFi__Mic__source"
M_SPDIF = "alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink.monitor"
M_SPK = "alsa_output.usb-Generic_USB_Audio-00.HiFi__Speaker__sink.monitor"
S_SPDIF = "alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink"
S_HDMI = "alsa_output.pci-0000_01_00.1.hdmi-stereo"
NS = "r78_ns"                       # probe-owned null sink
M_NS = "r78_ns.monitor"


def sh(argv, timeout=DEFAULT_TIMEOUT, env=None, cwd=None):
    """Bounded run -> (rc, stdout_bytes, stderr_text, wall_s, timed_out)."""
    e = dict(os.environ)
    if env:
        e.update(env)
    t0 = time.monotonic()
    try:
        p = subprocess.run(argv, capture_output=True, timeout=timeout,
                           env=e, cwd=cwd)
        return p.returncode, p.stdout, p.stderr.decode(errors="replace"), \
            round(time.monotonic() - t0, 3), False
    except subprocess.TimeoutExpired as exc:
        return None, (exc.stdout or b""), (exc.stderr or b"").decode(
            errors="replace"), round(time.monotonic() - t0, 3), True
    except OSError as exc:
        return None, b"", f"spawn failed: {exc}", round(
            time.monotonic() - t0, 3), False


def sh_capped(argv, cap=CAP_BYTES, timeout=DEFAULT_TIMEOUT, env=None,
              kill_after=None, term_after=None):
    """Run argv, read at most `cap` stdout bytes, then SIGTERM/SIGKILL."""
    e = dict(os.environ)
    if env:
        e.update(env)
    t0 = time.monotonic()
    p = subprocess.Popen(argv, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, env=e)
    buf = bytearray()
    cap_hit = False
    sig = None
    deadline = t0 + timeout
    term_at = t0 + term_after if term_after is not None else None
    kill_at = t0 + kill_after if kill_after is not None else None
    try:
        while True:
            now = time.monotonic()
            if now > deadline:
                break
            if term_at is not None and now >= term_at and sig is None:
                p.send_signal(signal.SIGTERM)
                sig = "TERM"
                term_at = None
            if kill_at is not None and now >= kill_at and sig != "KILL":
                p.send_signal(signal.SIGKILL)
                sig = "KILL"
                kill_at = None
            if len(buf) >= cap:
                cap_hit = True
                break
            chunk = p.stdout.read(min(65536, cap - len(buf)))
            if not chunk:
                break
            buf += chunk
    finally:
        if p.poll() is None:
            p.send_signal(signal.SIGTERM)
            sig = sig or "TERM"
            try:
                p.wait(timeout=3)
            except subprocess.TimeoutExpired:
                p.send_signal(signal.SIGKILL)
                p.wait(timeout=3)
                sig = "KILL"
        err = p.stderr.read() if p.stderr else b""
        p.stderr.close()
    rc = p.returncode
    return rc, len(buf), err.decode(errors="replace"), \
        round(time.monotonic() - t0, 3), cap_hit, sig, bytes(buf)


def inspect(path):
    """Structural walk of a written file. Never records raw content bytes."""
    insp = {"exists": os.path.exists(path)}
    if not insp["exists"]:
        return insp
    data = open(path, "rb").read()
    insp["bytes"] = len(data)
    insp["head8"] = data[:8].hex()
    insp["riff"] = data[:4] == b"RIFF" and data[8:12] == b"WAVE"
    insp["rfcnt"] = data[:4] in (b"FORM", b"RF64", b"FLLT") or data[:4]
    if not insp["riff"]:
        return insp
    riff_sz = struct.unpack("<I", data[4:8])[0]
    insp["riff_size_field"] = (
        "finalized" if riff_sz == len(data) - 8 else
        "placeholder_8" if riff_sz == 8 else
        "placeholder_ff" if riff_sz == 0xFFFFFFFF else
        "placeholder_80000000" if riff_sz == 0x80000000 else "other")
    off, chunks = 12, []
    while off + 8 <= len(data) and len(chunks) < 8:
        cid = data[off:off + 4].decode("latin1")
        csz = struct.unpack("<I", data[off + 4:off + 8])[0]
        chunks.append({"id": cid, "declared": csz, "offset": off})
        if cid == "data":
            break
        off += 8 + csz + (csz & 1)
    insp["chunks"] = chunks
    if chunks and chunks[0]["id"] == "fmt " and chunks[0]["declared"] >= 16:
        tag, ch, rate, _br, _ba, bits = struct.unpack("<HHIIHH", data[20:36])
        insp["fmt"] = {"tag": tag, "channels": ch, "rate": rate,
                       "bits": bits}
    for c in chunks:
        if c["id"] == "data":
            actual = len(data) - (c["offset"] + 8)
            insp["data_declared"] = c["declared"]
            insp["data_actual"] = actual
            insp["data_finalized"] = c["declared"] == actual
            insp["data_declared_field"] = (
                "finalized" if c["declared"] == actual else
                "zero" if c["declared"] == 0 else
                "placeholder_ff" if c["declared"] == 0xFFFFFFFF else
                "placeholder_80000000" if c["declared"] == 0x80000000
                else "other")
    return insp


def audio_stats(path, fmt_bits=16):
    """Content witness: peak |sample| + nonzero fraction over the data chunk
    of a wav (or whole file for raw). Independent of headers."""
    try:
        data = open(path, "rb").read()
    except OSError:
        return {}
    off = data.find(b"data")
    payload = data[off + 8:] if off >= 0 else data
    if fmt_bits == 16:
        n = len(payload) // 2
        if n == 0:
            return {"peak": 0, "nz_frac": 0.0, "frames": 0}
        vals = struct.unpack(f"<{n}h", payload[:n * 2])
        peak = max((abs(v) for v in vals), default=0)
        nz = sum(1 for v in vals if v != 0) / n
        return {"peak": peak, "nz_frac": round(nz, 4), "frames": n // 2}
    if fmt_bits == 24:
        b = payload
        peak = 0
        nz = 0
        n = len(b) // 3
        for i in range(0, n * 3, 3):
            v = int.from_bytes(b[i:i + 3] + (b"\xff" if b[i + 2] & 0x80
                                           else b"\x00"), "little",
                               signed=True)
            if abs(v) > peak:
                peak = abs(v)
            if v:
                nz += 1
        return {"peak": peak, "nz_frac": round(nz / max(n, 1), 4),
                "frames": n // 2}
    return {}


def payload_sha(path):
    """sha256 of data-chunk bytes only (header-free content identity)."""
    import hashlib
    data = open(path, "rb").read()
    off = data.find(b"data")
    payload = data[off + 8:] if off >= 0 else data
    return hashlib.sha256(payload).hexdigest()[:16]


def out_kind(insp):
    if not insp.get("exists"):
        return "missing"
    if insp.get("bytes") == 0:
        return "empty"
    if insp.get("riff"):
        if insp.get("data_actual") == 0:
            return "riff_wav_empty"
        return "riff_wav"
    if insp.get("bytes", 0) <= 64:
        return "partial_header"
    return "nonwav_bytes"


CLASSES = (
    ("no_target_node", r"no target node available"),
    ("pw_connect_failed", r"pw_context_connect\(\) failed"),
    ("pa_no_such_entity", r"No such entity"),
    ("pa_connect_failed", r"Connection failure|pa_context_connect\(\) failed"),
    ("pa_bad_file_format", r"Failed to open audio file"),
    ("alsa_channels", r"Channels count non available"),
    ("alsa_hwparams", r"Unable to install hw params"),
    ("alsa_unknown_pcm", r"Unknown PCM \S+"),
    ("alsa_busy", r"Device or resource busy"),
    ("ffmpeg_muxer", r"Unable to find a suitable output format|"
                     r"Error initializing the muxer|Error opening output files"),
    ("ffmpeg_alsa", r"cannot (?:set parameters|open audio device)"),
    ("ffmpeg_jack", r"Cannot connect to server|jack"),
    ("ffmpeg_esrch", r"No such process"),
    ("ffmpeg_io", r"Input/output error"),
    ("alsa_read_eintr", r"read error: Interrupted system call"),
    ("aborted_by_signal", r"Aborted by signal"),
)


def errclass(text):
    for name, pat in CLASSES:
        m = re.search(pat, text)
        if m:
            return name, m.group(0).strip()[:120]
    return None, None


def norm_err(text):
    t = re.sub(r"node \d+", "node <n>", text)
    t = re.sub(r"id=\d+ seq[:=]\d+", "id=<n> seq=<n>", t)
    t = re.sub(r"res:-?\d+", "res:<n>", t)
    t = re.sub(r"0x[0-9a-fA-F]+", "0x<n>", t)
    t = re.sub(r"/tmp/[A-Za-z0-9_.\-/]+", "<tmp>", t)
    lines = [ln for ln in t.splitlines() if ln.strip()]
    return lines[-1][:200] if lines else ""


# ---------- probe-owned fixtures ----------

def gen_tone(path, secs=2.0, rate=48000, amp=16384, f_l=1000, f_r=1500):
    """Distinct-frequency stereo tone: L=1 kHz, R=1.5 kHz — unmistakable."""
    n = int(secs * rate)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(rate)
        frames = bytearray()
        for i in range(n):
            l = int(amp * math.sin(2 * math.pi * f_l * i / rate))
            r = int(amp * math.sin(2 * math.pi * f_r * i / rate))
            frames += struct.pack("<hh", l, r)
        w.writeframes(bytes(frames))
    return path


def load_ns():
    """Load the probe-owned null sink; return module index or None."""
    rc, so, se, _w, _t = sh(
        ["pactl", "load-module", "module-null-sink",
         "sink_name=" + NS, "rate=48000", "channels=2",
         'sink_properties=device.description=r78scout'],
        timeout=8)
    idx = so.decode(errors="replace").strip()
    if rc != 0 or not idx.isdigit():
        return None, f"rc={rc} out={idx} err={se.strip()[:120]}"
    time.sleep(0.4)
    rc, so2, _se, _w, _t = sh(["pactl", "list", "sources", "short"],
                              timeout=8)
    ok = M_NS in so2.decode(errors="replace")
    return (int(idx), "monitor-present" if ok else "monitor-MISSING")


def unload_ns(idx):
    if idx is None:
        return
    sh(["pactl", "unload-module", str(idx)], timeout=8)


def play_tone(tone, target=NS, timeout=8):
    """Play the tone file into target sink. Bounded by file duration."""
    return sh(["pw-cat", "-p", "--target", target, tone], timeout=timeout)


def links_feeding(port_glob="pw-record:input"):
    """pw-link -l snapshot -> list of 'producer -> consumer' strings where
    consumer matches port_glob. The honest consumption witness."""
    rc, so, _se, _w, _t = sh(["pw-link", "-l"], timeout=8)
    txt = so.decode(errors="replace")
    out = []
    lines = txt.splitlines()
    for i, ln in enumerate(lines):
        if re.match(r"^\s*\|->\s*(.+)", ln):
            m = re.match(r"^\s*\|->\s*(.+)", ln)
            if port_glob in m.group(1):
                producer = lines[i - 1].strip() if i else "?"
                out.append(f"{producer} -> {m.group(1).strip()}")
        elif re.match(r"^\s*\|<-\s*(.+)", ln):
            m = re.match(r"^\s*\|<-\s*(.+)", ln)
            if port_glob in lines[max(i - 1, 0)] or port_glob in ln:
                out.append(f"{ln.strip()} feeds {lines[i-1].strip()}")
    # simpler: walk pairs
    return sorted(set(out)), txt


def pwlink_map(txt, port_glob):
    """Parse `pw-link -l` text: producer_port -> [consumer_ports] and back."""
    producers = {}
    cur = None
    for ln in txt.splitlines():
        s = ln.strip()
        if not s.startswith("|"):
            cur = s
        elif s.startswith("|->"):
            dst = s[3:].strip()
            if port_glob in dst:
                producers.setdefault(cur, []).append(dst)
        elif s.startswith("|<-"):
            src = s[3:].strip()
            if cur and port_glob in cur:
                producers.setdefault(src, []).append(cur)
    return producers


def capture_while(argv, path, settle=0.9, during=None, timeout=15):
    """Spawn argv writing `path`; at `settle` seconds run during() callable;
    then wait for exit (or timeout TERM). Returns (leg-dict, during-result).
    """
    if os.path.exists(path):
        os.unlink(path)
    p = subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                         stderr=subprocess.PIPE)
    t0 = time.monotonic()
    time.sleep(settle)
    dres = during() if during else None
    deadline = t0 + timeout
    rc = None
    while time.monotonic() < deadline:
        rc = p.poll()
        if rc is not None:
            break
        time.sleep(0.05)
    if rc is None:
        p.send_signal(signal.SIGTERM)
        try:
            rc = p.wait(timeout=4)
        except subprocess.TimeoutExpired:
            p.send_signal(signal.SIGKILL)
            rc = p.wait(timeout=4)
    se = p.stderr.read().decode(errors="replace")
    p.stderr.close()
    insp = inspect(path)
    st = audio_stats(path)
    leg = {"argv": argv, "rc": rc, "wall_s": round(time.monotonic() - t0, 3),
           "err_class": errclass(se)[0], "err_line": norm_err(se),
           "out_kind": out_kind(insp), "bytes": insp.get("bytes"),
           "data_actual": insp.get("data_actual"),
           "riff_size_field": insp.get("riff_size_field"),
           "data_declared_field": insp.get("data_declared_field"),
           "fmt": insp.get("fmt"), "peak": st.get("peak"),
           "nz_frac": st.get("nz_frac"),
           "sha16": payload_sha(path) if insp.get("bytes") else None}
    return leg, dres


def mk():
    for d in (SEAT, SCRATCH, RAW):
        os.makedirs(d, exist_ok=True)
    return tempfile.mkdtemp(prefix="r78-scout-", dir=SCRATCH)


def emit(obj, fname):
    p = os.path.join(SEAT, fname)
    open(p, "w").write(json.dumps(obj, indent=1, sort_keys=True))
    print(f"WROTE {p}", file=sys.stderr)
    return p


def du():
    tot = 0
    for r, _d, fs in os.walk(SCRATCH):
        for f in fs:
            try:
                tot += os.path.getsize(os.path.join(r, f))
            except OSError:
                pass
    return tot
