#!/usr/bin/env bash
# r75-scribe landing watch — read-only snapshots appended to landing-watch.log.
# One line per probe; never mutates anything (no checkout, no run, no touch).
cd /home/vgpnk/Projects/shokunin/audio-shokunin || exit 1
LOG=corpus/live/r75-scribe/landing-watch.log
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
scratch=$(ls -d corpus/live/r75-* 2>/dev/null | sed 's|.*/||' | tr '\n' ',')
dirty=$(git status --porcelain --untracked-files=no | wc -l)
r74dirty=$(git status --porcelain --untracked-files=no | grep -c 'r74' )
printf '%s head=%s fixture=%s fixture_r75_refs=%s r75_receipts=%s total_receipts=%s reports75=%s scratch=%s tracked_modified=%s\n' \
  "$ts" "$head1" "$fblob" "$frefs" "$r75receipts" "$totalreceipts" "$reports" "$scratch" "$dirty" >> "$LOG"
