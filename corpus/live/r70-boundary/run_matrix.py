#!/usr/bin/env python3
"""r70 boundary — full edge matrix driver.

Groups:
  A attach shapes at/around hold=0 (oneshot / linger0 / rdwr / parked / rescue)
  B hold ladder on `linger` (the canonical shape) — fine band around h*
  C chunked feeds (byte / dribble / burst-stall) on dec_act
  D arm_timeout confound cells (short timeout, hold>timeout, dec_hcom control)
  E hold ladder under nice-19 CPU saturation (does h* move?)

Per leg: verdict class (au-magic / blocked / decode / other), exit, samples,
error, wall_s — plus load1 sampled at leg start. TSV + full JSON + per-leg
stderr logs under runs/.
"""
import json
import os
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
HCOM = "corpus/live/round-66/pair_dec_hcom.wav"


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
        r = hp.run_leg(member,
                       log_path=str(lp), **kw)
        r.update({"tag": tag, "rep": i, "group": group,
                  "load1": load1()})
        rows.append(r)
        print(f"{group:9} {tag:34} r{i}  {r['class']:9} "
              f"exit={str(r['exit']):4} wall={r['wall_s']:7.3f} "
              f"err={str(r['error'])[:60]}", flush=True)
    return rows


def main():
    (LOGS).mkdir(parents=True, exist_ok=True)
    all_rows = []

    print("=== A: attach shapes (hold=0 degenerate + parked/rescue) ===")
    all_rows += leg("oneshot-h0", "A", reps=8, shape="oneshot", hold=0.0,
                    timeout=4.0)
    all_rows += leg("linger-h0", "A", reps=4, shape="linger", hold=0.0,
                    timeout=4.0)
    all_rows += leg("rdwr-forever", "A", reps=4, shape="rdwr", timeout=4.0)
    all_rows += leg("parked+oneshot", "A", reps=3, shape="parked",
                    timeout=4.0)
    # rescue: writer1 oneshot-detaches; writer2 attaches at delay, parks
    # rescue_park then closes (EOF at delay+park -> verdict if < timeout)
    for d, pk in [(0.05, 0.4), (0.3, 0.4), (1.5, 0.4), (3.5, 0.3)]:
        all_rows += leg(f"rescue-d{d}-p{pk}", "A", reps=3, shape="rescue",
                        rescue_delay=d, rescue_park=pk, timeout=6.0)
    all_rows += leg("rescue-d8-late", "A", reps=2, shape="rescue",
                    rescue_delay=8.0, rescue_park=0.5, timeout=6.0)

    print("=== B: hold ladder (linger/canonical shape) ===")
    for h in [0.0, 0.02, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1, 0.12,
              0.15, 0.2, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0]:
        reps = 8 if h <= 0.12 else (6 if h <= 0.3 else 5)
        all_rows += leg(f"linger-h{h}", "B", reps=reps, shape="linger",
                        hold=h, timeout=4.0)

    print("=== C: chunked feeds on dec_act ===")
    all_rows += leg("byte-h0", "C", reps=4, shape="linger", hold=0.0,
                    feed="byte", byte_gap=0.002, timeout=6.0)
    all_rows += leg("byte-h0.05", "C", reps=3, shape="linger", hold=0.05,
                    feed="byte", byte_gap=0.002, timeout=6.0)
    all_rows += leg("dribble-h0", "C", reps=4, shape="linger", hold=0.0,
                    feed="dribble", chunk_gap=0.03, timeout=6.0)
    all_rows += leg("dribble-h0.05", "C", reps=3, shape="linger", hold=0.05,
                    feed="dribble", chunk_gap=0.03, timeout=6.0)
    all_rows += leg("burst300-stall1.2-h0", "C", reps=4, shape="linger",
                    hold=0.0, feed="burst", burst_bytes=300, stall_s=1.2,
                    timeout=6.0)
    all_rows += leg("burst300-stall9-h0", "C", reps=1, shape="linger",
                    hold=0.0, feed="burst", burst_bytes=300, stall_s=9.0,
                    timeout=6.0)
    # detection needs the 257B prefetch; ffmpeg then sees ZERO tail bytes.
    # does au-magic need the tail, or just EOF?
    all_rows += leg("firstn257-h0.3", "C", reps=3, shape="linger", hold=0.3,
                    feed="firstn", first_n=257, timeout=5.0)
    all_rows += leg("firstn257-h1.0", "C", reps=3, shape="linger", hold=1.0,
                    feed="firstn", first_n=257, timeout=5.0)
    all_rows += leg("firstn600-h0.3", "C", reps=2, shape="linger", hold=0.3,
                    feed="firstn", first_n=600, timeout=5.0)

    print("=== D: arm_timeout confound ===")
    all_rows += leg("linger-h1.0-t0.5", "D", reps=2, shape="linger", hold=1.0,
                    timeout=0.5)
    all_rows += leg("linger-h12-t11", "D", reps=1, shape="linger", hold=12.0,
                    timeout=11.0)
    all_rows += leg("linger-h12-t13.5", "D", reps=1, shape="linger", hold=12.0,
                    timeout=13.5)
    all_rows += leg("hcom-oneshot-h0", "D", reps=3, member=HCOM,
                    shape="oneshot", hold=0.0, timeout=4.0)

    print("=== E: ladder under nice-19 CPU saturation (32 hogs) ===")
    hogs = []
    hog_code = "import time\nwhile True: sum(i*i for i in range(1000))"
    for _ in range(32):
        hogs.append(subprocess.Popen(["nice", "-n", "19", "python3", "-c",
                                      hog_code],
                                     stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL))
    time.sleep(1.0)
    try:
        print(f"    load1 under hogs: {load1()}")
        for h in [0.1, 0.15, 0.2, 0.3, 0.5, 0.8, 1.0, 1.5, 2.0]:
            all_rows += leg(f"load-linger-h{h}", "E", reps=4, shape="linger",
                            hold=h, timeout=6.0, nice_leg=True)
        all_rows += leg("load-oneshot-h0", "E", reps=2, shape="oneshot",
                        hold=0.0, timeout=6.0, nice_leg=True)
    finally:
        for p in hogs:
            p.kill()
        for p in hogs:
            p.wait()

    # receipts
    (RUNS / "legs.json").write_text(json.dumps(all_rows, indent=1) + "\n")
    with open(RUNS / "hold_ladder.tsv", "w") as fh:
        fh.write("group\ttag\trep\tshape\thold\tfeed\ttimeout\tclass\tdetected"
                 "\troute\texit\tsamples\twall_s\ttimed_out\tload1\terror\n")
        for r in all_rows:
            fh.write("\t".join(str(r.get(k)) for k in
                               ("group", "tag", "rep", "shape", "hold",
                                "feed", "timeout", "class", "detected",
                                "route", "exit", "samples", "wall_s",
                                "timed_out", "load1", "error")) + "\n")
    # orphan audit: no ffmpeg may reference my scratch
    out = subprocess.run(["sh", "-c",
                          "ps -eo args | grep ffmpeg | grep r70-boundary | "
                          "grep -v grep | wc -l"],
                         capture_output=True, text=True)
    print(f"orphan audit: {out.stdout.strip()} ffmpeg procs reference "
          f"r70-boundary (must be 0)")


if __name__ == "__main__":
    main()
