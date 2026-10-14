#!/usr/bin/env bash
# r64-scribe sweep: per-variant codec map + decode counts.
# Routes recorded per file: ffprobe negotiation, ffmpeg direct decode,
# SoX detection (-V4), SoX decode bytes, SoX --i handler tag.
set -u
cd "$(dirname "$0")"
V=variants
L=logs
T=results.tsv
printf 'file\tvb\tcontainer\tcodec\tbprs\tdur\tpackets\tff_dec\tff_exit\tff_err\tsox_detect\tsox_f32\tsox_exit\tsox_tag\n' > "$T"

for f in "$V"/*.wav; do
  n=$(basename "$f" .wav)
  vb=${n#vb}; vb=${vb%%_*}
  cont=${n##*_c}

  codec=$(ffprobe -v error -show_entries stream=codec_name -of csv=p=0 "$f" 2>/dev/null)
  bprs=$(ffprobe -v error -show_entries stream=bits_per_raw_sample -of csv=p=0 "$f" 2>/dev/null)
  dur=$(ffprobe -v error -show_entries stream=duration -of csv=p=0 "$f" 2>/dev/null)
  pkts=$(ffprobe -v error -show_entries packet=size -of csv=p=0 "$f" 2>/dev/null \
         | awk -F, '{print $NF}' | paste -sd+ -)

  ffmpeg -v warning -i "$f" -f f32le -acodec pcm_f32le - 2>"$L/ff_$n.err" >"$L/ff_$n.raw"
  ffexit=$?
  ffdec=$(( $(wc -c < "$L/ff_$n.raw") / 4 ))
  fferr=$(grep -c 'Invalid PCM packet' "$L/ff_$n.err" || true)

  sox -V4 "$f" -n stat >"$L/sox_$n.log" 2>&1
  detect=$(grep -o "detected file format type \`[^']*'" "$L/sox_$n.log" | sed "s/.*\`//;s/'//" | head -1)

  sox "$f" -t f32 - 2>"$L/soxdec_$n.err" >"$L/soxdec_$n.raw"
  sexit=$?
  sf32=$(( $(wc -c < "$L/soxdec_$n.raw") / 4 ))

  tag=$(sox --i "$f" 2>/dev/null | grep -c '(ffmpeg)' || true)

  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$n" "$vb" "$cont" "$codec" "$bprs" "$dur" "$pkts" \
    "$ffdec" "$ffexit" "$fferr" "$detect" "$sf32" "$sexit" "$tag" >> "$T"
done
echo "rows: $(( $(wc -l < "$T") - 1 ))"
