#!/usr/bin/env python3
"""Decisive probe: why does `pw-profiler -J -n 0` sometimes survive SIGHUP?

Replays of the committed r89 probe under co-tenancy (r89-verifier live)
failed `g_hup` 3/3 with rc == -9 (the harness's own SIGKILL at the 9 s
bound) while the committed receipts and a plain spot die rc == -1 on HUP
12/12. A process survives a default-action fatal signal only if the signal
is blocked, ignored, or caught — so this spot reads /proc/<pid>/status
SigBlk/SigIgn/SigCgt immediately before and after the HUP, and again while
it is still alive, then reports the state transitions.

usage: spot_hup_state.py [n] [sig_at] [hold_s] [suffix]
"""
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

N = int(sys.argv[1]) if len(sys.argv) > 1 else 3
SIG_AT = float(sys.argv[2]) if len(sys.argv) > 2 else 0.8
HOLD = float(sys.argv[3]) if len(sys.argv) > 3 else 4.0
SUFFIX = sys.argv[4] if len(sys.argv) > 4 else ""
OUT = Path(__file__).resolve().parent.parent / "receipts" / \
    f"spot-hup-state{SUFFIX}.json"

MASKS = ("SigBlk", "SigIgn", "SigCgt")


def masks(pid):
    try:
        txt = Path(f"/proc/{pid}/status").read_text()
    except OSError as exc:
        return {"error": str(exc)[:60]}
    out = {"state": None}
    for ln in txt.splitlines():
        for m in MASKS:
            if ln.startswith(m + ":"):
                out[m] = ln.split(":", 1)[1].strip()
        if ln.startswith("State:"):
            out["state"] = ln.split(":", 1)[1].strip()
    return out


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
    rec = {"i": i, "pid": proc.pid, "sig_at": SIG_AT}
    while True:
        now = time.monotonic() - t0
        if not fired and now >= SIG_AT:
            rec["masks_before_hup"] = masks(proc.pid)
            rec["alive_at_sig"] = proc.poll() is None
            if rec["alive_at_sig"]:
                try:
                    proc.send_signal(signal.SIGHUP)
                except ProcessLookupError:
                    rec["alive_at_sig"] = False
            fired = True
            time.sleep(0.05)
            rec["masks_after_hup_50ms"] = masks(proc.pid)
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
        if now >= HOLD:
            rec["masks_at_bound"] = masks(proc.pid)
            rec["killed_at_bound"] = True
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
    rec.update({"exit_code": proc.returncode,
                "signal": (signal.Signals(-proc.returncode).name
                           if (proc.returncode or 0) < 0 else None),
                "wall_s": round(time.monotonic() - t0, 3),
                "stdout_bytes": len(buf)})
    return rec


rows = [one(i) for i in range(N)]
summary = {"n": N, "sig_at": SIG_AT, "hold_s": HOLD,
           "loadavg": Path("/proc/loadavg").read_text().strip(),
           "hup_deaths": sum(1 for r in rows if r["exit_code"] == -1),
           "survived_to_bound": sum(1 for r in rows if r.get("killed_at_bound")),
           "rows": rows}
OUT.write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
