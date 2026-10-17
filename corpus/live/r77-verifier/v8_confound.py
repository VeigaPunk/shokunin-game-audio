#!/usr/bin/env python3
"""r77 verifier — empirical confirmation of N3's mechanism.

Hypothesis: with a FOREIGN pw-record client already linked to the default
sink monitor, a pw-record cell that targets the same node yields an EMPTY
`pw-link` delta (the pre-spawn snapshot already contains the identical
producer set, so the difference cancels) while its content witness still
carries the tone — i.e. the capture consumed the node, and only the
differenced topology witness was blinded. That is what turns a contended
host into a HARD failure instead of the arm's intended `ambiguous_topology`
confound.

Bounded: one foreign capture (5 s, 960044 B) + one 2 s cell (384044 B).
"""
import importlib.util
import json
import signal
import subprocess
import tempfile
import time
from pathlib import Path

_here = Path(__file__).with_name("v1_lattice.py")
_spec = importlib.util.spec_from_file_location("v1", _here)
v1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v1)

OUT = v1.OUT


def main():
    sink = v1.default_sink()
    entry = {"probe": "r77-verifier N3 mechanism — foreign client cancels "
                      "the differenced topology witness",
             "default_sink": sink, "failures": []}
    with tempfile.TemporaryDirectory(prefix="r77v-confound-") as tmp:
        foreign = subprocess.Popen(
            ["pw-record", "-P", "stream.capture.sink=true", "--target", sink,
             "-n", "240000", "--rate", "48000", "--channels", "2",
             "--format", "s16", str(Path(tmp) / "foreign.wav")],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            start_new_session=True)
        time.sleep(0.6)
        entry["raw_table_consumed_before_cell"] = v1.consumed(v1.link_map())
        entry["cell"] = v1.cell("confound_default_sink", sink, True, tmp,
                                sink, True)
        entry["raw_table_consumed_after_cell"] = v1.consumed(v1.link_map())
        if foreign.poll() is None:
            foreign.terminate()
        try:
            foreign.wait(timeout=5)
        except subprocess.TimeoutExpired:
            import os
            os.killpg(foreign.pid, signal.SIGKILL)
            foreign.wait()
        entry["foreign_exit"] = foreign.returncode
    f = entry["failures"]
    cell = entry["cell"]
    if entry["raw_table_consumed_before_cell"] != [sink]:
        f.append(f"the foreign client was not linked to {sink} before the "
                 f"cell — the experiment did not set up "
                 f"(got {entry['raw_table_consumed_before_cell']})")
    if cell.get("consumed_nodes") != []:
        f.append(f"expected the differenced witness to be EMPTY under a "
                 f"foreign client on the same node, got "
                 f"{cell.get('consumed_nodes')}")
    if cell.get("file", {}).get("carries_tone") is not True:
        f.append("the cell's content witness must still show the tone — the "
                 "capture did consume the fallback")
    if cell.get("file", {}).get("bytes") != 384044:
        f.append(f"expected a full 384044 B capture, got "
                 f"{cell.get('file', {}).get('bytes')}")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "v8_confound.json").write_text(json.dumps(entry, indent=2) + "\n")
    print(json.dumps({"receipt": str(OUT / "v8_confound.json"),
                      "failures": entry["failures"],
                      "cell_consumed": cell.get("consumed_nodes"),
                      "cell_tone": cell.get("file", {}).get("carries_tone"),
                      "raw_before": entry["raw_table_consumed_before_cell"]}))


if __name__ == "__main__":
    main()
