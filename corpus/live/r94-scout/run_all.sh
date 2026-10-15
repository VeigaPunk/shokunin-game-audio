#!/bin/bash
# r94 scout — sequential stage battery, default pass then -D (no-dither) pass.
cd "$(dirname "$0")"
set -u
for st in prep gain rate remix trim fade repeat_pad_silence dither stat chain; do
  echo "=== $st default $(date -u +%H:%M:%S) ==="
  python3 probes/r94driver.py "$st" 3
done
for st in gain rate remix trim fade repeat_pad_silence dither chain; do
  echo "=== $st -D $(date -u +%H:%M:%S) ==="
  R94_PREFIX="-D" R94_SUFFIX="_D" python3 probes/r94driver.py "$st" 3
done
echo "ALL DONE $(date -u +%H:%M:%S)"
