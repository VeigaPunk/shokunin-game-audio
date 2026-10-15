#!/bin/bash
# r85 boundary driver — sequential stages (single lane). Every stage is
# seat-owned; hogs are started/stopped inside the python stages.
cd "$(dirname "$0")" || exit 1
export PYTHONDONTWRITEBYTECODE=1
echo "DRIVER START $(date -u +%H:%M:%S)"
for st in b2 b3 b4 b5 b6 b7 b8 b9; do
  echo "=== $st $(date -u +%H:%M:%S) ==="
  python3 -B r85b_probe.py "$st" > "runs/stage-$st.log" 2>&1
  echo "rc=$? $(date -u +%H:%M:%S)"
  tail -4 "runs/stage-$st.log"
done
echo "=== cleanup $(date -u +%H:%M:%S) ==="
python3 -B r85b_probe.py cleanup > runs/stage-cleanup.log 2>&1
echo "rc=$?"
tail -3 runs/stage-cleanup.log
python3 -B r85b_probe.py b0 > runs/stage-b0final.log 2>&1
echo "rc=$?"
tail -2 runs/stage-b0final.log
echo "DRIVER DONE $(date -u +%H:%M:%S)"
