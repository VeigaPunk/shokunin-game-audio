#!/usr/bin/env bash
# r75-scribe raw-surface inventory — bounded, read-only consumer invocations.
# Purpose: capture the RAW stderr/stdout line shapes that the r75 parser
# (paplay/aplay/ffplay legs) will have to parse. This is NOT a measurement:
# no receipt is written, no probe mode is invoked, no fixture code runs.
# Bounds: every invocation wrapped in `timeout -s KILL` (carried guard).
set -u
cd /home/vgpnk/Projects/shokunin/audio-shokunin || exit 1
OUT=corpus/live/r75-scribe/raw
mkdir -p "$OUT"
T="timeout -s KILL"

{
  echo "host=$(hostname) date_utc=$(date -u +%Y%m%dT%H%M%SZ) local=$(date +%Y%m%dT%H%M%S%z)"
  echo "--- paplay --version ---"
  $T 10 paplay --version 2>&1; echo "rc=$?"
  echo "--- aplay --version ---"
  $T 10 aplay --version 2>&1; echo "rc=$?"
  echo "--- ffplay -version ---"
  $T 10 ffplay -version 2>&1; echo "rc=$?"
  echo "--- aplay -l ---"
  $T 10 aplay -l 2>&1; echo "rc=$?"
} > "$OUT/versions-and-enum.txt" 2>&1

# inaudible 0.2 s silence pacer (scribe scratch only; deterministic)
ffmpeg -hide_banner -loglevel error -f lavfi -i anullsrc=r=44100:cl=mono \
       -t 0.2 -c:a pcm_s16le -y "$OUT/silence.wav" >/dev/null 2>&1
echo "silence_sha256=$(sha256sum "$OUT/silence.wav" | cut -d' ' -f1)" \
  >> "$OUT/versions-and-enum.txt"

# paplay file-mode (live pipewire-pulse); stdout+stderr separated, rc recorded
{
  echo "--- paplay file (silence.wav) ---"
  $T 20 paplay "$OUT/silence.wav" > "$OUT/paplay-file.stdout" \
      2> "$OUT/paplay-file.stderr"
  echo "rc=$?"
  echo "stdout_bytes=$(stat -c %s "$OUT/paplay-file.stdout")"
  echo "stderr_bytes=$(stat -c %s "$OUT/paplay-file.stderr")"
} > "$OUT/paplay-file.txt" 2>&1

# ffplay file-mode, SDL dummy driver, audio only, no window
{
  echo "--- ffplay file (silence.wav, SDL_AUDIODRIVER=dummy) ---"
  SDL_AUDIODRIVER=dummy $T 30 ffplay -nodisp -autoexit -vn -loglevel info \
      "$OUT/silence.wav" > "$OUT/ffplay-file.stdout" \
      2> "$OUT/ffplay-file.stderr"
  echo "rc=$?"
  echo "stdout_bytes=$(stat -c %s "$OUT/ffplay-file.stdout")"
  echo "stderr_bytes=$(stat -c %s "$OUT/ffplay-file.stderr")"
  echo "stderr_lines=$(wc -l < "$OUT/ffplay-file.stderr")"
} > "$OUT/ffplay-file.txt" 2>&1

# aplay device-open mode on the same silence (kernel device coupling surface)
{
  echo "--- aplay -q file (silence.wav, default device) ---"
  $T 15 aplay -q "$OUT/silence.wav" > "$OUT/aplay-file.stdout" \
      2> "$OUT/aplay-file.stderr"
  echo "rc=$?"
  echo "stdout_bytes=$(stat -c %s "$OUT/aplay-file.stdout")"
  echo "stderr_bytes=$(stat -c %s "$OUT/aplay-file.stderr")"
} > "$OUT/aplay-file.txt" 2>&1

# raw line shapes of the captured streams
for f in "$OUT"/*.stderr "$OUT"/*.stdout; do
  echo "=== $f ($(wc -l < "$f") lines) ==="
  head -12 "$f" | sed 's/^/  | /'
done > "$OUT/shapes.txt" 2>&1
echo "raw-surface inventory complete"
