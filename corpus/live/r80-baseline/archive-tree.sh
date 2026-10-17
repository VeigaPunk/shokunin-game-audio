#!/usr/bin/env bash
# r80-baseline tree archive — `git archive HEAD` materialized into
# corpus/live/r80-baseline/tree/ (gitignored: corpus/.gitignore `live/*/*tree*`),
# with a tar receipt in /tmp and a file-set equality check against git ls-tree.
set -eu
cd /home/vgpnk/Projects/shokunin/audio-shokunin
OUT=corpus/live/r80-baseline
HEAD=$(git rev-parse HEAD)
mkdir -p "$OUT/tree"
git archive --format=tar "$HEAD" > /tmp/r80-baseline-work/head-${HEAD:0:7}.tar
tar -xf /tmp/r80-baseline-work/head-${HEAD:0:7}.tar -C "$OUT/tree"
{
  echo "archived_at_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "HEAD: $HEAD"
  echo "tar: /tmp/r80-baseline-work/head-${HEAD:0:7}.tar"
  echo "tar_sha256: $(sha256sum /tmp/r80-baseline-work/head-${HEAD:0:7}.tar | cut -d' ' -f1)"
  echo "tar_bytes: $(stat -c %s /tmp/r80-baseline-work/head-${HEAD:0:7}.tar)"
  echo "tar_members: $(tar -tf /tmp/r80-baseline-work/head-${HEAD:0:7}.tar | wc -l)"
  echo "extracted_files: $(find "$OUT/tree" -type f | wc -l)"
  echo "extracted_dirs: $(find "$OUT/tree" -type d | wc -l)"
  echo "fixture_sha256_in_tree: $(sha256sum "$OUT/tree/corpus/fixtures/measure_audio.py" | cut -d' ' -f1)"
  echo "fixture_sha256_in_worktree: $(sha256sum corpus/fixtures/measure_audio.py | cut -d' ' -f1)"
  git ls-tree -r -z --name-only "$HEAD" | tr '\0' '\n' | LC_ALL=C sort > /tmp/r80-baseline-work/ls-tree.txt
  (cd "$OUT/tree" && find . -type f -printf '%P\n' | LC_ALL=C sort) > /tmp/r80-baseline-work/extracted.txt
  echo "ls_tree_files: $(wc -l < /tmp/r80-baseline-work/ls-tree.txt)"
  echo "file_set_symdiff: $(comm -3 /tmp/r80-baseline-work/ls-tree.txt /tmp/r80-baseline-work/extracted.txt | wc -l)"
  echo "--- symdiff sample (if any) ---"
  comm -3 /tmp/r80-baseline-work/ls-tree.txt /tmp/r80-baseline-work/extracted.txt | head -20
} | tee "$OUT/tree-archive.txt"
