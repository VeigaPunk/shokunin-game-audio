#!/usr/bin/env bash
# r86-simplifier — reproduce every receipt in this directory.
# Read-only w.r.t. the tracked tree: the fold is applied to SCRATCH
# copies only; the patch is never applied to corpus/fixtures/.
set -euo pipefail
cd "$(dirname "$0")"
REPO="$(git rev-parse --show-toplevel)"
export TMPDIR="${TMPDIR:-$REPO/../tmp}"
PIN="fa5994a029507e666315cd40257988510579284f"

echo "== 0. pin the base blob =="
git -C "$REPO" show "$PIN:corpus/fixtures/measure_audio.py" \
    > base-measure_audio.py
sha256sum base-measure_audio.py
git -C "$REPO" show "$PIN" -- corpus/fixtures/measure_audio.py \
    > r86-diff.patch
python3 - <<'EOF'
src = open("base-measure_audio.py", encoding="utf-8").read().splitlines()
open("r86-block.py", "w", encoding="utf-8").write(
    "\n".join(src[23729:25451]) + "\n")
print("r86-block.py:", 25451 - 23729, "lines")
EOF

echo "== 1. fold (exact-match, abort on 0/multi) =="
python3 fold-r86-simplifier.py | tee fold-apply.txt

echo "== 2. compile =="
{
  echo "== py_compile folded/measure_audio.py =="
  python3 -m py_compile folded/measure_audio.py && echo "OK (rc=0)"
  echo
  echo "== ast.parse both =="
  python3 -c "
import ast
for p in ('base-measure_audio.py','folded/measure_audio.py'):
    ast.parse(open(p,encoding='utf-8').read()); print(p,'AST OK')
"
} | tee pycompile.txt
rm -rf folded/__pycache__

echo "== 3. static proofs =="
python3 static-proofs.py | tee static-proofs.txt

echo "== 4. differential proofs =="
python3 differential.py | tee differential.txt

echo "== 5. receipt census =="
python3 receipt-census.py | tee receipt-census.txt

echo "== 6. lock proof (two TMPDIRs, real shipped module) =="
python3 lock-proof.py | tee lock-proof.txt

echo "== 7. symbol census / dead scan =="
python3 symdiff.py | tee symdiff.txt
python3 symscan.py | tee symscan.txt
python3 deadscan.py | tee deadscan.txt
python3 legcensus.py | tee legcensus.txt
python3 legcensus2.py | tee legcensus2.txt

echo "== 8. patch generation + round-trip =="
{ echo '--- a/corpus/fixtures/measure_audio.py'
  echo '+++ b/corpus/fixtures/measure_audio.py'
  diff -u base-measure_audio.py folded/measure_audio.py | tail -n +3 \
      || true   # diff exits 1 on differences
} > ../r86-simplifier.patch
{
  echo "== git apply --check (live working tree) =="
  git -C "$REPO" apply --check --numstat "$PWD/../r86-simplifier.patch"
  echo "rc=$?"
  echo
  echo "== patch -p1 round-trip on a scratch copy =="
  rm -rf scratch && mkdir -p scratch/corpus/fixtures
  cp base-measure_audio.py scratch/corpus/fixtures/measure_audio.py
  (cd scratch && patch -p1 --batch < ../../r86-simplifier.patch)
  cmp scratch/corpus/fixtures/measure_audio.py folded/measure_audio.py \
      && echo "byte-identical to folded"
  sha256sum scratch/corpus/fixtures/measure_audio.py \
            folded/measure_audio.py
} | tee patch-check.txt

echo "== 9. CLI wiring check =="
{
  echo "== folded --help exposes the r86 flag =="
  python3 folded/measure_audio.py --help > cli-help-folded.txt 2>&1
  echo "help rc=$? ; occurrences of --probe-pwctl-r86: $(grep -c \
      'probe-pwctl-r86' cli-help-folded.txt)"
  echo
  echo "== probe-mutex sum: same basename required (argparse prog) =="
  rm -rf scratch-base && mkdir -p scratch-base
  cp base-measure_audio.py scratch-base/measure_audio.py
  brc=0
  python3 scratch-base/measure_audio.py --probe-pwctl-r86 \
      --probe-pactlmon-r85 > cli-mutex-base.txt 2>&1 || brc=$?
  echo "base rc=$brc"
  frc=0
  python3 folded/measure_audio.py --probe-pwctl-r86 \
      --probe-pactlmon-r85 > cli-mutex-folded.txt 2>&1 || frc=$?
  echo "folded rc=$frc"
  cmp cli-mutex-base.txt cli-mutex-folded.txt \
      && echo "identical stderr/usage"
  tail -1 cli-mutex-folded.txt
} | tee cli-check.txt
rm -rf scratch scratch-base folded/__pycache__ __pycache__

echo "== 10. hash census =="
{
  echo "# r86-simplifier artifact hashes ($(date -u +%Y-%m-%d))"
  echo
  sha256sum base-measure_audio.py folded/measure_audio.py \
      ../r86-simplifier.patch r86-block.py r86-diff.patch
  echo
  sha256sum fold-r86-simplifier.py static-proofs.py differential.py \
      receipt-census.py lock-proof.py lock-worker.py symdiff.py \
      symscan.py deadscan.py legcensus.py legcensus2.py
  echo
  sha256sum cli-check.txt cli-help-folded.txt cli-mutex-base.txt \
      cli-mutex-folded.txt deadscan.txt differential.txt \
      fold-apply.txt labrat-probe.txt legcensus2.txt legcensus.txt \
      lock-proof.txt patch-check.txt pycompile.txt receipt-census.txt \
      static-proofs.txt symdiff.txt symscan.txt
} > sha256.txt
sha256sum sha256.txt
echo "run-all complete"
