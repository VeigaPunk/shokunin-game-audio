#!/usr/bin/env bash
# r89 verifier co-tenancy stress: three tree copies, three simultaneous
# --probe-pwprof-r89 runs. Different ROOTs => three independent family
# locks (the r84-r88 F1 residual), so the runs genuinely co-tenant — the
# way the wave actually runs (sibling seats replay the same fixture).
# Launched through runone.py so the g_hup leg measures the host law.
set -u
export TMPDIR=/home/vgpnk/Projects/shokunin/tmp
LANE=/home/vgpnk/Projects/shokunin/audio-shokunin
V=$LANE/corpus/live/r89-verifier
RUNONE=$V/runs/runone.py
OUT=$V/runs
echo "=== cotenancy round start $(date -u +%Y-%m-%dT%H:%M:%S.%3NZ) loadavg $(cut -d' ' -f1 /proc/loadavg)" | tee -a "$OUT/battery.log"
pids=()
for i in 1 2 3; do
  tree=$V/runs/cotree$i
  cd "$tree" || exit 1
  python3 "$RUNONE" python3 corpus/fixtures/measure_audio.py --probe-pwprof-r89 \
      > "$OUT/cot$i.stdout.json" 2> "$OUT/cot$i.stderr.log" &
  pids+=($!)
  echo "cot$i pid=${pids[-1]} start $(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)" | tee -a "$OUT/battery.log"
done
for i in 1 2 3; do
  wait "${pids[$((i-1))]}"
  echo "cot$i rc=$? end $(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)" | tee -a "$OUT/battery.log"
  rec=$(python3 -c "import json;print(json.load(open('$OUT/cot$i.stdout.json'))['receipt'])" 2>/dev/null)
  if [ -n "$rec" ]; then
    cp "$rec" "$OUT/cot$i.receipt.json"
    sha256sum "$OUT/cot$i.receipt.json" >> "$OUT/receipt-shas.txt"
  fi
done
echo "=== cotenancy round done $(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)" | tee -a "$OUT/battery.log"
