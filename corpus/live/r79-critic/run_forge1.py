#!/usr/bin/env python3
"""Run the REAL `loopback_capture_lattice_r79_entry()` from the forge1
scratch copy and print the verdict surface."""
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "forge1_measure_audio", HERE / "forge1-measure_audio.py")
mod = importlib.util.module_from_spec(spec)
sys.modules["forge1_measure_audio"] = mod
spec.loader.exec_module(mod)

entry = mod.loopback_capture_lattice_r79_entry()
leg = entry["legs"]["b01_sink_prop"]
out = {
    "failures": entry.get("failures"),
    "coverage_blocked": entry.get("coverage_blocked"),
    "named_outcomes": entry.get("named_outcomes"),
    "confound_observed": entry.get("confound_observed"),
    "b01": {
        "outcome": leg.get("outcome"),
        "producers_union": leg.get("producers_union"),
        "expected_producers": leg.get("expected_producers"),
        "confound": leg.get("confound"),
        "target_object_lies": leg.get("target_object_lies"),
        "tap_carries_tone": (leg.get("tap") or {}).get("carries_tone"),
        "killed_at_bound": leg.get("killed_at_bound"),
        "exit_code": leg.get("exit_code"),
    },
    "b04_producers": entry["legs"]["b04_real_source"].get("producers_union"),
    "b09_producers": entry["legs"]["b09_prop_garbage_sinkprop"].get(
        "producers_union"),
    "own_nodes_after": entry.get("own_nodes_after"),
}
print(json.dumps(out, indent=1))
print("ENTRY_GREEN" if not entry.get("failures") else "ENTRY_RED")
