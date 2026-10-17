#!/usr/bin/env bash
# r80-baseline comparisons — per-case field stability, pid-normalized.
# Reference groups are pre-commit; fresh groups are the post-r79-commit
# battery (runs-a, runs-b).
set -u
cd /home/vgpnk/Projects/shokunin/audio-shokunin
OUT=corpus/live/r80-baseline
PC="python3 $OUT/percase.py"

B=corpus/live/r79-author/receipt-runB-20261015T072219089606Z-capture-r79.json
C=corpus/live/r79-author/receipt-runC-20261015T072746218296Z-capture-r79.json
V1=corpus/live/runs/20261015T080513286525Z-capture-r79/measurements.json
V2=corpus/live/runs/20261015T081045790824Z-capture-r79/measurements.json
D=corpus/live/runs/20261015T084630169601Z-capture-r79/measurements.json
A79=$OUT/runs-a/capture-r79.receipt.json
B79=$OUT/runs-b/capture-r79.receipt.json

ANCHOR=corpus/live/r79-baseline/anchor-receipt-20261015T060513912020Z-capture-r78.json
R78=corpus/live/runs/20261015T081421351571Z-capture-r78/measurements.json
A78=$OUT/runs-a/capture-r78.receipt.json
B78=$OUT/runs-b/capture-r78.receipt.json

NORMALREF=corpus/live/runs/20261014T142151899785Z-normal/measurements.json
ANORM=$OUT/runs-a/normal.receipt.json
BNORM=$OUT/runs-b/normal.receipt.json

# primary: per-case stability of the r79 family vs the r79-author receipts
$PC --split 2 "$B" "$C" "$A79" "$B79" > "$OUT/stability-r79-vs-author-BC.txt" 2>&1
# wider reference set (author B/C + verifier V1/V2), all pre-fold bytes
$PC --split 4 "$B" "$C" "$V1" "$V2" "$A79" "$B79" > "$OUT/stability-r79-6way.txt" 2>&1
# same-bytes control: fold-verify run D (the committed blob) vs the battery
$PC --split 1 "$D" "$A79" "$B79" > "$OUT/stability-r79-vs-runD.txt" 2>&1
# r78 family: pre-r79 clean tree (anchor) and pre-fold r79 tree (verify R78)
$PC --split 1 "$ANCHOR" "$A78" "$B78" > "$OUT/stability-r78-vs-anchor.txt" 2>&1
$PC --split 1 "$R78" "$A78" "$B78" > "$OUT/stability-r78-vs-prefold.txt" 2>&1
# battery self-consistency (pure run noise floor)
$PC --split 1 "$A78" "$B78" > "$OUT/stability-r78-runsAB.txt" 2>&1
$PC --split 1 "$A79" "$B79" > "$OUT/stability-r79-runsAB.txt" 2>&1
# normal family vs the tracked canonical receipt
$PC --split 1 "$NORMALREF" "$ANORM" "$BNORM" > "$OUT/stability-normal.txt" 2>&1
# verdict-surface delta (legs / classes / named outcomes)
python3 "$OUT/fold-delta.py" "$B" "$C" "$V1" "$V2" -- "$A79" "$B79" \
  > "$OUT/fold-delta-prefold-vs-commit.txt" 2>&1

{
  for f in "$B" "$C" "$V1" "$V2" "$D" "$ANCHOR" "$R78" "$NORMALREF" \
           "$A79" "$B79" "$A78" "$B78" "$ANORM" "$BNORM"; do
    [ -f "$f" ] && sha256sum "$f"
  done
} > "$OUT/receipt-shas.txt"
echo COMPARE_DONE
