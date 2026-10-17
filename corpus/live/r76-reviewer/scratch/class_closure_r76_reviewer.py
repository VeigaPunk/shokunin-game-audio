#!/usr/bin/env python3
"""r76 REVIEWER: class-derivation closure.

Sever four consumers, KEEP the wound files, then feed the SAME bytes to the
committed fixture's own classifiers (imported from a scratch copy of the
committed tree — never from corpus/fixtures, so the tracked .pyc is not
rewritten). Prints raw numbers beside the fixture's labels so any
disagreement between label and evidence is visible.
"""
import importlib.util
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

FIX = Path(__file__).resolve().parent / "tree" / "corpus" / "fixtures" / \
    "measure_audio.py"
OUT = Path(__file__).resolve().parent / "sev_wounds"
OUT.mkdir(exist_ok=True)


def load_fixture():
    spec = importlib.util.spec_from_file_location("ma_r76_reviewer", FIX)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["ma_r76_reviewer"] = mod
    spec.loader.exec_module(mod)
    return mod


def sh(cmd, timeout=10):
    p = subprocess.run(cmd, capture_output=True, timeout=timeout)
    return p.stdout.decode(errors="replace"), p.returncode


def inventory():
    out, _ = sh(["pactl", "list", "sources", "short"])
    srcs, mons = [], []
    for ln in out.splitlines():
        parts = ln.split()
        if len(parts) >= 2:
            (mons if parts[1].endswith(".monitor") else srcs).append(parts[1])
    info, _ = sh(["pactl", "info"])
    src = sink = None
    for ln in info.splitlines():
        if ln.startswith("Default Source:"):
            src = ln.split(":", 1)[1].strip()
        if ln.startswith("Default Sink:"):
            sink = ln.split(":", 1)[1].strip()
    if src not in srcs:
        src = srcs[0] if srcs else None
    al, _ = sh(["arecord", "-l"])
    import re
    m = re.search(r"card (\d+): (\S+) \[[^\]]*\], device (\d+):", al)
    hw = f"hw:{m.group(1)},{m.group(3)}" if m else None
    return src, sink, hw


def raw(path):
    d = path.read_bytes()
    r = {"file_bytes": len(d)}
    if d[:4] == b"RIFF" and d[8:12] == b"WAVE":
        r["riff_size_field"] = struct.unpack("<I", d[4:8])[0]
        off = 12
        while off + 8 <= len(d):
            cid = d[off:off + 4].decode("latin1")
            csz = struct.unpack("<I", d[off + 4:off + 8])[0]
            if cid == "data":
                r["data_declared"] = csz
                r["data_actual"] = len(d) - (off + 8)
                break
            off += 8 + csz + (csz & 1)
    return r


def sever(argv, dest, sig, wait):
    proc = subprocess.Popen(argv + [str(dest)], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, start_new_session=True)
    try:
        proc.wait(timeout=wait)
    except subprocess.TimeoutExpired:
        if proc.poll() is None:
            proc.send_signal(sig)
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()
    return proc.returncode


def main():
    ma = load_fixture()
    src, sink, hw = inventory()
    print(f"# fixture copy: {FIX}  sha-of-source-check separate")
    print(f"# inventory src={src} sink={sink} hw={hw}")
    rows = []
    plan = [("pwrecord", ["pw-record", "--target", src, "--rate", "48000",
                          "--channels", "2", "--format", "s16"], 1.5),
            ("parecord", ["parecord", "-d", "@DEFAULT_SOURCE@"], 2.5),
            ("ffmpeg", ["ffmpeg", "-nostdin", "-nostats", "-v", "error",
                        "-f", "pulse", "-i", src, "-y"], 2.5),
            ("arecord", ["arecord", "-D", hw, "-f", "S16_LE", "-r", "48000",
                         "-c", "2", "-t", "wav"], 1.5)]
    for sig, tag in ((signal.SIGTERM, "term"), (signal.SIGKILL, "kill")):
        for name, argv, wait in plan:
            dest = OUT / f"{name}_{tag}.wav"
            if dest.exists():
                dest.unlink()
            rc = sever(argv, dest, sig, wait)
            r = raw(dest) if dest.exists() else {}
            insp = ma._capture_wav_inspect(dest)
            row = {"cell": f"{name}_{tag}", "rc": rc, "raw": r,
                   "fixture_inspect": insp,
                   "fixture_out_kind": ma._capture_out_kind(insp)}
            if insp.get("exists") and insp.get("bytes"):
                row["fixture_parsers"] = ma._capture_parser_verdict(dest, insp)
            rows.append(row)
    # honest frame count from the fixture's own fmt leaf vs wave's report
    for row in rows:
        p = row.get("fixture_parsers") or {}
        insp = row["fixture_inspect"]
        fmt = insp.get("fmt") or {}
        fb = fmt.get("channels", 0) * (fmt.get("bits", 0) // 8)
        if p.get("wave_opens") and fb:
            with wave.open(str(OUT / (row["cell"] + ".wav")), "rb") as w:
                n = w.getnframes()
            honest = insp.get("data_actual", 0) // fb
            row["cross_check"] = {
                "wave_nframes": n, "honest_from_fixture_fmt": honest,
                "ratio": (n / honest) if honest else None,
                "fixture_wave_frames_class": p.get("wave_frames_class")}
    print(json.dumps(rows, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
