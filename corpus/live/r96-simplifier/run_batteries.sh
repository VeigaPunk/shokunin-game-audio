#!/usr/bin/env bash
# r96 simplifier before/after battery runner — serialized, logged, bounded.
set -u
R96S=/home/vgpnk/Projects/shokunin/r96s
LOG=$R96S/run-log.txt
export TMPDIR=/home/vgpnk/Projects/shokunin/tmp

foreign() { pgrep -af -- "--probe-pulsecli-r96" | tr '\n' '|' || true; }

run_one() {
  tag=$1; tree=$2
  sha=$(sha256sum "$R96S/$tree/corpus/fixtures/measure_audio.py" | cut -c1-12)
  waited=0
  while pgrep -f -- "--probe-pulsecli-r96" >/dev/null && [ "$waited" -lt 900 ]; do
    sleep 10; waited=$((waited+10))
  done
  echo "$(date -u +%FT%TZ) START $tag tree=$tree sha=$sha waited=${waited}s foreign_pre=[$(foreign)] load=$(cut -d' ' -f1-3 /proc/loadavg)" >> "$LOG"
  start=$(date +%s)
  ( cd "$R96S/$tree/corpus/fixtures" && timeout -s KILL 1200 python3 measure_audio.py --probe-pulsecli-r96 > "$R96S/$tag.out" 2> "$R96S/$tag.err" )
  rc=$?
  end=$(date +%s)
  receipt=$(python3 -c "import json;print(json.load(open('$R96S/$tag.out')).get('receipt','?'))" 2>/dev/null || echo '?')
  echo "$(date -u +%FT%TZ) END $tag rc=$rc wall=$((end-start))s receipt=$receipt foreign_post=[$(foreign)] load=$(cut -d' ' -f1-3 /proc/loadavg)" >> "$LOG"
}

run_one base1 base
run_one f1 f1
run_one f2 f2
run_one f12 f12
run_one base2 base
run_one f3 f3
run_one f13 f13
echo "$(date -u +%FT%TZ) ALL DONE" >> "$LOG"
