#!/usr/bin/env python3
"""r72-boundary: libsndfile 1.2.2 transport arm — boundary scratch mirror of
the declared `--probe-sndfile-transport-r72` move (receipt family
`sndfile_*_r72_probe`, keyed per member x transport).

Mirrors the r71 ffprobe arm shape (corpus/fixtures/measure_audio.py:570-730)
and the frontier ctypes harness (corpus/live/frontier-sndfile/probe_sndfile.py):

  file           sf_open(path)                        named,   seekable
  stdin_pipe     sf_open_fd(fresh pipe fd)            unnamed, unseekable
  redirected_fd  sf_open_fd(fresh O_RDONLY file fd)   unnamed, seekable
  fifo_path      sf_open(fifo) + writer thread        named,   unseekable

Per arm: detection verdict (SF_INFO.format + SFC_GET_FORMAT_* names,
sf_format_check, sf_strerror) + decode verdict (sf_readf_short count).
Plus a CLI detection leg (`sndfile-info <path>`, file arm only — sndfile-info
takes paths only and exits 0 even on reject; the verdict is stdout text).

Receipt: runs/<stamp>-sndfile-transport-r72/measurements.json
  mode = probe-sndfile-transport-r72
  keys = sndfile_<member>_r72_probe  (member x transport inside transport_axis)

This is a boundary-seat scratch implementation: the tracked fixture is the
author's scope; this file is NOT imported by corpus/fixtures/measure_audio.py.
"""
import ctypes
import json
import os
import re
import signal
import subprocess
import sys
import tempfile
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent          # corpus/live/r72-boundary
CORPUS = HERE.parent.parent                     # corpus
LIB = ctypes.CDLL("libsndfile.so.1")

SFM_READ = 0x10
SFC_GET_FORMAT_MAJOR_COUNT = 0x1030
SFC_GET_FORMAT_MAJOR = 0x1031
SFC_GET_FORMAT_SUBTYPE_COUNT = 0x1032
SFC_GET_FORMAT_SUBTYPE = 0x1033

ARM_TIMEOUT_S = 15
FIFO_HOLD_S = 1.0
READ_FRAMES_REQUEST = 65536

# TRANSPORT_R71_MEMBERS verbatim (measure_audio.py:556-566)
MEMBERS = {
    "posttable_nomatch": ("round-68", "posttable_nomatch.wav"),
    "txw_piperefuse": ("round-68", "txw_piperefuse.wav"),
    "dec_act": ("round-66", "pair_dec_act.wav"),
    "dec_hcom": ("round-66", "pair_dec_hcom.wav"),
    "extsuffix_wav": ("round-69", "extsuffix_nomatch.wav"),
    "extsuffix_bin": ("round-69", "extsuffix_nomatch.bin"),
    "extsuffix_txw": ("round-69", "extsuffix_nomatch.txw"),
    "extsuffix_f32": ("round-69", "extsuffix_nomatch.f32"),
    "extsuffix_snd": ("round-69", "extsuffix_nomatch.snd"),
}
ARMS = (("file", True, True), ("stdin_pipe", False, False),
        ("redirected_fd", False, True), ("fifo_path", True, False))


class SF_INFO(ctypes.Structure):
    _fields_ = [("frames", ctypes.c_int64),
                ("samplerate", ctypes.c_int),
                ("channels", ctypes.c_int),
                ("format", ctypes.c_int),
                ("sections", ctypes.c_int),
                ("seekable", ctypes.c_int)]


class SF_FORMAT_INFO(ctypes.Structure):
    _fields_ = [("format", ctypes.c_int),
                ("name", ctypes.c_char_p),
                ("extension", ctypes.c_char_p)]


LIB.sf_version_string.restype = ctypes.c_char_p
LIB.sf_open.restype = ctypes.c_void_p
LIB.sf_open.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(SF_INFO)]
LIB.sf_open_fd.restype = ctypes.c_void_p
LIB.sf_open_fd.argtypes = [ctypes.c_int, ctypes.c_int,
                           ctypes.POINTER(SF_INFO), ctypes.c_int]
LIB.sf_close.argtypes = [ctypes.c_void_p]
LIB.sf_strerror.restype = ctypes.c_char_p
LIB.sf_strerror.argtypes = [ctypes.c_void_p]
LIB.sf_error_str.restype = ctypes.c_char_p
LIB.sf_error_str.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t]
LIB.sf_format_check.argtypes = [ctypes.POINTER(SF_INFO)]
LIB.sf_command.restype = ctypes.c_int
LIB.sf_command.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_int]
LIB.sf_readf_short.restype = ctypes.c_int64
LIB.sf_readf_short.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_short),
                               ctypes.c_int64]


class ArmTimeout(Exception):
    pass


def _alarm(signum, frame):
    raise ArmTimeout()


signal.signal(signal.SIGALRM, _alarm)


