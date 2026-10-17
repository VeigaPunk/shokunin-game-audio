#!/usr/bin/env bash
# r89 RE-VERIFY mutation runs — revert-the-fix mutants in scratch trees.
# M1 mut-sigreset  : sigreset no-op, launched under nohup -> g_hup must RED.
# M2 mut-footglobal: pre-fold GLOBAL x_foot law, run with a HELD foreign
#                    pw-profiler client in the window -> x_foot must RED.
#                    (the committed arm under the same held-client context is
#                    the `held-foreign` run of battery-cot.sh)
set -u
export TMPDIR=/home/vgpnk/Projects/shokunin/tmp
export PYTHONDONTWRITEBYTECODE=1
LANE=/home/vgpnk/Projects/shokunin/audio-shokunin
BASE=$LANE/corpus/live/r89-reverify
OUT=$BASE/runs

one() {  # tree name
  local tree=$1 name=$2
  cd "$BASE/$tree" || exit 1
  echo "=== $name start $(date -u +%Y-%m-%dT%H:%M:%S.%3NZ) load $(cut -d' ' -f1 /proc/loadavg)" >> "$OUT/battery-mut.log"
  python3 corpus/fixtures/measure_audio.py --probe-pwprof-r89 \
      > "$OUT/$name.stdout.json" 2> "$OUT/$name.stderr.log"
  local rc=$?
  echo "=== $name end rc=$rc $(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)" >> "$OUT/battery-mut.log"
  local rec
  rec=$(python3 -c "import json;print(json.load(open('$OUT/$name.stdout.json')).get('receipt',''))" 2>/dev/null)
  echo "rc=$rc receipt=$rec" >> "$OUT/battery-mut.log"
  if [ -n "$rec" ]; then
    cp "$rec" "$OUT/$name.receipt.json"
    sha256sum "$OUT/$name.receipt.json" >> "$OUT/receipt-shas.txt"
  fi
}

# M1 — pre-fold signal disposition (no sigreset), nohup launcher
one mut-sigreset mut-sigreset-nohup

# M2 — pre-fold global x_foot law, held foreign pw-profiler in the window
( exec -a r89v-foreign-holder pw-profiler -J -n 0 > /dev/null 2>&1 ) &
FH=$!
echo "foreign holder pid $FH $(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)" >> "$OUT/foreign-holder.log"
sleep 1.5
one mut-footglobal mut-footglobal-held &
P=$!
wait $P
kill "$FH" 2>/dev/null
wait "$FH" 2>/dev/null
echo "foreign holder reaped $(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)" >> "$OUT/foreign-holder.log"
echo "=== mutation battery done $(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)" >> "$OUT/battery-mut.log"
