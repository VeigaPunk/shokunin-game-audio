#!/usr/bin/env bash
# healthy 3-run sequence: control1, candidate, control2 — all residue-pinned.
# Sequential (never concurrent: the r79 entries witness host state).
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"
mkdir -p receipts
run_side() {
  local side="$1" tag="$2"
  echo "=== $tag start $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
  ( cd "$side" && python3 ../pidpin.py 0 python3 corpus/fixtures/measure_audio.py \
      --probe-capture-r79 ) > "receipts/healthy-${tag}.stdout.json" \
      2> "receipts/healthy-${tag}.stderr.log"
  echo "EXIT=$?"
  ls -1t "$side/live/runs" | head -1 > "receipts/healthy-${tag}.dir"
  echo "=== $tag end $(date -u +%Y-%m-%dT%H:%M:%SZ) receipt=$(cat receipts/healthy-${tag}.dir) ==="
}
run_side control c1
run_side cand    d1
run_side control c2
echo SEQUENCE-DONE
