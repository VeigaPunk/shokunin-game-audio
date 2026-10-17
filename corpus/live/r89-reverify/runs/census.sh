#!/usr/bin/env bash
# r89 RE-VERIFY census: law re-derivation over every re-verifier receipt,
# plus the baseline comparison against the r89 verifier's 1464/1484.
set -u
LANE=/home/vgpnk/Projects/shokunin/audio-shokunin
OUT=$LANE/corpus/live/r89-reverify/runs
RECEIPTS=$(ls $OUT/*.receipt.json | grep -v normal)
echo "receipts: $(echo "$RECEIPTS" | wc -l)"
python3 "$OUT/laws2.py" $RECEIPTS > "$OUT/laws-matrix.txt" 2>&1
tail -1 "$OUT/laws-matrix.txt"
echo "--- per-receipt fail/blocked lines:"
grep -E " FAIL | BLOCKED " "$OUT/laws-matrix.txt" | sed 's/^LAW //' | awk '{print $1, $2, $3, $4, $5}' | sort | uniq -c | sort -rn | head -20
