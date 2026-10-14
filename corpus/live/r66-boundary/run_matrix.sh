#!/usr/bin/env bash
# r66-boundary probe matrix. Per fixture x mode:
#   file : sox -V4 f -n stat
#   pipe : cat f | sox -V4 - -n stat          (non-seekable stdin)
#   redir: sox -V4 - -n stat < f             (seekable stdin)
#   t-*  : forced handler legs (detection skipped) — pipe and file
#   i    : sox --i f                          (input-info surface)
#   ff   : ffprobe codec/format               (cross-implementation compare)
# Logs -> runs/logs/<fixture>.<mode>.log ; summary -> runs/matrix.tsv
set -u
cd "$(dirname "$0")"
P=probes; L=runs/logs; mkdir -p "$L"
TSV=runs/matrix.tsv
printf 'fixture\tmode\tdetected\texit\tsamples\tinfo_or_fail\n' > "$TSV"

emit() { # fixture mode exit logfile
  local f=$1 mode=$2 ex=$3 log=$4 det samp tail
  det=$(grep -o "detected file format type \`[^']*'" "$log" | head -1 | sed "s/.*\`//;s/'//")
  samp=$(grep -o 'Samples read: *[0-9]*' "$log" | head -1 | grep -o '[0-9]*$')
  tail=$(grep -E 'FAIL|WARN' "$log" | tail -1 | sed 's/.*sox //' | cut -c1-100)
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$f" "$mode" "${det:--}" "$ex" "${samp:--}" "${tail:-ok}" >> "$TSV"
}

for f in "$P"/*.bin "$P"/*.wav; do
  [ -e "$f" ] || continue
  n=$(basename "$f")

  sox -V4 "$f" -n stat >"$L/$n.file.log" 2>&1;         emit "$n" file  $? "$L/$n.file.log"
  cat "$f" | sox -V4 - -n stat >"$L/$n.pipe.log" 2>&1;  emit "$n" pipe  $? "$L/$n.pipe.log"
  sox -V4 - -n stat < "$f" >"$L/$n.redir.log" 2>&1;     emit "$n" redir $? "$L/$n.redir.log"

  for t in wve gsrt hcom act wav; do
    cat "$f" | sox -V4 -t $t - -n stat >"$L/$n.pt$t.log" 2>&1
    emit "$n" "pipe-t$t" $? "$L/$n.pt$t.log"
  done
  for t in wve gsrt hcom; do
    sox -V4 -t $t "$f" -n stat >"$L/$n.ft$t.log" 2>&1;  emit "$n" "file-t$t" $? "$L/$n.ft$t.log"
  done

  sox --i "$f" >"$L/$n.i.log" 2>&1;                     emit "$n" info  $? "$L/$n.i.log"
  { echo "== ffprobe =="; ffprobe -v error -show_entries stream=codec_name:format=format_name -of csv=p=0 "$f" 2>&1; echo "ffprobe_exit=$?"; } >"$L/$n.ff.log" 2>&1
  ff=$(cat "$L/$n.ff.log" | tr '\n' '|' | cut -c1-100)
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$n" ffprobe '-' '-' '-' "$ff" >> "$TSV"
done
echo "== matrix done =="
