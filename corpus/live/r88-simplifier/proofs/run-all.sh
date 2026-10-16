#!/usr/bin/env bash
# r88 simplifier — reproduce every artifact of this seat end-to-end.
# Reads the committed pin, writes only under corpus/live/r88-simplifier/.
# TMPDIR must point at the shared lane tmp dir.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
TREE="$(cd "$HERE/../../../.." && pwd)"
export PYTHONDONTWRITEBYTECODE=1
export TMPDIR="${TMPDIR:-/home/vgpnk/Projects/shokunin/tmp}"
LOG="$HERE/run-all.log"
: > "$LOG"
RC=0

step() {
  local name="$1"; shift
  echo "===== $name =====" >> "$LOG"
  "$@" >> "$LOG" 2>&1
  local rc=$?
  echo "----- $name rc=$rc" >> "$LOG"
  if [ $rc -ne 0 ]; then RC=1; fi
}

step static-census      python3 "$HERE/static-census.py"
step deadscan           python3 "$HERE/deadscan.py"
step receipt-census     python3 "$HERE/receipt-census.py"
step fold               python3 "$HERE/fold-r88-simplifier.py"
step static-proofs      python3 "$HERE/static-proofs.py"
step differential       python3 "$HERE/differential.py"
step receipt-proofs     python3 "$HERE/receipt-proofs.py"
step lock-proof         python3 "$HERE/lock-proof.py"
step observations       python3 "$HERE/observations.py"

step pycompile-ast python3 - "$HERE/folded/measure_audio.py" <<'PY'
import ast, sys
src = sys.argv[1]
t = open(src, encoding="utf-8").read()
ast.parse(t)
print("ast.parse OK:", src)
PY

echo "===== patch checks =====" >> "$LOG"
{
  echo "-- numstat:"; git -C "$TREE" apply --numstat "$HERE/fold.diff"
  echo "-- check:";   git -C "$TREE" apply --check  "$HERE/fold.diff" && echo "clean"
  echo "-- round-trip:"
  RT="$TMPDIR/r88simp-rt"
  rm -rf "$RT"; mkdir -p "$RT/corpus/fixtures"
  cp "$HERE/base-measure_audio.py" "$RT/corpus/fixtures/measure_audio.py"
  ( cd "$RT" && patch -p1 --silent < "$HERE/fold.diff" )
  sha256sum "$RT/corpus/fixtures/measure_audio.py" "$HERE/folded/measure_audio.py"
} >> "$LOG" 2>&1
RT_RC=$?
if [ $RT_RC -ne 0 ]; then RC=1; fi
echo "----- patch checks rc=$RT_RC" >> "$LOG"

echo "===== tracked-write census =====" >> "$LOG"
git -C "$TREE" status --short -- corpus/fixtures/measure_audio.py \
  >> "$LOG" 2>&1
echo "(empty above = the fixture is clean vs HEAD)" >> "$LOG"

echo "===== run-all rc=$RC =====" >> "$LOG"
echo "run-all rc=$RC (log: $LOG)"
exit $RC
