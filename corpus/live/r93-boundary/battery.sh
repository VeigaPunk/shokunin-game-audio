#!/usr/bin/env bash
# r93-boundary battery — single lane, sequential; each stage is a fresh process
# (fresh pw-cli client, fresh filter-chain module, fresh null sink per leg).
#   battery.sh quiet   -> quiet-ish arm (no own hogs; foreign load recorded)
#   battery.sh load    -> >=12 concurrent own hogs (12 CPU + 2 audio) per stage
set -u
cd "$(dirname "$0")"
PHASE="${1:-quiet}"
LOGDIR=runs
mkdir -p "$LOGDIR"
LOG="$LOGDIR/$PHASE.log"

run() {
  local name="$1"; shift
  printf '=== %s %s :: %s ===\n' "$(date -u +%H:%M:%S)" "$name" "$*" >> "$LOG"
  printf '    loadavg=%s\n' "$(cut -d' ' -f1-3 /proc/loadavg)" >> "$LOG"
  python3 probes/r93bdriver.py "$@" >> "$LOG" 2>&1
  local rc=$?
  printf -- '--- %s exit=%s loadavg=%s\n' "$(date -u +%H:%M:%S)" "$rc" \
         "$(cut -d' ' -f1-3 /proc/loadavg)" >> "$LOG"
  return $rc
}

if [ "$PHASE" = "quiet" ]; then
  run "core-r2"    core 2 --cond quiet
  run "core-r3"    core 3 --cond quiet
  run "window"     window 1 --cond quiet
  run "history"    history 1 --cond quiet
  run "hist2"      hist2 1 --cond quiet
  run "labels"     labels 1 --cond quiet
  run "ref"        ref 1 --cond quiet
  run "rate"       rate 1 --cond quiet
  run "quantum"    quantum 1 --cond quiet
  run "flags"      flags 1 --cond quiet
  run "defaults"   defaults 1 --cond quiet
elif [ "$PHASE" = "load" ]; then
  run "core-r1-load"    core 1 --load 12 --cond load12
  run "core-r2-load"    core 2 --load 12 --cond load12
  run "quantum-load"    quantum 1 --load 12 --cond load12
  run "amp-load"        amp 1 --load 12 --cond load12
  run "freq-load"       freq 1 --load 12 --cond load12
  run "rate-load"       rate 1 --load 12 --cond load12
  run "window-load"     window 1 --load 12 --cond load12
  run "hist2-load"      hist2 1 --load 12 --cond load12
  run "history-load"    history 1 --load 12 --cond load12
  run "labels-load"     labels 1 --load 12 --cond load12
  run "defaults-load"   defaults 1 --load 12 --cond load12
  run "flags-load"      flags 1 --load 12 --cond load12
fi
echo "battery $PHASE done at $(date -u +%H:%M:%S)" >> "$LOG"
