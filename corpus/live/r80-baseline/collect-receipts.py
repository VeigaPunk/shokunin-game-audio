#!/usr/bin/env python3
"""Collect each battery run's canonical receipt into its runs-<x>/ dir.

battery.sh appends EXIT= to the stdout capture before parsing it, so its
inline copy is skipped; this collector is the authoritative mapping. For
every `CMD <ts> <mode>` line in runs-<x>/commands.log it takes the
earliest canonical `corpus/live/runs/<stamp>-<suffix>/measurements.json`
with stamp >= ts (stamps are UTC, so a lexicographic compare is exact),
claims it once, copies it beside the log, and records the sha256.
"""
import json, re, shutil, sys
from hashlib import sha256
from pathlib import Path

ROOT = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
OUT = ROOT / "corpus/live/r80-baseline"
RUNS = ROOT / "corpus/live/runs"
SUFFIX = {"normal": "normal", "capture-r78": "capture-r78",
          "capture-r79": "capture-r79"}
CMD_RE = re.compile(r"^CMD (\S+) (\S+)")

def main():
    claimed = set()
    for leg in ("a", "b"):
        d = OUT / f"runs-{leg}"
        log = (d / "commands.log")
        if not log.exists():
            continue
        shas = []
        for line in log.read_text().splitlines():
            m = CMD_RE.match(line)
            if not m:
                continue
            ts, mode = m.group(1), m.group(2)
            # commands.log stamps are ISO (2026-10-15T08:47:28Z); receipt dirs
            # are 20261015T084728...Z -> normalise before comparing
            ts = ts.replace("-", "").replace(":", "")
            suffix = SUFFIX.get(mode)
            if suffix is None:
                continue
            cands = sorted(
                p for p in RUNS.glob(f"*-{suffix}/measurements.json")
                if p.parent.name.split("-")[0] >= ts and str(p) not in claimed)
            if not cands:
                print(f"!! no canonical receipt for {leg}/{mode} (ts {ts})")
                continue
            src = cands[0]
            claimed.add(str(src))
            dst = d / f"{mode}.receipt.json"
            shutil.copyfile(src, dst)
            h = sha256(dst.read_bytes()).hexdigest()
            shas.append(f"{h}  {src}")
            print(f"{leg} {mode} <- {src.parent.name}  {h[:16]}…")
            # sanity: receipt mode field
            try:
                assert json.loads(dst.read_text())["mode"].endswith(suffix), \
                    f"mode mismatch in {dst}"
            except AssertionError as e:
                print(f"!! {e}")
        if shas:
            (d / "receipt-shas.txt").write_text("\n".join(shas) + "\n")

if __name__ == "__main__":
    main()
