#!/usr/bin/env python3
"""r70 boundary — fifo writer-hold edge harness.

One leg = `sox -V6 <fifo> -n stat` on a named fifo under a parameterized
writer. Reproduces the canonical `transport_matrix` fifo arm protocol
(measure_audio.py TRANSPORT_R67_*: blocking O_WRONLY writer, one-shot write,
then `time.sleep(fifo_writer_hold_s)` before close) and mutates the attach
shape / feed shape / hold / arm timeout around it.

Writer shapes (the fifo endpoint lifecycle):
  oneshot   — O_WRONLY (blocks until reader), one write of all bytes, close.
              hold is meaningless; this is the degenerate hold=0 cell.
  linger    — canonical: O_WRONLY, write, flush, sleep(hold), close.
  rdwr      — O_RDWR fd opened in the main thread BEFORE sox spawn (never
              blocks; counts as a permanently attached writer). Bytes are
              written through it; the fd stays open for the whole leg.
              hold is meaningless — a writer endpoint exists at every t.
  parked    — rdwr-shape parking fd + a separate oneshot feed writer.
  rescue    — oneshot feed closes at ~t0; a second O_WRONLY writer attaches
              at t = `rescue_delay` and parks for `rescue_park` s with no
              data. Tests whether ANY attached writer unblocks open#2.

Feed shapes (inside the writer, only where noted):
  whole     — one write (canonical `fh.write(data)`).
  byte      — 1-byte writes with `byte_gap` s between them.
  dribble   — 64 B chunks with `chunk_gap` s between them.
  burst     — `burst_bytes`, stall `stall_s`, then the rest, then hold.

Leg verdict = canonical fields: detected format, route, exit, samples,
normalized error (last `sox FAIL` tail after `':`), plus wall_s and
timed_out. Timeout kills the whole process GROUP (sox + ffmpeg child) —
the canonical subprocess.run(timeout=) would orphan a blocked ffmpeg.
"""
import json
import os
import re
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
SCRATCH = ROOT / "corpus" / "live" / "r70-boundary"
FIFODIR = SCRATCH / "runs" / "fifos"
SOX = ["sox", "-V6", "-n", "stat"]  # input path inserted at index 2
DET = re.compile(r"detected file format type `(\S+?)'")
SMP = re.compile(r"Samples read:\s*(\d+)")
CANON_HOLD = 1.0
CANON_TIMEOUT = 10.0


def norm_error(text):
    fails = [l for l in text.strip().splitlines() if "sox FAIL" in l]
    if not fails:
        return None
    m = re.search(r"':\s*(.*)$", fails[-1])
    return m.group(1) if m else fails[-1]


def verdict_class(err, exit_code, timed_out):
    if timed_out:
        return "blocked"
    if err is None:
        return "decode"
    if "Sun/NeXT" in err:
        return "au-magic"
    return "other"


def feed_write(wfd, data, feed="whole", byte_gap=0.002, chunk=64,
               chunk_gap=0.03, burst_bytes=300, stall_s=1.2, first_n=None):
    if feed == "byte":
        for i in range(len(data)):
            os.write(wfd, data[i:i + 1])
            time.sleep(byte_gap)
    elif feed == "dribble":
        for i in range(0, len(data), chunk):
            os.write(wfd, data[i:i + chunk])
            time.sleep(chunk_gap)
    elif feed == "burst":
        os.write(wfd, data[:burst_bytes])
        time.sleep(stall_s)
        os.write(wfd, data[burst_bytes:])
    elif feed == "firstn":
        os.write(wfd, data[:first_n])
    else:
        os.write(wfd, data)


