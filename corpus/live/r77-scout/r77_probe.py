#!/usr/bin/env python3
"""R77 scout pre-measurement harness — capture/playback frontier on THIS host.

Own harness, own classifiers (never imports corpus/fixtures). Every leg is
bounded three ways: inner consumer bound, outer subprocess timeout, and a
byte cap enforced by the reader (stdout consumers) or by the consumer's own
duration flag (file consumers). Rotation dirs stay under the seat's scratch.
"""
import json
import os
import re
import shutil
import signal
import struct
import subprocess
import sys
import tempfile
import time
import wave

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))  # repo root
SEAT = os.path.join(ROOT, "corpus", "live", "r77-scout")
SCRATCH = os.path.join(SEAT, "scratch")
RAW = os.path.join(SEAT, "raw")

CAP_BYTES = 262144          # 256 KiB hard per-leg cap
DEFAULT_TIMEOUT = 12.0

LINE = "alsa_input.usb-Generic_USB_Audio-00.HiFi__Line__source"
MIC = "alsa_input.usb-Generic_USB_Audio-00.HiFi__Mic__source"
M_SPDIF = "alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink.monitor"
M_SPK = "alsa_output.usb-Generic_USB_Audio-00.HiFi__Speaker__sink.monitor"
S_SPDIF = "alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink"


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
    """Run argv, read at most `cap` stdout bytes, then SIGTERM/SIGKILL.

    Returns (rc, nbytes, stderr_text, wall_s, cap_hit, signal_sent).
    """
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
    insp["riff"] = data[:4] == b"RIFF" and data[8:12] == b"WAVE"
    if not insp["riff"]:
        insp["head4"] = data[:4].decode("latin1")
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


def out_kind(insp):
    if not insp.get("exists"):
        return "missing"
    if insp.get("bytes") == 0:
        return "empty"
    if insp.get("data_actual") == 0 and insp.get("riff"):
        return "riff_wav_empty"          # 44-byte header, no audio
    if insp.get("riff"):
        return "riff_wav"
    return "raw_stream"


def readers(path):
    """Four independent readers on one artifact: stdlib wave, ffprobe, soxi,
    sndfile-info. Each returns a normalized verdict string."""
    v = {}
    try:
        with wave.open(path, "rb") as w:
            v["wave_frames"] = w.getnframes()
            v["wave_rate"] = w.getframerate()
            v["wave_ch"] = w.getnchannels()
            v["wave"] = "opens"
    except Exception as exc:                                  # noqa: BLE001
        v["wave"] = f"rejects:{type(exc).__name__}"
        v["wave_msg"] = str(exc)[:120]
    rc, so, se, _w, _t = sh(["ffprobe", "-v", "error", "-show_entries",
                             "stream=nb_frames,duration,sample_rate,channels",
                             "-of", "json", path], timeout=20)
    v["ffprobe_rc"] = rc
    try:
        j = json.loads(so)
        st = (j.get("streams") or [{}])[0]
        v["ffprobe"] = {"nb_frames": st.get("nb_frames"),
                        "duration": st.get("duration"),
                        "rate": st.get("sample_rate")}
    except Exception:                                          # noqa: BLE001
        v["ffprobe"] = None
    v["ffprobe_err"] = se.strip().splitlines()[-1][:120] if se.strip() else ""
    rc, so, se, _w, _t = sh(["soxi", "-s", path], timeout=20)
    v["soxi_rc"] = rc
    v["soxi_samples"] = so.decode(errors="replace").strip()[:40]
    v["soxi_err"] = se.strip().splitlines()[-1][:120] if se.strip() else ""
    rc, so, se, _w, _t = sh(["sndfile-info", path], timeout=20)
    v["sndfile_rc"] = rc
    txt = so.decode(errors="replace")
    m = re.search(r"Frames\s*:\s*(\d+)", txt)
    v["sndfile_frames"] = m.group(1) if m else None
    m = re.search(r"Sample Rate\s*:\s*(\d+)", txt)
    v["sndfile_rate"] = m.group(1) if m else None
    v["sndfile_err"] = se.strip().splitlines()[-1][:120] if se.strip() else ""
    return v


