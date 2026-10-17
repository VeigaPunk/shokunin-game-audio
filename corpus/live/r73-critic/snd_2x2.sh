#!/bin/bash
# r73-critic: seekable x name 2x2 control for pw-cat on the .snd member bytes.
# Rows: (a) regular file named m.snd (seekable+named)  (b) regular file named m.dat (seekable+unnamed)
#       (c) fifo named m.snd (non-seekable+named)      (d) fifo named m.dat (non-seekable+unnamed)
set -u
R=/home/vgpnk/Projects/shokunin/audio-shokunin
M=$R/corpus/live/round-69/extsuffix_nomatch.snd
O=$R/corpus/live/r73-critic
d=$(mktemp -d /tmp/r73c-2x2-XXXXXX)
cp "$M" "$d/m.snd"
cp "$M" "$d/m.dat"
mkfifo "$d/f.snd"
mkfifo "$d/f.dat"
run() { # label tool args...
  label=$1; shift
  s=$(date +%s%N)
  timeout -s KILL 20 "$@" > "$O/$label.stdout" 2> "$O/$label.stderr"
  rc=$?
  e=$(date +%s%N)
  echo "$label rc=$rc wall_ms=$(( (e-s)/1000000 ))"
}
run pwcat-seek-named   pw-cat -p "$d/m.snd"
run pwcat-seek-unnamed pw-cat -p "$d/m.dat"
( cat "$M" > "$d/f.snd" ) & w1=$!
( cat "$M" > "$d/f.dat" ) & w2=$!
sleep 0.2
run pwcat-pipe-named   pw-cat -p "$d/f.snd"
run pwcat-pipe-unnamed pw-cat -p "$d/f.dat"
wait $w1 2>/dev/null; wait $w2 2>/dev/null
rm -rf "$d"
