#!/usr/bin/env python3
"""r74-scout ARM B: pw-cat ops-2 pre-measurement.

Cells:
  RAW  : --raw on a .wav-named fifo (name axis death), with same-bytes
         non-raw controls and .bin/.snd name controls.
  TARGET: `--target 0` (documented "don't link") kill class vs the
         writerless-fifo open-block kill class; /proc wchan introspection.
Every leg bounded; fifo legs use a one-shot writer thread.
"""
import json
import os
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIFOS = ROOT / "fifos"
LOGS = ROOT / "logs"
MEMBER = Path("/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/"
              "round-66/pair_dec_act.wav")   # libsndfile-openable wav
SNDBYTES = Path("/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/"
                "round-69/extsuffix_nomatch.snd")
ENV = dict(os.environ)
ENV["XDG_RUNTIME_DIR"] = "/run/user/1000"
ENV.pop("PIPEWIRE_RUNTIME_DIR", None)
SINK = "52"      # object.serial of alsa_output...hdmi-stereo (pw-dump)
results = []


def feed(fifo, data, linger=0.0):
    try:
        with open(fifo, "wb") as fh:
            fh.write(data)
            if linger:
                time.sleep(linger)
    except OSError as exc:
        print("writer:", exc, file=sys.stderr)


def fifo_leg(label, fname, data, extra, timeout=15):
    fifo = FIFOS / fname
    if fifo.exists():
        fifo.unlink()
    os.mkfifo(fifo)
    t = threading.Thread(target=feed, args=(fifo, data), daemon=True)
    t.start()
    argv = ["timeout", "-s", "KILL", str(timeout), "pw-cat", "-p"] + extra \
        + [str(fifo)]
    t0 = time.monotonic()
    p = subprocess.run(argv, capture_output=True, env=ENV)
    wall = time.monotonic() - t0
    t.join(timeout=2)
    rec = {"cell": label, "input": str(fifo.name), "bytes": len(data),
           "argv": " ".join(argv), "rc": p.returncode,
           "wall_s": round(wall, 3),
           "stderr": p.stderr.decode(errors="replace").strip()[:200],
           "stdout": p.stdout.decode(errors="replace").strip()[:200]}
    try:
        fifo.unlink()
    except OSError:
        pass
    results.append(rec)
    print("%-8s %-14s rc=%-4s %6.3fs  %s" % (label, fname, rec["rc"], wall,
                                             rec["stderr"][:70]), flush=True)
    return rec


def timeout_leg(label, argv, timeout, kill_after=None):
    full = ["timeout"]
    if kill_after is not None:
        full += ["-k", str(kill_after)]
    full += ["-s", "TERM", str(timeout)] + argv
    t0 = time.monotonic()
    p = subprocess.run(full, capture_output=True, env=ENV)
    wall = time.monotonic() - t0
    rec = {"cell": label, "argv": " ".join(full), "rc": p.returncode,
           "wall_s": round(wall, 3),
           "stderr": p.stderr.decode(errors="replace").strip()[:200]}
    results.append(rec)
    print("%-8s rc=%-4s %6.3fs  %s" % (label, rec["rc"], wall,
                                       rec["stderr"][:70]), flush=True)
    return rec


