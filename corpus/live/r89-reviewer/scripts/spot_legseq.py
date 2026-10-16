#!/usr/bin/env python3
"""Minimal reproduction attempt for the r89 `g_hup` survival.

My three frozen-tree replays failed `g_hup` 3/3 (rc -9 = the harness's own
SIGKILL at the 9 s bound, ~684-688 KiB streamed) while the committed
receipts (2/2) and standalone HUP spots (15/15) die rc -1 at ~0.8 s. This
spot replays the *exact* four-leg sequence of `pwprof_gate_r89_entry`
(g_term, g_int, g_kill, g_hup) with the seat's own null sink + pw-play
follower attached, using the pinned fixture's own helpers, while a sampler
thread records the /proc state+signal masks of every `pw-profiler -J -n 0`
child of this process every 20 ms.

usage: spot_legseq.py [tree]
"""
import json
import os
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

TREE = Path(sys.argv[1] if len(sys.argv) > 1 else
            Path(__file__).resolve().parent.parent / "tree")
sys.path.insert(0, str(TREE / "corpus" / "fixtures"))
import measure_audio as M  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "receipts" / \
    "spot-legseq.json"
MASKS = ("SigBlk", "SigIgn", "SigCgt")
samples = []
stop = threading.Event()


def procs():
    out = []
    for d in Path("/proc").iterdir():
        if not d.name.isdigit():
            continue
        try:
            cmd = (d / "cmdline").read_bytes().replace(b"\0", b" ").decode()
            stat = (d / "stat").read_text()
        except OSError:
            continue
        if "pw-profiler" in cmd and "-J" in cmd and "-n 0" in cmd:
            ppid = int(stat.rsplit(")", 1)[1].split()[1])
            if ppid == os.getpid():
                st = (d / "status").read_text(errors="replace")
                rec = {"pid": int(d.name), "t": round(
                    time.monotonic() - T0, 3), "state": None}
                for ln in st.splitlines():
                    for m in MASKS:
                        if ln.startswith(m + ":"):
                            rec[m] = ln.split(":", 1)[1].strip()
                    if ln.startswith("State:"):
                        rec["state"] = ln.split(":", 1)[1].strip()
                out.append(rec)
    return out


def sampler():
    while not stop.is_set():
        for rec in procs():
            samples.append(rec)
        time.sleep(0.02)


T0 = time.monotonic()
th = threading.Thread(target=sampler, daemon=True)
th.start()

failures, entry = [], {"probe": "r89r spot legseq"}
loads, players = {}, []
legs = {}
try:
    loads[M.PWPROF_R89_NS] = M._pwprof_r89_load_ns(M.PWPROF_R89_NS)
    with M.tempfile.TemporaryDirectory(prefix="r89r-legseq-") as tmp:
        ctx = M._pwprof_r89_ctx(tmp)
        tag = f"{M.PWPROF_R89_PREFIX}_pl"
        legs["link"] = {"player": M._pwprof_r89_ensure_player(ctx, tag)}
        players.append(ctx.get("player"))
        legs["g_term"] = M._pwprof_r89_stream(
            ["pw-profiler", "-J", "-n", "0"], 9.0, sig_at=1.0,
            sig=signal.SIGTERM, keep_raw=True)
        legs["g_int"] = M._pwprof_r89_stream(
            ["pw-profiler", "-J", "-n", "0"], 9.0, sig_at=1.0,
            sig=signal.SIGINT, keep_raw=True)
        legs["g_kill"] = M._pwprof_r89_stream(
            ["pw-profiler", "-J", "-n", "0"], 9.0, sig_at=1.0,
            sig=signal.SIGKILL, keep_raw=True)
        legs["g_hup"] = M._pwprof_r89_stream(
            ["pw-profiler", "-J", "-n", "0"], 9.0, sig_at=0.8,
            sig=signal.SIGHUP, keep_raw=True)
finally:
    stop.set()
    th.join(timeout=1.0)
    M._pwprof_r89_teardown(entry, failures, loads, players)

report = {"tree": str(TREE), "loadavg": Path("/proc/loadavg").read_text().strip(),
          "legs": {k: {kk: (v.get(kk) if kk != "stdout_raw" else "<raw>")
                       for kk in ("exit_code", "signal", "killed_at_bound",
                                  "alive_at_sig", "wall_s", "stdout_bytes",
                                  "stdout_raw")}
                   for k, v in legs.items()},
          "teardown": {"unloads": entry.get("unloads"),
                       "sinks_gone": entry.get("sinks_gone"),
                       "own_nodes_after": entry.get("own_nodes_after")},
          "samples": samples}
OUT.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: v for k, v in report.items() if k != "samples"},
                 indent=2))
print("samples:", len(samples))
for s in samples:
    print(" ", s)
