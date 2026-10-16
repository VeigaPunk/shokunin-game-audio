#!/usr/bin/env bash
# r88 reviewer — two real frozen-tree probes from the SAME ROOT (same
# fixed-path lock), different TMPDIRs, started 5 s apart.  If the lock
# serializes, r88r3's receipt stamp must land after r88r2's end.
set -u
LANE=/home/vgpnk/Projects/shokunin/audio-shokunin
R=$LANE/corpus/live/r88-reviewer
TREE=$R/tree
cd "$TREE"

run() {
  local tag=$1 tmp=$2
  local s e rc
  s=$(date +%s.%N)
  TMPDIR="$tmp" PYTHONDONTWRITEBYTECODE=1 timeout 900 \
    python3 corpus/fixtures/measure_audio.py --probe-btwit-r88 \
    > "$R/runs/$tag.stdout.json" 2> "$R/runs/$tag.stderr.log"
  rc=$?
  e=$(date +%s.%N)
  echo "$tag rc=$rc start=$s end=$e wall=$(echo "$e - $s" | bc)" \
    >> "$R/receipts/serialization.log"
}

run r88r2 "$R/tmpdir-a" &
sleep 5
run r88r3 "$R/tmpdir-b"
wait
echo "done $(date -u +%FT%TZ)" >> "$R/receipts/serialization.log"
cat "$R/receipts/serialization.log"
