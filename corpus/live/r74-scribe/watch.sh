#!/usr/bin/env bash
# r74 scribe landing watch — read-only snapshot appended to landing-watch.log
set -u
cd /home/vgpnk/Projects/shokunin/audio-shokunin
LOG=corpus/live/r74-scribe/landing-watch.log
{
  echo "=== $(date -u +%Y%m%dT%H%M%SZ) (local $(date +%H:%M:%S)) ==="
  echo "HEAD: $(git log --oneline -1)"
  echo "worktree tracked-modified: $(git status --porcelain --untracked-files=no | wc -l)"
  echo "fixture blob: $(git hash-object corpus/fixtures/measure_audio.py)"
  echo "r74 refs in fixture: $(grep -c 'r74' corpus/fixtures/measure_audio.py)"
  echo "r74 receipt dirs: $(ls corpus/live/runs 2>/dev/null | grep -c 'r74')"
  echo "reports/round-74: $(ls reports/round-74 2>/dev/null | tr '\n' ' ')"
  echo "newest runs: $(ls -t corpus/live/runs | head -3 | tr '\n' ' ')"
  echo "sibling scratch: $(ls -d corpus/live/r74-* 2>/dev/null | tr '\n' ' ')"
  echo "sibling scratch newest files: $(find corpus/live/r74-boundary corpus/live/r74-critic corpus/live/r74-scout corpus/live/r74-reviewer corpus/live/r74-simplifier corpus/live/r74-baseline 2>/dev/null -type f -newermt '-3 minutes' | head -5 | tr '\n' ' ')"
} >> "$LOG"
tail -12 "$LOG"
