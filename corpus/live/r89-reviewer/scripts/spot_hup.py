#!/usr/bin/env python3
"""Independent spot: does SIGHUP really terminate `pw-profiler -J -n 0`?

The r89 gate arms `g_hup` at rc == -1 (default SIGHUP death, no flush). My
co-tenant replay saw rc == -9 (the harness's own SIGKILL at the 9 s bound)
with the process still streaming at 9.076 s — i.e. HUP did not kill it.
This spot replays the minimal pattern (continuously drained stdout, signal at
0.8 s, 6 s bound) N times and records each outcome. It imports nothing from
the fixture and creates no PipeWire objects.

usage: spot_hup.py [n] [sig_at]
"""
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

N = int(sys.argv[1]) if len(sys.argv) > 1 else 6
SIG_AT = float(sys.argv[2]) if len(sys.argv) > 2 else 0.8
SUFFIX = sys.argv[3] if len(sys.argv) > 3 else ""
OUT = Path(__file__).resolve().parent.parent / "receipts" / \
    f"spot-hup{SUFFIX}.json"


def one(i):
    proc = subprocess.Popen(["pw-profiler", "-J", "-n", "0"],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            stdin=subprocess.DEVNULL,
                            start_new_session=True)
    os.set_blocking(proc.stdout.fileno(), False)
    t0 = time.monotonic()
    buf = bytearray()
    fired = False
    alive_at_sig = None
    killed = False
    while True:
        now = time.monotonic() - t0
        if not fired and now >= SIG_AT:
            alive_at_sig = proc.poll() is None
            if alive_at_sig:
                try:
                    proc.send_signal(signal.SIGHUP)
                except ProcessLookupError:
                    alive_at_sig = False
            fired = True
        if proc.poll() is not None:
            while True:
                try:
                    chunk = os.read(proc.stdout.fileno(), 65536)
                except (BlockingIOError, OSError):
                    chunk = b""
                if not chunk:
                    break
                buf += chunk
            break
        if now >= 6.0:
            killed = True
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.wait()
            continue
        try:
            chunk = os.read(proc.stdout.fileno(), 65536)
            if chunk:
                buf += chunk
        except (BlockingIOError, OSError):
            pass
        time.sleep(0.01)
    return {"i": i, "sig_at": SIG_AT, "alive_at_sig": alive_at_sig,
            "killed_at_bound": killed, "exit_code": proc.returncode,
            "signal": (signal.Signals(-proc.returncode).name
                       if (proc.returncode or 0) < 0 else None),
            "wall_s": round(time.monotonic() - t0, 3),
            "stdout_bytes": len(buf),
            "ends_mid_token": not buf.rstrip().endswith(b"}]")}


rows = [one(i) for i in range(N)]
summary = {
    "n": N, "sig_at": SIG_AT, "loadavg": Path("/proc/loadavg").read_text().strip(),
    "hup_deaths": sum(1 for r in rows if r["exit_code"] == -1),
    "survived_to_bound": sum(1 for r in rows if r["killed_at_bound"]),
    "rows": rows}
OUT.write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
