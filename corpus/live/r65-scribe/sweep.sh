#!/usr/bin/env bash
# r65-scribe probe sweep: per file record detected type, route signatures,
# decode outcome, forced-reader verdicts, ffprobe comparison. All receipts
# land in logs/.
set -u
cd "$(dirname "$0")"
V=variants; L=logs
mkdir -p "$L"
OUT=results.tsv
printf 'file\tsize\tsha256\tdetected\tsox_stat_exit\tdetect_line\tsox_i_exit\tsox_i_suffix\tsox_dec_exit\tsox_dec_bytes\tsox_dec_err\tffp_fmt\tffp_codec\tffp_exit\ttwav_exit\ttwav_err\ttact_exit\ttact_bytes\ttact_err\ttgsrt_exit\ttgsrt_err\tthcom_exit\tthcom_err\n' > "$OUT"

for f in "$V"/*.wav "$V"/*.bin; do
  base=$(basename "$f"); lg="$L/$base"
  size=$(stat -c%s "$f"); sha=$(sha256sum "$f" | cut -d' ' -f1)

  sox -V4 "$f" -n stat >"$lg.stat.out" 2>"$lg.stat.err"; sx=$?
  det=$(grep -o "detected file format type \`[^']*'" "$lg.stat.err" | sed "s/.*\`//;s/'//")
  dline=$(grep -o "detected file format type \`[^']*'" "$lg.stat.err")
  [ -z "$det" ] && det="NONE"; [ -z "$dline" ] && dline=$(tail -1 "$lg.stat.err" | tr '\t' ' ')

  sox --i "$f" >"$lg.i.out" 2>"$lg.i.err"; ix=$?
  suffix=$(grep -o "(ffmpeg)" "$lg.i.out" || true)
  [ -z "$suffix" ] && { grep -q "Input File" "$lg.i.out" && suffix="native-info"; }
  [ -z "$suffix" ] && suffix="err:$(tail -1 "$lg.i.err" | tr '\t' ' ' | cut -c1-60)"

  sox "$f" -t f32 - 2>"$lg.dec.err" | wc -c >"$lg.dec.out"; dx=${PIPESTATUS[0]}
  dbytes=$(cat "$lg.dec.out")
  derr=$(tail -1 "$lg.dec.err" | tr '\t' ' ' | cut -c1-80)

  ffprobe -v error -show_entries format=format_name:stream=codec_name -of default=noprint_wrappers=1 "$f" >"$lg.ffp.out" 2>"$lg.ffp.err"; fx=$?
  ffmt=$(grep -o 'format_name=[^ ]*' "$lg.ffp.out" | cut -d= -f2 | tr ',' '+')
  fcodec=$(grep -o 'codec_name=[^ ]*' "$lg.ffp.out" | cut -d= -f2 | tr ',' '+' | head -1)
  [ -z "$ffmt" ] && ffmt="-"; [ -z "$fcodec" ] && fcodec="$(tail -1 "$lg.ffp.err" | tr '\t' ' ' | cut -c1-50)"

  sox -t wav "$f" -n stat >"$lg.twav.out" 2>"$lg.twav.err"; twx=$?
  twerr=$(tail -1 "$lg.twav.err" | tr '\t' ' ' | cut -c1-60)
  sox -t act "$f" -t f32 - 2>"$lg.tact.err" | wc -c >"$lg.tact.out"; tax=${PIPESTATUS[0]}
  tabytes=$(cat "$lg.tact.out")
  taerr=$(tail -1 "$lg.tact.err" | tr '\t' ' ' | cut -c1-60)
  sox -t gsrt "$f" -n stat >"$lg.tgsrt.out" 2>"$lg.tgsrt.err"; tgx=$?
  tgerr=$(tail -1 "$lg.tgsrt.err" | tr '\t' ' ' | cut -c1-60)
  sox -t hcom "$f" -n stat >"$lg.thcom.out" 2>"$lg.thcom.err"; thx=$?
  therr=$(tail -1 "$lg.thcom.err" | tr '\t' ' ' | cut -c1-60)

  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$base" "$size" "$sha" "$det" "$sx" "$dline" "$ix" "$suffix" "$dx" "$dbytes" "$derr" \
    "$ffmt" "$fcodec" "$fx" "$twx" "$twerr" "$tax" "$tabytes" "$taerr" "$tgx" "$tgerr" "$thx" "$therr" >> "$OUT"
done
column -t -s$'\t' "$OUT" | cut -c1-220
