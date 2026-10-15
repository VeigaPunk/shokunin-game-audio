#!/usr/bin/env python3
"""r93b CPU hog — bounded, self-named, wall-capped, killed by exact PID only.

Usage: r93b_hog.py <seconds> [spin]
Prints one line at start and one at end (with pid) so the parent can prove the
child lived for the whole leg window. Never self-daemonises; no forks.
"""
import ctypes
import os
import sys
import time


def main():
    dur = float(sys.argv[1]) if len(sys.argv) > 1 else 600.0
    try:
        libc = ctypes.CDLL("libc.so.6", use_errno=True)
        libc.prctl(15, b"r93b_hog", 0, 0, 0)  # PR_SET_NAME
    except Exception:
        pass
    t0 = time.time()
    print("r93b_hog pid=%d start=%.3f dur=%.1f" % (os.getpid(), t0, dur), flush=True)
    x = 12345
    while time.time() - t0 < dur:
        for _ in range(500000):
            x = (x * 1103515245 + 12345) & 0x7FFFFFFF
    print("r93b_hog pid=%d end=%.3f x=%d" % (os.getpid(), time.time(), x), flush=True)


if __name__ == "__main__":
    main()
