#!/usr/bin/env python3
"""r89 critic: natural-rate co-tenancy probe (READ-ONLY).

The committed `x_foot` arm requires, across a ~0.35 s bracket:
    pwprof_during == pwprof_before + 1   AND   nodes_delta == 0
It takes that bracket with three `pw-dump` invocations (c0, c1) while a
sibling wave-B seat is running the SAME probe from another tree.

This probe samples the two arm INPUTS directly (light read verbs only —
`pw-cli ls Client`, `pw-cli ls Node`, `pactl list modules short`; no
object is created, loaded, unloaded, linked or destroyed and no stream
is spawned) and reports, over every observed ~0.35 s window, whether
that window would have satisfied the arm. Sliding-window census at the
natural rate = the arm's false-FAIL rate under live co-tenancy.
"""
import json
import re
import subprocess
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent
DURATION_S = 24.0
PERIOD_S = 0.12
WINDOW_LO, WINDOW_HI = 0.30, 0.45


def clients():
    p = subprocess.run(["pw-cli", "ls", "Client"], capture_output=True,
                       timeout=10)
    names = re.findall(r'application\.name = "([^"]*)"',
                       p.stdout.decode(errors="replace"))
    return names


def nodes():
    p = subprocess.run(["pw-cli", "ls", "Node"], capture_output=True,
                       timeout=10)
    return re.findall(r'node\.name = "([^"]*)"',
                      p.stdout.decode(errors="replace"))


def modules():
    p = subprocess.run(["pactl", "list", "modules", "short"],
                       capture_output=True, timeout=10)
    return [l for l in p.stdout.decode(errors="replace").splitlines()
            if l.strip()]


samples = []
t0 = time.monotonic()
while time.monotonic() - t0 < DURATION_S:
    ts = time.monotonic() - t0
    try:
        cl = clients()
        nd = nodes()
        md = modules()
    except Exception as exc:                     # bounded, loud
        samples.append({"t": round(ts, 3), "error": str(exc)[:80]})
        continue
    samples.append({"t": round(ts, 3),
                    "pwprof_clients": cl.count("pw-profiler"),
                    "pwplay_clients": cl.count("pw-play"),
                    "clients": len(cl),
                    "nodes": len(nd),
                    "modules": len(md),
                    "r89a_nodes": [n for n in nd if "r89a" in n],
                    "r89a_modules": [l for l in md if "r89a" in l]})
    time.sleep(PERIOD_S)

ok = [s for s in samples if "error" not in s]
windows = []
for i, a in enumerate(ok):
    for b in ok[i + 1:]:
        dt = b["t"] - a["t"]
        if dt < WINDOW_LO:
            continue
        if dt > WINDOW_HI:
            break
        windows.append({
            "t0": a["t"], "t1": b["t"], "dt": round(dt, 3),
            "pwprof_delta": b["pwprof_clients"] - a["pwprof_clients"],
            "node_delta": b["nodes"] - a["nodes"],
            "module_delta": b["modules"] - a["modules"],
            "arm_pass": (b["pwprof_clients"] - a["pwprof_clients"] == 1
                         and b["nodes"] - a["nodes"] == 0)})

res = {
    "duration_s": DURATION_S, "period_s": PERIOD_S,
    "samples": len(samples), "usable_samples": len(ok),
    "pwprof_client_counts": sorted({s["pwprof_clients"] for s in ok}),
    "node_counts": [min(s["nodes"] for s in ok),
                    max(s["nodes"] for s in ok)],
    "module_counts": [min(s["modules"] for s in ok),
                      max(s["modules"] for s in ok)],
    "r89a_nodes_seen": sorted({n for s in ok for n in s["r89a_nodes"]}),
    "r89a_modules_seen": sorted({m for s in ok for m in s["r89a_modules"]}),
    "windows": len(windows),
    "windows_arm_pass": sum(1 for w in windows if w["arm_pass"]),
    "windows_arm_fail": sum(1 for w in windows if not w["arm_pass"]),
    "arm_fail_rate": (round(sum(1 for w in windows if not w["arm_pass"])
                            / len(windows), 3) if windows else None),
    "fail_reasons": {
        "pwprof_delta_not_plus1": sum(1 for w in windows
                                      if w["pwprof_delta"] != 1),
        "node_delta_nonzero": sum(1 for w in windows
                                  if w["node_delta"] != 0),
    },
    "window_detail": windows,
    "raw": samples,
}
(OUT / "churn.json").write_text(json.dumps(res, indent=2) + "\n")

print(f"samples {len(ok)}/{len(samples)} over {DURATION_S}s "
      f"(period {PERIOD_S}s)")
print("pw-profiler client counts seen:", res["pwprof_client_counts"])
print("node counts min/max:", res["node_counts"])
print("module counts min/max:", res["module_counts"])
print("r89a nodes seen:", res["r89a_nodes_seen"])
print("r89a modules seen:", len(res["r89a_modules_seen"]))
print(f"0.35s windows: {len(windows)}  arm-pass {res['windows_arm_pass']}"
      f"  arm-FAIL {res['windows_arm_fail']}  rate {res['arm_fail_rate']}")
print("fail reasons:", res["fail_reasons"])
