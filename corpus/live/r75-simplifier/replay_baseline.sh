#!/bin/bash
# r75 simplifier pre-landing harness validation: replay --probe-consumers-r73
# and --probe-lavfsweep-r74 in the scratch tree (committed bytes) and compare
# against the committed receipts. Never writes into the shared tree.
set -uo pipefail
R=/home/vgpnk/Projects/shokunin/audio-shokunin
S=$R/corpus/live/r75-simplifier
cd "$S/tree" || exit 1
for arm in consumers-r73 lavfsweep-r74; do
  case $arm in
    consumers-r73) flag=--probe-consumers-r73;;
    lavfsweep-r74) flag=--probe-lavfsweep-r74;;
  esac
  timeout -s KILL 1500 python3 corpus/fixtures/measure_audio.py "$flag" \
    > "$S/baseline-$arm.out" 2> "$S/baseline-$arm.err"
  rc=$?
  receipt=$(python3 -c "import json;print(json.load(open('$S/baseline-$arm.out'))['receipt'])" 2>/dev/null)
  echo "$arm rc=$rc receipt=$receipt"
  [ -n "$receipt" ] && cp "$receipt" "$S/baseline-$arm-receipt.json"
done
echo DONE
