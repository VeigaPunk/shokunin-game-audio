#!/bin/bash
# r73-critic: mpv seekability x name 2x2 control on the hcom member bytes.
set -u
R=/home/vgpnk/Projects/shokunin/audio-shokunin
M=$R/corpus/live/round-66/pair_dec_hcom.wav
O=$R/corpus/live/r73-critic
d=$(mktemp -d /tmp/r73c-mpv2x2-XXXXXX)
cp "$M" "$d/m.dat"
mkfifo "$d/f.wav"
run() {
  label=$1; shift
  s=$(date +%s%N)
  timeout -s KILL 15 "$@" > "$O/$label.stdout" 2> "$O/$label.stderr"
  rc=$?
  e=$(date +%s%N)
  echo "$label rc=$rc wall_ms=$(( (e-s)/1000000 ))"
}
run mpv-seek-unnamed mpv --no-config --vo=null --ao=null --audio-display=no --really-quiet --log-file="$O/mpv-file-unnamed.dat.log" "$d/m.dat"
( cat "$M" > "$d/f.wav" ) & w=$!
sleep 0.2
run mpv-pipe-named mpv --no-config --vo=null --ao=null --audio-display=no --really-quiet --log-file="$O/mpv-fifo-named-wav.log" "$d/f.wav"
wait $w 2>/dev/null
# fd://0 non-seekable corroboration (stdin redirect from a regular file)
s=$(date +%s%N)
timeout -s KILL 15 mpv --no-config --vo=null --ao=null --audio-display=no --really-quiet --log-file="$O/mpv-fd0.log" fd://0 < "$M" > "$O/mpv-fd0.stdout" 2> "$O/mpv-fd0.stderr"
rc=$?
e=$(date +%s%N)
echo "mpv fd://0 rc=$rc wall_ms=$(( (e-s)/1000000 ))"
rm -rf "$d"
