#!/usr/bin/env bash
# r69 critic: independent 4-transport x renamed-member matrix.
# Arms mirror measure_audio.py TRANSPORT_R67_ARMS + transport_leg extraction:
#   file (named+seekable) / stdin_pipe (anon) / redirected_fd (anon+seekable)
#   / fifo_path (named non-seekable, 1.0s writer linger = FIFO_WRITER_HOLD_S)
# Fields mirror transport_leg: detected / exit / samples / error(post-': msg or
# whole FAIL line when no post-quote pattern) / last-FAIL-line.
set -u
cd "$(dirname "$0")/../../.."   # audio-shokunin repo root
PROBE_DIR="corpus/live/r69-critic/probes"
OUT="corpus/live/r69-critic/runs"
LOG="corpus/live/r69-critic/logs"
HOLD="${HOLD:-1.0}"
TAG="${TAG:-hold${HOLD}}"
mkdir -p "$OUT" "$LOG"
TSV="$OUT/matrix-${TAG}.tsv"
printf 'member\tarm\texit\tdetected\tsamples\terror\tlastfail\n' > "$TSV"

extract() { # stderr-file -> detected TAB samples TAB error TAB lastfail
  local f="$1" det samp err lf
  det=$(grep -o "detected file format type \`[^']*'" "$f" | head -1 | sed "s/.*\`//;s/'//")
  samp=$(grep -o 'Samples read: *[0-9]*' "$f" | head -1 | grep -o '[0-9]*')
  lf=$(grep 'sox FAIL' "$f" | tail -1)
  # mirror transport_error(): text after LAST `':  on last FAIL line; else whole line
  err=$(printf '%s' "$lf" | grep -o "': .*$" | tail -1 | sed "s/^': //")
  [ -z "$err" ] && err="$lf"
  printf '%s\t%s\t%s\t%s' "${det:-null}" "${samp:-null}" "${err:-none}" "${lf:-none}"
}

for probe in "$PROBE_DIR"/cz_nomatch.* "$PROBE_DIR"/r68_nomatch.*; do
  name=$(basename "$probe")
  for arm in file stdin_pipe redirected_fd fifo_path; do
    lf="$LOG/${name}.${arm}.${TAG}.stderr"
    case "$arm" in
      file)
        timeout 10 sox -V6 "$probe" -n stat >/dev/null 2>"$lf"; code=$? ;;
      stdin_pipe)
        cat "$probe" | timeout 10 sox -V6 - -n stat >/dev/null 2>"$lf"; code=$? ;;
      redirected_fd)
        timeout 10 sox -V6 - -n stat >/dev/null 2>"$lf" < "$probe"; code=$? ;;
      fifo_path)
        # mirror transport_matrix: tmp dir + fifo named EXACTLY path.name;
        # ONE open held through write + HOLD linger (writer lingers attached)
        tmpd=$(mktemp -d -t transport-r67-XXXXXXXX)
        fifo="$tmpd/$name"
        mkfifo "$fifo"
        ( exec 3>"$fifo"; cat "$probe" >&3; sleep "$HOLD"; exec 3>&- ) &
        wpid=$!
        timeout 10 sox -V6 "$fifo" -n stat >/dev/null 2>"$lf"; code=$?
        wait $wpid 2>/dev/null; rm -rf "$tmpd" ;;
    esac
    row=$(extract "$lf")
    printf '%s\t%s\t%s\t%s\n' "$name" "$arm" "$code" "$row" >> "$TSV"
  done
done
column -t -s$'\t' "$TSV"
