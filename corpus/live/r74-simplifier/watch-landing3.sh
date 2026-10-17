#!/bin/bash
# r74 simplifier: poll for the author's fixture SOURCE landing only.
cd /home/vgpnk/Projects/shokunin/audio-shokunin || exit 99
LOG=corpus/live/r74-simplifier/landing-poll3.txt
: > "$LOG"
for i in $(seq 1 900); do
  ts=$(date -u +"%H:%M:%SZ")
  head=$(git rev-parse --short HEAD)
  src=$(git diff --name-only HEAD -- corpus/fixtures/measure_audio.py corpus/fixtures/build_artifacts.py | wc -l)
  rep=$(ls reports/round-74/ 2>/dev/null | wc -l)
  printf '%s HEAD=%s srcdiff=%s reports74=%s\n' "$ts" "$head" "$src" "$rep" >> "$LOG"
  if [ "$src" -gt 0 ]; then
    printf '%s SOURCE-LANDING src=%s reports74=%s\n' "$ts" "$src" "$rep" >> "$LOG"
    break
  fi
  sleep 30
done
