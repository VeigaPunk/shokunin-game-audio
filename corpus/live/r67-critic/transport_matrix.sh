#!/usr/bin/env bash
# r67-critic transport matrix on the 10 tracked autodetect members.
# transports: file | pipe(cat|sox -) | redir(sox - < f) | devstdin-path |
#             devstdin-on-pipe | fifo-path(writer) | fifo-fd(sox - < fifo)
set -u
cd "$(dirname "$0")"
R=/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live
L=logs; mkdir -p "$L"
TSV=matrix.tsv
printf 'member\ttransport\tdetected\texit\tsamples\tlastline\n' > "$TSV"
emit() { local m=$1 t=$2 ex=$3 log=$4 det samp tail
  det=$(grep -o "detected file format type \`[^']*'" "$log" | head -1 | sed "s/.*\`//;s/'//")
  samp=$(grep -o 'Samples read: *[0-9]*' "$log" | head -1 | grep -o '[0-9]*$')
  tail=$(grep -E 'FAIL|WARN' "$log" | tail -1 | sed 's/.*sox //' | cut -c1-110)
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$m" "$t" "${det:--}" "$ex" "${samp:--}" "${tail:-ok}" >> "$TSV"
}
for d in round-65 round-66; do
  for f in "$R/$d"/*.wav; do
    [ -e "$f" ] || continue; n=$(basename "$f")
    timeout 20 sox -V4 "$f" -n stat                 >"$L/$n.file.log" 2>&1;      emit "$n" file      $? "$L/$n.file.log"
    cat "$f" | timeout 20 sox -V4 - -n stat         >"$L/$n.pipe.log" 2>&1;      emit "$n" pipe      $? "$L/$n.pipe.log"
    timeout 20 sox -V4 - -n stat < "$f"             >"$L/$n.redir.log" 2>&1;     emit "$n" redir     $? "$L/$n.redir.log"
    timeout 20 sox -V4 /dev/stdin -n stat < "$f"    >"$L/$n.devstdin.log" 2>&1;  emit "$n" devstdin  $? "$L/$n.devstdin.log"
    cat "$f" | timeout 20 sox -V4 /dev/stdin -n stat >"$L/$n.devstdinpipe.log" 2>&1; emit "$n" devstdin-pipe $? "$L/$n.devstdinpipe.log"
  done
done
echo done
