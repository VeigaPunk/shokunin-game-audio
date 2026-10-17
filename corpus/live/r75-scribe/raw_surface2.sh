#!/usr/bin/env bash
# r75-scribe raw-surface inventory, part 2 — error/gate surfaces (bounded).
# Synthetic inputs only (text file misnamed .wav); no corpus member is touched,
# no probe mode runs, no receipt is written. All arms `timeout -s KILL`.
set -u
cd /home/vgpnk/Projects/shokunin/audio-shokunin || exit 1
OUT=corpus/live/r75-scribe/raw
T="timeout -s KILL"
printf 'this is not audio\n' > "$OUT/noise.wav"
echo "noise_sha256=$(sha256sum "$OUT/noise.wav" | cut -d' ' -f1)" > "$OUT/raw2-summary.txt"

{
  echo "--- paplay noise.wav (invalid input surface) ---"
  $T 15 paplay "$OUT/noise.wav" > "$OUT/paplay-noise.stdout" 2> "$OUT/paplay-noise.stderr"
  echo "rc=$?"; echo "stderr_lines=$(wc -l < "$OUT/paplay-noise.stderr")"
} >> "$OUT/raw2-summary.txt" 2>&1

{
  echo "--- ffplay noise.wav (invalid input surface) ---"
  SDL_AUDIODRIVER=dummy $T 20 ffplay -nodisp -autoexit -vn -loglevel info \
      "$OUT/noise.wav" > "$OUT/ffplay-noise.stdout" 2> "$OUT/ffplay-noise.stderr"
  echo "rc=$?"; echo "stderr_lines=$(wc -l < "$OUT/ffplay-noise.stderr")"
} >> "$OUT/raw2-summary.txt" 2>&1

{
  echo "--- SDL_AUDIODRIVER=bogus ffplay silence.wav (driver-gate surface) ---"
  SDL_AUDIODRIVER=bogus $T 20 ffplay -nodisp -autoexit -vn -loglevel info \
      "$OUT/silence.wav" > "$OUT/ffplay-bogusdrv.stdout" 2> "$OUT/ffplay-bogusdrv.stderr"
  echo "rc=$?"; echo "stderr_lines=$(wc -l < "$OUT/ffplay-bogusdrv.stderr")"
} >> "$OUT/raw2-summary.txt" 2>&1

{
  echo "--- aplay noise.wav (invalid input surface) ---"
  $T 15 aplay -q "$OUT/noise.wav" > "$OUT/aplay-noise.stdout" 2> "$OUT/aplay-noise.stderr"
  echo "rc=$?"; echo "stderr_lines=$(wc -l < "$OUT/aplay-noise.stderr")"
} >> "$OUT/raw2-summary.txt" 2>&1

{
  for f in "$OUT"/paplay-noise.stderr "$OUT"/ffplay-noise.stderr \
           "$OUT"/ffplay-bogusdrv.stderr "$OUT"/aplay-noise.stderr; do
    echo "=== $(basename "$f") ==="
    cat -A "$f" | tail -8 | sed 's/^/  | /'
  done
} >> "$OUT/raw2-summary.txt" 2>&1
cat "$OUT/raw2-summary.txt"
