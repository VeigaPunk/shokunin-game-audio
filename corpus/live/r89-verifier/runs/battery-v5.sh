#!/usr/bin/env bash
# r89 verifier battery — frozen tree at 0d732989 (corpus/live/r89-verifier/tree).
# Serialized by the fixture's own fixed-path family lock.
set -u
export TMPDIR=/home/vgpnk/Projects/shokunin/tmp
LANE=/home/vgpnk/Projects/shokunin/audio-shokunin
TREE=$LANE/corpus/live/r89-verifier/tree
OUT=$LANE/corpus/live/r89-verifier/runs
cd "$TREE" || exit 1
for i in $(seq 0 5); do
  if [ "$i" = 0 ]; then
    name=normal
    args=""
  else
    name=r89v$i
    args="--probe-pwprof-r89"
  fi
  echo "=== $name start $(date -u +%Y-%m-%dT%H:%M:%S.%3NZ) loadavg $(cut -d' ' -f1 /proc/loadavg)" | tee -a "$OUT/battery.log"
  # shellcheck disable=SC2086
  python3 corpus/fixtures/measure_audio.py $args \
      > "$OUT/$name.stdout.json" 2> "$OUT/$name.stderr.log"
  rc=$?
  echo "=== $name end rc=$rc $(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)" | tee -a "$OUT/battery.log"
  rec=$(python3 -c "import json,sys;print(json.load(open('$OUT/$name.stdout.json'))['receipt'])" 2>/dev/null)
  echo "rc=$rc receipt=$rec" >> "$OUT/battery.log"
  if [ -n "$rec" ]; then
    cp "$rec" "$OUT/$name.receipt.json"
    sha256sum "$OUT/$name.receipt.json" >> "$OUT/receipt-shas.txt"
  fi
done
echo "=== battery done $(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)" | tee -a "$OUT/battery.log"
