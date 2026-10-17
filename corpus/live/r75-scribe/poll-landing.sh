#!/usr/bin/env bash
# r75-scribe (recovery generation) landing poll — read-only, appends to
# landing-watch.log. Exits early only if HEAD moves (author/integrator land).
cd /home/vgpnk/Projects/shokunin/audio-shokunin || exit 1
LOG=corpus/live/r75-scribe/landing-watch.log
base=6f905c3
for i in $(seq 1 26); do
  ts=$(date -u +%Y%m%dT%H%M%SZ)
  head1=$(git log --oneline -1 | cut -c1-7)
  fblob=$(git hash-object corpus/fixtures/measure_audio.py | cut -c1-12)
  frefs=$(grep -c 'r75' corpus/fixtures/measure_audio.py)
  [ -z "$frefs" ] && frefs=0
  r75receipts=$(ls corpus/live/runs 2>/dev/null | grep -c 'r75')
  [ -z "$r75receipts" ] && r75receipts=0
  totalreceipts=$(ls -d corpus/live/runs/*/ 2>/dev/null | wc -l)
  reports=$(ls reports/round-75 2>/dev/null | tr '\n' ',' )
  [ -z "$reports" ] && reports=ABSENT
  ascratch=$(ls corpus/live/r75-author 2>/dev/null | wc -l)
  newcommits=$(git log --oneline "$base"..HEAD 2>/dev/null | wc -l)
  printf '%s head=%s fixture=%s fixture_r75_refs=%s r75_receipts=%s total_receipts=%s reports75=%s author_scratch_files=%s new_commits_vs_%s=%s\n' \
    "$ts" "$head1" "$fblob" "$frefs" "$r75receipts" "$totalreceipts" "$reports" "$ascratch" "$base" "$newcommits" >> "$LOG"
  if [ "$newcommits" -gt 0 ]; then
    echo "$ts LANDED: $(git log --oneline "$base"..HEAD | head -5)" >> "$LOG"
    break
  fi
  sleep 45
done
echo "$(date -u +%Y%m%dT%H%M%SZ) poll-exit" >> "$LOG"
