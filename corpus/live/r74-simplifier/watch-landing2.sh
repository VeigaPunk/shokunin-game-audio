#!/bin/bash
# r74 simplifier: poll for the author's SOURCE landing (ignore pyc/untracked).
cd /home/vgpnk/Projects/shokunin/audio-shokunin || exit 99
LOG=corpus/live/r74-simplifier/landing-poll2.txt
: > "$LOG"
for i in $(seq 1 720); do
  ts=$(date -u +"%H:%M:%SZ")
  head=$(git rev-parse --short HEAD)
  src=$(git diff --name-only HEAD -- corpus/fixtures/measure_audio.py corpus/fixtures/build_artifacts.py | wc -l)
  r74rep=$(ls reports/round-74/ 2>/dev/null | wc -l)
  r74scr=$(ls corpus/live/r74-author/ 2>/dev/null | wc -l)
  printf '%s HEAD=%s srcdiff=%s reports74=%s author_scratch=%s\n' "$ts" "$head" "$src" "$r74rep" "$r74scr" >> "$LOG"
  if [ "$src" -gt 0 ] || [ "$r74rep" -gt 0 ] || [ "$r74scr" -gt 0 ]; then
    printf '%s LANDING-SIGNAL src=%s reports74=%s author_scratch=%s\n' "$ts" "$src" "$r74rep" "$r74scr" >> "$LOG"
    break
  fi
  sleep 20
done
