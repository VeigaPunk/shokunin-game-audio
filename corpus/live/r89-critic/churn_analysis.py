#!/usr/bin/env python3
"""r89 critic: corrected sliding-window analysis of churn.json.

MAPPING (important, and the reason this file exists): the committed
`x_foot` arm takes c0 (before), spawns its own `pw-profiler -J -n 30`
foot, sleeps 0.35 s, then takes c1 (during). The arm requires
`c1 - c0 == 1`. The seat's own foot contributes exactly +1, so the arm
passes iff the BACKGROUND pw-profiler client count is UNCHANGED over the
bracket (background delta == 0). The raw poller in churn.py samples the
background only (it spawns no profiler client), so:
    arm_pass  <=>  pwprof_delta == 0  AND  node_delta == 0
(churn.py's own `arm_pass` field used delta == 1 — that is the
own-foot-included form and is WRONG for the background series; this file
is the corrected read.)
"""
import json
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent
raw = json.loads((OUT / "churn.json").read_text())
w = raw["window_detail"]

res = {
    "source": "churn.json",
    "mapping": "arm_pass <=> background pwprof_delta == 0 and node_delta == 0",
    "windows": len(w),
    "pwprof_delta_distribution": dict(Counter(x["pwprof_delta"] for x in w)),
    "node_delta_distribution": dict(Counter(x["node_delta"] for x in w)),
    "windows_arm_pass": sum(1 for x in w
                            if x["pwprof_delta"] == 0 and x["node_delta"] == 0),
    "windows_arm_fail": sum(1 for x in w
                            if not (x["pwprof_delta"] == 0
                                    and x["node_delta"] == 0)),
    "fail_client_half_only": sum(1 for x in w if x["pwprof_delta"] != 0),
    "fail_node_half_only": sum(1 for x in w if x["node_delta"] != 0),
    "samples": raw["usable_samples"],
    "duration_s": raw["duration_s"],
    "pwprof_client_counts_seen": raw["pwprof_client_counts"],
    "node_counts_min_max": raw["node_counts"],
    "r89a_nodes_seen": raw["r89a_nodes_seen"],
    "r89a_modules_seen": len(raw["r89a_modules_seen"]),
}
res["arm_fail_rate"] = round(res["windows_arm_fail"] / res["windows"], 3)
res["client_half_fail_rate"] = round(res["fail_client_half_only"]
                                     / res["windows"], 3)
res["node_half_fail_rate"] = round(res["fail_node_half_only"]
                                   / res["windows"], 3)
(OUT / "churn-analysis.json").write_text(json.dumps(res, indent=2) + "\n")
print(json.dumps(res, indent=2))
