#!/bin/bash
cd "$(dirname "$0")"
for st in s1 s2 s3 s4 s5 s6; do
  echo "=== $st start $(date -u +%H:%M:%S) ==="
  python3 r90b_probe.py "$st" 3 > "runs/$st.log" 2>&1
  echo "=== $st rc=$? $(date -u +%H:%M:%S) ==="
  tail -2 "runs/$st.log"
done
echo "=== s7 cleanup $(date -u +%H:%M:%S) ==="
python3 r90b_probe.py s7 1 > runs/s7.log 2>&1
echo "=== s7 rc=$? $(date -u +%H:%M:%S) ==="
tail -2 runs/s7.log
echo "ALL DONE $(date -u +%H:%M:%S)"
