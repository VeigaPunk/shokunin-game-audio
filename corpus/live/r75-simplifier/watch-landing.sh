#!/bin/bash
# r75 simplifier: poll for the AUTHOR landing (fixture diff), not sibling
# reports. Primary signal: tracked modification of corpus/fixtures/
# measure_audio.py. Secondary: r75-author.md / corpus/live/r75-author/ /
# corpus/live/round-75/ / runs matching *r75*. 20 s cycle; breaks on signal.
cd /home/vgpnk/Projects/shokunin/audio-shokunin || exit 99
LOG=corpus/live/r75-simplifier/landing-poll.txt
: > "$LOG"
for i in $(seq 1 900); do
  ts=$(date -u +"%H:%M:%SZ")
  head=$(git rev-parse --short HEAD)
  fixture=$(git status --porcelain -- corpus/fixtures/measure_audio.py 2>/dev/null | wc -l)
  authrep=$([ -f reports/round-75/r75-author.md ] && echo 1 || echo 0)
  r75scr=$(ls corpus/live/r75-author/ 2>/dev/null | wc -l)
  r75mem=$(ls corpus/live/round-75/ 2>/dev/null | wc -l)
  r75run=$(ls -d corpus/live/runs/*r75* 2>/dev/null | wc -l)
  printf '%s HEAD=%s fixture_dirty=%s author_rep=%s author_scratch=%s round75=%s runs75=%s\n' \
    "$ts" "$head" "$fixture" "$authrep" "$r75scr" "$r75mem" "$r75run" >> "$LOG"
  if [ "$fixture" -gt 0 ] || [ "$authrep" -gt 0 ] || [ "$r75scr" -gt 0 ] || [ "$r75mem" -gt 0 ] || [ "$r75run" -gt 0 ]; then
    printf '%s LANDING-SIGNAL\n' "$ts" >> "$LOG"
    break
  fi
  sleep 20
done
