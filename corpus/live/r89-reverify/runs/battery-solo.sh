#!/usr/bin/env bash
# r89 RE-VERIFY battery (seat r89-reverify) — committed bytes 5755be5b.
# Launched under nohup on purpose: that is the wave's own failing launcher
# context pre-fold (SIG_IGN HUP inheritance). Post-fold it must be green.
set -u
export TMPDIR=/home/vgpnk/Projects/shokunin/tmp
export PYTHONDONTWRITEBYTECODE=1
LANE=/home/vgpnk/Projects/shokunin/audio-shokunin
OUT=$LANE/corpus/live/r89-reverify/runs
TREE=$LANE/corpus/live/r89-reverify/tree
cd "$TREE" || exit 1
run() {
  local name=$1; shift
  echo "=== $name start $(date -u +%Y-%m-%dT%H:%M:%S.%3NZ) load $(cut -d' ' -f1 /proc/loadavg)" >> "$OUT/battery-solo.log"
  python3 corpus/fixtures/measure_audio.py "$@" > "$OUT/$name.stdout.json" 2> "$OUT/$name.stderr.log"
  local rc=$?
  echo "=== $name end rc=$rc $(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)" >> "$OUT/battery-solo.log"
  local rec
  rec=$(python3 -c "import json;print(json.load(open('$OUT/$name.stdout.json')).get('receipt',''))" 2>/dev/null)
  echo "rc=$rc receipt=$rec" >> "$OUT/battery-solo.log"
  if [ -n "$rec" ]; then
    cp "$rec" "$OUT/$name.receipt.json"
    sha256sum "$OUT/$name.receipt.json" >> "$OUT/receipt-shas.txt"
  fi
}
run normal
run r89v1 --probe-pwprof-r89
run r89v2 --probe-pwprof-r89
run r89v3 --probe-pwprof-r89
echo "=== solo battery done $(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)" >> "$OUT/battery-solo.log"
