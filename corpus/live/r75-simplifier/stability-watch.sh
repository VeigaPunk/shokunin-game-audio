#!/bin/bash
# r75 simplifier: stability watcher — declare STABLE when the fixture sha256
# is unchanged across 5 consecutive 30 s checks (2.5 min).
cd /home/vgpnk/Projects/shokunin/audio-shokunin || exit 99
LOG=corpus/live/r75-simplifier/stability-watch.txt
: > "$LOG"
prev=""
same=0
for i in $(seq 1 400); do
  ts=$(date -u +"%H:%M:%SZ")
  cur=$(sha256sum corpus/fixtures/measure_audio.py | cut -c1-16)
  if [ "$cur" = "$prev" ]; then same=$((same+1)); else same=0; fi
  printf '%s sha=%s same=%s\n' "$ts" "$cur" "$same" >> "$LOG"
  if [ "$same" -ge 5 ]; then
    printf '%s STABLE sha=%s\n' "$ts" "$cur" >> "$LOG"
    break
  fi
  prev="$cur"
  sleep 30
done
