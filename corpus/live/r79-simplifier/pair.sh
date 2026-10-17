#!/usr/bin/env bash
# Run one control/candidate probe pair (residue-pinned, back-to-back) and
# compare the two receipts. usage: pair.sh <tag> <mode> [probe-flag]
#   mode: healthy | monitor | authority
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"
TAG="$1"; MODE="$2"
FLAG="${3:---probe-capture-r79}"

run_side() {
  local side="$1" out="$2"
  local newest_before
  newest_before=$(ls -1 "$side/live/runs" 2>/dev/null | tail -1)
  if [ "$MODE" = healthy ]; then
    ( cd "$side" && python3 ../pidpin.py 0 python3 corpus/fixtures/measure_audio.py "$FLAG" ) \
      > "$out.stdout.json" 2> "$out.stderr.log"
  else
    ( cd "$side" && python3 ../pidpin.py 0 python3 ../faultrun.py "$MODE" \
        corpus/fixtures/measure_audio.py ) \
      > "$out.stdout.json" 2> "$out.stderr.log"
  fi
  echo "EXIT=$?" >> "$out.stdout.json"
}

mkdir -p receipts
run_side control "receipts/${TAG}-control"
run_side cand    "receipts/${TAG}-cand"

for side in control cand; do
  ls -1t "$side/live/runs" | head -1 > "receipts/${TAG}-${side}.dir"
done
C_JSON="control/live/runs/$(cat receipts/${TAG}-control.dir)/measurements.json"
D_JSON="cand/live/runs/$(cat receipts/${TAG}-cand.dir)/measurements.json"
echo "control receipt : $C_JSON"
echo "candidate receipt: $D_JSON"
sha256sum "$C_JSON" "$D_JSON" | tee "receipts/${TAG}-sha256.txt"
if [ -f classes.txt ]; then
  python3 compare.py "$C_JSON" "$D_JSON" --allow classes.txt \
    | tee "receipts/${TAG}-compare.txt"
else
  python3 compare.py "$C_JSON" "$D_JSON" | tee "receipts/${TAG}-compare.txt"
fi
