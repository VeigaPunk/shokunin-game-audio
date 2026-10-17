#!/usr/bin/env python3
"""r76 REVIEWER independent sever probe — no fixture import.

Re-derives, from raw bytes, the four capture consumers' TERM/KILL classes
the r76 author pinned:
  pw-record / parecord / ffmpeg / arecord
and prints RAW evidence (file size, RIFF size field, data declared vs
actual, stdlib wave getnframes vs honest frame count) so the class
derivation can be checked against numbers rather than labels.
"""
import json
import os
from pathlib import Path
import signal
import struct
import subprocess
import sys
import tempfile
import time
import wave

SRC = None            # filled from pactl
SINK = None
HW = None
WAIT = 1.5
KILL_WAIT = 5.0


def sh(cmd, timeout=10):
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=timeout)
        return p.stdout.decode(errors="replace"), p.returncode
    except Exception as exc:                                    # noqa: BLE001
        return f"<{type(exc).__name__}>", None


def inventory():
    global SRC, SINK, HW
    out, _ = sh(["pactl", "list", "sources", "short"])
    srcs, mons = [], []
    for ln in out.splitlines():
        parts = ln.split()
        if len(parts) >= 2:
            (mons if parts[1].endswith(".monitor") else srcs).append(parts[1])
    info, _ = sh(["pactl", "info"])
    for ln in info.splitlines():
        if ln.startswith("Default Source:"):
            SRC = ln.split(":", 1)[1].strip()
        if ln.startswith("Default Sink:"):
            SINK = ln.split(":", 1)[1].strip()
    al, _ = sh(["arecord", "-l"])
    import re
    m = re.search(r"card (\d+): (\S+) \[[^\]]*\], device (\d+):", al)
    HW = f"hw:{m.group(1)},{m.group(3)}" if m else None
    if SRC not in srcs:
        SRC = srcs[0] if srcs else None
    return {"sources": srcs, "monitors": mons, "SRC": SRC, "SINK": SINK,
            "HW": HW}


def raw_inspect(path):
    """Raw byte-level facts — no classification."""
    if not path.exists():
        return {"exists": False}
    d = path.read_bytes()
    r = {"exists": True, "file_bytes": len(d)}
    r["riff_magic"] = d[:4] == b"RIFF" and d[8:12] == b"WAVE"
    if r["riff_magic"]:
        r["riff_size_field"] = struct.unpack("<I", d[4:8])[0]
        r["riff_size_finalized"] = r["riff_size_field"] == len(d) - 8
        off = 12
        chunks = []
        while off + 8 <= len(d) and len(chunks) < 6:
            cid = d[off:off + 4].decode("latin1")
            csz = struct.unpack("<I", d[off + 4:off + 8])[0]
            chunks.append((cid, csz, off))
            if cid == "data":
                break
            off += 8 + csz + (csz & 1)
        r["chunks"] = [[c, s, o] for c, s, o in chunks]
        for cid, csz, o in chunks:
            if cid == "data":
                actual = len(d) - (o + 8)
                r["data_declared"] = csz
                r["data_actual"] = actual
                r["data_declared_finalized"] = csz == actual
        if chunks and chunks[0][0] == "fmt ":
            tag, ch, rate, _br, _ba, bits = struct.unpack("<HHIIHH",
                                                          d[20:36])
            r["fmt"] = {"tag": tag, "channels": ch, "rate": rate,
                        "bits": bits}
    return r


def parser_verdict(path, raw):
    v = {}
    try:
        with wave.open(str(path), "rb") as w:
            v["wave_opens"] = True
            v["wave_nframes"] = w.getnframes()
            v["wave_framerate"] = w.getframerate()
            v["wave_nchannels"] = w.getnchannels()
    except Exception as exc:                                     # noqa: BLE001
        v["wave_opens"] = False
        v["wave_error"] = f"{type(exc).__name__}: {exc}"
    fmt = raw.get("fmt") or {}
    fb = fmt.get("channels", 0) * (fmt.get("bits", 0) // 8)
    if fb and raw.get("data_actual") is not None:
        v["honest_frames"] = raw["data_actual"] // fb
        v["declared_frames"] = raw.get("data_declared", 0) // fb
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration", "-of", "json", str(path)],
                       capture_output=True, timeout=10)
    v["ffprobe_rc"] = p.returncode
    v["ffprobe_out"] = p.stdout.decode(errors="replace").strip()[:200]
    return v


def sever(argv, fname, sig, wait=WAIT):
    with tempfile.TemporaryDirectory(prefix="r76rev-sev-") as tmp:
        out = Path(tmp) / fname
        proc = subprocess.Popen(argv + [str(out)], stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                start_new_session=True)
        early = None
        try:
            proc.wait(timeout=wait)
            early = proc.returncode
        except subprocess.TimeoutExpired:
            pass
        if early is None:
            if proc.poll() is None:
                proc.send_signal(sig)
            try:
                proc.wait(timeout=KILL_WAIT)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
        err = proc.stderr.read().decode(errors="replace")
        raw = raw_inspect(out)
        cell = {"argv": " ".join(argv) + " <out>",
                "sig": "TERM" if sig == signal.SIGTERM else "KILL",
                "early_exit_code": early, "exit_code": proc.returncode,
                "stderr_last": (err.strip().splitlines() or [""])[-1][:160]}
        cell["raw"] = raw
        if raw.get("exists") and raw.get("file_bytes"):
            cell["parsers"] = parser_verdict(out, raw)
        return cell


def main():
    inv = inventory()
    print(json.dumps({"inventory": inv}, indent=1))
    src = SRC or "alsa_input.nonexistent"
    consumers = [
        ("pwrecord", ["pw-record", "--target", src, "--rate", "48000",
                      "--channels", "2", "--format", "s16"], "s.wav"),
        ("parecord", ["parecord", "-d", "@DEFAULT_SOURCE@"], "s.wav"),
    ]
    if SRC:
        consumers.append(("ffmpeg", ["ffmpeg", "-nostdin", "-nostats", "-v",
                                     "error", "-f", "pulse", "-i", src, "-y"],
                          "s.wav"))
    if HW:
        consumers.append(("arecord", ["arecord", "-D", HW, "-f", "S16_LE",
                                      "-r", "48000", "-c", "2", "-t", "wav"],
                          "s.wav"))
    # pulse consumers first, arecord last (device-release ordering)
    order = [c for c in consumers if c[0] != "arecord"] + \
            [c for c in consumers if c[0] == "arecord"]
    cells = {}
    for sig in (signal.SIGTERM, signal.SIGKILL):
        for name, argv, fn in order:
            key = f"{name}_{'term' if sig == signal.SIGTERM else 'kill'}"
            cells[key] = sever(argv, fn, sig,
                               wait=2.5 if name in ("parecord", "ffmpeg")
                               else WAIT)
    print(json.dumps({"cells": cells}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