def run_leg(member_rel, shape="linger", hold=CANON_HOLD, timeout=8.0,
            feed="whole", rescue_delay=None, rescue_park=8.0,
            nice_leg=False, strace_path=None, log_path=None,
            feed_kw=None, **feed_extra):
    """Run one fifo leg; return the verdict dict."""
    path = ROOT / member_rel
    data = path.read_bytes()
    FIFODIR.mkdir(parents=True, exist_ok=True)
    fifo = FIFODIR / (path.name + "." + str(os.getpid()) + ".fifo")
    if fifo.exists():
        fifo.unlink()
    os.mkfifo(fifo)
    feed_kw = {**(feed_kw or {}), **feed_extra}
    rdwr_fd = None
    threads = []
    wtrace = []

    def w_oneshot_then_hold(h):
        try:
            fd = os.open(str(fifo), os.O_WRONLY)  # blocks until reader
            wtrace.append(("open", round(time.monotonic() - t0, 4)))
            feed_write(fd, data, feed, **feed_kw)
            wtrace.append(("wrote", round(time.monotonic() - t0, 4)))
            if h:
                time.sleep(h)
            os.close(fd)
            wtrace.append(("closed", round(time.monotonic() - t0, 4)))
        except OSError as exc:
            wtrace.append(("oserror", round(time.monotonic() - t0, 4),
                           str(exc)))

    def w_rescue():
        try:
            time.sleep(rescue_delay)
            fd = os.open(str(fifo), os.O_WRONLY)
            wtrace.append(("r2open", round(time.monotonic() - t0, 4)))
            time.sleep(rescue_park)
            os.close(fd)
            wtrace.append(("r2closed", round(time.monotonic() - t0, 4)))
        except OSError as exc:
            wtrace.append(("r2oserror", round(time.monotonic() - t0, 4),
                           str(exc)))

    t0 = time.monotonic()
    if shape in ("rdwr", "parked"):
        rdwr_fd = os.open(str(fifo), os.O_RDWR)  # never blocks
        if shape == "rdwr":
            os.write(rdwr_fd, data)
        else:
            th = threading.Thread(target=w_oneshot_then_hold, args=(0.0,),
                                  daemon=True)
            threads.append(th)
            th.start()
    else:
        th = threading.Thread(target=w_oneshot_then_hold,
                              args=(0.0 if shape == "oneshot" else hold,),
                              daemon=True)
        threads.append(th)
        th.start()
    if shape == "rescue":
        threads.append(threading.Thread(target=w_rescue, daemon=True))
        threads[-1].start()

    cmd = (["nice", "-n", "19"] if nice_leg else []) + \
        ["sox", "-V6", str(fifo), "-n", "stat"]
    if strace_path:
        cmd = ["strace", "-f", "-tt", "-e",
               "trace=%file,exit_group,wait4,write", "-o",
               str(strace_path)] + cmd
    timed_out = False
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                start_new_session=True)
        try:
            _, err_b = proc.communicate(timeout=timeout)
            code = proc.returncode
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(proc.pid, signal.SIGKILL)  # sox + ffmpeg child
            _, err_b = proc.communicate()
            code = None
    finally:
        wall = time.monotonic() - t0
        if rdwr_fd is not None:
            os.close(rdwr_fd)
        for th in threads:
            th.join(timeout=max(0.1, min(timeout, 2.0)))
        try:
            fifo.unlink()
        except FileNotFoundError:
            pass
    text = (err_b or b"").decode(errors="replace")
    if log_path:
        Path(log_path).parent.mkdir(parents=True, exist_ok=True)
        Path(log_path).write_text(text)
    det = DET.search(text)
    smp = SMP.search(text)
    err = norm_error(text)
    if timed_out:
        err = f"blocked: no verdict within {timeout} s"
    leg = {"detected": det.group(1) if det else None,
           "route": ("ffmpeg" if (det and det.group(1) == "act")
                     or "(ffmpeg)" in text else "native" if det else "none"),
           "exit": code, "samples": int(smp.group(1)) if smp else None,
           "error": err, "wall_s": round(wall, 3), "timed_out": timed_out,
           "shape": shape, "hold": hold, "timeout": timeout, "feed": feed,
           "rescue_delay": rescue_delay, "nice": nice_leg,
           "member": member_rel, "wtrace": wtrace}
    # (wtrace already present; kept for clarity)
    leg["class"] = verdict_class(err, code, timed_out)
    if text.strip():
        tail = text.strip().splitlines()[-1]
        leg["stderr_tail"] = re.sub(r"`[^']*'", "`<input>'",
                                    re.sub(r" @ 0x[0-9a-f]+\]", "]",
                                           tail))[-160:]
    return leg


def main():
    """CLI: one leg, JSON on stdout."""
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--member", default="corpus/live/round-66/pair_dec_act.wav")
    ap.add_argument("--shape", default="linger",
                    choices=["oneshot", "linger", "rdwr", "parked", "rescue"])
    ap.add_argument("--hold", type=float, default=CANON_HOLD)
    ap.add_argument("--timeout", type=float, default=8.0)
    ap.add_argument("--feed", default="whole",
                    choices=["whole", "byte", "dribble", "burst"])
    ap.add_argument("--rescue-delay", type=float, default=None)
    ap.add_argument("--rescue-park", type=float, default=8.0)
    ap.add_argument("--nice", action="store_true")
    ap.add_argument("--byte-gap", type=float, default=0.002)
    ap.add_argument("--chunk-gap", type=float, default=0.03)
    ap.add_argument("--burst-bytes", type=int, default=300)
    ap.add_argument("--stall-s", type=float, default=1.2)
    ap.add_argument("--strace", default=None)
    ap.add_argument("--log", default=None)
    a = ap.parse_args()
    leg = run_leg(a.member, shape=a.shape, hold=a.hold, timeout=a.timeout,
                  feed=a.feed, rescue_delay=a.rescue_delay,
                  rescue_park=a.rescue_park, nice_leg=a.nice,
                  strace_path=a.strace, log_path=a.log,
                  feed_kw={"byte_gap": a.byte_gap, "chunk_gap": a.chunk_gap,
                           "burst_bytes": a.burst_bytes, "stall_s": a.stall_s})
    print(json.dumps(leg))


if __name__ == "__main__":
    main()
