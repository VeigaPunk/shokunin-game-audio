#!/usr/bin/env bash
# r89 RE-VERIFY co-tenancy batch — tree2+tree3 concurrent (nohup), plus one
# committed-arm run on the lane tree with a HELD foreign pw-profiler client
# in the window (the deterministic pre-fix falsification context).
set -u
export TMPDIR=/home/vgpnk/Projects/shokunin/tmp
export PYTHONDONTWRITEBYTECODE=1
LANE=/home/vgpnk/Projects/shokunin/audio-shokunin
BASE=$LANE/corpus/live/r89-reverify
OUT=$BASE/runs

one() {  # tree name
  local tree=$1 name=$2
  cd "$BASE/$tree" || exit 1
  echo "=== $name start $(date -u +%Y-%m-%dT%H:%M:%S.%3NZ) load $(cut -d' ' -f1 /proc/loadavg)" >> "$OUT/battery-cot.log"
  python3 corpus/fixtures/measure_audio.py --probe-pwprof-r89 \
      > "$OUT/$name.stdout.json" 2> "$OUT/$name.stderr.log"
  local rc=$?
  echo "=== $name end rc=$rc $(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)" >> "$OUT/battery-cot.log"
  local rec
  rec=$(python3 -c "import json;print(json.load(open('$OUT/$name.stdout.json')).get('receipt',''))" 2>/dev/null)
  echo "rc=$rc receipt=$rec" >> "$OUT/battery-cot.log"
  if [ -n "$rec" ]; then
    cp "$rec" "$OUT/$name.receipt.json"
    sha256sum "$OUT/$name.receipt.json" >> "$OUT/receipt-shas.txt"
  fi
}

# round 1: two independent ROOTs, genuinely concurrent
one tree2 cot-r1-t2 &
P1=$!
one tree3 cot-r1-t3 &
P2=$!
wait $P1 $P2

# round 2
one tree2 cot-r2-t2 &
P1=$!
one tree3 cot-r2-t3 &
P2=$!
wait $P1 $P2

# held-foreign-client run on the committed lane tree: a persistent foreign
# pw-profiler client is present for the WHOLE x_foot window (pwprof_before=1,
# pwprof_during=1) — deterministic pre-fix failure context for the global arm,
# deterministic own-scope pass for the committed arm.
FOREIGN_LOG=$OUT/foreign-holder.log
( exec -a r89v-foreign-holder pw-profiler -J -n 0 > /dev/null 2>&1 ) &
FH=$!
echo "foreign holder pid $FH $(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)" >> "$FOREIGN_LOG"
sleep 1.5
one tree held-foreign &
P3=$!
wait $P3
kill "$FH" 2>/dev/null
wait "$FH" 2>/dev/null
echo "foreign holder reaped $(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)" >> "$FOREIGN_LOG"
echo "=== cot battery done $(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)" >> "$OUT/battery-cot.log"
