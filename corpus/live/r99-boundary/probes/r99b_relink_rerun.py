#!/usr/bin/env python3
"""Re-run the relink cell with full per-packet timestamps, quiet and under load."""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r99b_common import start_hogs, stop_hogs, hog_census, proc_cmdline, pid_alive, SEAT, receipt, loadavg
import r99b_driver as D

mode = sys.argv[1] if len(sys.argv) > 1 else "quiet"
if mode == "load":
    hogs = start_hogs(14, seconds=900)
    pids = [p.pid for p in hogs]
    print("hogs", pids, "loadavg", loadavg(), flush=True)
    time.sleep(30)
try:
    D.run_cells(mode, only="relink", reps=2)
finally:
    if mode == "load":
        marker = {p: ("r99b_hog" in proc_cmdline(p)) for p in pids}
        reaped = stop_hogs()
        receipt("relink-hogs.json", {"pids": pids, "marker_ok": marker, "reaped": reaped,
                                     "final_alive": [p for p in pids if pid_alive(p)],
                                     "final_census": hog_census(), "loadavg_after": loadavg()})
