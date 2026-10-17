#!/bin/bash
# One r91 (gstfrz) battery from one archive tree, serialized against other
# gstfrz batteries (the family lock is tree-relative, so it excludes nothing
# across trees) and logged with its own census on both sides.
#
# usage: run_battery.sh <tree> <tag>
set -u
tree=$1; tag=$2
logdir=/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r91-simplifier
cd "$tree" || exit 9
export TMPDIR=/home/vgpnk/Projects/shokunin/tmp
export PYTHONDONTWRITEBYTECODE=1
sha=$(sha256sum corpus/fixtures/measure_audio.py | cut -c1-16)
# quiet window: no other gstfrz battery in flight (any tree), bounded 8 min
for i in $(seq 1 48); do
  if ! pgrep -f "measure_audio.py --probe-gstfrz-r91" >/dev/null 2>&1; then
    break
  fi
  sleep 10
done
foreign=$(pgrep -fc "measure_audio.py --probe-" 2>/dev/null || true)
foreign=${foreign:-0}
echo "[$tag] START $(date -u +%FT%TZ) tree=$tree sha=$sha load=$(cut -d' ' -f1-3 /proc/loadavg) foreign_fixture_batteries=$foreign" >> "$logdir/run-log.txt"
timeout -s KILL 900 python3 corpus/fixtures/measure_audio.py --probe-gstfrz-r91 > "$logdir/$tag.out" 2>&1
rc=$?
run=$(ls -td corpus/live/runs/*-gstfrz-r91 2>/dev/null | head -1)
echo "[$tag] END   $(date -u +%FT%TZ) rc=$rc run=${run#$tree/} load=$(cut -d' ' -f1-3 /proc/loadavg)" >> "$logdir/run-log.txt"
python3 /home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r91-simplifier/summary_run.py "$tree" "$tag" "$run" "$rc" >> "$logdir/run-log.txt"
