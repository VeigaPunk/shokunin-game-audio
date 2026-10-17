#!/bin/bash
# r73-critic: named-fifo extension controls for pw-cat + sndfile-info corroboration.
set -u
R=/home/vgpnk/Projects/shokunin/audio-shokunin
M=$R/corpus/live/round-69/extsuffix_nomatch.snd
O=$R/corpus/live/r73-critic
d=$(mktemp -d /tmp/r73c-ext-XXXXXX)
for n in f.wav f.SND f.snd f.fifo; do mkfifo "$d/$n"; done
( cat "$M" > "$d/f.wav"  ) & w1=$!
( cat "$M" > "$d/f.SND"  ) & w2=$!
( cat "$M" > "$d/f.snd"  ) & w3=$!
( cat "$M" > "$d/f.fifo" ) & w4=$!
sleep 0.2
for n in f.wav f.SND f.snd f.fifo; do
  s=$(date +%s%N)
  timeout -s KILL 15 pw-cat -p "$d/$n" > "$O/pwcat-pipe-$n.stdout" 2> "$O/pwcat-pipe-$n.stderr"
  rc=$?
  e=$(date +%s%N)
  echo "pwcat pipe $n rc=$rc wall_ms=$(( (e-s)/1000000 ))"
done
wait $w1 2>/dev/null; wait $w2 2>/dev/null; wait $w3 2>/dev/null; wait $w4 2>/dev/null
# sndfile-info corroboration on a fresh named fifo
mkfifo "$d/g.snd"
( cat "$M" > "$d/g.snd" ) & w5=$!
sleep 0.2
s=$(date +%s%N)
timeout -s KILL 15 sndfile-info "$d/g.snd" > "$O/sndfile-info-pipe-named.txt" 2>&1
rc=$?
e=$(date +%s%N)
echo "sndfile-info pipe named .snd rc=$rc wall_ms=$(( (e-s)/1000000 ))"
wait $w5 2>/dev/null
rm -rf "$d"
