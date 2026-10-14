#!/usr/bin/env bash
# r65-critic probe harness — records detected format, route marker,
# samples read, exit codes, ffprobe view for every variant in var/.
cd "$(dirname "$0")"
OUT=results.tsv
printf 'file\tdetected\tsox_i_route\tv6_samples\tv6_exit\tfail_line\tdecode_bytes\tffp_codec\tffp_rate\tffp_exit\n' > "$OUT"

for f in var/*; do
  n=$(basename "$f")
  # 1) detection + verbose outcome
  v6=$(sox -V6 "$f" -n stat 2>&1); ex=$?
  det=$(printf '%s\n' "$v6" | grep -oE "detected file format type \`[a-zA-Z0-9-]+'" | sed "s/.*\`//; s/'//" | head -1)
  samp=$(printf '%s\n' "$v6" | sed -n 's/.*Samples read:[[:space:]]*\([0-9]*\).*/\1/p' | head -1)
  fail=$(printf '%s\n' "$v6" | grep -oE "(FAIL|WARN)[^\n]*" | head -1 | tr '\t' ' ')
  # 2) --i route line
  ii=$(sox --i "$f" 2>&1); iex=$?
  route=$(printf '%s\n' "$ii" | grep "Input File" | tr '\t' ' ')
  [ $iex -ne 0 ] && route="FAIL(ex$iex):$(printf '%s\n' "$ii" | grep -oE 'FAIL.*' | head -1 | tr '\t' ' ')"
  # 3) raw decode bytes through autodetect route
  db=$(sox "$f" -t f32 -e floating-point - 2>/dev/null | wc -c)
  # 4) ffprobe view
  fp=$(ffprobe -v error -select_streams a:0 -show_entries stream=codec_name,sample_rate -of csv=p=0 "$f" 2>/dev/null)
  fex=$?
  codec=$(printf '%s' "$fp" | cut -d, -f1); rate=$(printf '%s' "$fp" | cut -d, -f2)
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$n" "${det:-NONE}" "${route:-none}" "${samp:--}" "$ex" "${fail:--}" "$db" "${codec:--}" "${rate:--}" "$fex" >> "$OUT"
done
column -t -s$'\t' "$OUT"
