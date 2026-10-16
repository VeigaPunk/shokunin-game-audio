#!/usr/bin/env python3
"""r84-critic probe A — the r84 teardown unload predicate, live.

The r83 critic (F2) proved the shared `_gst_r81_sink_module_index`
predicate was a raw substring and destroyed a foreign nested module in a
real unload. The committed r84 tree ships an anchored regex + exact
field equality. This probe re-proves the current predicate on the
COMMITTED bytes with the r84 teardown path (`_gst_r81_unload_own`):

  a) r84c_a  vs r84c_a2   — nested name (the r83 destructive shape)
  b) r84c_ns_1 vs r84c_ns_12 — pid-prefix nesting (the r84 family's own
     exposure: r84a_ns_<pid> where one pid is a decimal prefix of the
     other)
  c) a mismatched query must unload NOTHING (not_listed)

Seat namespace r84c_* only; every loaded module unloaded by exact name
and verified gone. No tracked writes. TMPDIR under the lane.
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

SRC = Path("/home/vgpnk/Projects/shokunin/tmp/r84critic-src/corpus/fixtures")
sys.path.insert(0, str(SRC))
import measure_audio as M  # noqa: E402

PREFIX = "r84c"
OUT = Path(__file__).with_name("probeA-unload-anchor.json")


def modules():
    proc = subprocess.run(["pactl", "list", "modules", "short"],
                          capture_output=True, timeout=10)
    return proc.stdout.decode(errors="replace")


def load(name):
    proc = subprocess.run(
        ["pactl", "load-module", "module-null-sink", f"sink_name={name}",
         "sink_properties=device.description=" + name],
        capture_output=True, timeout=15)
    return {"rc": proc.returncode,
            "out": proc.stdout.decode(errors="replace").strip()}


def unload_by_name(name):
    idx = M._gst_r81_sink_module_index(name)
    if idx is None:
        return {"skipped": "not_listed"}
    proc = subprocess.run(["pactl", "unload-module", str(idx)],
                          capture_output=True, timeout=15)
    return {"index": idx, "rc": proc.returncode}


def main():
    rec = {"probe": "probeA-unload-anchor", "pid": os.getpid(),
           "loadavg": open("/proc/loadavg").read().split()[:3],
           "src_fixture_md5": M.__file__}
    names = [f"{PREFIX}_a", f"{PREFIX}_a2", f"{PREFIX}_ns_1",
             f"{PREFIX}_ns_12"]
    try:
        rec["loads"] = {n: load(n) for n in names}
        time.sleep(0.5)
        listing = modules()
        rec["modules_listed"] = [
            ln.strip() for ln in listing.splitlines()
            if PREFIX in ln]
        # --- (a) nested pair, the r83 destructive shape -----------------
        idx_a = M._gst_r81_sink_module_index(f"{PREFIX}_a")
        idx_a2 = M._gst_r81_sink_module_index(f"{PREFIX}_a2")
        rec["a"] = {"index_of_a": idx_a, "index_of_a2": idx_a2,
                    "distinct": idx_a is not None and idx_a != idx_a2}
        # fire the r84 teardown path with the CAPTURED id of `a`
        rec["a"]["unload"] = M._gst_r81_unload_own(
            idx_a, sink_name=f"{PREFIX}_a")
        time.sleep(0.4)
        after = modules()
        rec["a"]["a_still_listed"] = f"sink_name={PREFIX}_a\n" in after or \
            f"sink_name={PREFIX}_a " in after
        rec["a"]["a2_survived"] = f"sink_name={PREFIX}_a2" in after
        # --- (b) pid-prefix nesting -------------------------------------
        idx_1 = M._gst_r81_sink_module_index(f"{PREFIX}_ns_1")
        idx_12 = M._gst_r81_sink_module_index(f"{PREFIX}_ns_12")
        rec["b"] = {"index_of_ns_1": idx_1, "index_of_ns_12": idx_12}
        # the mismatched query: unload "ns_1" while only ns_12-like names
        # are protected by the anchor -> must unload NOTHING
        rec["b"]["unload_mismatched"] = M._gst_r81_unload_own(
            idx_12, sink_name=f"{PREFIX}_ns_1")
        time.sleep(0.3)
        after2 = modules()
        rec["b"]["ns_12_survived_mismatch"] = \
            f"sink_name={PREFIX}_ns_12" in after2
        rec["b"]["unload_ns_12"] = M._gst_r81_unload_own(
            idx_12, sink_name=f"{PREFIX}_ns_12")
    finally:
        rec["cleanup"] = {n: unload_by_name(n) for n in names}
        time.sleep(0.4)
        left = [ln.strip() for ln in modules().splitlines() if PREFIX in ln]
        rec["residue"] = left
        rec["sinks_left"] = [ln.strip() for ln in subprocess.run(
            ["pactl", "list", "sinks", "short"], capture_output=True,
            timeout=10).stdout.decode(errors="replace").splitlines()
            if PREFIX in ln]
    OUT.write_text(json.dumps(rec, indent=2) + "\n")
    print(json.dumps(rec, indent=2))


if __name__ == "__main__":
    main()
