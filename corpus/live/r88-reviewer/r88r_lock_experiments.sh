#!/usr/bin/env bash
# r88 reviewer — fixed-path lock experiments (bounded, ~10 s).
# 1) resolved path invariance across TMPDIRs
# 2) same-ROOT cross-TMPDIR serialization (hold 3.0 s, second waits)
# 3) cross-ROOT (altroot) NOT serialized — the r86-F1/r87-F7 class
set -u
LANE=/home/vgpnk/Projects/shokunin/audio-shokunin
R=$LANE/corpus/live/r88-reviewer
TREE_FX=$R/tree/corpus/fixtures/measure_audio.py
ALT_FX=$R/altroot/corpus/fixtures/measure_audio.py
mkdir -p "$R/tmpdir-a" "$R/tmpdir-b" "$R/altroot/corpus/fixtures"
cp "$TREE_FX" "$ALT_FX"

echo "== part1: resolved lock path under two TMPDIRs (same fixture copy)"
TMPDIR="$R/tmpdir-a" PYTHONDONTWRITEBYTECODE=1 python3 "$R/lockchild.py" "$TREE_FX"
TMPDIR="$R/tmpdir-b" PYTHONDONTWRITEBYTECODE=1 python3 "$R/lockchild.py" "$TREE_FX"

echo "== part2: same-ROOT cross-TMPDIR serialization (A holds 3.0 s)"
TMPDIR="$R/tmpdir-a" PYTHONDONTWRITEBYTECODE=1 python3 "$R/lockchild.py" "$TREE_FX" 3.0 > "$R/receipts/lock-part2-A.txt" 2>&1 &
A=$!
sleep 0.4
TMPDIR="$R/tmpdir-b" PYTHONDONTWRITEBYTECODE=1 python3 "$R/lockchild.py" "$TREE_FX" > "$R/receipts/lock-part2-B.txt" 2>&1
wait $A
echo "A: $(cat "$R/receipts/lock-part2-A.txt" | tr '\n' ' ')"
echo "B: $(cat "$R/receipts/lock-part2-B.txt" | tr '\n' ' ')"

echo "== part3: cross-ROOT (altroot) NOT serialized (A holds 3.0 s)"
TMPDIR="$R/tmpdir-a" PYTHONDONTWRITEBYTECODE=1 python3 "$R/lockchild.py" "$TREE_FX" 3.0 > "$R/receipts/lock-part3-A.txt" 2>&1 &
A=$!
sleep 0.4
TMPDIR="$R/tmpdir-b" PYTHONDONTWRITEBYTECODE=1 python3 "$R/lockchild.py" "$ALT_FX" > "$R/receipts/lock-part3-B.txt" 2>&1
wait $A
echo "A: $(cat "$R/receipts/lock-part3-A.txt" | tr '\n' ' ')"
echo "B: $(cat "$R/receipts/lock-part3-B.txt" | tr '\n' ' ')"

echo "== done $(date -u +%FT%TZ)"
