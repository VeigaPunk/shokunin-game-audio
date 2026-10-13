#!/usr/bin/env bash
# r63-scribe sweep runner: for each variant, record (a) sox -V4 detected type,
# (b) sox exit under -n stat, (c) f32 decode byte count where it succeeds,
# (d) sox --i '(ffmpeg)' tag presence. Writes results.tsv.
set -u
cd "$(dirname "$0")"
OUT=results.tsv
: > "$OUT"
printf 'variant\tsize\tb256\tdetected\tstat_exit\tf32_bytes\tffmpeg_tag\n' >> "$OUT"
for f in variants/*; do
  name=$(basename "$f")
  size=$(stat -c%s "$f")
  b256=$(od -A n -t x1 -j 256 -N 1 "$f" 2>/dev/null | tr -d ' \n')
  [ -z "$b256" ] && b256="--"
  det=$(sox -V4 "$f" -n stat 2>&1 | sed -n "s/.*detected file format type .\([a-zA-Z0-9_-]*\).*/\1/p" | head -1)
  [ -z "$det" ] && det="none"
  sox "$f" -n stat >/dev/null 2>&1; sexit=$?
  fbytes=$(sox "$f" -t f32 - 2>/dev/null | wc -c)
  tag=$(sox --i "$f" 2>/dev/null | grep -c "(ffmpeg)" || true)
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$name" "$size" "$b256" "$det" "$sexit" "$fbytes" "$tag" >> "$OUT"
done
echo "done: $(($(wc -l < "$OUT") - 1)) rows -> $OUT"
