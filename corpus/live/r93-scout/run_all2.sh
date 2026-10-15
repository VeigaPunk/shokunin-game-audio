#!/bin/bash
cd "$(dirname "$0")"
for st in lufs2gain labels passthrough gating mix hist2 window; do
  echo "=== $st $(date -u +%H:%M:%S) ==="
  python3 probes/r93driver.py "$st" 3 > "runs/$st.log" 2>&1
  echo "rc=$? $(date -u +%H:%M:%S)"
  tail -2 "runs/$st.log"
done
echo "ALL2 DONE $(date -u +%H:%M:%S)"
