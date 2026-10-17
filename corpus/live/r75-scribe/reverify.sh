#!/usr/bin/env bash
# r75-scribe recovery gen — independent re-verification of the dead seat's
# headline raw-surface claims (F6/F7). Bounded; child-env only; daemon untouched.
set -u
cd /home/vgpnk/Projects/shokunin/audio-shokunin || exit 1
OUT=corpus/live/r75-scribe/raw
T="timeout -s KILL"
{
  echo "date_utc=$(date -u +%Y%m%dT%H%M%SZ) host=$(hostname)"
  echo "--- F6a: ffplay invalid input (noise.wav, SDL dummy) ---"
  SDL_AUDIODRIVER=dummy $T 20 ffplay -nodisp -autoexit -vn -loglevel info \
      "$OUT/noise.wav" >"$OUT/rv-ffplay-noise.stdout" 2>"$OUT/rv-ffplay-noise.stderr"
  echo "rc=$? stderr_lines=$(wc -l <"$OUT/rv-ffplay-noise.stderr") stderr_bytes=$(stat -c %s "$OUT/rv-ffplay-noise.stderr")"
  grep -o 'Invalid data found when processing input' "$OUT/rv-ffplay-noise.stderr" | head -1
  echo "--- F6b: aplay text file (raw-PCM fallback) ---"
  $T 15 aplay "$OUT/noise.wav" >"$OUT/rv-aplay-noise.stdout" 2>"$OUT/rv-aplay-noise.stderr"
  echo "rc=$? stderr_lines=$(wc -l <"$OUT/rv-aplay-noise.stderr")"
  cat "$OUT/rv-aplay-noise.stderr"
  echo "--- F6c: paplay invalid input ---"
  $T 15 paplay "$OUT/noise.wav" >"$OUT/rv-paplay-noise.stdout" 2>"$OUT/rv-paplay-noise.stderr"
  echo "rc=$? stderr_lines=$(wc -l <"$OUT/rv-paplay-noise.stderr")"
  cat "$OUT/rv-paplay-noise.stderr"
  echo "--- F7a: paplay PIPEWIRE_RUNTIME_DIR=<empty tmp> ---"
  d=$(mktemp -d); PIPEWIRE_RUNTIME_DIR="$d" $T 15 paplay "$OUT/silence.wav" \
      >"$OUT/rv-pp-pipewire.stdout" 2>"$OUT/rv-pp-pipewire.stderr"
  echo "rc=$? stderr_bytes=$(stat -c %s "$OUT/rv-pp-pipewire.stderr")"
  echo "runtime_dir_entries=$(ls -A "$d" | tr '\n' ' ')"
  echo "--- F7b: paplay XDG_RUNTIME_DIR=<empty tmp> ---"
  d2=$(mktemp -d); XDG_RUNTIME_DIR="$d2" $T 15 paplay "$OUT/silence.wav" \
      >"$OUT/rv-pp-xdg.stdout" 2>"$OUT/rv-pp-xdg.stderr"
  echo "rc=$? stderr_lines=$(wc -l <"$OUT/rv-pp-xdg.stderr")"
  cat "$OUT/rv-pp-xdg.stderr"
  echo "runtime_dir_entries=$(ls -A "$d2" | tr '\n' ' ')"
  echo "--- F7c: paplay PULSE_SERVER=nonexistent ---"
  PULSE_SERVER=nonexistent $T 15 paplay "$OUT/silence.wav" \
      >"$OUT/rv-pp-pulseserver.stdout" 2>"$OUT/rv-pp-pulseserver.stderr"
  echo "rc=$? stderr_lines=$(wc -l <"$OUT/rv-pp-pulseserver.stderr")"
  cat "$OUT/rv-pp-pulseserver.stderr"
  rm -rf "$d" "$d2"
} 2>&1 | tee "$OUT/reverify.txt"
echo "reverify exit=$?"
