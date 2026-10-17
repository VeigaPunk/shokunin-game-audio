#!/bin/bash
# r74 simplifier final-revision proof sequence (rev3, sha 9d179d80).
# 1) rebuild scratch tree from the landed revision
# 2) control run: --probe-lavfsweep-r74
# 3) D-E1 treatment run (LAVF_R74_EXTENT_TIMEOUT_S deleted)
# 4) restore landed file; prior-row replay: --probe-consumers-r73
set -uo pipefail
R=/home/vgpnk/Projects/shokunin/audio-shokunin
S=$R/corpus/live/r74-simplifier

echo "== rebuild =="
bash "$S/build_scratch_tree.sh" > "$S/final-rebuild.log" 2>&1 || { echo "rebuild FAILED"; exit 1; }
sha256sum "$R/corpus/fixtures/measure_audio.py" "$S/tree/corpus/fixtures/measure_audio.py" > "$S/final-rev-sha.txt"

run_arm() {
  local flag="$1" tag="$2"
  cd "$S/tree" || exit 1
  timeout -s KILL 1500 python3 corpus/fixtures/measure_audio.py "$flag" \
    > "$S/final-$tag.out" 2> "$S/final-$tag.err"
  local rc=$?
  local receipt
  receipt=$(python3 -c "import json;print(json.load(open('$S/final-$tag.out'))['receipt'])" 2>/dev/null)
  echo "$tag rc=$rc receipt=$receipt"
  [ -n "$receipt" ] && cp "$receipt" "$S/final-$tag-receipt.json"
  return $rc
}

echo "== control (landed rev3) =="
run_arm --probe-lavfsweep-r74 control
echo "== D-E1 treatment =="
cp "$S/measure_audio.D-E1-final.py" "$S/tree/corpus/fixtures/measure_audio.py"
run_arm --probe-lavfsweep-r74 DE1
echo "== restore landed rev3 + prior-row replay (r73 arm) =="
cp "$R/corpus/fixtures/measure_audio.py" "$S/tree/corpus/fixtures/measure_audio.py"
run_arm --probe-consumers-r73 r73
echo "DONE"