def fmt_names():
    """major|subtype -> (name, ext) via SFC_GET_FORMAT_MAJOR/SUBTYPE."""
    def enum(count_cmd, item_cmd):
        n = ctypes.c_int(0)
        LIB.sf_command(None, count_cmd, ctypes.byref(n), ctypes.sizeof(n))
        out = {}
        for i in range(n.value):
            fi = SF_FORMAT_INFO()
            fi.format = i
            LIB.sf_command(None, item_cmd, ctypes.byref(fi), ctypes.sizeof(fi))
            out[fi.format] = (fi.name.decode(), (fi.extension or b"").decode())
        return out
    return {"majors": enum(SFC_GET_FORMAT_MAJOR_COUNT, SFC_GET_FORMAT_MAJOR),
            "subs": enum(SFC_GET_FORMAT_SUBTYPE_COUNT, SFC_GET_FORMAT_SUBTYPE)}


NAMES = fmt_names()


def _raw_err_str(snd):
    buf = ctypes.create_string_buffer(256)
    LIB.sf_error_str(snd, buf, 256)
    raw = buf.value.decode(errors="replace")
    return None if raw in ("", "No Error.") else raw


def verdict(snd, info):
    """Detection + decode verdict for one open SF_INFO. `snd` NULL -> the
    open failure text from sf_strerror(NULL) (deterministic, path-free)."""
    if not snd:
        return {"format_hex": None, "format_name": None, "format_check": None,
                "frames": None, "samplerate": None, "channels": None,
                "sf_seekable": None, "read_frames": None,
                "error": LIB.sf_strerror(None).decode(errors="replace"),
                "error_str": None}
    mj = NAMES["majors"].get(info.format & 0x0FFF0000, (None, None))
    st = NAMES["subs"].get(info.format & 0x0000FFFF, (None, None))
    name = f"{mj[0]}/{st[0]}" if mj[0] else None
    check = bool(LIB.sf_format_check(ctypes.byref(info)))
    buf = (ctypes.c_short * READ_FRAMES_REQUEST)()
    got = LIB.sf_readf_short(snd, buf, READ_FRAMES_REQUEST)
    err = _raw_err_str(snd)
    LIB.sf_close(snd)
    return {"format_hex": hex(info.format), "format_name": name,
            "format_check": check, "frames": info.frames,
            "samplerate": info.samplerate, "channels": info.channels,
            "sf_seekable": bool(info.seekable), "read_frames": got,
            "error": None, "error_str": err}


def arm_file(path):
    info = SF_INFO()
    snd = LIB.sf_open(os.fsencode(str(path)), SFM_READ, ctypes.byref(info))
    return verdict(snd, info)


def arm_fd(fd):
    info = SF_INFO()
    snd = LIB.sf_open_fd(fd, SFM_READ, ctypes.byref(info), 0)
    return verdict(snd, info)


def arm_stdin_pipe(data):
    r, w = os.pipe()
    try:
        os.write(w, data)
        os.close(w)
        return arm_fd(r)
    finally:
        os.close(r)


def arm_redirected_fd(path):
    fd = os.open(str(path), os.O_RDONLY)
    try:
        return arm_fd(fd)
    finally:
        os.close(fd)


def arm_fifo(path, data, hold):
    with tempfile.TemporaryDirectory(prefix="sndfile-r72-") as tmp:
        fifo = os.path.join(tmp, os.path.basename(str(path)))
        os.mkfifo(fifo)

        def feed():
            try:
                with open(fifo, "wb") as w:
                    w.write(data)
            except OSError:
                pass
            time.sleep(hold)

        t = threading.Thread(target=feed, daemon=True)
        t.start()
        try:
            return arm_file(fifo)
        finally:
            t.join(timeout=hold + 5)


def bounded(fn, *a, **kw):
    """Arm timeout guard (SIGALRM); a blocked arm records the r67/r71
    'blocked' convention instead of hanging the run."""
    try:
        signal.setitimer(signal.ITIMER_REAL, ARM_TIMEOUT_S)
        return fn(*a, **kw)
    except ArmTimeout:
        return {"format_hex": None, "format_name": None, "format_check": None,
                "frames": None, "samplerate": None, "channels": None,
                "sf_seekable": None, "read_frames": None,
                "error": f"blocked: no verdict within {ARM_TIMEOUT_S} s",
                "error_str": None}
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


