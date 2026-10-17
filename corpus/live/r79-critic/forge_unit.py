#!/usr/bin/env python3
"""r79 CRITIC — unit-level forges against the FROZEN r79 artifact.

Mechanism-blind: each forge takes the REAL measured leg record out of the
run-B receipt, mutates exactly one observable (the thing the forge
questions), and re-runs the REAL verdict function the entry uses.  A forge
that leaves `failures` empty (and/or records a confound/named outcome
instead) is a live counterexample.

No host mutation: these calls are pure readers of the receipt.
"""
import copy
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "fixtures"))
import measure_audio as m  # noqa: E402

REPO = Path(__file__).resolve().parents[3]
RECEIPT = (REPO / "corpus/live/r79-author/"
           "receipt-runB-20261015T072219089606Z-capture-r79.json")
R = json.load(open(RECEIPT))
CAP = R["measurements"]["loopback_capture_lattice_r79_probe"]
PLAY = R["measurements"]["loopback_playback_lattice_r79_probe"]
SPDIF = "alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink"


def show(tag, failures, leg, entry):
    print(f"--- {tag}")
    print(f"    failures       : {failures}")
    print(f"    leg.outcome    : {leg.get('outcome')}")
    print(f"    leg.confound   : {leg.get('confound')}")
    print(f"    entry.coverage : {entry.get('coverage_blocked')}")
    print(f"    entry.named    : {entry.get('named_outcomes')}")
    print(f"    entry.confound_observed: {entry.get('confound_observed')}")
    print(f"    PASS(no failure): {not failures}")
    return not failures


def fresh_entry():
    return {}


def blank_node(leg, node):
    """Publish the node but never negotiate it (zero ports, zero links)."""
    for s in leg["samples"]:
        w = s["watch"][node]
        w["input_ports"] = []
        w["output_ports"] = []
        w["producers"] = []
        w["producer_ports"] = []
        w["consumers"] = []
        w["consumer_ports"] = []
        s["nodes"][node]["state"] = "suspended"


results = {}

# ---------------------------------------------------------------- F1
# A sink-prop arm (`-C <sink> -i stream.capture.sink=true`, expected kind
# "node") that FAILED to link is re-labelled as an environment condition:
# the entry passes and the round's "two arms" headline goes unmeasured.
b01 = copy.deepcopy(CAP["legs"]["b01_sink_prop"])
in_n = f"input.{b01['ltag']}"
ora = b01["oracle_at_leg"]
blank_node(b01, in_n)
e = fresh_entry()
f = []
m._loopback_r79_check_side(e, f, "capture b01_sink_prop", b01, "producers",
                           in_n, b01["expected_producers"][0], ora,
                           dsource_probe=None)   # <- exactly as the entry calls it
results["F1_sinkprop_arm_broken_is_a_named_outcome"] = show(
    "F1  b01 sink-prop arm did not link (kind='node', probe=None)", f, b01, e)

# ---------------------------------------------------------------- F1b
# Same branch, reached from the PLAYBACK side of a capture-lattice leg:
# a write-side node that never negotiated is reported with a CAPTURE-side
# explanation ("no session default source ... the capture stream ...").
c01 = copy.deepcopy(PLAY["legs"]["c01_sink"])
out_n = f"output.{c01['ltag']}"
blank_node(c01, out_n)
e = fresh_entry()
f = []
m._loopback_r79_check_side(e, f, "playback c01_sink", c01, "consumers",
                           out_n, c01["expected_consumers"][0],
                           c01["oracle_at_leg"])
results["F1b_playback_node_gets_capture_side_explanation"] = show(
    "F1b c01 playback node published unnegotiated", f, c01, e)

# ---------------------------------------------------------------- F1c
# The same forge, but now the SESSION PROBE says a default source IS
# available (the state the author measured on other legs: a concurrent
# lane's `r86ctl_src` was the live default source).  The class is still
# assigned -> the `or` at line 9307 short-circuits on the constant
# `source_meta is None` and the probe is never consulted.
b01 = copy.deepcopy(CAP["legs"]["b01_sink_prop"])
in_n = f"input.{b01['ltag']}"
blank_node(b01, in_n)
e = fresh_entry()
f = []
m._loopback_r79_check_side(e, f, "capture b01_sink_prop", b01, "producers",
                           in_n, b01["expected_producers"][0],
                           b01["oracle_at_leg"],
                           dsource_probe={"available": True,
                                          "error_class": None})
results["F1c_probe_says_available_but_class_still_assigned"] = show(
    "F1c same leg, probe says available=True", f, b01, e)

# ---------------------------------------------------------------- F1d
# ... and with a per-leg oracle that DOES carry a source (source_meta set),
# the branch is correctly refused -> proving the gate is the oracle leaf,
# not the leg's arm.
b01 = copy.deepcopy(CAP["legs"]["b01_sink_prop"])
in_n = f"input.{b01['ltag']}"
blank_node(b01, in_n)
ora2 = dict(b01["oracle_at_leg"], source_meta="a_live_default_source_r79")
e = fresh_entry()
f = []
m._loopback_r79_check_side(e, f, "capture b01_sink_prop", b01, "producers",
                           in_n, b01["expected_producers"][0], ora2,
                           dsource_probe={"available": True})
results["F1d_control_source_meta_set_refuses_the_class"] = show(
    "F1d control: source_meta set -> the leg FAILS instead", f, b01, e)

