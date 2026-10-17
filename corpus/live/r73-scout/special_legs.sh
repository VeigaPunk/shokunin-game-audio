#!/usr/bin/env bash
# r73-scout: pw-cat / mpv special-semantics legs (writer-attach, daemon gate,
# pacing, SIGTERM immunity). Outputs under logs/special/.
set -u
cd "$(dirname "$0")"
export XDG_RUNTIME_DIR=/run/user/1000
S="$HOME/Projects/shokunin/audio-shokunin"
M="$S/corpus/live/round-66/pair_dec_hcom.wav"
L=logs/special
mkdir -p "$L"
now() { date +%s.%N; }
wall() { python3 -c "print(f'{$2-$1:.3f}')"; }

echo "### A1 daemon gate: PIPEWIRE_RUNTIME_DIR=emptyrt pw-cat -p file"
t0=$(now); PIPEWIRE_RUNTIME_DIR="$PWD/emptyrt" timeout -s KILL 8 pw-cat -p "$M" >"$L/A1.out" 2>&1; rc=$?; t1=$(now)
echo "A1 rc=$rc wall=$(wall $t0 $t1) :: $(tr '\n' ' ' <"$L/A1.out")"

echo "### A2 daemon gate: PIPEWIRE_RUNTIME_DIR=emptyrt pw-cat -p fifo (no writer)"
rm -f "$L/nw.fifo"; mkfifo "$L/nw.fifo"
t0=$(now); PIPEWIRE_RUNTIME_DIR="$PWD/emptyrt" timeout -s KILL 8 pw-cat -p "$L/nw.fifo" >"$L/A2.out" 2>&1; rc=$?; t1=$(now)
echo "A2 rc=$rc wall=$(wall $t0 $t1) :: $(tr '\n' ' ' <"$L/A2.out")"

echo "### A3 context: pactl info with dead runtime dir"
XDG_RUNTIME_DIR="$PWD/emptyrt" pactl info >"$L/A3.out" 2>&1; echo "A3 rc=$? :: $(head -1 "$L/A3.out")"

echo "### B1 writerless fifo: block + wchan + SIGTERM immunity"
rm -f "$L/b1.fifo"; mkfifo "$L/b1.fifo"
pw-cat -p "$L/b1.fifo" >"$L/B1.out" 2>&1 &
PID=$!
sleep 0.8
{ echo "pid=$PID"; echo "wchan=$(cat /proc/$PID/wchan 2>/dev/null)";
  echo "state=$(awk '{print $3}' /proc/$PID/stat 2>/dev/null)";
  echo "stdout_bytes=$(stat -c%s "$L/B1.out")"; } >"$L/B1.status"
kill -TERM "$PID" 2>/dev/null
sleep 1.5
if kill -0 "$PID" 2>/dev/null; then echo "sigterm: still alive 1.5s after SIGTERM" >>"$L/B1.status";
else echo "sigterm: died" >>"$L/B1.status"; fi
kill -KILL "$PID" 2>/dev/null; wait "$PID" 2>/dev/null; echo "rc_after_kill=$?" >>"$L/B1.status"
cat "$L/B1.status"
rm -f "$L/b1.fifo"

echo "### B2 writerless fifo under timeout -s KILL 5"
rm -f "$L/b2.fifo"; mkfifo "$L/b2.fifo"
t0=$(now); timeout -s KILL 5 pw-cat -p "$L/b2.fifo" >"$L/B2.out" 2>&1; rc=$?; t1=$(now)
echo "B2 rc=$rc wall=$(wall $t0 $t1)"; rm -f "$L/b2.fifo"

echo "### B3 writerless fifo under TERM(4s)+KILL-after(2s)"
rm -f "$L/b3.fifo"; mkfifo "$L/b3.fifo"
t0=$(now); timeout -k 2 4 pw-cat -p "$L/b3.fifo" >"$L/B3.out" 2>&1; rc=$?; t1=$(now)
echo "B3 rc=$rc wall=$(wall $t0 $t1)"; rm -f "$L/b3.fifo"

echo "### C1 zero-byte writer closes"
rm -f "$L/c1.fifo"; mkfifo "$L/c1.fifo"
( exec 3>"$L/c1.fifo"; sleep 0.2 ) &
t0=$(now); timeout -s KILL 8 pw-cat -p "$L/c1.fifo" >"$L/C1.out" 2>&1; rc=$?; t1=$(now)
echo "C1 rc=$rc wall=$(wall $t0 $t1) :: $(tr '\n' ' ' <"$L/C1.out")"; wait 2>/dev/null; rm -f "$L/c1.fifo"

