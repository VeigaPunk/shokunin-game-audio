#!/bin/bash
# Poll every 20s; append a line whenever the fixture hashes, the r71-author
# scratch, or the ffprobe artifact state changes.
cd "$(git rev-parse --show-toplevel)"
prev=""
for i in $(seq 1 240); do
  cur=$(sha256sum corpus/fixtures/measure_audio.py corpus/fixtures/build_artifacts.py 2>/dev/null | sha256sum | cut -d' ' -f1)
  cur="$cur $(ls -d corpus/live/r71-author corpus/artifacts/ffprobe_ledger_r71.json 2>/dev/null | tr '\n' ',') $(git status --porcelain -- corpus/fixtures corpus/artifacts corpus/live/round-71 2>/dev/null | sha256sum | cut -d' ' -f1)"
  if [ "$cur" != "$prev" ]; then
    echo "$(date -u +%H:%M:%S) $cur" >> corpus/live/r71-simplifier/watch.log
    prev="$cur"
  fi
  sleep 20
done
