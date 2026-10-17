#!/usr/bin/env bash
# r75 reviewer replay: 3 sequential runs of the committed fixture in the sandbox ROOT
set -u
S="$(cd "$(dirname "$0")" && pwd)"
cd "$S/replay/corpus/fixtures" || exit 9
for i in 1 2 3; do
  t0=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  timeout -s KILL 900 python3 -B measure_audio.py --probe-consumers2-r75 \
      > "$S/replay/corpus/live/replay-$i.stdout.json" \
      2> "$S/replay/corpus/live/replay-$i.stderr.log"
  rc=$?
  t1=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  echo "run=$i rc=$rc start=$t0 end=$t1"
done
echo "--- receipts ---"
for f in "$S/replay/corpus/live/runs"/*/measurements.json; do
  printf "%s  %s  %s\n" "$(sha256sum "$f" | cut -d' ' -f1)" "$(stat -c %s "$f")" "$f"
done
