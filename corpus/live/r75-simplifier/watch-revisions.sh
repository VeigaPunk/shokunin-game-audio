#!/bin/bash
# r75 simplifier: revision watcher — snapshots the fixture diff whenever its
# sha256 changes (20 s cycle). Captures every author revision even if the
# author revises between my interactive checks.
cd /home/vgpnk/Projects/shokunin/audio-shokunin || exit 99
S=corpus/live/r75-simplifier
LOG=$S/revisions.txt
: > "$LOG"
prev=""
n=0
for i in $(seq 1 720); do
  cur=$(sha256sum corpus/fixtures/measure_audio.py | cut -c1-16)
  if [ "$cur" != "$prev" ]; then
    n=$((n+1))
    ts=$(date -u +"%Y%m%dT%H%M%SZ")
    git diff -- corpus/fixtures/measure_audio.py > "$S/landing-snapshot$n.diff"
    lines=$(git diff --stat -- corpus/fixtures/measure_audio.py | tail -1)
    printf '%s rev%s sha=%s %s\n' "$ts" "$n" "$cur" "$lines" >> "$LOG"
    prev="$cur"
  fi
  sleep 20
done
