#!/usr/bin/env bash
# r89 simplifier — rerun the whole proof suite from the pinned blob.
# Writes only inside this proofs/ directory and $TMPDIR scratch.
set -u
cd "$(dirname "$0")"
PROOFDIR="$(pwd)"
export TMPDIR="${TMPDIR:-/home/vgpnk/Projects/shokunin/tmp}"
export PYTHONDONTWRITEBYTECODE=1
TREE="$(cd ../../../.. && pwd)"

echo "== [1/9] fold (exact-string, region-scoped) =="
python3 fold-r89-simplifier.py || exit 1

echo "== [2/9] patch round-trip (patch -p1 -> byte identity) =="
RT="$TMPDIR/r89-simplifier-rt"
rm -rf "$RT"; mkdir -p "$RT/corpus/fixtures"
cp base-measure_audio.py "$RT/corpus/fixtures/measure_audio.py"
( cd "$RT" && patch -p1 --silent < "$PROOFDIR/fold.diff" ) || exit 1
cmp "$RT/corpus/fixtures/measure_audio.py" folded/measure_audio.py \
  && echo "ROUNDTRIP-BYTE-IDENTICAL" || exit 1
git -C "$TREE" apply --check "$PROOFDIR/fold.diff" \
  && echo "GIT-APPLY-CHECK-CLEAN vs committed tree" || exit 1
git -C "$TREE" apply --numstat "$PROOFDIR/fold.diff"
rm -rf "$RT"

echo "== [3/9] py_compile + ast.parse (folded copy) =="
python3 -m py_compile folded/measure_audio.py || exit 1
python3 -c "import ast; ast.parse(open('folded/measure_audio.py').read()); \
print('AST-PARSE-CLEAN')" || exit 1

echo "== [4/9] static proofs (S1..S13) =="
python3 static-proofs.py || exit 1

echo "== [5/9] static census + call-site dump =="
python3 census-r89-simplifier.py base-measure_audio.py > census.txt || exit 1
python3 callsite-dump.py base-measure_audio.py > callsite-dump.txt || exit 1
echo "census/callsite written"

echo "== [6/9] executed differential (D1..D8) =="
python3 differential.py || exit 1

echo "== [7/9] receipt census over the two pinned runs =="
python3 receipt-census.py || exit 1

echo "== [8/9] fixed-path lock proof (L0..L9) =="
python3 lock-proof.py || exit 1

echo "== [9/9] tracked tree untouched =="
git -C "$TREE" diff --quiet HEAD -- corpus/fixtures/measure_audio.py \
  && echo "TRACKED-FIXTURE-UNMODIFIED" || exit 1
sha256sum "$TREE/corpus/fixtures/measure_audio.py"

echo
echo "RUN-ALL: ALL SUITES PASS (patch NOT applied; nothing committed)"