def norm_err(text):
    """Named class + normalized line (counters scrubbed)."""
    t = re.sub(r"node \d+", "node <n>", text)
    t = re.sub(r"id=\d+ seq[:=]\d+", "id=<n> seq=<n>", t)
    t = re.sub(r"res:-?\d+", "res:<n>", t)
    t = re.sub(r"/tmp/[A-Za-z0-9_.\-]+", "<tmp>", t)
    lines = [ln for ln in t.splitlines() if ln.strip()]
    return lines[-1][:200] if lines else ""


CLASSES = (
    ("no_target_node", r"no target node available"),
    ("pw_connect_failed", r"pw_context_connect\(\) failed"),
    ("pa_no_such_entity", r"No such entity"),
    ("pa_connect_failed", r"Connection failure|pa_context_connect\(\) failed"),
    ("alsa_channels", r"Channels count non available"),
    ("alsa_hwparams", r"Unable to install hw params"),
    ("alsa_unknown_pcm", r"Unknown PCM \S+"),
    ("alsa_busy", r"Device or resource busy"),
    ("ffmpeg_muxer", r"Unable to find a suitable output format|"
                     r"Error initializing the muxer|Error opening output files"),
    ("ffmpeg_alsa", r"cannot (?:set parameters|open audio device)"),
    ("ffmpeg_esrch", r"No such process"),
    ("ffmpeg_io", r"Input/output error"),
    ("aborted_by_signal", r"Aborted by signal"),
)


def errclass(text):
    for name, pat in CLASSES:
        m = re.search(pat, text)
        if m:
            return name, m.group(0).strip()[:120]
    return None, None


def leg_file(name, argv, path, timeout=DEFAULT_TIMEOUT, env=None):
    if os.path.exists(path):
        os.unlink(path)
    rc, so, se, wall, timed = sh(argv, timeout=timeout, env=env)
    insp = inspect(path)
    return {"leg": name, "argv": [a if not a.startswith("/tmp/r77")
                                 else "<out>" for a in argv],
            "rc": rc, "timed_out": timed, "wall_s": wall,
            "err_class": errclass(se)[0], "err_line": norm_err(se),
            "out_kind": out_kind(insp), "bytes": insp.get("bytes"),
            "data_actual": insp.get("data_actual"),
            "riff_size_field": insp.get("riff_size_field"),
            "data_declared_field": insp.get("data_declared_field"),
            "fmt": insp.get("fmt")}


def leg_stdout(name, argv, path, cap=CAP_BYTES, timeout=DEFAULT_TIMEOUT,
               env=None, term_after=None, kill_after=None, container=None):
    rc, n, se, wall, cap_hit, sig, raw = sh_capped(
        argv, cap=cap, timeout=timeout, env=env, term_after=term_after,
        kill_after=kill_after)
    if container:
        open(path, "wb").write(container + raw)
    else:
        open(path, "wb").write(raw)
    insp = inspect(path)
    return {"leg": name, "argv": argv, "rc": rc, "signal": sig,
            "cap_hit": cap_hit, "nbytes_read": n, "wall_s": wall,
            "err_class": errclass(se)[0], "err_line": norm_err(se),
            "out_kind": out_kind(insp), "bytes": insp.get("bytes"),
            "data_actual": insp.get("data_actual"),
            "riff_size_field": insp.get("riff_size_field"),
            "data_declared_field": insp.get("data_declared_field"),
            "fmt": insp.get("fmt")}


def wav_header(path):
    """Minimal 44-byte canonical wav header for a to-be-appended payload."""
    d = open(path, "rb").read()
    return struct.pack("<4sI4s4sIHHIIHH4sI", b"RIFF", 36 + len(d), b"WAVE",
                       b"fmt ", 16, 1, 2, 48000, 48000 * 4, 4, 16,
                       b"data", len(d))


def mk():
    for d in (SEAT, SCRATCH, RAW):
        os.makedirs(d, exist_ok=True)
    return tempfile.mkdtemp(prefix="r77-scout-", dir=SCRATCH)


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
