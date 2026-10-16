#!/usr/bin/env bash
# r84 REVIEWER live check — one run of the PINNED committed blob
# (fbe65713:corpus/fixtures/measure_audio.py, sha256 8ed09d19…) from a
# mirrored tree so ROOT resolves inside this seat dir.
#
# Shared TMPDIR on purpose: the r84 family lock lives at
# $TMPDIR/measure_audio-alsapw-r84.lock, so this run waits behind any
# same-TMPDIR sibling run instead of racing it (see report F1: the lock
# is TMPDIR-scoped and does NOT exclude a sibling with a private TMPDIR).
set -u
SEAT=/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r84-reviewer
cd "$SEAT/tree" || exit 1
mkdir -p "$SEAT/runs"
export TMPDIR=/home/vgpnk/Projects/shokunin/tmp
{
  echo "start $(date -u +%H:%M:%S) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
  echo "concurrent r84 runs at start:"
  pgrep -af "probe-alsapw-r84" | grep -v "$$" || echo "  (none)"
} > "$SEAT/runs/r84r1.window.txt"
timeout 1500 python3 corpus/fixtures/measure_audio.py --probe-alsapw-r84 \
  > "$SEAT/runs/r84r1.stdout.json" 2> "$SEAT/runs/r84r1.stderr.log"
echo "rc=$?" >> "$SEAT/runs/r84r1.window.txt"
{
  echo "end $(date -u +%H:%M:%S) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
  echo "concurrent r84 runs at end:"
  pgrep -af "probe-alsapw-r84" || echo "  (none)"
} >> "$SEAT/runs/r84r1.window.txt"
cat "$SEAT/runs/r84r1.window.txt"
