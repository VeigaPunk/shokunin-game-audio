#!/usr/bin/env python3
"""r79-author diagnostic 3 — the scout's D2a-D2d/D17 record-target arms
against a live loopback, re-measured before the arm's expectations are
frozen (run 2 showed d2a/d2b erroring with `no target node available` and
d2c falling back to the default sink monitor, while the scout measured
all four landing as named).

R1  pw-record --target output.<lb>              (scout D2b: the copied
                                                 stream's own out ports)
R2  pw-record -P stream.capture.sink=true
        --target input.<lb>                     (scout D2c: the capture
                                                 node's monitor_* ports)
R3  pw-record --target 0 + manual pw-link of
        input.<lb>:monitor_* -> <rec>:input_*   (scout D17)

Bounded, probe-owned names only (`r79exp3_*`), tone never fed (topology
only), everything killed/unloaded in `finally`.
"""
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp_capture_ports as E  # noqa: E402

PID = os.getpid()
NS_A = f"r79exp3_a_{PID}"
NS_B = f"r79exp3_b_{PID}"
OUT = Path(__file__).resolve().parent / "exp-record-targets-r79.json"


def spawn_rec(label, extra, target, seconds=2.0):
    tag = f"r79exp3_rec_{label}_{PID}"
    argv = ["pw-record", *extra, "-P", f"node.name={tag}", "--target",
            target, "-n", str(int(48000 * seconds)), "--rate", "48000",
            "--channels", "2", "--format", "s16", f"/tmp/{tag}.wav"]
    return tag, subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                                 stderr=subprocess.PIPE,
                                 start_new_session=True)


def main():
    out = {"pid": PID}
    mids = []
    lb = None
    try:
        for nm in (NS_A, NS_B):
            _, so, _ = E.run(["pactl", "load-module", "module-null-sink",
                              "sink_name=" + nm])
            mids.append(int(so.strip()) if so.strip().isdigit() else None)
        time.sleep(0.6)
        lb_tag = f"r79exp3_lb_{PID}"
        lb = subprocess.Popen(
            ["pw-loopback", "-n", lb_tag, "-C", NS_A,
             "-i", "stream.capture.sink=true", "-P", NS_B],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            start_new_session=True)
        time.sleep(1.6)
        in_node, out_node = f"input.{lb_tag}", f"output.{lb_tag}"
        out["loopback_ports"] = {"input": E.ports_of(in_node),
                                 "output": E.ports_of(out_node)}
        for label, extra, target in (
                ("r1", [], out_node),
                ("r2", ["-P", "stream.capture.sink=true"], in_node),
                ("r3", [], "0")):
            tag, proc = spawn_rec(label, extra, target)
            rows, t0 = [], time.monotonic()
            for a in (0.8, 1.6):
                left = a - (time.monotonic() - t0)
                if left > 0:
                    time.sleep(left)
                names, ids, edges = E.graph()
                rows.append({"at_s": a, "found": tag in names,
                             "state": ids.get(names.get(tag), {}).get("state"),
                             "ports": E.ports_of(tag),
                             "producers": E.edges_of(tag, ids, edges, "in")})
            if label == "r3":
                pairs = [(f"{in_node}:monitor_FL", f"{tag}:input_FL"),
                         (f"{in_node}:monitor_FR", f"{tag}:input_FR")]
                out["r3_pins"] = E.run(["pw-link", pairs[0][0],
                                        pairs[0][1]])[0]
                out["r3_pins_err"] = E.run(["pw-link", pairs[0][0],
                                            pairs[0][1]])[2][:120]
                out["r3_pins2"] = E.run(["pw-link", pairs[1][0],
                                         pairs[1][1]])[0]
                out["r3_pins2_err"] = E.run(["pw-link", pairs[1][0],
                                             pairs[1][1]])[2][:120]
                time.sleep(0.5)
                names, ids, edges = E.graph()
                rows.append({"at_s": 2.1,
                             "producers": E.edges_of(tag, ids, edges, "in")})
            try:
                proc.wait(timeout=4)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
            out[label] = {"tag": tag, "target": target, "extra": extra,
                          "rows": rows, "exit_code": proc.returncode,
                          "stderr": proc.stderr.read().decode(
                              errors="replace")[:200]}
            time.sleep(0.3)
    finally:
        if lb is not None and lb.poll() is None:
            os.killpg(lb.pid, signal.SIGKILL)
            lb.wait()
        for m in mids:
            if m is not None:
                E.run(["pactl", "unload-module", str(m)])
    OUT.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
