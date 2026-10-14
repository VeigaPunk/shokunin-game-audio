#!/bin/bash
# Detection-fork constructions: same member, truncated fifo delivery vs full.
# usage: detection_fork.sh <member> <deliver_bytes> [linger_s]
set -u
M="$1"; N="${2:-0}"; LINGER="${3:-1.0}"
TMP=$(mktemp -d /tmp/r68critic-df-XXXX); trap 'rm -rf "$TMP"' EXIT
FIFO="$TMP/$(basename "$M")"; mkfifo "$FIFO"

echo "=== member: $M ; fifo delivers first $N bytes then closes (linger $LINGER after) ==="
( head -c "$N" "$M" > "$FIFO"; sleep "$LINGER" ) & W=$!
out=$(timeout 15 sox -V6 "$FIFO" -n stat 2>&1); code=$?
kill "$W" 2>/dev/null; wait "$W" 2>/dev/null
echo "exit=$code"; echo "$out" | grep -E "detected file format|Samples read|FAIL" | tail -4
