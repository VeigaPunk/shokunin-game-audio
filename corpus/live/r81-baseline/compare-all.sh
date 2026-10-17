#!/usr/bin/env bash
# r81-baseline comparisons — per-case field stability (pid-normalized),
# verdict-surface deltas, byte identity, row census.
#
# Fresh group: runs-a / runs-b, both produced by the fixture INSIDE the
# frozen tree at HEAD 15c6a35b (fixture sha ac9c64a1…).
# Reference groups: the nearest landed receipts per family.
#   normal      : the tracked canonical receipt (sha 8e8cdad6…)
#   capture-r78 : r79-verify R78 (081421351571Z) + newest tracked (055701745739Z)
#   capture-r79 : r80-baseline runs-a/runs-b (085638725489Z / 090549097852Z,
#                 pre-r80-fold bytes)
#   module-r80  : r80 fold run D (161018039047Z, 90 s pre-commit) + 160033687459Z
set -u
ROOT=/home/vgpnk/Projects/shokunin/audio-shokunin
cd "$ROOT"
OUT=corpus/live/r81-baseline
PC="python3 $OUT/percase.py"
A=$OUT/runs-a
B=$OUT/runs-b

CANON_NORMAL=corpus/live/runs/20261014T142151899785Z-normal/measurements.json
R78A=corpus/live/runs/20261015T081421351571Z-capture-r78/measurements.json
R78B=corpus/live/runs/20261015T055701745739Z-capture-r78/measurements.json
R79A=corpus/live/runs/20261015T085638725489Z-capture-r79/measurements.json
R79B=corpus/live/runs/20261015T090549097852Z-capture-r79/measurements.json
R80A=corpus/live/runs/20261015T160033687459Z-module-r80/measurements.json
R80B=corpus/live/runs/20261015T161018039047Z-module-r80/measurements.json

# --- noise floor: runs-a vs runs-b on identical bytes -------------------
$PC --split 1 "$A/normal.receipt.json" "$B/normal.receipt.json" \
  > "$OUT/stability-normal-runsAB.txt" 2>&1
$PC --split 1 "$A/capture-r78.receipt.json" "$B/capture-r78.receipt.json" \
  > "$OUT/stability-r78-runsAB.txt" 2>&1
$PC --split 1 "$A/capture-r79.receipt.json" "$B/capture-r79.receipt.json" \
  > "$OUT/stability-r79-runsAB.txt" 2>&1
$PC --split 1 "$A/module-r80.receipt.json" "$B/module-r80.receipt.json" \
  > "$OUT/stability-r80-runsAB.txt" 2>&1

# --- fresh battery vs the nearest landed reference group ----------------
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
  for f in "$CANON_NORMAL" "$R78A" "$R78B" "$R79A" "$R79B" "$R80A" "$R80B" \
           "$A/normal.receipt.json" "$A/capture-r78.receipt.json" \
           "$A/capture-r79.receipt.json" "$A/module-r80.receipt.json" \
           "$B/normal.receipt.json" "$B/capture-r78.receipt.json" \
           "$B/capture-r79.receipt.json" "$B/module-r80.receipt.json"; do
    [ -f "$f" ] && sha256sum "$f"
  done
} > "$OUT/receipt-shas.txt"
echo COMPARE_DONE
