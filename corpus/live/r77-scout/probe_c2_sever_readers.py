#!/usr/bin/env python3
"""R77 scout — FRONTIER 4 v2: reader disagreement matrix with UNIT-CORRECT
witnesses.

Unit calibration (measured on a synthetic 96000-frame 2ch/48k wav):
  soxi -s  == 96000  -> soxi -s reports FRAMES, not interleaved samples.
  sndfile-info `Frames` == 96000
  stdlib wave.getnframes() == 96000
  ffprobe stream.nb_read_frames == 24 -> a PACKET count, not frames (unusable)
  ffprobe stream/format duration == 2.000000 -> size-derived, honest

So the comparable witnesses are: wave | sndfile | soxi -s | soxi -D |
ffprobe duration. All five are read on the same bytes.
"""
import json
import os
import re
import signal
import subprocess
import sys
import time
import wave

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r77_probe import (LINE, M_SPDIF, emit, inspect, mk, norm_err,  # noqa
                       out_kind, sh)


def witness(path):
    w = {}
    try:
        with wave.open(path, "rb") as fh:
            w["wave_frames"] = fh.getnframes()
            w["wave_rate"] = fh.getframerate()
            w["wave_ch"] = fh.getnchannels()
    except Exception as exc:                                   # noqa: BLE001
        w["wave_frames"] = None
        w["wave_err"] = f"{type(exc).__name__}: {exc}"[:80]
    _rc, so, se, _wl, _t = sh(["sndfile-info", path], timeout=20)
    txt = so.decode(errors="replace")
    m = re.search(r"^Frames\s*:\s*(\d+)", txt, re.M)
    w["sndfile_frames"] = int(m.group(1)) if m else None
    if not m:
        w["sndfile_err"] = (se.strip().splitlines() or [""])[-1][:80]
    _rc, so, se, _wl, _t = sh(["soxi", "-s", path], timeout=20)
    v = so.decode(errors="replace").strip()
    w["soxi_s"] = int(v) if v.isdigit() else None
    if not v.isdigit():
        w["soxi_err"] = (se.strip().splitlines() or [""])[-1][:80]
    _rc, so, _se, _wl, _t = sh(["soxi", "-D", path], timeout=20)
    v = so.decode(errors="replace").strip()
    w["soxi_D"] = v or None
    _rc, so, _se, _wl, _t = sh(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=duration:format=duration", "-of", "json", path], timeout=25)
    try:
        j = json.loads(so)
        w["ffprobe_stream_dur"] = (j.get("streams") or [{}])[0].get("duration")
        w["ffprobe_fmt_dur"] = (j.get("format") or {}).get("duration")
    except Exception:                                          # noqa: BLE001
        w["ffprobe_stream_dur"] = None
        w["ffprobe_fmt_dur"] = None
    return w


def run_wound(label, argv, out, wait, sig):
    proc = subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                            stderr=subprocess.PIPE)
    time.sleep(wait)
    early = proc.poll()
    proc.send_signal(sig)
    try:
        proc.wait(timeout=8)
    except subprocess.TimeoutExpired:
        proc.send_signal(signal.SIGKILL)
        proc.wait(timeout=8)
    err = proc.stderr.read().decode(errors="replace")
    proc.stderr.close()
    insp = inspect(out)
    w = witness(out) if insp.get("exists") and insp.get("bytes") else {}
    fmt = insp.get("fmt") or {}
    honest = None
    if insp.get("data_actual") is not None and fmt.get("channels"):
        honest = insp["data_actual"] // (fmt["channels"] *
                                        max(fmt.get("bits", 16) // 8, 1))
    return {"leg": label,
            "argv": [a if a != out else "<out>" for a in argv],
            "early_exit_rc": early, "rc": proc.returncode, "sig": sig.name,
            "err_class": None, "err_tail": norm_err(err),
            "out_kind": out_kind(insp), "bytes": insp.get("bytes"),
            "riff_size_field": insp.get("riff_size_field"),
            "data_declared_field": insp.get("data_declared_field"),
            "fmt": fmt, "honest_frames": honest, "witness": w}


def classify(row):
    """Map each reader's answer to honest|inflated|short|zero|reject|absent."""
    w = row.get("witness") or {}
    h = row.get("honest_frames")
    if not w:
        return "no_file"
    def cls(n):
        if n is None:
            return "reject/absent"
        if h is None:
            return "?"
        if n == h:
            return "honest"
        if n == 0:
            return "zero"
        if n > h * 4:
            return "inflated"
        return "short"
    dur = {"soxi_D": w.get("soxi_D"), "ffprobe_stream": w.get(
        "ffprobe_stream_dur"), "ffprobe_fmt": w.get("ffprobe_fmt_dur")}
    honest_dur = round(h / 48000, 3) if h else None
    return {"wave": "reject" if w.get("wave_frames") is None
            else cls(w["wave_frames"]),
            "sndfile": cls(w.get("sndfile_frames")),
            "soxi_s": cls(w.get("soxi_s")),
            "durations": dur, "honest_frames": h,
            "honest_duration_s": honest_dur,
            "values": w}


def main():
    out = {"probe": "sever-readers2-r77", "tmp": mk(), "wounds": {}}
    T = out["tmp"]
    cases = [
        ("pwrecord", lambda p: ["pw-record", "--target", LINE, p]),
        ("pwcat", lambda p: ["pw-cat", "-r", "--target", LINE, p]),
        ("parec_filefmt", lambda p: ["parec", "-d", LINE,
                                     "--file-format=wav", p]),
        ("parecord", lambda p: ["parecord", "-d", LINE, p]),
        ("parec_default_source", lambda p: ["parec", "-d",
                                            "@DEFAULT_SOURCE@",
                                            "--file-format=wav", p]),
        ("arecord_hw", lambda p: ["arecord", "-D", "hw:0,0", "-f", "cd", p]),
        ("arecord_null", lambda p: ["arecord", "-D", "null", "-f", "cd", p]),
        ("ffmpeg_pulse", lambda p: ["ffmpeg", "-nostdin", "-nostats", "-v",
                                    "error", "-f", "pulse", "-i", LINE, "-y",
                                    p]),
        ("ffmpeg_monitor", lambda p: ["ffmpeg", "-nostdin", "-nostats", "-v",
                                      "error", "-f", "pulse", "-i", M_SPDIF,
                                      "-y", p]),
    ]
    for name, mkargv in cases:
        for signame, sig in (("TERM", signal.SIGTERM),
                             ("KILL", signal.SIGKILL)):
            for wait in (1.0, 2.5):
                p = os.path.join(T, f"{name}_{signame}_{wait}.wav")
                if os.path.exists(p):
                    os.unlink(p)
                row = run_wound(f"{name}_{signame}_w{wait}", mkargv(p), p,
                                wait, sig)
                row["class"] = classify(row)
                out["wounds"][f"{name}_{signame}_w{wait}"] = row
    emit(out, "probe-sever-readers2-r77.json")
    print(out["probe"])


if __name__ == "__main__":
    main()
