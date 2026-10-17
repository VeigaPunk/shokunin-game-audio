#!/usr/bin/env python3
"""r74 BOUNDARY scratch — fifo writer that keeps the fifo OPEN after the dump.

Usage: linger_writer.py <member> <fifo> <linger_s>
Blocks in open() until a reader attaches, writes the full member, then holds
the fd open for linger_s (no EOF for the reader).  Bounded by the caller's
`timeout -s KILL`.
"""
import sys
import time

member, fifo, linger = sys.argv[1], sys.argv[2], float(sys.argv[3])
data = open(member, "rb").read()
f = open(fifo, "wb", buffering=0)
while data:
    n = f.write(data)
    data = data[n:]
f.flush()
time.sleep(linger)
f.close()
