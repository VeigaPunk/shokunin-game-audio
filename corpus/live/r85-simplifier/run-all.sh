#!/usr/bin/env bash
# r85 simplifier — reproducible proof runner (read-only for the repo; writes
# only inside corpus/live/r85-simplifier/). Run from this directory:
#   TMPDIR=/home/vgpnk/Projects/shokunin/tmp bash run-all.sh
set -euo pipefail
cd "$(dirname "$0")"

echo "== 1. fold (regenerates proofs/folded/measure_audio.py + fold-apply.txt)"
rm -rf proofs/folded
python3 proofs/fold-r85-simplifier.py > /dev/null
tail -2 proofs/fold-apply.txt

echo "== 2. py_compile the folded copy -> proofs/pycompile.txt"
rm -rf proofs/folded/__pycache__
python3 -c "import py_compile; py_compile.compile('proofs/folded/measure_audio.py', doraise=True); print('py_compile: OK (proofs/folded/measure_audio.py)')" > proofs/pycompile.txt
cat proofs/pycompile.txt

echo "== 3. static proofs -> proofs/static-proofs.txt"
python3 proofs/static-proofs.py > /dev/null
tail -1 proofs/static-proofs.txt

echo "== 4. receipt census -> proofs/receipt-census.txt"
python3 proofs/receipt-census.py > /dev/null
tail -1 proofs/receipt-census.txt

echo "== 5. differential -> proofs/differential.txt"
python3 proofs/differential.py > /dev/null
tail -1 proofs/differential.txt

echo "== 6. bimodal-arms (either-way) -> proofs/bimodal-arms.txt"
python3 proofs/bimodal-arms.py > /dev/null
tail -1 proofs/bimodal-arms.txt

echo "== 7. regenerate the patch"
diff -u proofs/base-measure_audio.py proofs/folded/measure_audio.py \
  | sed -e '1s|.*|--- a/corpus/fixtures/measure_audio.py|' \
        -e '2s|.*|+++ b/corpus/fixtures/measure_audio.py|' \
  > r85-simplifier.patch || true   # diff exits 1 when the files differ

echo "== 8. patch checks -> proofs/patch-check.txt"
REPO="$(git -C . rev-parse --show-toplevel)"
{
  echo "# r85 simplifier patch checks (read-only; the patch is NOT applied)"
  echo
  echo "\$ git -C $REPO apply --check corpus/live/r85-simplifier/r85-simplifier.patch"
  git -C "$REPO" apply --check corpus/live/r85-simplifier/r85-simplifier.patch \
    && echo "clean (applies to the live tree; corpus/fixtures/measure_audio.py sha256 == the 2a49d540 blob, which is what the patch is anchored to)"
  echo
  echo "\$ git -C $REPO apply --numstat corpus/live/r85-simplifier/r85-simplifier.patch"
  git -C "$REPO" apply --numstat corpus/live/r85-simplifier/r85-simplifier.patch
  echo
  echo "\$ patch -p1 --dry-run < r85-simplifier.patch   (scratch copy of the pinned blob)"
  rm -rf proofs/rt
  mkdir -p proofs/rt/corpus/fixtures
  cp proofs/base-measure_audio.py proofs/rt/corpus/fixtures/measure_audio.py
  (cd proofs/rt && patch -p1 --dry-run < ../../r85-simplifier.patch)
  echo
  echo "\$ patch -p1 < r85-simplifier.patch && sha256sum   (round-trip identity)"
  (cd proofs/rt && patch -p1 < ../../r85-simplifier.patch > /dev/null && sha256sum corpus/fixtures/measure_audio.py ../folded/measure_audio.py)
  echo
  echo "hunks: $(grep -c '^@@' r85-simplifier.patch)"
  echo "lines: added=$(awk '/^\+\+\+|^---/{next} /^\+/{a++} END{print a+0}' r85-simplifier.patch) deleted=$(awk '/^\+\+\+|^---/{next} /^-/{d++} END{print d+0}' r85-simplifier.patch)"
  echo
  echo "hunk base line numbers (must all fall inside the r85 block 21579..23728):"
  grep '^@@' r85-simplifier.patch | sed -e 's/@@ -\([0-9]*\).*/  base \1/'
} > proofs/patch-check.txt
cat proofs/patch-check.txt

echo "== 9. census -> proofs/census.txt"
python3 proofs/census.py > proofs/census.txt
head -1 proofs/census.txt

echo "== 10. deadscan -> proofs/deadscan.txt"
python3 proofs/deadscan.py > proofs/deadscan.txt
tail -3 proofs/deadscan.txt

echo "== 11. sha256 census -> proofs/sha256.txt"
sha256sum r85-simplifier.patch proofs/base-measure_audio.py \
  proofs/folded/measure_audio.py proofs/*.py proofs/*.txt \
  > proofs/sha256.txt
cat proofs/sha256.txt

echo "== 12. cleanup pycache"
find proofs -name __pycache__ -type d -prune -exec rm -rf {} +
echo "done"
