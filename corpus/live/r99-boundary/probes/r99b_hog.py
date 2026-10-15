#!/usr/bin/env python3
"""r99-boundary CPU hog. argv-marked (r99b_hog) for own-PID-only reaping.

usage: r99b_hog.py SECONDS [TAG]
Self-terminates after SECONDS; prints "<pid> <tag> ready" then spins.
"""
import os, sys, time


def main():
    secs = float(sys.argv[1]) if len(sys.argv) > 1 else 3600.0
    tag = sys.argv[2] if len(sys.argv) > 2 else "hog"
    t_end = time.monotonic() + secs
    print("%d %s ready" % (os.getpid(), tag), flush=True)
    x = 0x12345678
    n = 0
    while time.monotonic() < t_end:
        for _ in range(20000):
            x = (x * 1103515245 + 12345) & 0xFFFFFFFF
            x ^= x >> 7
        n += 1
    print("%d %s done %d" % (os.getpid(), tag, n), flush=True)


if __name__ == "__main__":
    main()
