#!/usr/bin/env python3
"""r99-boundary load pass: hold >=12 own hogs across cells + LAN arms.

usage: r99b_loadrun.py [--n 14] [--warmup 90] [--only ...]
Writes runs/load/hogs-all.json (lifecycle + CPU accounting) and
receipts/load-summary.json. Own PIDs only (argv marker r99b_hog).
"""
import argparse, json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r99b_common import (loadavg, procs_running, start_hogs, stop_hogs, hog_census, receipt,
                         proc_cmdline, pid_alive, SEAT)
import r99b_driver as D


def cpu_of(pid):
    try:
        parts = open("/proc/%d/stat" % pid).read().rsplit(")", 1)[1].split()
        return (int(parts[11]) + int(parts[12])) / os.sysconf("SC_CLK_TCK")
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=14)
    ap.add_argument("--warmup", type=float, default=60.0)
    ap.add_argument("--only", default=None)
    ap.add_argument("--skip-lan", action="store_true")
    a = ap.parse_args()

    t0 = time.time()
    load_before = loadavg()
    hogs = start_hogs(a.n, seconds=3600.0)
    pids = [p.pid for p in hogs]
    cpu0 = {p: cpu_of(p) for p in pids}
    print("hogs:", pids, "loadavg", load_before, flush=True)
    time.sleep(a.warmup)
    load_warm = loadavg()
    print("warmup done, loadavg", load_warm, flush=True)

    try:
        D.run_cells("load", only=a.only)
        if not a.skip_lan:
            D.run_lan("load")
    finally:
        cpu1 = {p: cpu_of(p) for p in pids}
        census = hog_census()
        marker_before = {p: ("r99b_hog" in proc_cmdline(p)) for p in pids}
        reaped = stop_hogs()
    lifecycle = {
        "n_requested": a.n, "pids": pids,
        "marker_ok": marker_before,  # sampled BEFORE reaping (post-reap sampling is vacuous)
        "cpu_s": {p: (round(cpu1[p] - cpu0[p], 2) if cpu0[p] is not None and cpu1[p] is not None else None)
                  for p in pids},
        "census_during": census,
        "reaped": reaped,
        "final_alive": [p for p in pids if pid_alive(p)],
        "final_census": hog_census(),
        "loadavg_before": load_before, "loadavg_warm": load_warm, "loadavg_after": loadavg(),
        "wall_s": round(time.time() - t0, 1),
    }
    os.makedirs(os.path.join(SEAT, "runs", "load"), exist_ok=True)
    json.dump(lifecycle, open(os.path.join(SEAT, "runs", "load", "hogs-all.json"), "w"), indent=1, default=str)
    receipt("load-summary.json", lifecycle)
    print(json.dumps({k: lifecycle[k] for k in ("n_requested", "final_alive", "final_census",
                                                "loadavg_before", "loadavg_warm", "loadavg_after",
                                                "wall_s")}, indent=1))
    total = sum(v for v in lifecycle["cpu_s"].values() if v)
    print("hog CPU total: %.1f CPU-s over %.1f s wall -> %.2f CPU-equivalents"
          % (total, lifecycle["wall_s"], total / max(lifecycle["wall_s"], 1)))


if __name__ == "__main__":
    main()