def sndfile_info_leg(arg, log_path):
    """CLI detection leg. sndfile-info exits 0 even on reject (frontier
    gotcha) — the verdict is stdout text. The argument is normalized to
    <input> in the parsed fields (absolute host paths stay out of receipts)."""
    proc = subprocess.run(["sndfile-info", arg], capture_output=True,
                          timeout=ARM_TIMEOUT_S)
    out = proc.stdout.decode(errors="replace")
    log_path.write_bytes(proc.stdout)
    def find(rx):
        m = re.search(rx, out, re.M)
        return m.group(1).strip() if m else None
    reason = None
    lines = [ln.strip() for ln in out.strip().splitlines() if ln.strip()]
    if lines and "Error" in out:
        reason = lines[-1]
    return {"exit": proc.returncode,
            "error_line": (find(r"^Error\s*:\s*(.*)$") or "").replace(arg, "<input>") or None,
            "format_hex": find(r"^Format\s*:\s*(0x[0-9A-Fa-f]+)"),
            "frames": (int(find(r"^Frames\s*:\s*(\d+)$")) if find(r"^Frames\s*:\s*(\d+)$") else None),
            "samplerate": (int(find(r"^Sample Rate\s*:\s*(\d+)$")) if find(r"^Sample Rate\s*:\s*(\d+)$") else None),
            "channels": (int(find(r"^Channels\s*:\s*(\d+)$")) if find(r"^Channels\s*:\s*(\d+)$") else None),
            "reason": reason}


def member_entry(member, path, hold, cli):
    data = path.read_bytes()
    rel = str(path.relative_to(CORPUS))
    arms = {"file": bounded(arm_file, path),
            "stdin_pipe": bounded(arm_stdin_pipe, data),
            "redirected_fd": bounded(arm_redirected_fd, path),
            "fifo_path": bounded(arm_fifo, path, data, hold)}
    for transport, named, seekable in ARMS:
        arms[transport]["named"] = named
        arms[transport]["seekable"] = seekable
    groups, dgroups = [], []
    for transport in ("file", "stdin_pipe", "redirected_fd", "fifo_path"):
        a = arms[transport]
        sig = (a["format_name"], a["read_frames"], a["error"])
        dsig = (a["format_name"], a["error"])
        for g in groups:
            if g[0] == sig:
                g[1].append(transport)
                break
        else:
            groups.append((sig, [transport]))
        for g in dgroups:
            if g[0] == dsig:
                g[1].append(transport)
                break
        else:
            dgroups.append((dsig, [transport]))
    entry = {"path": rel, "pair_member": member,
             "decoder": f"libsndfile ({LIB.sf_version_string().decode()})",
             "transport_axis": arms,
             "transport_protocol": {"arm_timeout_s": ARM_TIMEOUT_S,
                                    "fifo_writer_hold_s": hold,
                                    "fifo_feed": "one-shot write then writer lingers"},
             "sndfile_info_cli": cli,
             "transport_verdict_groups": [
                 {"transports": ts, "sndfile_format": sig[0],
                  "read_frames": sig[1], "error": sig[2]}
                 for sig, ts in groups],
             "sndfile_detect_groups": [
                 {"transports": ts, "sndfile_format": sig[0], "error": sig[1]}
                 for sig, ts in dgroups],
             "transport_fork": len(groups) > 1,
             "failures": []}
    if entry["transport_fork"]:
        desc = " vs ".join("/".join(ts) + "=" + (sig[2] or str(sig[0]))
                           for sig, ts in groups)
        entry["failures"].append(
            f"transport: libsndfile verdict forks across transports ({desc})")
    return entry


def main():
    hold = float(os.environ.get("MEASURE_FIFO_WRITER_HOLD_S", FIFO_HOLD_S))
    logdir = HERE / "logs"
    logdir.mkdir(exist_ok=True)
    measurements = {}
    for member, (directory, filename) in MEMBERS.items():
        path = CORPUS / "live" / directory / filename
        rel = str(path.relative_to(CORPUS))
        cli = sndfile_info_leg(str(path), logdir / f"info-{member}.txt")
        measurements[f"sndfile_{member}_r72_probe"] = member_entry(
            member, path, hold, cli)
        print(f"{member}: " + "; ".join(
            f"{t}={a['format_name'] or 'REJ'}:{a['read_frames']}:{(a['error'] or '')[:38]}"
            for t, a in measurements[f"sndfile_{member}_r72_probe"]["transport_axis"].items()
            if t in ("file", "stdin_pipe", "redirected_fd", "fifo_path")),
            file=sys.stderr)
    receipt = {"mode": "probe-sndfile-transport-r72",
               "decoder": {"library": "libsndfile.so.1",
                           "version": LIB.sf_version_string().decode()},
               "transport_protocol": {
                   "arm_timeout_s": ARM_TIMEOUT_S,
                   "fifo_writer_hold_s": hold,
                   "fifo_feed": "one-shot write then writer lingers"},
               "measurements": measurements}
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    out = HERE / "runs" / (stamp + "-sndfile-transport-r72")
    out.mkdir(parents=True)
    (out / "measurements.json").write_text(
        json.dumps(receipt, indent=2, allow_nan=False) + "\n")
    failed = {k: v["failures"] for k, v in measurements.items() if v["failures"]}
    print(json.dumps({"receipt": str(out / "measurements.json"),
                      "failures": failed}))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
