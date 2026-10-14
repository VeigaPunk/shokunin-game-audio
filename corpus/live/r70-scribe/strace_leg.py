#!/usr/bin/env python3
"""r70-scribe strace legs — which syscall does the fifo arm block IN?

usage: strace_leg.py <feed> <hold_s> <outbase>
Runs one `strace -f -tt -e trace=openat,read,close,execve,wait4,exit_group
sox -V6 <fifo> -n stat` leg under the given writer protocol (same feeds as
run_hold_ladder.py: oneshot | chunked | waitclose), kills the whole process
group at 10 s, keeps the raw strace at <outbase>.trace and the sox stderr at
<outbase>.stderr.
"""
import os
import signal
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

MEMBER = Path("/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/round-66/pair_dec_act.wav")
TIMEOUT = 10.0
CHUNK_BYTES = 64
CHUNK_GAP_S = 0.005


def main():
    feed, hold, outbase = sys.argv[1], float(sys.argv[2]), sys.argv[3]
    data = MEMBER.read_bytes()
    tmp = tempfile.mkdtemp(prefix="straceleg-r70-")
    fifo = Path(tmp) / MEMBER.name
    os.mkfifo(fifo)
    release = threading.Event()

    def feed_oneshot():
        try:
            with fifo.open("wb") as fh:
                fh.write(data); fh.flush(); time.sleep(hold)
        except OSError:
            pass

    def feed_chunked():
        try:
            with fifo.open("wb") as fh:
                for i in range(0, len(data), CHUNK_BYTES):
                    fh.write(data[i:i + CHUNK_BYTES]); fh.flush()
                    time.sleep(CHUNK_GAP_S)
                time.sleep(hold)
        except OSError:
            pass

    def feed_waitclose():
        try:
            with fifo.open("wb") as fh:
                fh.write(data); fh.flush()
                release.wait(timeout=TIMEOUT + 30)
        except OSError:
            pass

    w = threading.Thread(target={"oneshot": feed_oneshot,
                                 "chunked": feed_chunked,
                                 "waitclose": feed_waitclose}[feed],
                         daemon=True)
    w.start()
    proc = subprocess.Popen(
        ["strace", "-f", "-tt", "-o", outbase + ".trace",
         "-e", "trace=openat,read,close,execve,wait4,exit_group",
         "sox", "-V6", str(fifo), "-n", "stat"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        start_new_session=True)
    t0 = time.monotonic()
    try:
        _, err = proc.communicate(timeout=TIMEOUT)
        status = f"exit {proc.returncode}"
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        _, err = proc.communicate()
        status = "blocked (killpg at 10 s)"
    finally:
        release.set()
        w.join(timeout=hold + 40)
    Path(outbase + ".stderr").write_bytes(err)
    print(f"feed={feed} hold={hold} -> {status} wall={time.monotonic()-t0:.3f}s")


if __name__ == "__main__":
    main()
