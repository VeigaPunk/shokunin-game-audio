#!/usr/bin/env bash
# r80-baseline freeze watcher — HEAD + fixture sha256 every 10 s while the
# battery runs, so no receipt can be attributed to a moving tree.
set -u
cd /home/vgpnk/Projects/shokunin/audio-shokunin
OUT=corpus/live/r80-baseline/head-watch.log
: > "$OUT"
for _ in $(seq 1 400); do
  printf '%s head=%s fixture_sha256=%s dirty_paths=%s\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    "$(git rev-parse --short HEAD)" \
    "$(sha256sum corpus/fixtures/measure_audio.py | cut -d' ' -f1)" \
    "$(git status --porcelain | wc -l)" >> "$OUT"
  sleep 10
done
