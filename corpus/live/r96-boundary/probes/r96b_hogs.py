#!/usr/bin/env python3
"""r96-boundary load harness — >=12 concurrent CPU hogs, own PIDs only.

start N  : spawn N `yes` hogs (own session each), record PIDs to scratch/hogs.json
stop     : kill exactly the recorded PIDs (then their own sessions), verify gone
status   : loadavg + alive list

No name-pattern kills, no namespace-blind sweeps: only PIDs this seat spawned.
"""
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r96b_lib as L  # noqa: E402

HOGS = os.path.join(L.ROOT, "scratch", "hogs.json")


def start(n=12):
    if os.path.exists(HOGS):
        with open(HOGS) as fh:
            old = json.load(fh)
        if old.get("pids"):
            raise SystemExit("hogs already recorded; stop first")
    before = L.loadavg()
    pids = []
    for i in range(n):
        p = subprocess.Popen(["yes"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             stdin=subprocess.DEVNULL, start_new_session=True)
        pids.append(p.pid)
    time.sleep(4.0)
    after = L.loadavg()
    rec = {"pids": pids, "n": n, "started": time.time(), "loadavg_before": before, "loadavg_after": after}
    os.makedirs(os.path.dirname(HOGS), exist_ok=True)
    with open(HOGS, "w") as fh:
        json.dump(rec, fh, indent=1)
    print(json.dumps(rec, indent=1))
    return rec


def stop():
    if not os.path.exists(HOGS):
        print(json.dumps({"note": "no hogs.json"}))
        return
    with open(HOGS) as fh:
        rec = json.load(fh)
    alive_before = [p for p in rec["pids"] if os.path.exists(f"/proc/{p}")]
    for pid in rec["pids"]:
        try:
            os.killpg(os.getpgid(pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
    time.sleep(1.5)
    alive_after = [p for p in rec["pids"] if os.path.exists(f"/proc/{p}")]
    rec["alive_before"] = len(alive_before)
    rec["alive_after"] = alive_after
    rec["loadavg_stop"] = L.loadavg()
    with open(HOGS, "w") as fh:
        json.dump(rec, fh, indent=1)
    os.unlink(HOGS)
    print(json.dumps(rec, indent=1))
    return rec


def status():
    alive = []
    if os.path.exists(HOGS):
        with open(HOGS) as fh:
            rec = json.load(fh)
        alive = [p for p in rec["pids"] if os.path.exists(f"/proc/{p}")]
    print(json.dumps({"loadavg": L.loadavg(), "alive": alive}, indent=1))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "start":
        start(int(sys.argv[2]) if len(sys.argv) > 2 else 12)
    elif cmd == "stop":
        stop()
    else:
        status()
