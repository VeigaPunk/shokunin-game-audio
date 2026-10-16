#!/usr/bin/env bash
# r88-verifier battery: replays v4 and v5 of the frozen c19bec96 tree.
set -u
TREE=/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r88-verifier/tree
R=/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r88-verifier/runs
export TMPDIR=/home/vgpnk/Projects/shokunin/tmp
cd "$TREE"
for v in v4 v5; do
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) r88${v}: python3 corpus/fixtures/measure_audio.py --probe-btwit-r88" >> "$R/commands.log"
  start=$(date -u +%s)
  timeout 600 python3 corpus/fixtures/measure_audio.py --probe-btwit-r88 > "$R/r88${v}.stdout.json" 2> "$R/r88${v}.stderr.log"
  rc=$?
  end=$(date -u +%s)
  echo "r88${v} rc=$rc wall=$((end-start))s" >> "$R/commands.log"
  rec=$(python3 -c "import json,sys;print(json.load(open('$R/r88${v}.stdout.json'))['receipt'])" 2>/dev/null)
  if [ -n "$rec" ]; then cp "$rec" "$R/r88${v}.receipt.json"; fi
  sha256sum "$R/r88${v}.receipt.json" >> "$R/receipt-shas.txt"
done
echo "battery-v45 done $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$R/commands.log"
