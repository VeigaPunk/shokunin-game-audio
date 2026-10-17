#!/bin/bash
# r73-critic: controls + hazards receipts -> controls.tsv
# (a) pw-cat .snd 2x2: seekable x name; (b) pw-cat extension variants on fifo;
# (c) mpv hcom 2x2: seekable x name; (d) mpv fd://0; (e) daemon gate; (f) pacing; (g) hazards.
set -u
R=/home/vgpnk/Projects/shokunin/audio-shokunin
L=$R/corpus/live
O=$R/corpus/live/r73-critic
CTS=$O/controls.tsv
: > "$CTS"
SND=$L/round-69/extsuffix_nomatch.snd
HCOM=$L/round-66/pair_dec_hcom.wav
TONE=$L/frontier-pipewire/tone4s.wav

leg() { # label consumer transport rc wall_ms note
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4" "$5" "$6" >> "$CTS"
}

d=$(mktemp -d /tmp/r73c-ctl-XXXXXX)
cp "$SND" "$d/m.snd"; cp "$SND" "$d/m.dat"
mkfifo "$d/f.snd"; mkfifo "$d/f.dat"; mkfifo "$d/f.wav"; mkfifo "$d/f.SND"; mkfifo "$d/f.fifo"
( cat "$SND" > "$d/f.snd" ) & w1=$!; ( cat "$SND" > "$d/f.dat" ) & w2=$!
( cat "$SND" > "$d/f.wav" ) & w3=$!; ( cat "$SND" > "$d/f.SND" ) & w4=$!
( cat "$SND" > "$d/f.fifo" ) & w5=$!
sleep 0.2
s=$(date +%s%N); timeout -s KILL 15 pw-cat -p "$d/m.snd" > "$O/ctl-pwcat-seek-named.out" 2> "$O/ctl-pwcat-seek-named.err"; rc=$?; e=$(date +%s%N)
leg pwcat-seek-named pw-cat file $rc $(( (e-s)/1000000 )) ".snd bytes, regular file named m.snd"
s=$(date +%s%N); timeout -s KILL 15 pw-cat -p "$d/m.dat" > "$O/ctl-pwcat-seek-unnamed.out" 2> "$O/ctl-pwcat-seek-unnamed.err"; rc=$?; e=$(date +%s%N)
leg pwcat-seek-unnamed pw-cat file $rc $(( (e-s)/1000000 )) "$(head -1 "$O/ctl-pwcat-seek-unnamed.err")"
s=$(date +%s%N); timeout -s KILL 15 pw-cat -p "$d/f.snd" > "$O/ctl-pwcat-pipe-named.out" 2> "$O/ctl-pwcat-pipe-named.err"; rc=$?; e=$(date +%s%N)
leg pwcat-pipe-named pw-cat fifo $rc $(( (e-s)/1000000 )) ".snd bytes, fifo named f.snd"
s=$(date +%s%N); timeout -s KILL 15 pw-cat -p "$d/f.dat" > "$O/ctl-pwcat-pipe-unnamed.out" 2> "$O/ctl-pwcat-pipe-unnamed.err"; rc=$?; e=$(date +%s%N)
leg pwcat-pipe-unnamed pw-cat fifo $rc $(( (e-s)/1000000 )) "$(head -1 "$O/ctl-pwcat-pipe-unnamed.err")"
s=$(date +%s%N); timeout -s KILL 15 pw-cat -p "$d/f.wav" > "$O/ctl-pwcat-pipe-wav.out" 2> "$O/ctl-pwcat-pipe-wav.err"; rc=$?; e=$(date +%s%N)
leg pwcat-pipe-f.wav pw-cat fifo $rc $(( (e-s)/1000000 )) "$(head -1 "$O/ctl-pwcat-pipe-wav.err")"
s=$(date +%s%N); timeout -s KILL 15 pw-cat -p "$d/f.SND" > "$O/ctl-pwcat-pipe-SND.out" 2> "$O/ctl-pwcat-pipe-SND.err"; rc=$?; e=$(date +%s%N)
leg pwcat-pipe-f.SND pw-cat fifo $rc $(( (e-s)/1000000 )) "case-insensitive extension fallback"
s=$(date +%s%N); timeout -s KILL 15 pw-cat -p "$d/f.fifo" > "$O/ctl-pwcat-pipe-f.fifo.out" 2> "$O/ctl-pwcat-pipe-f.fifo.err"; rc=$?; e=$(date +%s%N)
leg pwcat-pipe-f.fifo pw-cat fifo $rc $(( (e-s)/1000000 )) "$(head -1 "$O/ctl-pwcat-pipe-f.fifo.err")"
wait $w1 2>/dev/null; wait $w2 2>/dev/null; wait $w3 2>/dev/null; wait $w4 2>/dev/null; wait $w5 2>/dev/null

