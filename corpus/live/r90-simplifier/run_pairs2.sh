#!/usr/bin/env bash
# r90-simplifier, second pass: the same-code control pair and the fold-1
# re-run (the first `f1` battery tripped the host-flaky `m_phantom` leg that
# an independent seat's run tripped too).
#
#   5. f1   (after1b)  -- fold 1 again
#   6. base (before3)  -- pristine again, immediately after, for the
#                         reverse-order (folded -> pristine) pair
set -u
ROOT=/home/vgpnk/Projects/shokunin/r90s
EVID=/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r90-simplifier
export TMPDIR=/home/vgpnk/Projects/shokunin/tmp

quiet() { ! pgrep -f "measure_audio\.py --probe-wpstate-r9[0]" >/dev/null; }
wait_quiet() {
  while :; do
    if quiet; then sleep 20; quiet && return 0; fi
    sleep 5
  done
}

for spec in "f1:after1b" "base:before3"; do
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
  sleep 15
done
echo "SECOND PASS DONE" >> "$EVID/run-log.txt"
