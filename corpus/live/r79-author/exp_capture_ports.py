#!/usr/bin/env python3
"""r79-author diagnostic 2 — do CAPTURE streams get ports at all when
their target does not resolve, and does an ACTIVE default source make the
`pw-loopback -C` no-prop fallback link?

Context: diagnostic 1 refuted "no session default source key" (writing
`default.audio.source` changed nothing; WirePlumber dropped the key again
mid-leg). This script tests the two remaining mechanisms with the same
bounded shape:

  P1  pw-record --target <a real, resolvable SOURCE>   -> ports?
  P2  pw-record --target 0                             -> ports?
  P3  pw-record --target <garbage>                     -> ports?
  P4  loopback no-prop `-C` while a holder keeps the default source
      RUNNING (the source is suspended in every earlier sample) -> does
      the fallback link once the source is active?

Writes only its own JSON; every node carries `r79exp2_<pid>`, the probe
null sink is unloaded by its captured module id, all children are killed
by pgid, and the holder is bounded.
"""
import json
import os
import re
import signal
import subprocess
import time
from pathlib import Path

PID = os.getpid()
NS = f"r79exp2_ns_{PID}"
OUT = Path(__file__).resolve().parent / "exp-capture-ports-r79.json"
SRC = "alsa_input.usb-Generic_USB_Audio-00.HiFi__Line__source"


def run(argv, timeout=10):
    try:
        p = subprocess.run(argv, capture_output=True, timeout=timeout)
        return p.returncode, p.stdout.decode(errors="replace"), \
            p.stderr.decode(errors="replace")
    except (subprocess.TimeoutExpired, OSError) as exc:
        return None, "", str(exc)[:120]


def graph():
    rc, out, _ = run(["pw-dump"])
    try:
        dump = json.loads(out or "[]")
    except ValueError:
        return {}, {}, []
    names, ids, edges = {}, {}, []
    for obj in dump:
        info = obj.get("info") or {}
        props = info.get("props") or {}
        if str(obj.get("type", "")).endswith("Node"):
            nm = props.get("node.name")
            if nm:
                names[nm] = obj.get("id")
                ids[obj.get("id")] = {"name": nm,
                                      "state": info.get("state")}
        if str(obj.get("type", "")).endswith("Link"):
            edges.append((props.get("link.output.node"),
                          props.get("link.input.node")))
    return names, ids, edges


def edges_of(node, ids, edges, direction):
    out = []
    for o, i in edges:
        if direction == "in" and ids.get(i, {}).get("name") == node and \
                ids.get(o, {}).get("name"):
            out.append(ids[o]["name"])
        if direction == "out" and ids.get(o, {}).get("name") == node and \
                ids.get(i, {}).get("name"):
            out.append(ids[i]["name"])
    return sorted(set(out))


def ports_of(tag):
    o = [ln.strip() for ln in run(["pw-link", "-o"])[1].splitlines()
         if ln.strip().startswith(f"{tag}:")]
    i = [ln.strip() for ln in run(["pw-link", "-i"])[1].splitlines()
         if ln.strip().startswith(f"{tag}:")]
    return o, i


def sample(tag, at):
    names, ids, edges = graph()
    o, i = ports_of(tag)
    return {"at_s": at, "found": tag in names,
            "state": ids.get(names.get(tag), {}).get("state"),
            "output_ports": o, "input_ports": i,
            "producers": edges_of(tag, ids, edges, "in"),
            "consumers": edges_of(tag, ids, edges, "out")}


def record_leg(label, target, at=(1.2, 2.4)):
    tag = f"r79exp2_rec_{label}_{PID}"
    proc = subprocess.Popen(
        ["pw-record", "-P", f"node.name={tag}", "--target", target,
         "-n", "48000", "--rate", "48000", "--channels", "2",
         "--format", "s16", f"/tmp/{tag}.wav"],
        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
        start_new_session=True)
    rows, t0 = [], time.monotonic()
    for a in at:
        left = a - (time.monotonic() - t0)
        if left > 0:
            time.sleep(left)
        rows.append(sample(tag, a))
    try:
        proc.wait(timeout=4)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        proc.wait()
    return {"tag": tag, "target": target, "samples": rows,
            "exit_code": proc.returncode,
            "stderr": proc.stderr.read().decode(errors="replace")[:160]}


def loopback_leg(label, at=(1.6, 3.0), bound=4.5):
    tag = f"r79exp2_lb_{label}_{PID}"
    node = f"input.{tag}"
    proc = subprocess.Popen(
        ["pw-loopback", "-n", tag, "-C", "no_such_node_r79exp2",
         "-P", NS],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        start_new_session=True)
    rows, t0 = [], time.monotonic()
    for a in at:
        left = a - (time.monotonic() - t0)
        if left > 0:
            time.sleep(left)
        rows.append(sample(node, a))
    try:
        proc.wait(timeout=max(0.2, bound - (time.monotonic() - t0)))
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        proc.wait()
    return {"node": node, "samples": rows, "exit_code": proc.returncode}


def main():
    out = {"pid": PID, "sink": NS, "src": SRC}
    mid = None
    holder = None
    try:
        _, so, _ = run(["pactl", "load-module", "module-null-sink",
                        "sink_name=" + NS])
        mid = int(so.strip()) if so.strip().isdigit() else None
        out["sink_module"] = mid
        time.sleep(0.6)
        out["p1_resolvable_source"] = record_leg("p1", SRC)
        out["p2_target_zero"] = record_leg("p2", "0")
        out["p3_garbage"] = record_leg("p3", "no_such_source_r79exp2")
        out["pre_source_state"] = {
            k: v for k, v in graph()[1].items() if v["name"] == SRC}
        out["leg_before_holder"] = loopback_leg("pre")
        # activate the default source for the length of one leg
        holder = subprocess.Popen(
            ["pw-record", "-P", f"node.name=r79exp2_hold_{PID}",
             "--target", SRC, "-n", "480000", "--rate", "48000",
             "--channels", "2", "--format", "s16",
             f"/tmp/r79exp2_hold_{PID}.wav"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            start_new_session=True)
        time.sleep(1.2)
        names, ids, edges = graph()
        out["source_state_while_held"] = {
            v["name"]: v["state"] for v in ids.values() if v["name"] == SRC}
        out["leg_with_holder"] = loopback_leg("held")
    finally:
        if holder is not None and holder.poll() is None:
            os.killpg(holder.pid, signal.SIGKILL)
            holder.wait()
        if mid is not None:
            out["unload_rc"] = run(["pactl", "unload-module",
                                    str(mid)])[0]
        time.sleep(0.5)
        out["default_source_meta"] = re.search(
            r"value:'(.*?)'(?:\s*type|\s*$)",
            run(["pw-metadata", "-n", "default", "0",
                 "default.audio.source"])[1] or "").group(1) \
            if re.search(r"value:'(.*?)'(?:\s*type|\s*$)",
                         run(["pw-metadata", "-n", "default", "0",
                              "default.audio.source"])[1] or "") else None
    OUT.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
