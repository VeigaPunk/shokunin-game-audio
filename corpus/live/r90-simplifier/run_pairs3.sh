#!/usr/bin/env bash
# r90-simplifier, third pass: fold-1 after-runs until one lands on a host
# window where the (host-racy) `m_phantom` leg is green.
#
# Context: 6 batteries so far — base OK / f1 FAIL / base OK / f2 OK /
# f1 FAIL / base FAIL. The pristine tree failing at 10:06 kills the
# "fold correlates with the flake" reading; the leg is host-racy. This pass
# runs f1 until a green one exists, then one more pristine run as the
# adjacent control.
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

for spec in "f1:after1c" "f1:after1d" "base:before4"; do
  tree=${spec%%:*}; tag=${spec##*:}
  wait_quiet
  cd "$ROOT/$tree" || exit 1
  {
    echo "=== $tag tree=$tree $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "sha256 $(sha256sum corpus/fixtures/measure_audio.py | cut -d' ' -f1)"
  } >> "$EVID/run-log.txt"
  timeout 900 python3 corpus/fixtures/measure_audio.py --probe-wpstate-r90 \
      > "$EVID/$tree.$tag.out" 2>&1
  rc=$?
  {
    echo "$tag rc=$rc $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    tail -c 400 "$EVID/$tree.$tag.out"
    echo
  } >> "$EVID/run-log.txt"
  sleep 15
done
echo "THIRD PASS DONE" >> "$EVID/run-log.txt"
