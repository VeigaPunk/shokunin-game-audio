#!/usr/bin/env python3
"""Byte-identity of the r82 battery receipts against every landed receipt
of the same mode.

For each mode, the reference set is every `corpus/live/runs/*-<mode>/
measurements.json` in the WORKTREE (tracked + untracked = everything a
prior seat actually landed), plus the r82 battery's own two receipts. A
fresh receipt is reported byte-identical iff its sha256 appears in the
prior set; the matching prior dirs are named.
"""
import json
from hashlib import sha256
from pathlib import Path

ROOT = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
OUT = ROOT / "corpus/live/r82-baseline"
RUNS = ROOT / "corpus/live/runs"
MODES = ["normal", "capture-r78", "capture-r79", "module-r80"]

def h(p):
    return sha256(Path(p).read_bytes()).hexdigest()

def main():
    print("# byte-identity: fresh receipt sha vs every landed receipt of the same mode")
    for mode in MODES:
        priors = {}
        for p in sorted(RUNS.glob(f"*-{mode}/measurements.json")):
            priors.setdefault(h(p), []).append(p.parent.name)
        print(f"\n## {mode}: {len(priors)} distinct prior receipt bytes "
              f"across {sum(len(v) for v in priors.values())} landed receipts")
        for leg in ("a", "b"):
            fresh = OUT / f"runs-{leg}" / f"{mode}.receipt.json"
            if not fresh.exists():
                print(f"  runs-{leg}: (missing)")
                continue
            fh = h(fresh)
            match = priors.get(fh)
            if match:
                newest = max(match)
                print(f"  runs-{leg}: {fh[:16]}… BYTE-IDENTICAL to "
                      f"{len(match)} landed receipt(s), newest {newest}")
            else:
                print(f"  runs-{leg}: {fh[:16]}… no prior byte match")

if __name__ == "__main__":
    main()
