#!/usr/bin/env python3
"""Bounded side-check: does a purely numeric module-null-sink sink_name
enumerate as a node on this host? (r85 reviewer, probe-owned objects.)"""
import json
import subprocess
import sys
import time

DIG = sys.argv[1] if len(sys.argv) > 1 else "777888999"


def run(argv, timeout=15):
    p = subprocess.run(argv, capture_output=True, timeout=timeout)
    return p.returncode, p.stdout.decode(errors="replace")


def dump_nodes():
    rc, out = run(["pw-dump"])
    d = json.loads(out or "[]")
    nodes = []
    for o in d:
        if not str(o.get("type", "")).endswith("Node"):
            continue
        info = o.get("info") or {}
        props = info.get("props") or {}
        if not isinstance(props, dict):
            props = {}
        nodes.append((str(props.get("node.name")), props.get("object.serial")))
    return nodes


rc, out = run(["pactl", "load-module", "module-null-sink",
               "sink_name=" + DIG])
mid = out.strip()
print("load rc", rc, "mid", mid)
try:
    for i in range(12):
        time.sleep(0.5)
        rc_s, sinks = run(["pactl", "list", "sinks", "short"])
        names = dump_nodes()
        hit_sink = [ln for ln in sinks.splitlines() if DIG in ln]
        hit_node = [n for n, s in names if n and DIG in str(n)]
        print(i, "pactl_sink:", hit_sink, "pw_node:", hit_node)
        if hit_sink or hit_node:
            break
finally:
    rc_m, mods = run(["pactl", "list", "modules", "short"])
    idx = [ln.split("\t")[0] for ln in mods.splitlines() if DIG in ln]
    print("module_lines:", idx)
    if idx:
        print("unload rc",
              run(["pactl", "unload-module", idx[0]])[0])
