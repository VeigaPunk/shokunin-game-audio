#!/bin/bash
# r64-boundary sweep runner: per-variant detect + ffprobe codec/packets + sox count.
cd "$(dirname "$0")"
OUT=runs/sweep.tsv
: > "$OUT"
printf 'variant\tvalid\tdetected\tcodec\tbps_probe\twidth\tpackets\tpred_count\tsox_bytes\tsox_samples\texit\terr\n' >> "$OUT"
for f in variants/s_valid_*.wav; do
  n=$(basename "$f")
  vb=${n#s_valid_}; vb=${vb%.wav}; vb=$((10#$vb))
  det=$(sox -V6 "$f" -n stat 2>&1 | grep -o "detected file format type \`[a-z0-9-]*'" | head -1 | tr -d "\`'")
  codec=$(ffprobe -v error -select_streams a:0 -show_entries stream=codec_name -of csv=p=0 "$f" 2>/dev/null)
  bpsp=$(ffprobe -v error -select_streams a:0 -show_entries stream=bits_per_sample -of csv=p=0 "$f" 2>/dev/null)
  pkts=$(ffprobe -v error -select_streams a:0 -show_entries packet=size -of csv=p=0 "$f" 2>/dev/null | paste -sd+ -)
  # width from codec name (u8=1 s16=2 s24=3 s32=4 s64=8)
  w=0
  case "$codec" in
    pcm_u8|pcm_s8) w=1;; pcm_s16le|pcm_u16le) w=2;; pcm_s24le|pcm_u24le) w=3;;
    pcm_s32le|pcm_u32le|pcm_f32le) w=4;; pcm_s64le|pcm_f64le) w=8;; esac
  pred="-"
  if [ -n "$pkts" ] && [ "$w" -gt 0 ]; then
    pred=$(python3 -c "print(sum(int(p)//$w for p in '$pkts'.split('+')))")
  fi
  bytes=$(sox "$f" -t f32 - 2>/dev/null | wc -c)
  # separate pass for exit+err (pipe hides exit code)
  err=$(sox "$f" -n stat 2>&1 >/dev/null | grep -o "FAIL[^\"]*" | head -1)
  sox "$f" -n stat >/dev/null 2>&1; code=$?
  [ "$bytes" = "0" ] && samp="-" || samp=$((bytes/4))
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$n" "$vb" "${det:-?}" "${codec:-NONE}" "${bpsp:-?}" "$w" "${pkts:-none}" "$pred" "$bytes" "$samp" "$code" "${err:-ok}" >> "$OUT"
done
echo "== sweep done =="
column -t -s$'\t' "$OUT"
