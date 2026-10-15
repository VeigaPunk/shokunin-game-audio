#!/usr/bin/env python3
"""r78b p0 — env snapshot + harness smoke (honored vs garbage leg)."""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r78b_lib import *

out = {"seat": "r78-boundary", "ts": time.time(),
       "env": foreign_note(),
       "pre_default": get_default_sink(),
       "pre_meta_keys": list(metadata_default()[0].keys())}

# hygiene: drop any leaked r78b sinks from a crashed earlier run
out["pre_cleanup"] = unload_all_mine()

make_tone(TONE, dur=1.8)
m1, rc1, e1 = load_null(NS, "r78b probe A")
time.sleep(0.4)
m2, rc2, e2 = load_null(NS2, "r78b probe B")
time.sleep(0.6)
out["null_sinks"] = {"ns": m1, "ns2": m2}
out["ns_serial"] = serial_of(NS)
out["ns2_serial"] = serial_of(NS2)
out["spdif_serial"] = serial_of(S_SPDIF)
out["line_serial"] = serial_of(LINE)
out["node_states"] = {n: node_state(n) for n in (NS, NS2, S_SPDIF, S_SPK)}

# leg A: honored target
out["leg_honored"] = pwplay("r78bsm_a", ["--target", NS, TONE],
                          timeout=10.0)
# leg B: garbage target -> should fall back to default sink (SPDIF)
out["leg_garbage"] = pwplay("r78bsm_b", ["--target", "no_such_sink_r78b", TONE],
                          timeout=10.0)

out["post_default"] = get_default_sink()
save("probe-p0-smoke-r78b.json", out)
print(json.dumps({k: out[k] for k in
                  ("null_sinks", "ns_serial", "node_states",
                   "pre_default")}, indent=1, default=str))
for leg in ("leg_honored", "leg_garbage"):
    l = out[leg]
    print(leg, "rc", l["rc"], "wall", l["wall_s"], "carried", l["carried"],
          "mid.links", l["mid"].get("links"))