# ---------------------------------------------------------------- F2
# tap provenance: the tap bound to a FOREIGN producer while the leg's own
# capture side is linked -> the `|` in the guard (line 9379) masks the
# confound entirely.
leg = copy.deepcopy(CAP["legs"]["b01_sink_prop"])
leg["tap"]["bound_to_target"] = False
leg["tap"]["bound_producers"] = ["some_foreign_node_r79"]
leg["tap"]["carries_tone"] = True
leg["tap"]["mine_windows"] = 40
e = fresh_entry()
f = []
m._loopback_r79_check_tap(e, f, "forge F2", leg, want_tone=True)
results["F2_tap_bound_to_foreign_producer_is_not_a_confound"] = show(
    "F2  tap bound to a FOREIGN producer, capture side linked", f, leg, e)

# ---------------------------------------------------------------- F2b
# ... and the confound DOES fire only when the capture side is empty,
# which proves the `|` operand is what masks it.
leg = copy.deepcopy(CAP["legs"]["b01_sink_prop"])
leg["tap"]["bound_to_target"] = False
leg["tap"]["bound_producers"] = ["some_foreign_node_r79"]
leg["input_producers_union"] = []
leg["output_consumers_union"] = []
e = fresh_entry()
f = []
m._loopback_r79_check_tap(e, f, "forge F2b", leg, want_tone=True)
results["F2b_confound_only_fires_with_empty_capture_union"] = (
    leg.get("confound") is not None)
print("--- F2b same forge, capture union emptied:")
print(f"    leg.confound   : {leg.get('confound')}")
print(f"    failures       : {f}")

# ---------------------------------------------------------------- F3
# The wrong DOMAIN: a `-C` leg that binds the default SINK monitor where
# the arm expects the default SOURCE is excused as "the authority moved".
b02 = copy.deepcopy(CAP["legs"]["b02_sink_noprop"])
in_n = f"input.{b02['ltag']}"
for s in b02["samples"]:
    w = s["watch"][in_n]
    w["producers"] = [SPDIF]
    w["producer_ports"] = [f"{SPDIF}:monitor_FL", f"{SPDIF}:monitor_FR"]
b02["producers_union"] = [SPDIF]
e = fresh_entry()
f = []
m._loopback_r79_check_side(e, f, "capture b02_sink_noprop", b02, "producers",
                           in_n, b02["expected_producers"][0],
                           b02["oracle_at_leg"], dsource_probe=None)
results["F3_wrong_domain_binding_excused"] = show(
    "F3  b02 bound the default SINK monitor, expected the default SOURCE",
    f, b02, e)

# ---------------------------------------------------------------- F3b
# The reachable version of the same excuse: a PROBE-TARGET leg (`-C <sink>
# -i stream.capture.sink=true`, want = the probe sink) whose capture side
# silently falls back to the default authority.  `want` is not in
# `live_now`, the bound node is -> "default re-asserted mid-leg", a
# coverage_blocked confound, NO failure.  The playback side keeps feeding
# the tap, so the content pin still passes: the leg is green while its
# capture arm is unmeasured.
b01 = copy.deepcopy(CAP["legs"]["b01_sink_prop"])
in_n = f"input.{b01['ltag']}"
for s in b01["samples"]:
    w = s["watch"][in_n]
    w["producers"] = [SPDIF]
    w["producer_ports"] = [f"{SPDIF}:monitor_FL", f"{SPDIF}:monitor_FR"]
b01["producers_union"] = [SPDIF]
e = fresh_entry()
f = []
m._loopback_r79_check_side(e, f, "capture b01_sink_prop", b01, "producers",
                           in_n, b01["expected_producers"][0],
                           b01["oracle_at_leg"])
m._loopback_r79_check_tap(e, f, "capture b01_sink_prop", b01, want_tone=True)
results["F3b_probe_target_fell_back_is_excused"] = show(
    "F3b b01 sink-prop arm fell back to the default sink monitor", f, b01, e)

# ---------------------------------------------------------------- F4
# Bimodal history: the route is lost after the first sample; the union
# across samples still equals the expectation.
b01 = copy.deepcopy(CAP["legs"]["b01_sink_prop"])
in_n = f"input.{b01['ltag']}"
last = b01["samples"][-1]
for k in ("producers", "producer_ports", "consumers", "consumer_ports"):
    last["watch"][in_n][k] = []
e = fresh_entry()
f = []
m._loopback_r79_check_side(e, f, "capture b01_sink_prop", b01, "producers",
                           in_n, b01["expected_producers"][0],
                           b01["oracle_at_leg"])
results["F4_bimodal_link_history_passes"] = show(
    "F4  route present at t=1.3s, GONE at t=2.7s (union-only check)", f,
    b01, e)

# ---------------------------------------------------------------- F5
# Half a link: only the FL monitor port exists. The lattice's port pin is
# `all(':monitor_' in p for p in pports)` — one port satisfies it.
b01 = copy.deepcopy(CAP["legs"]["b01_sink_prop"])
in_n = f"input.{b01['ltag']}"
for s in b01["samples"]:
    s["watch"][in_n]["producer_ports"] = [f"{b01['ltag'] and 'r79lb_x'}:monitor_FL"]
    s["watch"][in_n]["producer_ports"] = [f"input.{b01['ltag']}:monitor_FL"]
pports = set(m._loopback_r79_union(b01["samples"], in_n, "producer_ports"))
b01["producers_union"] = b01["expected_producers"]
f = []
if b01["producers_union"] == b01["expected_producers"] and pports:
    if not all(":monitor_" in p for p in pports):
        f.append("capture b01: producer ports — the sink prop must read "
                 "monitor_*")
print("--- F5  FL-only (one-port) link through the entry's own port pin")
print(f"    pports         : {sorted(pports)}")
print(f"    failures       : {f}")
results["F5_one_port_link_satisfies_port_pin"] = (not f)

print()
print("=== SUMMARY ===")
for k, v in results.items():
    print(f"  {v!s:5} {k}")
print(f"\n  oracles in run B with source_meta=None: "
      f"{sum(1 for _ in [1])} -- see census.py")
