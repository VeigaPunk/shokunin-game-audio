#!/bin/bash
# r75 simplifier final-revision proof sequence (fill TREATMENT file in once
# the candidate is chosen). Sequence:
#  1) rebuild scratch tree from the landed revision
#  2) control run: --probe-consumers2-r75 (landed bytes)
#  3) treatment run: deletion applied
#  4) restore landed file; prior-row replays: --probe-consumers-r73,
#     --probe-lavfsweep-r74
# Usage: run_final_proofs.sh <treatment-file.py> [arm-flag]
set -uo pipefail
R=/home/vgpnk/Projects/shokunin/audio-shokunin
S=$R/corpus/live/r75-simplifier
TREATMENT=${1:?usage: run_final_proofs.sh <treatment-file.py> [arm-flag]}
ARM=${2:---probe-consumers2-r75}

echo "== rebuild =="
bash "$S/build_scratch_tree.sh" > "$S/final-rebuild.log" 2>&1 || { echo "rebuild FAILED"; exit 1; }
sha256sum "$R/corpus/fixtures/measure_audio.py" "$S/tree/corpus/fixtures/measure_audio.py" > "$S/final-rev-sha.txt"

run_arm() {
  local flag="$1" tag="$2"
  cd "$S/tree" || exit 1
  timeout -s KILL 2400 python3 corpus/fixtures/measure_audio.py "$flag" \
    > "$S/final-$tag.out" 2> "$S/final-$tag.err"
  local rc=$?
  local receipt
  receipt=$(python3 -c "import json;print(json.load(open('$S/final-$tag.out'))['receipt'])" 2>/dev/null)
  echo "$tag rc=$rc receipt=$receipt"
  [ -n "$receipt" ] && cp "$receipt" "$S/final-$tag-receipt.json"
  return $rc
}

echo "== control (landed) =="
run_arm "$ARM" control
echo "== treatment =="
cp "$TREATMENT" "$S/tree/corpus/fixtures/measure_audio.py"
run_arm "$ARM" treatment
echo "== restore landed + prior-row replays =="
cp "$R/corpus/fixtures/measure_audio.py" "$S/tree/corpus/fixtures/measure_audio.py"
run_arm --probe-consumers-r73 r73
run_arm --probe-lavfsweep-r74 r74
echo DONE
