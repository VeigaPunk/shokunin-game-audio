#!/usr/bin/env python3
"""r79-author bounded diagnostic — WHY does the `-C` no-prop fallback
stay unnegotiated on this host?

Observation to explain (run 2, 06:46Z): `pw-loopback -C <garbage> -P
<probe sink>` publishes `input.<n>` with ZERO ports and state `suspended`
(no producers at any sample), while the r79 scout measured the same leg
landing on the session DEFAULT SOURCE (the DualSense mic) on 2026-10-14.

Two candidate mechanisms:
  M1 no session default source exists right now (`default.audio.source`
     is absent from `pw-metadata -n default`, and `wpctl status` marks no
     source with `*`) -> nothing to autoconnect to.
  M2 the default source (USB Line Input) is SUSPENDED -> the policy
     refuses to link to a suspended source.

Falsifiable test: write `default.audio.source` = the already-configured
default source (`default.configured.audio.source`), re-run the SAME leg,
and compare. If the input node gains ports and links to that source, M1
is supported and M2 is refuted (that source is suspended in BOTH legs).
State is restored (key deleted again) in `finally`.

Writes only this JSON; every node it creates carries `r79exp_<pid>`, the
probe null sink module is unloaded by the id captured at load, and the
loopback legs are killed by their own pgid.
"""
import json
import os
import re
import signal
import subprocess
import time
from pathlib import Path

PID = os.getpid()
NS = f"r79exp_ns_{PID}"
OUT = Path(__file__).resolve().parent / "exp-default-source-r79.json"
KEY = "default.audio.source"


def run(argv, timeout=10):
    try:
        p = subprocess.run(argv, capture_output=True, timeout=timeout)
        return p.returncode, p.stdout.decode(errors="replace"), \
            p.stderr.decode(errors="replace")
    except (subprocess.TimeoutExpired, OSError) as exc:
        return None, "", str(exc)[:120]


def meta_get(key):
    rc, out, err = run(["pw-metadata", "-n", "default", "0", key])
    m = re.search(r"value:'(.*?)'(?:\s*type|\s*$)", out)
    return {"rc": rc, "raw": m.group(1) if m else None,
            "stderr": err.strip()[:120]}


def meta_set(key, value):
    return run(["pw-metadata", "-n", "default", "0", key, value])[0]


def meta_del(key):
    return run(["pw-metadata", "-n", "default", "-d", "0", key])[0]


def node_ports(tag):
    o = [ln.strip() for ln in run(["pw-link", "-o"])[1].splitlines()
         if ln.strip().startswith(f"{tag}:")]
    i = [ln.strip() for ln in run(["pw-link", "-i"])[1].splitlines()
         if ln.strip().startswith(f"{tag}:")]
    return o, i


def graph():
    """{name: node id} + link edge list, from one pw-dump."""
    rc, out, _ = run(["pw-dump"])
    try:
        dump = json.loads(out or "[]")
    except ValueError:
        return {}, [], []
    names, ids, edges = {}, {}, []
    for obj in dump:
        info = obj.get("info") or {}
        props = info.get("props") or {}
        if str(obj.get("type", "")).endswith("Node"):
            nm = props.get("node.name")
            if nm:
                names[nm] = obj.get("id")
                ids[obj.get("id")] = {"name": nm,
                                      "state": info.get("state"),
                                      "class": props.get("media.class")}
        if str(obj.get("type", "")).endswith("Link"):
            edges.append((props.get("link.output.node"),
                          props.get("link.input.node")))
    return names, ids, edges


def producers_of(node, ids, edges):
    out = []
    for o, i in edges:
        if ids.get(i, {}).get("name") == node and \
                ids.get(o, {}).get("name"):
            out.append(ids[o]["name"])
    return sorted(set(out))


def leg(label, seconds=4.5):
    node = f"input.r79exp_{label}_{PID}"
    proc = subprocess.Popen(
        ["pw-loopback", "-n", f"r79exp_{label}_{PID}", "-C",
         "no_such_node_r79exp", "-P", NS],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        start_new_session=True)
    samples = []
    t0 = time.monotonic()
    for at in (1.5, 3.0):
        left = at - (time.monotonic() - t0)
        if left > 0:
            time.sleep(left)
        names, ids, edges = graph()
        o, i = node_ports(node)
        samples.append({
            "at_s": at, "alive": proc.poll() is None,
            "node_found": node in names,
            "state": ids.get(names.get(node), {}).get("state"),
            "output_ports": o, "input_ports": i,
            "producers": producers_of(node, ids, edges)})
    os.killpg(proc.pid, signal.SIGKILL)
    proc.wait()
    time.sleep(0.4)
    return {"node": node, "samples": samples, "exit_code": proc.returncode}


def main():
    out = {"pid": PID, "sink": NS, "key": KEY}
    mid = None
    try:
        out["pre_metadata"] = meta_get(KEY)
        out["configured_source"] = meta_get("default.configured.audio.source")
        out["pre_pactl"] = [ln for ln in run(["pactl", "info"])[1].splitlines()
                            if ln.startswith("Default ")]
        _, so, _ = run(["pactl", "load-module", "module-null-sink",
                        "sink_name=" + NS])
        mid = int(so.strip()) if so.strip().isdigit() else None
        out["sink_module"] = mid
        time.sleep(0.6)
        out["leg_no_key"] = leg("nokey")
        out["mid_metadata"] = meta_get(KEY)
        src = None
        m = re.search(r'"name"\s*:\s*"([^"]+)"',
                      out["configured_source"].get("raw") or "")
        if m:
            src = m.group(1)
        out["written_source"] = src
        if src:
            out["write_rc"] = meta_set(KEY, json.dumps({"name": src}))
            time.sleep(0.4)
            out["post_write_metadata"] = meta_get(KEY)
            out["leg_key"] = leg("key")
        out["post_metadata"] = meta_get(KEY)
    finally:
        if mid is not None:
            out["unload_rc"] = run(["pactl", "unload-module",
                                    str(mid)])[0]
        if out.get("pre_metadata", {}).get("raw") is None:
            out["restore_delete_rc"] = meta_del(KEY)
        out["restored_metadata"] = meta_get(KEY)
    OUT.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
