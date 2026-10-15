#!/usr/bin/env python3
"""r83 REVIEWER live probe #2 — the props that only exist WHILE the leg is
alive (the first probe dumped after the bound and lost them): the
silent-drop default props and the -l/-d/-g latency lattice incl. the
uint32 wrap. Same seat-owned namespace rules as probe_live.py.
"""
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent
PID = os.getpid()
NS_A = f"r83r2_ns_a_{PID}"
NS_B = f"r83r2_ns_b_{PID}"
PREFIX = f"r83r2_{PID}"
GRP = f"r83r2_grp_{PID}"
RES = {"probe": "r83-reviewer-live2", "pid": PID, "legs": {}}
SPAWNED = []


def sh(argv, timeout=10):
    p = subprocess.run(argv, capture_output=True, timeout=timeout)
    return p.returncode, p.stdout.decode(errors="replace"), \
        p.stderr.decode(errors="replace")


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


def dump_nodes():
    rc, out, _ = sh(["pw-dump"], timeout=20)
    try:
        d = json.loads(out or "[]")
    except ValueError:
        return {}
    nodes = {}
    for o in d:
        if str(o.get("type", "")).endswith("Node"):
            props = ((o.get("info") or {}).get("props") or {})
            nodes[props.get("node.name")] = props
    return nodes


def leg(sid, tail, timeout=2.6, prop_keys=("node.latency", "node.group",
                                           "media.name", "bogus.prop",
                                           "node.name")):
    tag = f"{PREFIX}_{sid}"
    argv = ["pw-loopback", "-n", tag, "-C", NS_A, "-i",
            "stream.capture.sink=true", "-P", NS_B, *tail]
    p = subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                         stderr=subprocess.PIPE, start_new_session=True)
    SPAWNED.append(p.pid)
    rec = {"argv": " ".join(argv)}
    t0 = time.monotonic()
    seen = None
    while time.monotonic() - t0 < 3.0:
        nodes = dump_nodes()
        if f"input.{tag}" in nodes:
            seen = nodes
            break
        if p.poll() is not None:
            break
        time.sleep(0.12)
    if seen:
        inp = seen.get(f"input.{tag}") or {}
        outp = seen.get(f"output.{tag}") or {}
        rec["input_props"] = {k: inp.get(k) for k in prop_keys}
        rec["output_props"] = {k: outp.get(k) for k in prop_keys}
        rec["sampled_alive"] = True
        rec["sample_wait_s"] = round(time.monotonic() - t0, 3)
    else:
        rec["sampled_alive"] = False
        rec["note"] = "node never seen while live"
    left = timeout - (time.monotonic() - t0)
    try:
        p.wait(timeout=max(0.05, left))
        rec["killed_at_bound"] = False
    except subprocess.TimeoutExpired:
        os.killpg(p.pid, signal.SIGKILL)
        p.wait()
        rec["killed_at_bound"] = True
    rec["exit_code"] = p.returncode
    rec["stderr_head"] = p.stderr.read().decode(errors="replace") \
        .strip().splitlines()[:2]
    RES["legs"][sid] = rec
    return rec


def main():
    loads = {nm: ns_load(nm) for nm in (NS_A, NS_B)}
    RES["sink_loads"] = loads
    try:
        leg("ctl", [])
        leg("l5", ["-l", "5"])
        leg("l2_5", ["-l", "2.5"])
        leg("l10000", ["-l", "10000"])
        leg("lneg5", ["-l", "-5"])
        leg("d025", ["-d", "0.25"])
        leg("d10", ["-d", "1.0"])
        leg("ld_order", ["-l", "5", "-d", "0.25"])
        leg("dl_order", ["-d", "0.25", "-l", "5"])
        leg("l0", ["-l", "0"])
        leg("dabc", ["-d", "abc"])
        leg("g_group", ["-g", GRP])
        # the silent-drop default props, sampled WHILE alive
        tag = f"{PREFIX}_drop"
        p = subprocess.Popen(["pw-loopback", "-n", tag, "-C", NS_A,
                              "-i", "}{ garbage", "-P", NS_B],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.PIPE, start_new_session=True)
        SPAWNED.append(p.pid)
        rec = {"argv": f"pw-loopback -n {tag} -C <a> -i '}}{{ garbage' -P <b>"}
        t0 = time.monotonic()
        seen = None
        while time.monotonic() - t0 < 3.0:
            nodes = dump_nodes()
            if f"input.{tag}" in nodes:
                seen = nodes
                break
            if p.poll() is not None:
                break
            time.sleep(0.12)
        if seen:
            inp = seen.get(f"input.{tag}") or {}
            rec["input_props"] = {k: inp.get(k) for k in
                                  ("media.name", "bogus.prop", "node.name")}
            rec["sampled_alive"] = True
        try:
            p.wait(timeout=1.2)
            rec["killed_at_bound"] = False
        except subprocess.TimeoutExpired:
            os.killpg(p.pid, signal.SIGKILL)
            p.wait()
            rec["killed_at_bound"] = True
        rec["exit_code"] = p.returncode
        rec["stderr_full"] = p.stderr.read().decode(errors="replace")[:400]
        RES["legs"]["drop_silent"] = rec
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
        nd = dump_nodes()
        RES["own_nodes_after"] = sorted(n for n in nd
                                        if PREFIX in (n or ""))
    (OUT / "probe_live2.json").write_text(json.dumps(RES, indent=1) + "\n")
    for sid, r in RES["legs"].items():
        print(sid, json.dumps({k: v for k, v in r.items()
                               if k in ("input_props", "output_props",
                                        "sampled_alive", "exit_code",
                                        "killed_at_bound")}))
    print("teardown:", json.dumps({"sinks_gone": RES["sinks_gone"],
                                   "own_nodes_after":
                                       RES["own_nodes_after"],
                                   "leftover": RES["leftover_procs"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
