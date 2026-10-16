#!/usr/bin/env bash
# r87 reviewer — lock experiments. All locks live inside this seat's
# receipts dir; the lane lock (worktree corpus/live/) is never touched.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
TMP1="$HERE/tmp1"; TMP2="$HERE/tmp2"
mkdir -p "$TMP1" "$TMP2"
for t in tree1 tree2; do
  mkdir -p "$HERE/$t/corpus/fixtures" "$HERE/$t/corpus/live"
  cp "$HERE/runs/measure_audio_d1e687b9.py" "$HERE/$t/corpus/fixtures/measure_audio.py"
done
P="$HERE/r87r_lock_probe.py"
R="$HERE/runs/lock"

# --- resolve: r87 path under two TMPDIRs, same tree --------------------
TMPDIR="$TMP1" PYTHONDONTWRITEBYTECODE=1 python3 "$P" resolve tree1 "$R-resolve-tree1-tmp1.json"
TMPDIR="$TMP2" PYTHONDONTWRITEBYTECODE=1 python3 "$P" resolve tree1 "$R-resolve-tree1-tmp2.json"
TMPDIR="$TMP1" PYTHONDONTWRITEBYTECODE=1 python3 "$P" resolve tree2 "$R-resolve-tree2-tmp1.json"

# --- experiment A: same ROOT, two TMPDIRs (the r84-F1 case) -----------
TMPDIR="$TMP1" PYTHONDONTWRITEBYTECODE=1 python3 "$P" hold tree1 6 "$R-holdA.json" &
HOLD=$!
sleep 1.5
TMPDIR="$TMP2" PYTHONDONTWRITEBYTECODE=1 python3 "$P" wait tree1 "$R-waitA.json"
wait $HOLD

# --- experiment B: cross-ROOT, same TMPDIR (frozen-tree co-tenancy) ---
TMPDIR="$TMP1" PYTHONDONTWRITEBYTECODE=1 python3 "$P" hold tree1 5 "$R-holdB.json" &
HOLD=$!
sleep 1.2
TMPDIR="$TMP1" PYTHONDONTWRITEBYTECODE=1 python3 "$P" wait tree2 "$R-waitB.json"
wait $HOLD

# --- experiment C: worktree-path contrast (read-only stat only) --------
ls -l "$HERE/../measure_audio-pwbind-r87.lock" > "$R-lane-lock.txt" 2>&1 || true
echo "done"
