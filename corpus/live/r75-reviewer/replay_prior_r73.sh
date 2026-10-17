#!/usr/bin/env bash
# r75 reviewer: prior-mode (consumers-r73) replay in the same sandbox, to test the
# insertion-only claim at the data level (prior rows must not move).
set -u
S="$(cd "$(dirname "$0")" && pwd)"
cd "$S/replay/corpus/fixtures" || exit 9
timeout -s KILL 900 python3 -B measure_audio.py --probe-consumers-r73 \
  > "$S/replay/corpus/live/prior-r73.stdout.json" 2> "$S/replay/corpus/live/prior-r73.stderr.log"
echo "rc=$?"
for f in "$S/replay/corpus/live/runs"/*consumers-r73*/measurements.json; do
  printf "%s  %s  %s\n" "$(sha256sum "$f" | cut -d' ' -f1)" "$(stat -c %s "$f")" "$f"
done
