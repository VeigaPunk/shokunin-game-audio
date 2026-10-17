#!/bin/bash
# r75 simplifier proof driver (recovery generation).
#  1) verify scratch tree holds the landed blob
#  2) control run: --probe-consumers2-r75 on landed bytes
#  3) per treatment file: install, run, save stdout/stderr/receipt, restore
#  4) prior-row replays: --probe-consumers-r73, --probe-lavfsweep-r74
# Never writes into the shared tree; every run executes inside tree/.
set -uo pipefail
R=/home/vgpnk/Projects/shokunin/audio-shokunin
S=$R/corpus/live/r75-simplifier
TREE=$S/tree
FIXTURE=corpus/fixtures/measure_audio.py

landed_sha=$(sha256sum "$R/$FIXTURE" | cut -d' ' -f1)
tree_sha=$(sha256sum "$TREE/$FIXTURE" | cut -d' ' -f1)
echo "landed_sha=$landed_sha"
echo "tree_sha  =$tree_sha"
[ "$landed_sha" = "$tree_sha" ] || { echo "ABORT: tree does not hold landed bytes"; exit 1; }

run_arm() {  # $1=tag  $2=flag
  local tag="$1" flag="$2"
  ( cd "$TREE" && timeout -s KILL 2400 python3 "$FIXTURE" "$flag" ) \
    > "$S/proof-$tag.out" 2> "$S/proof-$tag.err"
  local rc=$?
  local receipt
  receipt=$(python3 -c "import json;print(json.load(open('$S/proof-$tag.out'))['receipt'])" 2>/dev/null)
  echo "$tag rc=$rc receipt=$receipt" >> "$S/proof-summary.txt"
  if [ -n "$receipt" ] && [ -f "$receipt" ]; then
    cp "$receipt" "$S/proof-$tag-receipt.json"
    echo "  sha=$(sha256sum "$S/proof-$tag-receipt.json" | cut -d' ' -f1)"
  fi
  return $rc
}

: > "$S/proof-summary.txt"
echo "== control (landed bytes) =="
run_arm control --probe-consumers2-r75

for t in t1-paplay-shadowed-pattern t2-ops-detect-fold t3-ops-invalid-fold t4-inert-time-branch; do
  echo "== $t =="
  cp "$S/$t.py" "$TREE/$FIXTURE"
  run_arm "$t" --probe-consumers2-r75
  cp "$R/$FIXTURE" "$TREE/$FIXTURE"
  now=$(sha256sum "$TREE/$FIXTURE" | cut -d' ' -f1)
  [ "$now" = "$landed_sha" ] || { echo "ABORT: restore failed after $t"; exit 1; }
done

echo "== prior-row replays (landed bytes) =="
run_arm r73 --probe-consumers-r73
run_arm r74 --probe-lavfsweep-r74
echo "== summary =="
cat "$S/proof-summary.txt"
echo "shared fixture sha after: $(sha256sum "$R/$FIXTURE" | cut -d' ' -f1)"
