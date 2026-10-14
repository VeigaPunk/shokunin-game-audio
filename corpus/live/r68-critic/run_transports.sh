#!/bin/bash
# r68 critic: 4-transport runner mirroring measure_audio.py transport_matrix arms.
# usage: run_transports.sh <member> [fifo_basename]
# Emits one block per arm: detected format, exit, samples, last sox FAIL line.
set -u
M="$1"
FBASE="${2:-$(basename "$M")}"
TMP=$(mktemp -d /tmp/r68critic-fifo-XXXX)
trap 'rm -rf "$TMP"' EXIT

echo "=== member: $M (fifo name: $FBASE) ==="

# arm 1: file
echo "--- file: sox -V6 $M -n stat"
out=$(sox -V6 "$M" -n stat 2>&1); code=$?
echo "exit=$code"
echo "$out" | grep -E "detected file format|Samples read|FAIL|assuming input" | tail -6

# arm 2: stdin_pipe (real pipe via cat)
echo "--- stdin_pipe: cat $M | sox -V6 - -n stat"
out=$(cat "$M" | sox -V6 - -n stat 2>&1); code=$?
echo "exit=$code"
echo "$out" | grep -E "detected file format|Samples read|FAIL|assuming input" | tail -6

# arm 3: redirected_fd (stdin = member's own fd, seekable)
echo "--- redirected_fd: sox -V6 - -n stat < $M"
out=$(sox -V6 - -n stat < "$M" 2>&1); code=$?
echo "exit=$code"
echo "$out" | grep -E "detected file format|Samples read|FAIL|assuming input" | tail -6

# arm 4: fifo_path (named fifo, one-shot writer + 1.0s linger — harness protocol)
FIFO="$TMP/$FBASE"
mkfifo "$FIFO"
echo "--- fifo_path: sox -V6 $FIFO -n stat (writer: write once, linger 1.0s)"
( cat "$M" > "$FIFO"; sleep 1.0 ) &
W=$!
out=$(timeout 15 sox -V6 "$FIFO" -n stat 2>&1); code=$?
kill "$W" 2>/dev/null; wait "$W" 2>/dev/null
echo "exit=$code"
echo "$out" | grep -E "detected file format|Samples read|FAIL|assuming input" | tail -6
echo
