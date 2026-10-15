#!/usr/bin/env bash
# r82-verifier2 battery: normal + --probe-ffmpeg-r82 x2 inside the frozen
# d6167399 tree. Mirrors r82-verify/battery.sh; tags r82w1/r82w2.
set -u
TREE=/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r82-verify2/tree
OUT=/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r82-verify2/runs
FIX=corpus/fixtures/measure_audio.py
cd "$TREE" || exit 2
run() {
  local tag="$1"; shift
  local sha_b sha_a rc
  sha_b=$(sha256sum "$FIX" | awk '{print $1}')
  {
    echo "=== $tag $(date -u +%Y-%m-%dT%H:%M:%S.%3NZ) ==="
    echo "SHA before=$sha_b"
    echo "CMD: timeout 900 python3 $FIX $*"
  } >> "$OUT/commands.log"
  timeout 900 python3 "$FIX" "$@" > "$OUT/$tag.stdout.json" 2> "$OUT/$tag.stderr.log"
  rc=$?
  sha_a=$(sha256sum "$FIX" | awk '{print $1}')
  {
    echo "rc=$rc"
    echo "SHA after=$sha_a"
    echo "=== end $tag $(date -u +%Y-%m-%dT%H:%M:%S.%3NZ) ==="
  } >> "$OUT/commands.log"
  echo "$tag rc=$rc sha=$sha_a"
}
run normal
run r82w1 --probe-ffmpeg-r82
run r82w2 --probe-ffmpeg-r82
