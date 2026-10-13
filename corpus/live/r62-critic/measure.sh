#!/usr/bin/env bash
# r62 critic: decode-count harness. Per file: ffprobe codec+duration,
# ffmpeg f32le stdout bytes, sox f32 stdout bytes. One CSV receipt.
set -u
ROOT="$(cd "$(dirname "$0")" && pwd)"
OUT="$ROOT/var"
CSV="$ROOT/counts.csv"
echo "file,codec,sample_fmt,bps,duration_s,ff_f32_bytes,ff_frames,sox_f32_bytes,sox_frames,sox_exit" > "$CSV"
for f in "$OUT"/*.wav; do
  name="$(basename "$f")"
  line="$(ffprobe -v error -show_entries stream=codec_name,sample_fmt,bits_per_sample,duration -of csv=p=0 "$f" 2>/dev/null | head -1)"
  ffb=$(ffmpeg -v error -i "$f" -f f32le -acodec pcm_f32le - 2>/dev/null | wc -c)
  sx=$(sox "$f" -t f32 -e floating-point - 2>/dev/null | wc -c)
  se=$?
  echo "$name,$line,$ffb,$((ffb/4)),$sx,$((sx/4)),$se" >> "$CSV"
done
echo "wrote $CSV"
