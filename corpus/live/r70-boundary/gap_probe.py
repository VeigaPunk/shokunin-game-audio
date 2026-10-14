#!/usr/bin/env python3
"""r70 boundary — gap cells the first matrix missed or misconfigured.

G1 true-rescue: feed writer detaches at ~t0 (hold=0 — the first matrix
   silently inherited hold=1.0 so every 'rescue' leg was really linger-h1.0
   and the flat 1.005 s wall was the feed hold, not the rescue). A second
   O_WRONLY writer attaches at delay d and parks p s. Tests whether ANY
   late-attached writer unblocks open #2, and whether the verdict is
   EOF-gated (wall ~= d+p) rather than attach-gated (wall ~= d).
G2 byte-feed anatomy: 1 B / 2 ms cadence put a write inside the readerless
   window between sox's detection close and the ffmpeg child's open #2 —
   wtrace records the writer-side oserror (EPIPE) the first matrix never
   captured. One leg under strace -f -tt for the reader-side view.
G3 fresh rep-stability at the ragged edge: linger h in {0, 0.02, 0.04,
   0.05} x 8 reps this session (prior run: 0->2/8, 0.02->7/8, >=0.04->8/8).
G4 load x edge: h in {0.02, 0.05, 0.5} under 32 nice-19 CPU hogs — the
   first matrix only load-tested h>=0.1, i.e. never asked whether h* moves.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hold_probe as hp

SCRATCH = hp.SCRATCH
RUNS = SCRATCH / "runs"
LOGS = RUNS / "logs"
MEMBER = "corpus/live/round-66/pair_dec_act.wav"


def load1():
    try:
        return float(open("/proc/loadavg").read().split()[0])
    except OSError:
        return None


def leg(tag, group, reps=1, **kw):
    rows = []
    member = kw.pop("member", MEMBER)
    for i in range(reps):
        lp = LOGS / group / f"{tag}-r{i}.log"
        r = hp.run_leg(member, log_path=str(lp), **kw)
        r.update({"tag": tag, "rep": i, "group": group, "load1": load1()})
        rows.append(r)
        print(f"{group:9} {tag:34} r{i}  {r['class']:9} "
              f"exit={str(r['exit']):4} wall={r['wall_s']:7.3f} "
              f"wt={r['wtrace']} err={str(r['error'])[:50]}", flush=True)
    return rows


def main():
    LOGS.mkdir(parents=True, exist_ok=True)
    rows = []

    print("=== G1: true rescue (feed hold=0, late writer attach) ===")
    for d, p in [(0.1, 0.3), (0.1, 2.0), (0.8, 0.3), (0.8, 2.0), (2.5, 0.3)]:
        rows += leg(f"rescue2-d{d}-p{p}", "G1", reps=3, shape="rescue",
                    hold=0.0, rescue_delay=d, rescue_park=p, timeout=7.0)

    print("=== G2: byte-feed anatomy (EPIPE window) ===")
    rows += leg("byte-h0-wt", "G2", reps=4, shape="linger", hold=0.0,
                feed="byte", byte_gap=0.002, timeout=7.0)
    rows += leg("byte-h0-strace", "G2", reps=1, shape="linger", hold=0.0,
                feed="byte", byte_gap=0.002, timeout=7.0,
                strace_path=str(RUNS / "byte-h0.strace"))
    rows += leg("dribble-h0-wt", "G2", reps=4, shape="linger", hold=0.0,
                feed="dribble", chunk_gap=0.03, timeout=7.0)
    rows += leg("burst-stall-wt", "G2", reps=2, shape="linger", hold=0.0,
                feed="burst", burst_bytes=300, stall_s=1.2, timeout=7.0)

    print("=== G3: fresh rep-stability at the ragged edge ===")
    for h in [0.0, 0.02, 0.04, 0.05]:
        rows += leg(f"re-linger-h{h}", "G3", reps=8, shape="linger",
                    hold=h, timeout=5.0)

    print("=== G4: edge holds under nice-19 CPU saturation ===")
    hog_code = "import time\nwhile True: sum(i*i for i in range(1000))"
    hogs = [subprocess.Popen(["nice", "-n", "19", "python3", "-c", hog_code],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
            for _ in range(32)]
    time.sleep(1.0)
    try:
        print(f"    load1 under hogs: {load1()}")
        for h in [0.02, 0.05, 0.5]:
            rows += leg(f"load-edge-h{h}", "G4", reps=4, shape="linger",
                        hold=h, timeout=6.0, nice_leg=True)
    finally:
        for p in hogs:
            p.kill()
        for p in hogs:
            p.wait()

    out = RUNS / "gap-legs.json"
    out.write_text(json.dumps(rows, indent=1) + "\n")
    with open(RUNS / "gap-legs.tsv", "w") as fh:
        fh.write("group\ttag\trep\tshape\thold\tfeed\ttimeout\tclass\tdetected"
                 "\troute\texit\twall_s\ttimed_out\tload1\twtrace\terror\n")
        for r in rows:
            fh.write("\t".join(str(r.get(k)) for k in
                               ("group", "tag", "rep", "shape", "hold",
                                "feed", "timeout", "class", "detected",
                                "route", "exit", "wall_s", "timed_out",
                                "load1", "wtrace", "error")) + "\n")
    chk = subprocess.run(["sh", "-c",
                          "ps -eo args | grep ffmpeg | grep r70-boundary | "
                          "grep -v grep | wc -l"],
                         capture_output=True, text=True)
    print(f"orphan audit: {chk.stdout.strip()} ffmpeg procs reference "
          f"r70-boundary (must be 0)")
    print(f"rows: {len(rows)} -> {out}")


if __name__ == "__main__":
    main()
