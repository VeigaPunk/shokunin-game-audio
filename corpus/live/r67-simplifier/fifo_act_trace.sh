#!/bin/bash
# Who blocks on the fifo arm for an act-detected member? strace the open/exec.
F=/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/round-66/pair_dec_act.wav
D=$(mktemp -d); FIFO=$D/m.wav; mkfifo $FIFO
( cat $F > $FIFO ) &
strace -f -e trace=openat,execve,read,lseek -o $D/tr.txt timeout 6 sox -V6 $FIFO -n stat 2>$D/err.txt
echo "sox exit=$?"
grep -n "openat\|execve\|ESPIPE\|fifo\|m.wav" $D/tr.txt | tail -30
echo "--- stderr tail ---"; tail -5 $D/err.txt
cp $D/tr.txt /home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r67-simplifier/strace-fifo-act.txt
rm -rf $D
