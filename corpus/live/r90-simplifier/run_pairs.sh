#!/usr/bin/env bash
# r90-simplifier: the fresh before/after battery pairs.
#
#   base  (pristine f50cf66a)   <- before of fold 1
#   f1    (base + fold 1)       <- after  of fold 1
#   base  (pristine f50cf66a)   <- before of fold 2   (fresh second baseline)
#   f2    (base + fold 2)       <- after  of fold 2
#
# Same-family exclusion is a FIXED per-tree path (`corpus/live/measure_audio-
# wpstate-r90.lock`), so two seats in different trees do NOT exclude each
# other: this runner therefore waits for a 20 s window with no other
# `--probe-wpstate-r90` process before it fires, and logs the pgrep census on
# both sides of every run. (Bracket in the pattern keeps pgrep from matching
# this script's own command line.)
set -u
ROOT=/home/vgpnk/Projects/shokunin/r90s
EVID=/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r90-simplifier
export TMPDIR=/home/vgpnk/Projects/shokunin/tmp

quiet() {
  ! pgrep -f "measure_audio\.py --probe-wpstate-r9[0]" >/dev/null
}

wait_quiet() {
  while :; do
    if quiet; then sleep 20; quiet && return 0; fi
    sleep 5
  done
}

for spec in "base:before1" "f1:after1" "base:before2" "f2:after2"; do
  tree=${spec%%:*}; tag=${spec##*:}
  wait_quiet
  cd "$ROOT/$tree" || exit 1
  {
    echo "=== $tag tree=$tree $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "sha256 $(sha256sum corpus/fixtures/measure_audio.py | cut -d' ' -f1)"
    echo "other-r90-procs-before $(pgrep -c -f 'measure_audio\.py --probe-wpstate-r9[0]' || true)"
  } >> "$EVID/run-log.txt"
  timeout 900 python3 corpus/fixtures/measure_audio.py --probe-wpstate-r90 \
      > "$EVID/$tree.$tag.out" 2>&1
  rc=$?
  {
    echo "$tag rc=$rc $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "other-r90-procs-after $(pgrep -c -f 'measure_audio\.py --probe-wpstate-r9[0]' || true)"
    tail -c 400 "$EVID/$tree.$tag.out"
    echo
  } >> "$EVID/run-log.txt"
  # give the store/module namespace a settle beat before the next pair
  sleep 15
done
echo "ALL FOUR RUNS DONE" >> "$EVID/run-log.txt"
