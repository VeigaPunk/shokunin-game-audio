#!/usr/bin/env bash
# r69 scout: identical no-match bytes x extension suffix x 4 transports.
# Arms mirror measure_audio.py TRANSPORT_R67_ARMS: file / stdin_pipe /
# redirected_fd / fifo_path. Each leg: sox -V6 <input> -n stat, 10 s cap.
set -u
cd "$(dirname "$0")/../../.."   # audio-shokunin repo root
PROBE_DIR="corpus/live/r69-scout/probes"
OUT="corpus/live/r69-scout/runs"
LOG="corpus/live/r69-scout/logs"
mkdir -p "$OUT" "$LOG"
TSV="$OUT/matrix-r69.tsv"
printf 'member\tarm\texit\tdetected\tsamples\terror\n' > "$TSV"

extract() { # stderr-file -> detected<TAB>samples<TAB>error
  local f="$1" det samp err
  det=$(grep -o "detected file format type \`[^']*'" "$f" | head -1 | sed "s/.*\`//;s/'//")
  samp=$(grep -o 'Samples read: *[0-9]*' "$f" | head -1 | grep -o '[0-9]*')
  err=$(grep 'sox FAIL' "$f" | tail -1 | sed "s/^[^:]*sox FAIL //")
  printf '%s\t%s\t%s' "${det:-null}" "${samp:-null}" "${err:-none}"
}

for probe in "$PROBE_DIR"/*; do
  name=$(basename "$probe")
  for arm in file stdin_pipe redirected_fd fifo_path; do
    lf="$LOG/${name}.${arm}.stderr"
    case "$arm" in
      file)
        timeout 10 sox -V6 "$probe" -n stat >/dev/null 2>"$lf"; code=$? ;;
      stdin_pipe)
        cat "$probe" | timeout 10 sox -V6 - -n stat >/dev/null 2>"$lf"; code=$? ;;
      redirected_fd)
        timeout 10 sox -V6 - -n stat >/dev/null 2>"$lf" < "$probe"; code=$? ;;
      fifo_path)
        fifo=$(mktemp -u --suffix=".$name")
        mkfifo "$fifo"
        ( cat "$probe" > "$fifo"; sleep 1 ) &
        timeout 10 sox -V6 "$fifo" -n stat >/dev/null 2>"$lf"; code=$?
        wait 2>/dev/null; rm -f "$fifo" ;;
    esac
    row=$(extract "$lf")
    printf '%s\t%s\t%s\t%s\n' "$name" "$arm" "$code" "$row" >> "$TSV"
  done
done
column -t -s$'\t' "$TSV"