echo "### D1 pacing: instant dump of tone4s (4 s audio) into fifo"
rm -f "$L/d1.fifo"; mkfifo "$L/d1.fifo"
( cat tone4s.wav >"$L/d1.fifo" ) &
t0=$(now); timeout -s KILL 20 pw-cat -p "$L/d1.fifo" >"$L/D1.out" 2>&1; rc=$?; t1=$(now)
echo "D1 rc=$rc wall=$(wall $t0 $t1)"; wait 2>/dev/null; rm -f "$L/d1.fifo"

echo "### D2 pacing: 1600B chunks / 0.2s on one writer fd (tone4s)"
rm -f "$L/d2.fifo"; mkfifo "$L/d2.fifo"
python3 - "$L/d2.fifo" <<'EOF' &
import sys, time
data = open('tone4s.wav','rb').read()
with open(sys.argv[1], 'wb', buffering=0) as fh:
    for i in range(0, len(data), 1600):
        fh.write(data[i:i+1600]); time.sleep(0.2)
EOF
t0=$(now); timeout -s KILL 25 pw-cat -p "$L/d2.fifo" >"$L/D2.out" 2>&1; rc=$?; t1=$(now)
echo "D2 rc=$rc wall=$(wall $t0 $t1)"; wait 2>/dev/null; rm -f "$L/d2.fifo"

echo "### D3 raw mode (-a) over fifo, tone4s"
rm -f "$L/d3.fifo"; mkfifo "$L/d3.fifo"
( cat tone4s.wav >"$L/d3.fifo" ) &
t0=$(now); timeout -s KILL 20 pw-cat -p -a "$L/d3.fifo" >"$L/D3.out" 2>&1; rc=$?; t1=$(now)
echo "D3 rc=$rc wall=$(wall $t0 $t1) :: $(tr '\n' ' ' <"$L/D3.out")"; wait 2>/dev/null; rm -f "$L/d3.fifo"

echo "### E1 --target 0 (unlinked stream) on tone4s file: TERM(4s)+KILL-after(2s)"
t0=$(now); timeout -k 2 4 pw-cat -p --target 0 tone4s.wav >"$L/E1.out" 2>&1; rc=$?; t1=$(now)
echo "E1 rc=$rc wall=$(wall $t0 $t1) :: $(tr '\n' ' ' <"$L/E1.out")"

echo "### F1 mpv writerless fifo (timeout -s KILL 5)"
rm -f "$L/f1.fifo"; mkfifo "$L/f1.fifo"
t0=$(now); timeout -s KILL 5 mpv --no-config --vo=null --ao=null --audio-display=no --really-quiet --log-file="$L/F1.log" "$L/f1.fifo" >"$L/F1.out" 2>&1; rc=$?; t1=$(now)
echo "F1 rc=$rc wall=$(wall $t0 $t1)"; rm -f "$L/f1.fifo"

echo "### F2 mpv fifo with 1.0s writer linger (dec_hcom)"
rm -f "$L/f2.fifo"; mkfifo "$L/f2.fifo"
python3 - "$L/f2.fifo" "$M" <<'EOF' &
import sys, time
data = open(sys.argv[2],'rb').read()
with open(sys.argv[1], 'wb', buffering=0) as fh:
    fh.write(data); time.sleep(1.0)
EOF
t0=$(now); timeout -s KILL 15 mpv --no-config --vo=null --ao=null --audio-display=no --really-quiet --log-file="$L/F2.log" "$L/f2.fifo" >"$L/F2.out" 2>&1; rc=$?; t1=$(now)
echo "F2 rc=$rc wall=$(wall $t0 $t1) :: $(grep -c 'Stream is not seekable' "$L/F2.log") not-seekable-lines; $(grep -E 'finished playback' "$L/F2.log" | tail -1)"; wait 2>/dev/null; rm -f "$L/f2.fifo"

echo "### F3 mpv fifo, zero-byte writer closes"
rm -f "$L/f3.fifo"; mkfifo "$L/f3.fifo"
( exec 3>"$L/f3.fifo"; sleep 0.2 ) &
t0=$(now); timeout -s KILL 8 mpv --no-config --vo=null --ao=null --audio-display=no --really-quiet --log-file="$L/F3.log" "$L/f3.fifo" >"$L/F3.out" 2>&1; rc=$?; t1=$(now)
echo "F3 rc=$rc wall=$(wall $t0 $t1) :: $(grep -E 'finished playback|Found ' "$L/F3.log" | tail -2 | tr '\n' ' | ')"; wait 2>/dev/null; rm -f "$L/f3.fifo"

echo "### done"
