#!/bin/bash
# r75 simplifier: build a scratch tree that reproduces the fixture's ROOT
# resolution (ROOT = <tree>/corpus) without writing into the shared tree.
# Member round dirs are symlinked read-only; runs/ + round-74 + round-75 are
# real dirs (any r74/r75 member generation cannot write through into the
# shared tree).
set -euo pipefail
REPO=/home/vgpnk/Projects/shokunin/audio-shokunin
SCRATCH="$REPO/corpus/live/r75-simplifier"
TREE="$SCRATCH/tree"

rm -rf "$TREE"
mkdir -p "$TREE/corpus/fixtures" "$TREE/corpus/artifacts" "$TREE/corpus/live/runs"

cp "$REPO/corpus/fixtures/measure_audio.py" "$TREE/corpus/fixtures/"
cp "$REPO/corpus/fixtures/build_artifacts.py" "$TREE/corpus/fixtures/"
cp "$REPO/corpus/fixtures/build_artifacts.sh" "$TREE/corpus/fixtures/" 2>/dev/null || true
cp -r "$REPO/corpus/artifacts/." "$TREE/corpus/artifacts/"

# symlink every round-* member dir except round-74 and round-75 (kept real)
for d in "$REPO"/corpus/live/round-*; do
  b=$(basename "$d")
  case "$b" in round-74|round-75) continue;; esac
  ln -s "../../../../$b" "$TREE/corpus/live/$b"
done

for r in round-74 round-75; do
  if [ -d "$REPO/corpus/live/$r" ]; then
    mkdir -p "$TREE/corpus/live/$r"
    cp -r "$REPO/corpus/live/$r/." "$TREE/corpus/live/$r/"
  fi
done

echo "scratch tree at $TREE"
find "$TREE/corpus" -maxdepth 1 | sort