cp "$HCOM" "$d/h.dat"; mkfifo "$d/h.wav"
( cat "$HCOM" > "$d/h.wav" ) & w6=$!
sleep 0.2
timeout -s KILL 15 mpv --no-config --vo=null --ao=null --audio-display=no --really-quiet --log-file="$O/ctl-mpv-seek-unnamed.log" "$d/h.dat" > /dev/null 2>&1; rc=$?
leg mpv-seek-unnamed mpv file $rc - "hcom bytes, regular file named h.dat ($(grep -c 'Seek failed (Operation not permitted)' "$O/ctl-mpv-seek-unnamed.log") x refresh-seek-EPERM)"
timeout -s KILL 15 mpv --no-config --vo=null --ao=null --audio-display=no --really-quiet --log-file="$O/ctl-mpv-pipe-named.log" "$d/h.wav" > /dev/null 2>&1; rc=$?
leg mpv-pipe-named mpv fifo $rc - "hcom bytes, fifo named h.wav ($(grep -c 'Stream is not seekable' "$O/ctl-mpv-pipe-named.log") x non-seekable)"
wait $w6 2>/dev/null
timeout -s KILL 15 mpv --no-config --vo=null --ao=null --audio-display=no --really-quiet --log-file="$O/ctl-mpv-fd0.log" fd://0 < "$HCOM" > /dev/null 2>&1; rc=$?
leg mpv-fd0 mpv fd://0 $rc - "stdin redirect from regular file is seekable ($(grep -c 'Seek failed (Operation not permitted)' "$O/ctl-mpv-fd0.log") x refresh-seek-EPERM)"
mkfifo "$d/s2.snd"; ( cat "$SND" > "$d/s2.snd" ) & w7=$!
sleep 0.2
timeout -s KILL 15 mpv --no-config --vo=null --ao=null --audio-display=no --really-quiet --log-file="$O/ctl-mpv-pipe-named-snd.log" "$d/s2.snd" > /dev/null 2>&1; rc=$?
leg mpv-pipe-named-snd mpv fifo $rc - "snd bytes, fifo named s2.snd (mpv has no extension fallback)"
wait $w7 2>/dev/null

PIPEWIRE_RUNTIME_DIR=$O/emptyrt timeout -s KILL 8 pw-cat -p "$HCOM" > "$O/ctl-nodaemon-file.out" 2> "$O/ctl-nodaemon-file.err"; rc=$?
leg nodaemon-file pw-cat file $rc - "$(head -1 "$O/ctl-nodaemon-file.err")"
mkfifo "$d/nw"; PIPEWIRE_RUNTIME_DIR=$O/emptyrt timeout -s KILL 8 pw-cat -p "$d/nw" > "$O/ctl-nodaemon-nowriterfifo.out" 2> "$O/ctl-nodaemon-nowriterfifo.err"; rc=$?
leg nodaemon-nowriterfifo pw-cat fifo $rc - "daemon gate precedes open() (no writer attached; returns instantly)"

s=$(date +%s%N); timeout -s KILL 20 pw-cat -p "$TONE" > "$O/ctl-pace-file.out" 2> "$O/ctl-pace-file.err"; rc=$?; e=$(date +%s%N)
leg pace-file-tone4s pw-cat file $rc $(( (e-s)/1000000 )) "4.0s tone; wall ~= duration"
mkfifo "$d/p1"; ( cat "$TONE" > "$d/p1" ) & w8=$!
sleep 0.2
s=$(date +%s%N); timeout -s KILL 20 pw-cat -p "$d/p1" > "$O/ctl-pace-instant.out" 2> "$O/ctl-pace-instant.err"; rc=$?; e=$(date +%s%N)
leg pace-fifo-instant pw-cat fifo $rc $(( (e-s)/1000000 )) "instant dump; wall ~= duration => playback-paced"
wait $w8 2>/dev/null
mkfifo "$d/p2"; ( for i in $(seq 1 40); do dd if="$TONE" bs=1600 skip=$((i-1)) count=1 2>/dev/null; sleep 0.2; done > "$d/p2" ) & w9=$!
sleep 0.2
s=$(date +%s%N); timeout -s KILL 30 pw-cat -p "$d/p2" > "$O/ctl-pace-trickle.out" 2> "$O/ctl-pace-trickle.err"; rc=$?; e=$(date +%s%N)
leg pace-fifo-trickle pw-cat fifo $rc $(( (e-s)/1000000 )) "8s delivery of 4s audio; streams, no underrun abort"
wait $w9 2>/dev/null

mkfifo "$d/p3"
s=$(date +%s%N); timeout -s TERM --kill-after=3 3 pw-cat -p "$d/p3" > "$O/ctl-nowriter.out" 2> "$O/ctl-nowriter.err"; rc=$?; e=$(date +%s%N)
leg nowriter-SIGTERM pw-cat fifo $rc $(( (e-s)/1000000 )) "TERM@3s ignored; KILL@+3s -> rc137, wall 6s"
mkfifo "$d/p4"; ( : > "$d/p4" ) & w10=$!
sleep 0.2
s=$(date +%s%N); timeout -s KILL 10 pw-cat -p "$d/p4" > "$O/ctl-emptywriter.out" 2> "$O/ctl-emptywriter.err"; rc=$?; e=$(date +%s%N)
leg emptywriter pw-cat fifo $rc $(( (e-s)/1000000 )) "$(head -1 "$O/ctl-emptywriter.err")"
wait $w10 2>/dev/null
s=$(date +%s%N); timeout -s KILL 5 pw-cat -p --target 0 "$HCOM" > "$O/ctl-target0.out" 2> "$O/ctl-target0.err"; rc=$?; e=$(date +%s%N)
leg target0-hang pw-cat file $rc $(( (e-s)/1000000 )) "unlinked stream hangs; KILL required"
rm -rf "$d"
echo "controls written: $CTS ($(wc -l < "$CTS") rows)"
