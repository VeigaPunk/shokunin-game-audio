#!/usr/bin/env bash
# r81-baseline freeze watcher: every 10 s, one line of (HEAD, fixture sha,
# fixture dirt, tree-fixture sha). Runs for the whole battery window.
set -u
cd /home/vgpnk/Projects/shokunin/audio-shokunin
OUT=corpus/live/r81-baseline
i=0
while [ "$i" -lt 900 ]; do
  printf '%s head=%s fixture=%s dirty=[%s] tree=%s\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    "$(git rev-parse --short HEAD)" \
    "$(sha256sum corpus/fixtures/measure_audio.py | cut -d' ' -f1 | cut -c1-16)" \
    "$(git status --porcelain -- corpus/fixtures/measure_audio.py | tr -d '\n')" \
    "$(sha256sum "$OUT/tree/corpus/fixtures/measure_audio.py" 2>/dev/null | cut -d' ' -f1 | cut -c1-16)" \
    >> "$OUT/head-watch.log"
  i=$((i+1))
  sleep 10
done
