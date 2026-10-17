#!/usr/bin/env python3
"""r81-baseline receipt collector/validator.

battery.sh now copies each receipt inline (the r80 fault is fixed at source),
so this script is the cross-check: for every `RECEIPT <mode> <stamp> <path>`
line in runs-<x>/commands.log it verifies (a) the recorded canonical path
exists inside the frozen tree, (b) its parent dir basename equals the
recorded stamp, (c) runs-<x>/<mode>.receipt.json is byte-equal to it, and
(d) the receipt's own `mode` field matches. Prints the sha256 table.
"""
import json, sys
from hashlib import sha256
from pathlib import Path

ROOT = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
OUT = ROOT / "corpus/live/r81-baseline"
SUFFIX = {"normal": "normal", "capture-r78": "capture-r78",
          "capture-r79": "capture-r79", "module-r80": "module-r80"}

def main():
    bad = 0
    for leg in ("a", "b"):
        d = OUT / f"runs-{leg}"
        log = d / "commands.log"
        if not log.exists():
            print(f"!! no commands.log for {leg}")
            bad += 1
            continue
        for line in log.read_text().splitlines():
            if not line.startswith("RECEIPT "):
                continue
            parts = line.split()
            if len(parts) < 4:
                print(f"!! {leg}: malformed RECEIPT line: {line}")
                bad += 1
                continue
            mode, stamp, path = parts[1], parts[2], parts[3]
            src = Path(path)
            if not src.exists():
                print(f"!! {leg}/{mode}: canonical receipt missing: {src}")
                bad += 1
                continue
            if src.parent.name != stamp:
                print(f"!! {leg}/{mode}: stamp mismatch {stamp} vs {src.parent.name}")
                bad += 1
            dst = d / f"{mode}.receipt.json"
            if not dst.exists():
                print(f"!! {leg}/{mode}: inline copy missing: {dst}")
                bad += 1
                continue
            h_src = sha256(src.read_bytes()).hexdigest()
            h_dst = sha256(dst.read_bytes()).hexdigest()
            same = "OK " if h_src == h_dst else "DIFF"
            if h_src != h_dst:
                bad += 1
            try:
                m = json.loads(dst.read_text())["mode"]
            except Exception as e:  # noqa: BLE001
                m = f"<unreadable: {e}>"
            exp = SUFFIX[mode]
            modeok = "OK " if str(m).endswith(exp) else "MODE!"
            if not str(m).endswith(exp):
                bad += 1
            print(f"{leg} {mode:12s} {stamp}  {h_dst[:16]}…  copy={same} mode={modeok} ({m})")
            print(f"     src={src}")
    print(f"collector_faults={bad}")

if __name__ == "__main__":
    main()
