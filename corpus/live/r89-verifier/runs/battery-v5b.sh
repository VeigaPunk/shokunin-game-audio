#!/usr/bin/env bash
# r89 verifier battery round 2 — HUP-disposition-corrected launcher.
# Each fixture run is exec'd through runone.py (SIGHUP/SIGINT/SIGQUIT ->
# SIG_DFL) so the g_hup leg measures the host's default-terminate law, not
# the launcher's inherited SIG_IGN. Waits for a foreign-fixture-free window
# (cap 240 s) so each replay is classified solo by construction; the
# fixture's own `contention.fixture_runs` field is the second witness.
set -u
export TMPDIR=/home/vgpnk/Projects/shokunin/tmp
LANE=/home/vgpnk/Projects/shokunin/audio-shokunin
TREE=$LANE/corpus/live/r89-verifier/tree
OUT=$LANE/corpus/live/r89-verifier/runs
RUNONE=$LANE/corpus/live/r89-verifier/runs/runone.py
cd "$TREE" || exit 1
for i in 3 4 5 6 7; do
  name=r89v$i
  # solo guard: wait until no other measure_audio.py is alive
  waited=0
  while pgrep -f 'measure_audio.py' > /dev/null 2>&1; do
    sleep 2; waited=$((waited+2))
    [ "$waited" -ge 240 ] && { echo "=== $name solo-guard timeout after ${waited}s" | tee -a "$OUT/battery.log"; break; }
  done
  echo "=== $name start $(date -u +%Y-%m-%dT%H:%M:%S.%3NZ) loadavg $(cut -d' ' -f1 /proc/loadavg) waited=${waited}s" | tee -a "$OUT/battery.log"
  python3 "$RUNONE" python3 corpus/fixtures/measure_audio.py --probe-pwprof-r89 \
      > "$OUT/$name.stdout.json" 2> "$OUT/$name.stderr.log" &
  pid=$!
  sleep 1
  echo "=== $name fixture pid=$pid $(grep -E 'SigIgn' /proc/$pid/status 2>/dev/null)" >> "$OUT/battery.log"
  wait $pid
  rc=$?
  echo "=== $name end rc=$rc $(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)" | tee -a "$OUT/battery.log"
  rec=$(python3 -c "import json;print(json.load(open('$OUT/$name.stdout.json'))['receipt'])" 2>/dev/null)
  echo "rc=$rc receipt=$rec" >> "$OUT/battery.log"
  if [ -n "$rec" ]; then
    cp "$rec" "$OUT/$name.receipt.json"
    sha256sum "$OUT/$name.receipt.json" >> "$OUT/receipt-shas.txt"
  fi
done
echo "=== battery2 done $(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)" | tee -a "$OUT/battery.log"
