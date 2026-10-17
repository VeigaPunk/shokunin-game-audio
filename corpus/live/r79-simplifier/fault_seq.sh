#!/usr/bin/env bash
# fault-injection pairs: the entries' blocked paths, control vs candidate.
#   monitor   — the null-sink monitor gate reports "not ready" (real module
#               load + real unload; every entry's monitor block fires)
#   authority — no default sink/source readable + no shipped filter-chain.conf
#               (the six authority blocks and the fc base block fire)
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"
mkdir -p receipts
run_side() {
  local fault="$1" side="$2" tag="$3"
  echo "=== $tag start $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
  ( cd "$side" && python3 ../pidpin.py 0 python3 ../faultrun.py "$fault" \
      corpus/fixtures/measure_audio.py ) > "receipts/${tag}.stdout.json" \
      2> "receipts/${tag}.stderr.log"
  echo "EXIT=$?"
  ls -1t "$side/corpus/live/runs" | head -1 > "receipts/${tag}.dir"
  echo "=== $tag end $(date -u +%Y-%m-%dT%H:%M:%SZ) receipt=$(cat receipts/${tag}.dir) ==="
}
run_side monitor   control fault-monitor-control
run_side monitor   cand    fault-monitor-cand
run_side authority control fault-authority-control
run_side authority cand    fault-authority-cand
echo FAULTS-DONE
