#!/usr/bin/env bash
# r68-scout transport x fallback matrix runner.
# Arms: file / stdin_pipe / redirected_fd / fifo_path (+extras dspipe, dsredir,
# fifo_noext, popen) on every probe in probes/.
# Output: runs/matrix.tsv + logs/<probe>.<arm>.stderr
set -u
cd "$(dirname "$0")"
OUT=runs/matrix.tsv
mkdir -p runs logs fifo
printf 'probe\tarm\texit\tdetected\tsamples\terror\n' > "$OUT"

leg() { # $1=probe $2=arm $3..=cmd...
  local probe="$1" arm="$2"; shift 2
  local err log="logs/${probe##*/}.${arm}.stderr"
  "$@" > /dev/null 2> "$log"
  local code=$?
  local det samp
  det=$(grep -o "detected file format type \`[^']*'" "$log" | head -1 | sed "s/.*\`//;s/'//")
  samp=$(grep -o 'Samples read: *[0-9]*' "$log" | grep -o '[0-9]*')
  err=$(grep 'sox FAIL' "$log" | tail -1 | sed "s/^.*': //")
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "${probe##*/}" "$arm" "$code" "${det:--}" "${samp:--}" "${err:--}" >> "$OUT"
}

for probe in probes/*; do
  [ -f "$probe" ] || continue
  base=${probe##*/}
  leg "$base" file        sox -V4 "$probe" -n stat
  leg "$base" stdin_pipe  bash -c "cat '$probe' | sox -V4 - -n stat"
  leg "$base" redir       bash -c "sox -V4 - -n stat < '$probe'"
  # fifo with the probe's own basename (extension preserved)
  fifo="fifo/$base"; rm -f "$fifo"; mkfifo "$fifo"
  ( cat "$probe" > "$fifo"; sleep 1 ) &
  leg "$base" fifo_path   sox -V4 "$fifo" -n stat
  wait 2>/dev/null
  # fifo with NO extension in the name
  fifo2="fifo/noext_member"; rm -f "$fifo2"; mkfifo "$fifo2"
  ( cat "$probe" > "$fifo2"; sleep 1 ) &
  leg "$base" fifo_noext  sox -V4 "$fifo2" -n stat
  wait 2>/dev/null
  # named seekable fd without extension: /dev/stdin on a redirected file
  leg "$base" dsredir     bash -c "sox -V4 /dev/stdin -n stat < '$probe'"
  # named unseekable without extension: /dev/stdin on a pipe
  leg "$base" dspipe      bash -c "cat '$probe' | sox -V4 /dev/stdin -n stat"
  # |cmd io_type=pipe
  leg "$base" popen       sox -V4 "|cat $probe" -n stat
done
echo "=== matrix ==="
column -t -s$'\t' "$OUT"
