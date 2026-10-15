#!/usr/bin/env python3
"""r78 SIMPLIFIER paired replay driver.

Gate on a quiet host (no sibling probe/battery process for 20 consecutive
seconds — the r78 entries are topology AND host-state witnesses: two
concurrent runs load null sinks, move `default.audio.sink` and contend for
the PCM, so a pair run in a busy window measures the other lane), then run
`--probe-capture-r78` back-to-back in the control env and the candidate env
(same host state), compare, and retry while either receipt is not clean.

usage: pair_replay.py [--attempts N] [--quiet S]
"""
import json
import os
import re
import subprocess
import sys
import time

CONTROL = "/tmp/r78-simpl/control"
CAND = "/tmp/r78-simpl/cand"
OUT = "/tmp/r78-simpl"
FOREIGN = re.compile(r"measure_audio\.py|pw-record|pw-play|pw-cat|arecord|"
                     r"parecord|parec |paplay|pacat |aplay |gst-launch|"
                     r"ffmpeg|sox ")
ENTRIES = ("playback_target_lattice_r78_probe",
           "playback_default_follow_r78_probe",
           "playback_target_loss_r78_probe", "playback_props_r78_probe",
           "playback_class_segv_r78_probe", "playback_aplay_axis_r78_probe",
           "capture_unlinked_zeros_r78_probe", "capture_parec_fix_r78_probe")


def foreign():
    me = os.getpid()
    out = []
    for p in subprocess.run(["ps", "-eo", "pid,args"], capture_output=True,
                            text=True).stdout.splitlines()[1:]:
        pid, _, args = p.strip().partition(" ")
        if int(pid) == me or "pair_replay" in args or "ps -eo" in args:
            continue
        if "nowriter-r75" in args:
            # a stale unpaced `aplay -D null` from the r75 lane (2h53m old,
            # not a live battery): it is a leftover process, not a probe run
            continue
        if FOREIGN.search(args) and "grep" not in args:
            out.append(f"{pid} {args[:90]}")
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
            print(f"[{time.strftime('%H:%M:%S')}] quiet_for="
                  f"{None if clean_since is None else round(time.time()-clean_since)}s "
                  f"foreign={f[:2]}", flush=True)
        time.sleep(5)


def run(env, tag):
    before = set(os.listdir(f"{env}/corpus/live/runs"))
    t0 = time.time()
    p = subprocess.run(["python3", "corpus/fixtures/measure_audio.py",
                        "--probe-capture-r78"], cwd=env, capture_output=True,
                       text=True, timeout=3600)
    after = set(os.listdir(f"{env}/corpus/live/runs")) - before
    rec = None
    for d in sorted(after):
        cand = f"{env}/corpus/live/runs/{d}/measurements.json"
        if os.path.exists(cand):
            rec = cand
    open(f"{OUT}/{tag}.stdout", "w").write(p.stdout)
    open(f"{OUT}/{tag}.stderr", "w").write(p.stderr)
    info = {"tag": tag, "env": env, "rc": p.returncode, "receipt": rec,
            "wall_s": round(time.time() - t0, 1),
            "stdout": p.stdout.strip()[:800],
            "stderr_tail": p.stderr.strip()[-400:]}
    if rec:
        m = json.load(open(rec))["measurements"]
        info["failures"] = {k: v["failures"] for k, v in m.items()
                            if v.get("failures")}
        info["confounds"] = {
            e: {kk: vv for kk, vv in (m[e] or {}).items()
                if kk in ("confound", "confound_observed", "contention",
                          "ambiguous_topology")}
            for e in ENTRIES if e in m}
    return info


def clean(info):
    """A pair is clean when neither side carries a failure and no entry
    raised its own confound flag. `contention.host_is_quiet` is REPORTED,
    never required: this host carries a stale unpaced `aplay -D null` from
    the r75 lane, so the fixture's own census reads host_is_quiet=false on
    every run — the round's canonical clean receipt carries the same flag."""
    if not info.get("receipt") or info.get("failures"):
        return False
    for e, c in (info.get("confounds") or {}).items():
        if c.get("confound_observed") or c.get("confound"):
            return False
    return True


def class_of(info):
    """The follow entry's host-landing class + the nofollow leg's spawn
    default. The entry admits BOTH `pactl_stale_default` and
    `pactl_delayed_default`, but the leaves differ (the nofollow leg's
    spawn default, its tap, the pin/follow pins), so a pair is only
    comparable when both sides landed the same class."""
    rec = info.get("receipt")
    if not rec:
        return None
    m = json.load(open(rec))["measurements"].get(
        "playback_default_follow_r78_probe") or {}
    sw = (m.get("switches") or {}).get("pactl") or {}
    nf = (m.get("legs") or {}).get("nofollow") or {}
    samples = nf.get("samples") or []
    spawn = (samples[0]["nodes"] if samples else None)
    cls = ("pactl_stale_default" if sw.get("pactl_stale_default")
           else "pactl_delayed_default" if sw.get("pactl_delayed_default")
           else None)
    return (cls, spawn)


def comparable(ctl, cand):
    return class_of(ctl) == class_of(cand)


def main():
    attempts = 4
    if "--attempts" in sys.argv:
        attempts = int(sys.argv[sys.argv.index("--attempts") + 1])
    os.makedirs(OUT, exist_ok=True)
    for i in range(1, attempts + 1):
        print(f"=== attempt {i}/{attempts} at {time.strftime('%H:%M:%S')}",
              flush=True)
        if not gate(timeout_s=900):
            return 2
        print(f"[{time.strftime('%H:%M:%S')}] gate clear", flush=True)
        ctl = run(CONTROL, "control")
        print(f"  control  rc={ctl['rc']} wall={ctl.get('wall_s')}s "
              f"failures={list(ctl.get('failures') or {})}", flush=True)
        cand = run(CAND, "cand")
        print(f"  candidate rc={cand['rc']} wall={cand.get('wall_s')}s "
              f"failures={list(cand.get('failures') or {})}", flush=True)
        ok = clean(ctl) and clean(cand) and comparable(ctl, cand)
        if not comparable(ctl, cand):
            print(f"  pair classes differ: control={class_of(ctl)} "
                  f"candidate={class_of(cand)} — not comparable", flush=True)
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
