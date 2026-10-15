#!/usr/bin/env bash
# r82-baseline tree archive — `git archive HEAD` materialized into
# corpus/live/r82-baseline/tree/ (gitignored: corpus/.gitignore `live/**/*tree*`),
# with a tar receipt in /tmp and a file-set equality check against git ls-tree.
set -eu
cd /home/vgpnk/Projects/shokunin/audio-shokunin
OUT=corpus/live/r82-baseline
HEAD=$(git rev-parse HEAD)
mkdir -p "$OUT/tree" /tmp/r82-baseline-work
git archive --format=tar "$HEAD" > /tmp/r82-baseline-work/head-${HEAD:0:7}.tar
tar -xf /tmp/r82-baseline-work/head-${HEAD:0:7}.tar -C "$OUT/tree"
{
  echo "archived_at_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "HEAD: $HEAD"
  echo "tar: /tmp/r82-baseline-work/head-${HEAD:0:7}.tar"
  echo "tar_sha256: $(sha256sum /tmp/r82-baseline-work/head-${HEAD:0:7}.tar | cut -d' ' -f1)"
  echo "tar_bytes: $(stat -c %s /tmp/r82-baseline-work/head-${HEAD:0:7}.tar)"
  echo "tar_members: $(tar -tf /tmp/r82-baseline-work/head-${HEAD:0:7}.tar | wc -l)"
  echo "extracted_files: $(find "$OUT/tree" -type f | wc -l)"
  echo "extracted_dirs: $(find "$OUT/tree" -type d | wc -l)"
  echo "fixture_sha256_in_tree: $(sha256sum "$OUT/tree/corpus/fixtures/measure_audio.py" | cut -d' ' -f1)"
  echo "fixture_sha256_in_worktree: $(sha256sum corpus/fixtures/measure_audio.py | cut -d' ' -f1)"
  git ls-tree -r -z --name-only "$HEAD" | tr '\0' '\n' | LC_ALL=C sort > /tmp/r82-baseline-work/ls-tree.txt
  (cd "$OUT/tree" && find . -type f -printf '%P\n' | LC_ALL=C sort) > /tmp/r82-baseline-work/extracted.txt
  echo "ls_tree_files: $(wc -l < /tmp/r82-baseline-work/ls-tree.txt)"
  echo "file_set_symdiff: $(comm -3 /tmp/r82-baseline-work/ls-tree.txt /tmp/r82-baseline-work/extracted.txt | wc -l)"
  echo "--- symdiff sample (if any) ---"
  comm -3 /tmp/r82-baseline-work/ls-tree.txt /tmp/r82-baseline-work/extracted.txt | head -20
  echo "--- tree receipt corpus ---"
  echo "tree_runs_files: $(find "$OUT/tree/corpus/live/runs" -type f | wc -l)"
  echo "tree_fixture_bytes: $(stat -c %s "$OUT/tree/corpus/fixtures/measure_audio.py")"
  echo "tree_fixture_git_blob: $(git rev-parse "$HEAD:corpus/fixtures/measure_audio.py")"
} | tee "$OUT/tree-archive.txt"
