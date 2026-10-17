#!/usr/bin/env bash
# r95v: wait for a responsive PipeWire daemon (bounded), then run the r95
# family on the FROZEN tree — twice for cross-run drift — then the two
# mutation runs.  Readiness = pw-dump AND pactl both answer < 6s.
set -u
SEAT=/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r95-verifier
LOG=$SEAT/runs/r95v-wait.log
export TMPDIR=/home/vgpnk/Projects/shokunin/tmp
deadline=$(( $(date +%s) + 2400 ))
attempt=0
run() {  # $1 label  $2 tree  $3 optional PATH prefix
  local label=$1 tree=$2 pathpfx=${3:-}
  ( cd "$tree" && PATH="${pathpfx}${PATH}" timeout 900 python3 corpus/fixtures/measure_audio.py --probe-jack-r95 \
      > "$SEAT/runs/r95v-$label.stdout" 2> "$SEAT/runs/r95v-$label.stderr" )
  local rc=$?
  echo "$(date -u +%H:%M:%SZ) $label rc=$rc stdout=$(head -c 300 "$SEAT/runs/r95v-$label.stdout")" >> "$LOG"
}
while [ "$(date +%s)" -lt "$deadline" ]; do
  attempt=$((attempt+1))
  s=$(date +%s%N); timeout -k 3 8 pw-dump >/dev/null 2>&1; rc1=$?; e=$(date +%s%N); ms1=$(( (e-s)/1000000 ))
  s=$(date +%s%N); timeout -k 3 8 pactl list sinks short >/dev/null 2>&1; rc2=$?; e=$(date +%s%N); ms2=$(( (e-s)/1000000 ))
  echo "$(date -u +%H:%M:%SZ) attempt=$attempt pw-dump rc=$rc1 ${ms1}ms pactl rc=$rc2 ${ms2}ms" >> "$LOG"
  if [ $rc1 -eq 0 ] && [ $rc2 -eq 0 ] && [ $ms1 -lt 6000 ] && [ $ms2 -lt 6000 ]; then
    echo "$(date -u +%H:%M:%SZ) READY" >> "$LOG"
    run runB "$SEAT/tree"
    run runC "$SEAT/tree"
    run mutstim "$SEAT/tree-mutstim"
    run mutlaw "$SEAT/tree-mutlaw"
    echo "$(date -u +%H:%M:%SZ) SEQUENCE DONE" >> "$LOG"
    exit 0
  fi
  sleep 40
done
echo "$(date -u +%H:%M:%SZ) DEADLINE reached without a responsive daemon" >> "$LOG"
exit 1
