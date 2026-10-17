#!/usr/bin/env python3
"""R77 scout — FRONTIER 4: cross-decoder partial-header disagreement matrix.

{pw-record, parec, arecord, ffmpeg} x {TERM, KILL} x
readers {stdlib wave, ffprobe, soxi, sndfile-info}.

r76 pinned wave vs ffprobe only; soxi and sndfile-info are the new axis.
For each wound we record the honest frame count (payload/ (ch*bps)) and each
reader's frame answer, then classify agreement.
"""
import os
import signal
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r77_probe import (LINE, M_SPDIF, emit, inspect, mk, readers,  # noqa
                       out_kind)

TMP = mk()


def run_wound(label, argv, out, wait=1.0, sig=signal.SIGTERM):
    proc = subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                            stderr=subprocess.PIPE)
    time.sleep(wait)
    early = proc.poll()
    proc.send_signal(sig)
    try:
        proc.wait(timeout=6)
    except subprocess.TimeoutExpired:
        proc.send_signal(signal.SIGKILL)
        proc.wait(timeout=6)
    err = proc.stderr.read().decode(errors="replace")
    proc.stderr.close()
    insp = inspect(out)
    rd = readers(out) if insp.get("exists") and insp.get("bytes") else {}
    honest = None
    fmt = insp.get("fmt") or {}
    if insp.get("data_actual") is not None and fmt.get("channels"):
        honest = insp["data_actual"] // (fmt["channels"] *
                                         max(fmt.get("bits", 16) // 8, 1))
    return {"leg": label,
            "argv": [a if a != out else "<out>" for a in argv],
            "early_exit_rc": early, "rc": proc.returncode,
            "sig": sig.name, "err_tail": err.strip().splitlines()[-1][:160]
            if err.strip() else "",
            "out_kind": out_kind(insp), "bytes": insp.get("bytes"),
            "riff_size_field": insp.get("riff_size_field"),
            "data_declared_field": insp.get("data_declared_field"),
            "data_actual": insp.get("data_actual"),
            "fmt": fmt, "honest_frames": honest, "readers": rd}


def verdict(row):
    r = row.get("readers") or {}
    if not r:
        return "no_file"
    h = row.get("honest_frames") or 0
    wf = r.get("wave_frames")
    sf = r.get("sndfile_frames")
    sf = int(sf) if sf and sf.isdigit() else None
    soxi = r.get("soxi_samples")
    soxi = int(soxi) if soxi and soxi.isdigit() else None
    ff = (r.get("ffprobe") or {}).get("nb_frames")
    ff = int(ff) if ff and str(ff).isdigit() else None
    def cls(n):
        if n is None:
            return "err"
        if n == h:
            return "honest"
        if n > h * 4:
            return "inflated"
        return "short"
    return {"wave": cls(wf), "sndfile": cls(sf), "soxi": cls(soxi),
            "ffprobe": cls(ff),
            "values": {"honest": h, "wave": wf, "sndfile": sf, "soxi": soxi,
                       "ffprobe": ff},
            "wave_err": r.get("wave"), "soxi_rc": r.get("soxi_rc"),
            "sndfile_rc": r.get("sndfile_rc"),
            "ffprobe_rc": r.get("ffprobe_rc")}


def main():
    out = {"probe": "sever-readers-r77", "tmp": TMP, "wounds": {}}
    cases = [
        ("pwrecord", lambda p: ["pw-record", "--target", LINE, p]),
        ("pwcat", lambda p: ["pw-cat", "-r", "--target", LINE, p]),
        ("parec_filefmt", lambda p: ["parec", "-d", LINE,
                                     "--file-format=wav", p]),
        ("parecord", lambda p: ["parecord", "-d", LINE, p]),
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
            p = os.path.join(TMP, f"{name}_{signame}.wav")
            if os.path.exists(p):
                os.unlink(p)
            row = run_wound(f"{name}_{signame}", mkargv(p), p, sig=sig)
            row["verdict"] = verdict(row)
            out["wounds"][f"{name}_{signame}"] = row
    emit(out, "probe-sever-readers-r77.json")
    print(out["probe"])


if __name__ == "__main__":
    main()
