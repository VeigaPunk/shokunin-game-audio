#!/usr/bin/env bash
# r65-scout measurement harness. For each probe:
#   detect = sox -V4 'detected file format type' line (authoritative)
#   route  = sox --i 'Input File' suffix + Duration presence
#   decode = sox <f> -t f32 - | wc -c   (+ exit)
#   ffprobe codec_name (route-agnostic container read)
# Writes runs/probe-table.tsv + per-probe logs under runs/logs/.
set -u
ROOT="$(cd "$(dirname "$0")" && pwd)"
P="$ROOT/probes"
R="$ROOT/runs"
mkdir -p "$R/logs"
OUT="$R/probe-table.tsv"
printf 'probe\tbytes\tdetected\tsox_exit\tdecoded_bytes\tsoxi_input\tsoxi_duration\tffprobe_codec\n' > "$OUT"

for f in "$P"/*; do
    name="$(basename "$f")"
    bytes=$(stat -c %s "$f")
    log="$R/logs/$name.log"
    : > "$log"

    # detection + decode (single sox run, -V4 to stderr)
    sox -V4 "$f" -t f32 - >"$R/logs/$name.f32" 2>"$R/logs/$name.v4"
    sox_exit=$?
    det=$(grep -o "detected file format type .\{0,1\}[a-zA-Z0-9_-]*'" "$R/logs/$name.v4" | head -1 | sed "s/.*type .\{0,1\}\([a-zA-Z0-9_-]*\)'/\1/")
    [ -z "$det" ] && det="(none)"
    decoded=$(stat -c %s "$R/logs/$name.f32")
    [ "$decoded" = "0" ] && rm -f "$R/logs/$name.f32"

    # soxi route signature
    soxi_input=$(sox --i "$f" 2>"$R/logs/$name.i.err" | grep 'Input File' | sed 's/^Input File *: *//')
    soxi_dur=$(sox --i "$f" 2>/dev/null | grep -c 'Duration')
    [ -z "$soxi_input" ] && soxi_input="(soxi failed: $(tr '\n' ' ' <"$R/logs/$name.i.err" | head -c 80))"

    # ffprobe container read
    codec=$(ffprobe -v error -show_entries stream=codec_name -of csv=p=0 "$f" 2>/dev/null | head -1)
    [ -z "$codec" ] && codec="(none)"

    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$name" "$bytes" "$det" "$sox_exit" "$decoded" "$soxi_input" "$soxi_dur" "$codec" >> "$OUT"
    {
        echo "=== $name  ($bytes B)"
        echo "--- detect: $det   sox_exit: $sox_exit   decoded_bytes: $decoded"
        echo "--- soxi: $soxi_input   duration_lines: $soxi_dur   ffprobe: $codec"
        echo "--- -V4 tail:"; tail -6 "$R/logs/$name.v4"
    } >> "$log"
done
column -t -s $'\t' "$OUT"
