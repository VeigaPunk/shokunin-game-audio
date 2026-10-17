#!/bin/bash
# r73-critic: pw-cat pacing + writer-attach hazard controls.
set -u
R=/home/vgpnk/Projects/shokunin/audio-shokunin
T=$R/corpus/live/frontier-pipewire/tone4s.wav
O=$R/corpus/live/r73-critic
d=$(mktemp -d /tmp/r73c-pace-XXXXXX)

echo "== tone4s.wav: $(stat -c '%s bytes' $T)"

s=$(date +%s%N)
timeout -s KILL 20 pw-cat -p "$T" > "$O/pwcat-file-tone4s.stdout" 2> "$O/pwcat-file-tone4s.stderr"
rc=$?; e=$(date +%s%N)
echo "pwcat file tone4s rc=$rc wall_ms=$(( (e-s)/1000000 ))"

mkfifo "$d/p1"
( cat "$T" > "$d/p1" ) & w=$!
sleep 0.2
s=$(date +%s%N)
timeout -s KILL 20 pw-cat -p "$d/p1" > "$O/pwcat-fifo-tone4s-instant.stdout" 2> "$O/pwcat-fifo-tone4s-instant.stderr"
rc=$?; e=$(date +%s%N)
echo "pwcat fifo tone4s instant rc=$rc wall_ms=$(( (e-s)/1000000 ))"
wait $w 2>/dev/null

mkfifo "$d/p2"
( for i in $(seq 1 40); do dd if="$T" bs=1600 skip=$((i-1)) count=1 2>/dev/null; sleep 0.2; done > "$d/p2" ) & w=$!
sleep 0.2
s=$(date +%s%N)
timeout -s KILL 30 pw-cat -p "$d/p2" > "$O/pwcat-fifo-tone4s-trickle.stdout" 2> "$O/pwcat-fifo-tone4s-trickle.stderr"
rc=$?; e=$(date +%s%N)
echo "pwcat fifo tone4s trickle rc=$rc wall_ms=$(( (e-s)/1000000 ))"
wait $w 2>/dev/null

mkfifo "$d/p3"
s=$(date +%s%N)
timeout -s TERM --kill-after=3 3 pw-cat -p "$d/p3" > "$O/pwcat-fifo-nowriter.stdout" 2> "$O/pwcat-fifo-nowriter.stderr"
rc=$?; e=$(date +%s%N)
echo "pwcat fifo no-writer (TERM@3s, KILL@+3s) rc=$rc wall_ms=$(( (e-s)/1000000 ))"

mkfifo "$d/p4"
( : > "$d/p4" ) & w=$!
sleep 0.2
s=$(date +%s%N)
timeout -s KILL 10 pw-cat -p "$d/p4" > "$O/pwcat-fifo-emptywriter.stdout" 2> "$O/pwcat-fifo-emptywriter.stderr"
rc=$?; e=$(date +%s%N)
echo "pwcat fifo empty-writer rc=$rc wall_ms=$(( (e-s)/1000000 ))"
wait $w 2>/dev/null
rm -rf "$d"
