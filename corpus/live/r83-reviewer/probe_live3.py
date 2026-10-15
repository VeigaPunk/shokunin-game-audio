#!/usr/bin/env python3
"""r83 REVIEWER live probe #3 — does a crash/drop leg leak a node the
fixture's witnesses (tag substring + PWCAT_R83_PREFIX) cannot see?

The fixture's `_pwcat_r83_shot` witnesses only nodes whose name CONTAINS
the leg tag; teardown witnesses only `r83a_<pid>`-tagged names and the
probe sink names. A leg that crashes AFTER publishing a default-named
node (`input.capture.props` / `pw-*`-style) would be invisible to both.
This probe diffs the whole node table across the crash legs.
"""
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent
PID = os.getpid()
NS_A = f"r83r3_ns_a_{PID}"
NS_B = f"r83r3_ns_b_{PID}"
RES = {"probe": "r83-reviewer-live3", "pid": PID, "legs": {}}
SPAWNED = []


def sh(argv, timeout=15):
    p = subprocess.run(argv, capture_output=True, timeout=timeout)
    return p.returncode, p.stdout.decode(errors="replace"), \
        p.stderr.decode(errors="replace")


def nodes():
    rc, out, _ = sh(["pw-dump"])
    try:
        d = json.loads(out or "[]")
    except ValueError:
        return {}
    out_n = {}
    for o in d:
        if str(o.get("type", "")).endswith("Node"):
            props = ((o.get("info") or {}).get("props") or {})
            out_n[props.get("node.name")] = props.get("media.class")
    return out_n


def sink_names():
    return [l.split("\t")[1] for l in
            sh(["pactl", "list", "short", "sinks"])[1].splitlines()
            if l.strip()]


def ns_load(name):
    rc, out, err = sh(["pactl", "load-module", "module-null-sink",
                       "sink_name=" + name])
    mid = out.strip()
    t0 = time.monotonic()
    while time.monotonic() - t0 < 6:
        if name in sink_names():
            return {"module_id": int(mid) if mid.isdigit() else None,
                    "rc": rc}
        time.sleep(0.15)
    return {"module_id": int(mid) if mid.isdigit() else None, "rc": rc,
            "error": err[:120]}


def module_index_for_sink(name):
    idx = None
    for block in sh(["pactl", "list", "modules"])[1].split("Module #"):
        if f"sink_name={name}" in block:
            m = __import__("re").match(r"(\d+)", block)
            if m:
                idx = int(m.group(1))
    return idx


def unload_own(name, captured):
    idx = module_index_for_sink(name)
    leaf = {"verified_index": idx, "captured": captured}
    if idx is None:
        leaf["skipped"] = "not_listed"
        return leaf
    leaf["recycled"] = (captured is not None and idx != captured)
    rc, _, err = sh(["pactl", "unload-module", str(idx)])
    leaf["exit_code"] = rc
    leaf["stderr_tail"] = err.strip()[:120] or None
    return leaf


def leg(sid, argv, timeout=3.0):
    before = nodes()
    rec = {"argv": " ".join(argv)}
    p = subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                         stderr=subprocess.PIPE, start_new_session=True)
    SPAWNED.append(p.pid)
    try:
        p.wait(timeout=timeout)
        rec["killed_at_bound"] = False
    except subprocess.TimeoutExpired:
        os.killpg(p.pid, signal.SIGKILL)
        p.wait()
        rec["killed_at_bound"] = True
    rec["exit_code"] = p.returncode
    rec["stderr_head"] = p.stderr.read().decode(errors="replace") \
        .strip().splitlines()[:2]
    time.sleep(0.4)
    after = nodes()
    rec["new_nodes_any_name"] = {k: v for k, v in after.items()
                                 if k not in before}
    rec["tagged_new_nodes"] = sorted(
        k for k in rec["new_nodes_any_name"] if sid in (k or ""))
    RES["legs"][sid] = rec


def main():
    for t in ("pw-loopback", "pw-cat", "pw-record"):
        if shutil.which(t) is None:
            print("MISSING", t)
            return 2
    loads = {nm: ns_load(nm) for nm in (NS_A, NS_B)}
    RES["sink_loads"] = loads
    try:
        # default naming (no -n): the fixture's tag witness cannot see these
        leg("crash_lb_i_empty", ["pw-loopback", "-C", NS_A, "-i", "",
                                 "-P", NS_B])
        leg("crash_lb_o_empty", ["pw-loopback", "-C", NS_A, "-i",
                                 "stream.capture.sink=true", "-o", "",
                                 "-P", NS_B])
        leg("crash_pc_empty", ["pw-cat", "-p", "-P", "", "--target",
                               NS_B, "/dev/null"])
        leg("crash_pr_empty", ["pw-record", "-P", "", "--target", NS_A,
                               str(OUT / "tmp" / "x.wav")])
        leg("drop_default_name", ["pw-loopback", "-C", NS_A, "-i",
                                  "}{ garbage", "-P", NS_B])
        leg("err_default_name", ["pw-loopback", "-C", NS_A, "-i",
                                 "a=b }{ c=d", "-P", NS_B])
    finally:
        RES["leftover_procs"] = []
        for pid in SPAWNED:
            if Path(f"/proc/{pid}").exists():
                RES["leftover_procs"].append(pid)
                try:
                    os.killpg(pid, signal.SIGKILL)
                except (ProcessLookupError, PermissionError):
                    pass
        RES["unloads"] = {nm: unload_own(nm, leaf.get("module_id"))
                          for nm, leaf in loads.items()}
        after = sink_names()
        RES["sinks_gone"] = {nm: nm not in after for nm in loads}
        nd = nodes()
        RES["own_nodes_after"] = sorted(n for n in nd if str(PID) in (n or ""))
    (OUT / "probe_live3.json").write_text(json.dumps(RES, indent=1) + "\n")
    for sid, r in RES["legs"].items():
        print(sid, "rc=", r["exit_code"], "killed=", r["killed_at_bound"],
              "NEW:", json.dumps(r["new_nodes_any_name"]))
    print("teardown:", json.dumps({"sinks_gone": RES["sinks_gone"],
                                   "own_nodes_after":
                                       RES["own_nodes_after"],
                                   "leftover": RES["leftover_procs"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
