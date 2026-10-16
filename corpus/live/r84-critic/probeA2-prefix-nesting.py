#!/usr/bin/env python3
"""r84-critic probe A2 — pid-prefix nesting under the anchored predicate.

The r84 family's own exposure: `r84a_ns_<pid>` / `r84a_ns2_<pid>`; two
family runs whose pids are decimal prefixes of each other (e.g. 351263
vs 3512630) put `sink_name=r84a_ns_351263` as a raw substring of
`sink_name=r84a_ns_3512630`. The committed predicate must NOT answer a
`r84c_ns_1` query with the `r84c_ns_12` module. Only the longer name is
loaded here, so the query must return None and the teardown path must
unload nothing.
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
OUT = Path(__file__).with_name("probeA2-prefix-nesting.json")


def modules():
    return subprocess.run(["pactl", "list", "modules", "short"],
                          capture_output=True, timeout=10
                          ).stdout.decode(errors="replace")


def main():
    rec = {"probe": "probeA2-prefix-nesting", "pid": os.getpid()}
    long_name = f"{PREFIX}_ns_12"
    short_name = f"{PREFIX}_ns_1"
    try:
        proc = subprocess.run(
            ["pactl", "load-module", "module-null-sink",
             f"sink_name={long_name}"], capture_output=True, timeout=15)
        rec["load"] = {"rc": proc.returncode,
                       "out": proc.stdout.decode(errors="replace").strip()}
        time.sleep(0.4)
        rec["modules_listed"] = [ln.strip() for ln in modules().splitlines()
                                 if PREFIX in ln]
        rec["index_query_short_name"] = M._gst_r81_sink_module_index(
            short_name)
        rec["index_query_long_name"] = M._gst_r81_sink_module_index(
            long_name)
        rec["unload_via_short_name"] = M._gst_r81_unload_own(
            None, sink_name=short_name)
        time.sleep(0.3)
        rec["long_name_survived"] = long_name in modules()
    finally:
        idx = M._gst_r81_sink_module_index(long_name)
        rec["cleanup"] = subprocess.run(
            ["pactl", "unload-module", str(idx)] if idx is not None
            else ["true"], capture_output=True, timeout=15).returncode
        time.sleep(0.3)
        rec["residue"] = [ln.strip() for ln in modules().splitlines()
                          if PREFIX in ln]
    OUT.write_text(json.dumps(rec, indent=2) + "\n")
    print(json.dumps(rec, indent=2))


if __name__ == "__main__":
    main()
