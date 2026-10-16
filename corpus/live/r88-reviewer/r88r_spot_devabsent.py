#!/usr/bin/env python3
"""r88 reviewer SPOT — fault-inject the bz_device arm.

Falsifiable claim: "btabs_bluez_r88_entry() FAILS when the busctl device
record is absent."  Method: import the frozen committed fixture, replace
only the `busctl tree` call with a tree that carries the hci0 adapter but
NO dev_* device path, then run the real entry against the live host.
If the entry returns failures == [] with devices == [], the arm is
fail-open (evidence-only: the green receipts do contain the real device).

Creates/cleans only its own r88a_<pid> null sink (the entry's own
teardown).  TMPDIR must be set by the caller.
"""
import importlib.util
import json
import os
import sys

FX = ("/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/"
      "r88-reviewer/tree/corpus/fixtures/measure_audio.py")
spec = importlib.util.spec_from_file_location("fx", FX)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

orig = m._btwit_r88_busctl


def patched(*args, **kwargs):
    if args and args[0] == "tree":
        return {"argv": "busctl --system tree org.bluez",
                "exit_code": 0, "signal": None, "killed_at_bound": False,
                "wall_s": 0.0, "stdout_head": ["/org/bluez/hci0"],
                "stdout": "/org/bluez/hci0\n",
                "stdout_bytes": 17, "stderr_head": [], "stderr": "",
                "stderr_bytes": 0, "error_class": None, "error_hit": None}
    return orig(*args, **kwargs)


m._btwit_r88_busctl = patched
entry = m.btabs_bluez_r88_entry()
out = {
    "pid": os.getpid(),
    "devices": entry["legs"]["bz_device"]["devices"],
    "adapters": entry["legs"]["bz_tree"]["adapters"],
    "failures": entry["failures"],
    "coverage_blocked": entry.get("coverage_blocked"),
    "sinks_gone": entry.get("sinks_gone"),
    "own_nodes_after": entry.get("own_nodes_after"),
    "loadavg": entry.get("loadavg"),
}
print(json.dumps(out, indent=1))
