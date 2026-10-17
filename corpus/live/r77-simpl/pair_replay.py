#!/usr/bin/env python3
"""r77 simplifier PAIRED replay driver.

Gate on a quiet host, then run `--probe-capture-r77` back-to-back in the
control env and the candidate env (same host state), compare, and retry while
either receipt is not clean (`failures: {}` for the six capture entries and no
confound flag).

usage: pair_replay.py [--attempts N] [--force]
"""
import json
import os
import re
import subprocess
import sys
import time

CONTROL = "/tmp/r77-simpl-control"
CAND = "/tmp/r77-simpl-cand"
OUT = "/tmp/r77-simpl"
FOREIGN = re.compile(r"measure_audio\.py|pw-record|arecord|parecord|parec |"
                     r"pw-cat|pw-play|paplay|gst-launch|ffmpeg|sox ")
ENTRIES = ("capture_source_lattice_r77_probe", "capture_target_loss_r77_probe",
           "capture_readers_r77_probe", "capture_arecord_sever_r77_probe",
           "capture_split_sentinel_r77_probe", "capture_format_axis_r77_probe")


def foreign():
    me = os.getpid()
    out = []
    for p in subprocess.run(["ps", "-eo", "pid,args"], capture_output=True,
                            text=True).stdout.splitlines()[1:]:
        pid, _, args = p.strip().partition(" ")
        if int(pid) == me or "pair_replay" in args or "ps -eo" in args:
            continue
        if FOREIGN.search(args) and "grep" not in args:
            out.append(f"{pid} {args[:80]}")
    return out


def gate(quiet_s=20, timeout_s=3600):
    t0 = time.time()
    clean_since = None
    while True:
        f = foreign()
        if f:
            clean_since = None
        elif clean_since is None:
            clean_since = time.time()
        elif time.time() - clean_since >= quiet_s:
            return True
        if time.time() - t0 > timeout_s:
            print(f"GATE TIMEOUT after {timeout_s}s; foreign={f}")
            return False
        if int(time.time()) % 30 == 0:
            print(f"[{time.strftime('%H:%M:%S')}] "
                  f"quiet_for={None if clean_since is None else round(time.time()-clean_since)}s "
                  f"foreign={f[:2]}", flush=True)
        time.sleep(5)


def run(env, tag):
    before = set(os.listdir(f"{env}/corpus/live/runs"))
    t0 = time.time()
    p = subprocess.run(["python3", "corpus/fixtures/measure_audio.py",
                        "--probe-capture-r77"], cwd=env, capture_output=True,
                       text=True, timeout=1800)
    after = set(os.listdir(f"{env}/corpus/live/runs")) - before
    rec = None
    for d in sorted(after):
        cand = f"{env}/corpus/live/runs/{d}/measurements.json"
        if os.path.exists(cand):
            rec = cand
    open(f"{OUT}/{tag}.stdout.json", "w").write(p.stdout)
    open(f"{OUT}/{tag}.stderr.log", "w").write(p.stderr)
    info = {"tag": tag, "env": env, "rc": p.returncode, "receipt": rec,
            "wall_s": round(time.time() - t0, 1),
            "stdout": p.stdout.strip()[:1200],
            "stderr_tail": p.stderr.strip()[-400:]}
    if rec:
        m = json.load(open(rec))["measurements"]
        info["failures"] = {k: v["failures"] for k, v in m.items()
                            if v.get("failures")}
        info["confounds"] = {
            e: {kk: vv for kk, vv in m[e].items()
                if kk in ("confound", "confound_observed", "contention",
                          "ambiguous_topology")}
            for e in ENTRIES if e in m}
    return info


def clean(info):
    if not info.get("receipt") or info.get("failures"):
        return False
    for e, c in (info.get("confounds") or {}).items():
        if c.get("confound_observed") or c.get("confound"):
            return False
        if isinstance(c.get("contention"), dict) and \
                not c["contention"].get("host_is_quiet", True):
            return False
    return True


def main():
    attempts = 4
    if "--attempts" in sys.argv:
        attempts = int(sys.argv[sys.argv.index("--attempts") + 1])
    os.makedirs(OUT, exist_ok=True)
    for i in range(1, attempts + 1):
        print(f"=== attempt {i}/{attempts} at {time.strftime('%H:%M:%S')}",
              flush=True)
        if not gate():
            return 2
        print(f"[{time.strftime('%H:%M:%S')}] gate clear", flush=True)
        ctl = run(CONTROL, "control")
        print(f"  control  rc={ctl['rc']} wall={ctl.get('wall_s')}s "
              f"failures={list(ctl.get('failures') or {})}", flush=True)
        cand = run(CAND, "cand")
        print(f"  candidate rc={cand['rc']} wall={cand.get('wall_s')}s "
              f"failures={list(cand.get('failures') or {})}", flush=True)
        ok = clean(ctl) and clean(cand)
        json.dump({"control": ctl, "candidate": cand, "clean": ok},
                  open(f"{OUT}/pair.run.json", "w"), indent=1)
        if ok:
            print("PAIR CLEAN", flush=True)
            return 0
        print(f"  pair not clean (control={clean(ctl)} cand={clean(cand)}); "
              f"retrying", flush=True)
    return 1


if __name__ == "__main__":
    sys.exit(main())
