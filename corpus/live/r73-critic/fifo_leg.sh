#!/bin/bash
# r73-critic: generic fifo leg. usage: fifo_leg.sh <label> <member> <tool-cmd...>
# tool-cmd receives the fifo path appended as last arg. Writer: cat member > fifo.
set -u
label=$1; member=$2; shift 2
d=$(mktemp -d /tmp/r73c-fifo-XXXXXX)
fifo=$d/m.fifo
mkfifo "$fifo"
( cat "$member" > "$fifo" ) &
wpid=$!
sleep 0.2
s=$(date +%s%N)
timeout -s KILL 20 "$@" "$fifo" > "/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r73-critic/$label.stdout" 2> "/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r73-critic/$label.stderr"
rc=$?
e=$(date +%s%N)
echo "$label rc=$rc wall_ms=$(( (e - s) / 1000000 ))"
wait "$wpid" 2>/dev/null
rm -rf "$d"
