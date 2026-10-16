#!/usr/bin/env python3
"""Watcher v2: record EVERY pw-profiler process (with ppid + state + masks)
while a full r89 fixture run is live, so the g_hup leg can be observed in
context. No fixture matching by cwd; the fixture pid(s) are recovered in
analysis from the recorded `measure_audio` parents.

usage: watch_hup2.py <seconds> <out.json>
"""
import json
import os
import sys
import time
from pathlib import Path

SECONDS = float(sys.argv[1])
OUT = Path(sys.argv[2])
MASKS = ("SigBlk", "SigIgn", "SigCgt")


def scan():
    prof, fx = [], []
    for d in Path("/proc").iterdir():
        if not d.name.isdigit():
            continue
        try:
            cmd = (d / "cmdline").read_bytes().replace(b"\0", b" ").decode()
            if "pw-profiler" not in cmd and "measure_audio" not in cmd:
                continue
            stat = (d / "stat").read_text()
            st = (d / "status").read_text(errors="replace")
        except OSError:
            continue
        ppid = int(stat.rsplit(")", 1)[1].split()[1])
        rec = {"pid": int(d.name), "ppid": ppid, "cmd": cmd.strip(),
               "state": None}
        for ln in st.splitlines():
            for m in MASKS:
                if ln.startswith(m + ":"):
                    rec[m] = ln.split(":", 1)[1].strip()
            if ln.startswith("State:"):
                rec["state"] = ln.split(":", 1)[1].strip()
        (prof if "pw-profiler" in cmd else fx).append(rec)
    return prof, fx


t0 = time.monotonic()
prof_samples, fx_samples = [], []
while time.monotonic() - t0 < SECONDS:
    now = round(time.monotonic() - t0, 3)
    prof, fx = scan()
    for r in prof:
        r["t"] = now
        prof_samples.append(r)
    for r in fx:
        r["t"] = now
        fx_samples.append(r)
    time.sleep(0.02)

OUT.write_text(json.dumps({"prof": prof_samples, "fixtures": fx_samples},
                          indent=2) + "\n")
print(json.dumps({"prof_samples": len(prof_samples),
                  "fixtures": len(fx_samples)}))
