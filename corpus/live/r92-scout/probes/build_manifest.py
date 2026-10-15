#!/usr/bin/env python3
"""Build manifest.sha256 + RECEIPTS.md for corpus/live/r92-scout/."""
import hashlib
import os
import sys
import time

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "manifest.sha256")
REC = os.path.join(HERE, "RECEIPTS.md")


def sha(p, n=1 << 20):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while True:
            b = f.read(n)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def walk(root):
    out = []
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d != "__pycache__"]
        for f in sorted(fn):
            p = os.path.join(dp, f)
            out.append(p)
    return sorted(out)


def main():
    files = []
    for p in walk(HERE):
        rel = os.path.relpath(p, HERE)
        if rel in ("manifest.sha256", "RECEIPTS.md"):
            continue
        files.append((rel, os.path.getsize(p), sha(p)))
    with open(OUT, "w") as f:
        for rel, size, h in files:
            f.write("%s  %s  %d\n" % (h, rel, size))
    total = sum(s for _, s, _ in files)
    lines = [
        "# r92-scout receipts index",
        "",
        "Seat: SCOUT (leaf), round 92. Surface: **`libpipewire-module-filter-chain`**",
        "(PipeWire 1.6.8 SPA filter-graph host) + `wpexec` as the script-side loader.",
        "",
        "Generated %s. %d files, %.2f MB. Every path below is untracked scratch; "
        "nothing outside `corpus/live/r92-scout/` was written except the round report."
        % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), len(files), total / 1e6),
        "",
        "## Receipts (JSON) — one per stage, each leg triple-bounded",
        "",
        "| file | stage | what it holds |",
        "| --- | --- | --- |",
        "| `runs/f0/receipt.json` | f0 | loader feasibility, load shape, lifecycle (nodes die with pw-cli) |",
        "| `receipts/f1_ports.json` | f1 | exact port names of every object; link-shape matrix |",
        "| `receipts/f2_e2e.json` | f2 | end-to-end hop matrix + the suspended negative control |",
        "| `receipts/f3_driver.json` | f3 | driver law S1-S4 (`node.passive`, class mismatch) |",
        "| `receipts/v2_links.json` | links | `links=[...]` grammar, quoted vs unquoted port names |",
        "| `receipts/v2_labels.json` | labels | **measured** builtin-label inventory (not strings) |",
        "| `receipts/v2_dsp.json` | dsp | transfer function, 17 graphs x 3 reps, pre/post dual tap (v1 1-rep copy kept as `receipts/dsp.json`) |",
        "| `receipts/v2_ir.json` | ir | impulse response: convolver / delay, delta stimulus |",
        "| `receipts/v2_clamp.json` | clamp | control-value clamp law |",
        "| `receipts/v2_absent.json` | absent | ladspa / lv2 / sofa / ffmpeg / ebur128 classes |",
        "| `receipts/v2_configs.json` | configs | the 12 shipped `filter-chain/*.conf`, load matrix |",
        "| `receipts/shape.json` | shape | v1 load-shape census (superseded by v2) |",
        "| `receipts/f4_wpexec.json` | wpexec | interpreter legs W1-W8 + residue law |",
        "",
        "## Probes",
        "",
        "| file | role |",
        "| --- | --- |",
        "| `probes/pwlib.py` | own bounded runner (killpg + wall cap + byte cap), own synth, own DFT/biquad reference |",
        "| `probes/driver.py` | v1 driver (superseded) |",
        "| `probes/driver2.py` | v2 rig: single-driver topology + pre/post dual tap |",
        "| `probes/f0_load.py` | loader feasibility |",
        "| `probes/f1_ports.py` | port/link census |",
        "| `probes/f2_e2e.py` | hop matrix |",
        "| `probes/f3_driver.py` | driver-law arms S1-S4 |",
        "| `probes/f4_wpexec.py` | wpexec legs |",
        "| `probes/audit.py` | teardown audit |",
        "",
        "## Sources read (not written by this seat)",
        "",
        "`sources/READ-SOURCES.sha256` — sha256 of the 19 on-disk files this seat read",
        "as sources (1.6.8 filter-chain man page, `wpexec` man page, the 12 shipped",
        "`filter-chain/*.conf`, `filter-chain.conf`, the two official WirePlumber",
        "examples, and the two Lua scripts `linking/rescan.lua`,",
        "`node/filter-graph.lua`).",
        "",
        "## Notes",
        "",
        "- `scratch/` holds the stimuli (own synth) and the captured WAVs referenced by the",
        "  receipts. `runs/v2_all.log` is the full stage log.",
        "- No sibling fixture (`corpus/fixtures/measure_audio.py`) was read, imported or executed.",
        "- Teardown: every mutating leg unloads its own module by index verified against the",
        "  seat name; the final sweep in `driver2.py` asserts zero r92s nodes, modules and processes.",
        "",
    ]
    with open(REC, "w") as f:
        f.write("\n".join(lines))
    print("manifest: %d files, %.2f MB" % (len(files), total / 1e6))
    print("receipts: %s" % REC)


if __name__ == "__main__":
    main()
