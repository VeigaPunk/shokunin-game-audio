#!/bin/bash
# r93 scout — sequential stage battery (single lane; no sibling probe overlap by design)
cd "$(dirname "$0")"
for st in portmap amp freq stereo modes window history peaks lufs2gain edge refflat; do
  echo "=== $st $(date -u +%H:%M:%S) ==="
  python3 probes/r93driver.py "$st" 3 > "runs/$st.log" 2>&1
  echo "rc=$? $(date -u +%H:%M:%S)"
  tail -3 "runs/$st.log"
done
echo "ALL DONE $(date -u +%H:%M:%S)"
