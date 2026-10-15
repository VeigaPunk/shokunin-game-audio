#!/usr/bin/env python3
"""Smoke: harness self-test before any frontier leg."""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r78p as H

out = {"toolchain": H.toolchain()}

H.make_tone(dur=2.0)
out["tone"] = H.peaks(H.TONE)

rc, out_pl, err, wall, to = H.sh(["pw-link", "-l"], timeout=6)
out["pwlink_raw_head"] = out_pl.decode(errors="replace").splitlines()[:14]

mid, rc2, err2 = H.load_null(H.NS)
out["ns_load"] = {"module": mid, "rc": rc2, "err": err2}
mid2, rc3, err3 = H.load_null(H.NS2)
out["ns2_load"] = {"module": mid2, "rc": rc3, "err": err3}
time.sleep(0.4)

# baseline: tone into NS, witnesses on NS/NS2/SPDIF
mon = H.Monitors()
leg = H.one_leg(mon, ["pw-play", "-P", "node.name=r78p_smoke", "--target",
                      H.NS, H.TONE], "r78p_smoke", probe_at=0.8, timeout=8)
out["baseline_leg"] = leg
out["witness_now"] = mon.result()

H.unload(mid)
H.unload(mid2)
out["after_unload_pactl"] = H.sh(["pactl", "list", "sinks", "short"])[1].decode()
H.save("probe-smoke-r78p.json", out)
print(json.dumps({k: out[k] for k in ("tone", "ns_load", "baseline_leg")},
                 indent=1)[:3000])
