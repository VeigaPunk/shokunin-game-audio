#!/usr/bin/env python3
"""r100b CPU hog — own-load arm only (seat: audio r100-boundary).

Started by `r100b_run.py`, which records pid + /proc starttime + comm and kills
exactly those pids after verifying both. Nothing else on the host is signalled.
"""
import time

x = 12345
while True:
    x = (x * 1103515245 + 12345) & 0x7FFFFFFF
    if x == 1:
        time.sleep(0)
