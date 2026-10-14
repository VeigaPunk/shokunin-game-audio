#!/usr/bin/env bash
# Verifier's own eyes: run the 4 transports on each r68 member with raw sox
# (same -V6 invocation the fixture uses), capturing exit + FAIL/detected lines.
set -u
REPO=/home/vgpnk/Projects/shokunin/audio-shokunin
OUT=$REPO/corpus/live/r68-verifier/raw-transports.txt
: > "$OUT"
for member in posttable_nomatch.wav txw_piperefuse.wav; do
  p=$REPO/corpus/live/round-68/$member
  echo "===== $member =====" >> "$OUT"
  # file
  echo "-- file --" >> "$OUT"
  sox -V6 "$p" -n stat 2>&1 | grep -E "detected file format type|sox FAIL|Samples read|Input File" >> "$OUT"
  echo "exit=$?" >> "$OUT"
  sox -V6 "$p" -n stat >/dev/null 2>>"$OUT"; echo "raw_exit_file=$?" >> "$OUT"
  # stdin_pipe
  echo "-- stdin_pipe --" >> "$OUT"
  cat "$p" | sox -V6 - -n stat 2>&1 | grep -E "detected file format type|sox FAIL|Samples read" >> "$OUT"
  cat "$p" | sox -V6 - -n stat >/dev/null 2>/tmp/vpipe.err; echo "raw_exit_pipe=$?" >> "$OUT"
  grep -E "sox FAIL|detected" /tmp/vpipe.err >> "$OUT"
  # redirected_fd
  echo "-- redirected_fd --" >> "$OUT"
  sox -V6 - -n stat < "$p" 2>&1 | grep -E "detected file format type|sox FAIL|Samples read" >> "$OUT"
  sox -V6 - -n stat < "$p" >/dev/null 2>/tmp/vredir.err; echo "raw_exit_redir=$?" >> "$OUT"
  grep -E "sox FAIL|detected" /tmp/vredir.err >> "$OUT"
  # fifo_path
  echo "-- fifo_path --" >> "$OUT"
  d=$(mktemp -d); fifo=$d/$member; mkfifo "$fifo"
  ( cat "$p" > "$fifo"; sleep 1 ) &
  sox -V6 "$fifo" -n stat 2>&1 | grep -E "detected file format type|sox FAIL|Samples read" >> "$OUT"
  ( cat "$p" > "$fifo"; sleep 1 ) &
  sox -V6 "$fifo" -n stat >/dev/null 2>/tmp/vfifo.err; echo "raw_exit_fifo=$?" >> "$OUT"
  grep -E "sox FAIL|detected" /tmp/vfifo.err >> "$OUT"
  wait; rm -rf "$d"
done
cat "$OUT"
