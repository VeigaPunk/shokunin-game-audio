#!/bin/bash
cd "$(dirname "$0")"
for st in edge modes passthrough l2gcheck ctlgrammar labels2; do
  echo "=== $st $(date -u +%H:%M:%S) ==="
  python3 probes/r93driver.py "$st" 3 > "runs/$st.log" 2>&1
  echo "rc=$? $(date -u +%H:%M:%S)"
  tail -2 "runs/$st.log"
done
echo "ALL3 DONE $(date -u +%H:%M:%S)"
