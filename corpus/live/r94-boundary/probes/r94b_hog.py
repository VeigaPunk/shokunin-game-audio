#!/usr/bin/env python3
"""r94b_hog — own-PID CPU load generator for the r94-boundary seat.

argv carries the marker `r94b_hog` (the kill path re-verifies it before
signalling).  Pure userspace integer loop; opens no file, no socket, no device.
Terminates on SIGTERM/SIGINT (default disposition).
"""
import signal
import sys
import time

signal.signal(signal.SIGTERM, signal.SIG_DFL)
signal.signal(signal.SIGINT, signal.SIG_DFL)

x = 12345
t_end = time.monotonic() + 3600.0
while time.monotonic() < t_end:
    for _ in range(200000):
        x = (x * 1103515245 + 12345) & 0x7FFFFFFF
    if x < 0:  # unreachable; keeps x live
        sys.stdout.write("x")
