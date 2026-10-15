#!/usr/bin/env bash
# r82-verify2 spot s2 — independent re-derivation of the a7 armed leg:
# `-channels 0` on the alsa indev must be rc=8 + `Option channels not
# found` (option ABSENT on the indev), vs pulse indev 222 ERANGE (e2).
set -u
OUT=/tmp/r82w-spot
mkdir -p "$OUT"
echo "CMD: ffmpeg -hide_banner -loglevel warning -nostdin -y -f alsa -channels 0 -i hw:0,0 -t 1.0 -c:a pcm_s16le $OUT/a7.wav"
ffmpeg -hide_banner -loglevel warning -nostdin -y -f alsa \
    -channels 0 -i hw:0,0 -t 1.0 -c:a pcm_s16le "$OUT/a7.wav" \
    > "$OUT/s2_a7.out" 2> "$OUT/s2_a7.err"
rc=$?
echo "rc=$rc"
echo "--- stderr:"; cat "$OUT/s2_a7.err"
echo "--- control (pulse indev -channels 0, expect 222 ERANGE):"
ffmpeg -hide_banner -loglevel warning -nostdin -y -f pulse \
    -channels 0 -i default -t 1.0 -c:a pcm_s16le "$OUT/e2.wav" \
    > "$OUT/s2_e2.out" 2> "$OUT/s2_e2.err"
echo "rc=$?"; cat "$OUT/s2_e2.err"
