#!/bin/bash
# r74 simplifier: poll for the author landing. Records HEAD, tracked-dirty
# count, reports/round-74 and corpus/live/r74-author presence each cycle.
cd /home/vgpnk/Projects/shokunin/audio-shokunin || exit 99
LOG=corpus/live/r74-simplifier/landing-poll.txt
: > "$LOG"
for i in $(seq 1 240); do
  ts=$(date -u +"%H:%M:%SZ")
  head=$(git rev-parse --short HEAD)
  dirty=$(git status --porcelain 2>/dev/null | grep -vc '^??')
  r74rep=$(ls reports/round-74/ 2>/dev/null | wc -l)
  r74scr=$(ls corpus/live/r74-author/ 2>/dev/null | wc -l)
  printf '%s HEAD=%s dirty=%s reports74=%s author_scratch=%s\n' "$ts" "$head" "$dirty" "$r74rep" "$r74scr" >> "$LOG"
  if [ "$dirty" -gt 0 ] || [ "$r74rep" -gt 0 ] || [ "$r74scr" -gt 0 ]; then
    printf '%s LANDING-SIGNAL\n' "$ts" >> "$LOG"
    break
  fi
  sleep 20
done
