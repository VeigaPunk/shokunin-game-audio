#!/usr/bin/env python3
"""Watcher: sample every `pw-profiler` child of a live r89 fixture run.

Finds the fixture process (cmdline `measure_audio.py --probe-pwprof-r89`,
cwd = the given tree), then every 20 ms records the state + signal masks of
each of its pw-profiler children, tagged with the child's start offset. Used
to observe the `g_hup` leg in a full run: the 4th `-J -n 0` child is g_hup
(legs 1-3 are g_term / g_int / g_kill).

usage: watch_hup.py <tree> <seconds> <out.json>
"""
import json
import os
import sys
import time
from pathlib import Path

TREE = Path(sys.argv[1]).resolve()
SECONDS = float(sys.argv[2])
OUT = Path(sys.argv[3])
MASKS = ("SigBlk", "SigIgn", "SigCgt")


def find_fixture():
    for d in Path("/proc").iterdir():
        if not d.name.isdigit():
            continue
        try:
            cmd = (d / "cmdline").read_bytes().replace(b"\0", b" ").decode()
            cwd = os.readlink(d / "cwd")
        except OSError:
            continue
        if "measure_audio.py --probe-pwprof-r89" in cmd and \
                Path(cwd) == TREE:
            return int(d.name)
    return None


def children(ppid):
    out = []
    for d in Path("/proc").iterdir():
        if not d.name.isdigit():
            continue
        try:
            cmd = (d / "cmdline").read_bytes().replace(b"\0", b" ").decode()
            stat = (d / "stat").read_text()
            st = (d / "status").read_text(errors="replace")
        except OSError:
            continue
        if "pw-profiler" not in cmd:
            continue
        if int(stat.rsplit(")", 1)[1].split()[1]) != ppid:
            continue
        rec = {"pid": int(d.name), "cmd": cmd.strip(),
               "state": None}
        for ln in st.splitlines():
            for m in MASKS:
                if ln.startswith(m + ":"):
                    rec[m] = ln.split(":", 1)[1].strip()
            if ln.startswith("State:"):
                rec["state"] = ln.split(":", 1)[1].strip()
        out.append(rec)
    return out


t0 = time.monotonic()
fixture = None
while fixture is None and time.monotonic() - t0 < 20:
    fixture = find_fixture()
    time.sleep(0.05)
samples = []
seen = {}
if fixture is not None:
    while time.monotonic() - t0 < SECONDS:
        now = round(time.monotonic() - t0, 3)
        for rec in children(fixture):
            if rec["pid"] not in seen:
                seen[rec["pid"]] = now
            rec["t"] = now
            rec["child_age"] = round(now - seen[rec["pid"]], 3)
            samples.append(rec)
        time.sleep(0.02)

OUT.write_text(json.dumps(
    {"fixture_pid": fixture, "tree": str(TREE), "samples": samples},
    indent=2) + "\n")
print(json.dumps({"fixture_pid": fixture, "samples": len(samples)}))
