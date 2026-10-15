#!/usr/bin/env bash
# r82-baseline comparisons — per-case field stability (pid-normalized),
# verdict-surface deltas, byte identity, row census.
#
# Fresh group: runs-a / runs-b, both produced by the fixture INSIDE the
# frozen tree at HEAD b7d80d0 (fixture sha 5eaba74b…).
# Reference groups: the r81-baseline receipts (same four modes, previous
# freeze 15c6a35b / fixture ac9c64a1) + the tracked canonical normal receipt.
set -u
ROOT=/home/vgpnk/Projects/shokunin/audio-shokunin
cd "$ROOT"
OUT=corpus/live/r82-baseline
R81=corpus/live/r81-baseline
PC="python3 $OUT/percase.py"
A=$OUT/runs-a
B=$OUT/runs-b

CANON_NORMAL=corpus/live/runs/20261014T142151899785Z-normal/measurements.json
R78A=$R81/runs-a/capture-r78.receipt.json
R78B=$R81/runs-b/capture-r78.receipt.json
R79A=$R81/runs-a/capture-r79.receipt.json
R79B=$R81/runs-b/capture-r79.receipt.json
R80A=$R81/runs-a/module-r80.receipt.json
R80B=$R81/runs-b/module-r80.receipt.json

# --- noise floor: runs-a vs runs-b on identical bytes -------------------
$PC --split 1 "$A/normal.receipt.json" "$B/normal.receipt.json" \
  > "$OUT/stability-normal-runsAB.txt" 2>&1
$PC --split 1 "$A/capture-r78.receipt.json" "$B/capture-r78.receipt.json" \
  > "$OUT/stability-r78-runsAB.txt" 2>&1
$PC --split 1 "$A/capture-r79.receipt.json" "$B/capture-r79.receipt.json" \
  > "$OUT/stability-r79-runsAB.txt" 2>&1
$PC --split 1 "$A/module-r80.receipt.json" "$B/module-r80.receipt.json" \
  > "$OUT/stability-r80-runsAB.txt" 2>&1

# --- fresh battery vs the r81-baseline reference group ------------------
$PC --split 1 "$CANON_NORMAL" "$A/normal.receipt.json" "$B/normal.receipt.json" \
  > "$OUT/stability-normal-vs-canonical.txt" 2>&1
$PC --split 2 "$R78A" "$R78B" "$A/capture-r78.receipt.json" "$B/capture-r78.receipt.json" \
  > "$OUT/stability-r78-vs-prior.txt" 2>&1
$PC --split 2 "$R79A" "$R79B" "$A/capture-r79.receipt.json" "$B/capture-r79.receipt.json" \
  > "$OUT/stability-r79-vs-prior.txt" 2>&1
$PC --split 2 "$R80A" "$R80B" "$A/module-r80.receipt.json" "$B/module-r80.receipt.json" \
  > "$OUT/stability-r80-vs-prior.txt" 2>&1

# --- verdict surface (sets/multisets, not index-wise) -------------------
python3 "$OUT/fold-delta.py" "$R78A" "$R78B" -- \
  "$A/capture-r78.receipt.json" "$B/capture-r78.receipt.json" \
  > "$OUT/fold-delta-r78.txt" 2>&1
python3 "$OUT/fold-delta.py" "$R79A" "$R79B" -- \
  "$A/capture-r79.receipt.json" "$B/capture-r79.receipt.json" \
  > "$OUT/fold-delta-r79.txt" 2>&1
python3 "$OUT/fold-delta.py" "$R80A" "$R80B" -- \
  "$A/module-r80.receipt.json" "$B/module-r80.receipt.json" \
  > "$OUT/fold-delta-r80.txt" 2>&1

# --- byte identity + row census -----------------------------------------
python3 "$OUT/byteid.py" > "$OUT/byte-identity.txt" 2>&1
python3 "$OUT/rows.py" -v \
  "$A/normal.receipt.json" "$A/capture-r78.receipt.json" \
  "$A/capture-r79.receipt.json" "$A/module-r80.receipt.json" \
  "$B/normal.receipt.json" "$B/capture-r78.receipt.json" \
  "$B/capture-r79.receipt.json" "$B/module-r80.receipt.json" \
  > "$OUT/rows.txt" 2>&1

# --- receipt sha table ---------------------------------------------------
{
  echo "# reference receipts"
  for f in "$CANON_NORMAL" "$R78A" "$R78B" "$R79A" "$R79B" "$R80A" "$R80B"; do
    [ -f "$f" ] && sha256sum "$f"
  done
  echo "# r82 fresh receipts (runs-a / runs-b)"
  for f in "$A/normal.receipt.json" "$A/capture-r78.receipt.json" \
           "$A/capture-r79.receipt.json" "$A/module-r80.receipt.json" \
           "$B/normal.receipt.json" "$B/capture-r78.receipt.json" \
           "$B/capture-r79.receipt.json" "$B/module-r80.receipt.json"; do
    [ -f "$f" ] && sha256sum "$f"
  done
} > "$OUT/receipt-shas.txt"
echo COMPARE_DONE
