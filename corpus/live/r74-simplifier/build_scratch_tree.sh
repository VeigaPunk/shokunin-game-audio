#!/bin/bash
# r74 simplifier: build a scratch tree that reproduces the fixture's ROOT
# resolution (ROOT = <tree>/corpus) without writing into the shared tree.
# Member round dirs are symlinked read-only; runs/ + round-74 are real dirs.
set -euo pipefail
REPO=/home/vgpnk/Projects/shokunin/audio-shokunin
SCRATCH="$REPO/corpus/live/r74-simplifier"
TREE="$SCRATCH/tree"

rm -rf "$TREE"
mkdir -p "$TREE/corpus/fixtures" "$TREE/corpus/artifacts" "$TREE/corpus/live/runs"

cp "$REPO/corpus/fixtures/measure_audio.py" "$TREE/corpus/fixtures/"
cp "$REPO/corpus/fixtures/build_artifacts.py" "$TREE/corpus/fixtures/"
cp "$REPO/corpus/fixtures/build_artifacts.sh" "$TREE/corpus/fixtures/" 2>/dev/null || true
cp -r "$REPO/corpus/artifacts/." "$TREE/corpus/artifacts/"

# symlink every round-* member dir except round-74 (kept real so any r74
# member generation cannot write through into the shared tree)
for d in "$REPO"/corpus/live/round-*; do
  b=$(basename "$d")
  [ "$b" = "round-74" ] && continue
  ln -s "../../../../$b" "$TREE/corpus/live/$b"
done

# round-74: copy real member bytes if the dir exists (regular files, not symlink)
if [ -d "$REPO/corpus/live/round-74" ]; then
  mkdir -p "$TREE/corpus/live/round-74"
  cp -r "$REPO/corpus/live/round-74/." "$TREE/corpus/live/round-74/"
fi

echo "scratch tree at $TREE"
find "$TREE/corpus" -maxdepth 1 | sort