def introspect(label, argv, hold=1.2):
    """Start a hanging pw-cat, sample /proc, then SIGTERM it; record the
    exact death class. Returns the record."""
    p = subprocess.Popen(argv, env=ENV, start_new_session=True,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(hold)
    pid = p.pid
    wchan = state = None
    try:
        wchan = Path("/proc/%d/wchan" % pid).read_text().strip()
        state = None
        for line in Path("/proc/%d/status" % pid).read_text().splitlines():
            if line.startswith("State:"):
                state = line.split(None, 1)[1]
    except OSError:
        pass
    t_term = time.monotonic()
    p.terminate()                      # SIGTERM only
    try:
        p.wait(timeout=2.0)
        died = True
        rc = p.returncode
        term_wall = round(time.monotonic() - t_term, 3)
    except subprocess.TimeoutExpired:
        died = False
        rc = None
        term_wall = None
        os.killpg(p.pid, signal.SIGKILL)
        p.wait()
    rec = {"cell": label, "argv": " ".join(argv), "wchan": wchan,
           "state": state, "term_terminable": died, "rc_after_term": rc,
           "term_wall_s": term_wall,
           "stderr": p.stderr.read().decode(errors="replace").strip()[:200]}
    results.append(rec)
    print("%-8s wchan=%-22s state=%-4s TERM->%s %s"
          % (label, wchan, state, ("rc=%s in %ss" % (rc, term_wall))
             if died else "IGNORED (needed KILL)", rec["stderr"][:50]),
          flush=True)
    return rec


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else "all"
    data = SNDBYTES.read_bytes()
    if only in ("all", "raw"):
        print("== RAW group (member bytes = extsuffix_nomatch.snd, %d B)"
              % len(data))
        fifo_leg("R1", "r74raw1.wav", data, [])               # no-raw .wav
        fifo_leg("R2", "r74raw2.wav", data, ["--raw"])        # raw .wav
        fifo_leg("R3", "r74raw3.bin", data, ["--raw"])        # raw .bin
        fifo_leg("R4", "r74raw4.snd", data, [])               # no-raw .snd
        fifo_leg("R5", "r74raw5.snd", data, ["--raw"])        # raw .snd
        file_wav = FIFOS / "r74raw6.wav"
        file_wav.write_bytes(data)
        p = subprocess.run(["timeout", "-s", "KILL", "15", "pw-cat", "-p",
                            "--raw", str(file_wav)], capture_output=True,
                           env=ENV)
        rec = {"cell": "R6", "input": file_wav.name,
               "argv": "pw-cat -p --raw", "rc": p.returncode, "wall_s": None,
               "stderr": p.stderr.decode(errors="replace").strip()[:200]}
        results.append(rec)
        print("%-8s file .wav --raw    rc=%-4s  %s"
              % ("R6", rec["rc"], rec["stderr"][:60]))
        p = subprocess.run(["timeout", "-s", "KILL", "15", "pw-cat", "-p",
                            str(file_wav)], capture_output=True, env=ENV)
        rec = {"cell": "R7", "input": file_wav.name, "argv": "pw-cat -p",
               "rc": p.returncode, "wall_s": None,
               "stderr": p.stderr.decode(errors="replace").strip()[:200]}
        results.append(rec)
        print("%-8s file .wav no-raw   rc=%-4s  %s"
              % ("R7", rec["rc"], rec["stderr"][:60]))

    if only in ("all", "target"):
        print("== TARGET group (input = %s)" % MEMBER)
        timeout_leg("T1", ["pw-cat", "-p", "--target", "0", str(MEMBER)], 4)
        timeout_leg("T2", ["pw-cat", "-p", "--target", "0", str(MEMBER)], 4,
                    kill_after=1)
        timeout_leg("T2b", ["pw-cat", "-p", "--target", "0", str(MEMBER)], 4)
        timeout_leg("T4", ["pw-cat", "-p", str(MEMBER)], 6)          # linked
        timeout_leg("T5", ["pw-cat", "-p", "--target", SINK, str(MEMBER)], 6)
        introspect("T3", ["pw-cat", "-p", "--target", "0", str(MEMBER)])
        # writerless fifo open-block, kill-class contrast
        wf = FIFOS / "r74raw_writerless.fifo"
        if wf.exists():
            wf.unlink()
        os.mkfifo(wf)
        timeout_leg("T6a", ["pw-cat", "-p", str(wf)], 4, kill_after=2)
        introspect("T6b", ["pw-cat", "-p", str(wf)])
        try:
            wf.unlink()
        except OSError:
            pass
    out = ROOT / "runs" / ("pwcat-ops2%s.json" % ("" if only == "all"
                                                  else "-" + only))
    out.write_text(json.dumps(results, indent=1) + "\n")


if __name__ == "__main__":
    main()
