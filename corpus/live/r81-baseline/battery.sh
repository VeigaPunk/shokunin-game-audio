#!/usr/bin/env bash
# r81-baseline battery — the file's default `normal` mode plus the three
# newest probe entries (r78, r79, r80), executed TWICE (runs-a, runs-b).
#
# The battery runs the FIXTURE INSIDE THE FROZEN TREE with CWD = tree root,
# so every receipt the fixture writes lands under
# corpus/live/r81-baseline/tree/corpus/live/runs/ (gitignored scratch) and
# the worktree is never touched. The tree fixture sha is re-recorded before
# and after every single run.
#
# FIX (attempt-1 tooling fault, recorded): the first version redirected
# stderr to a REPO-RELATIVE path inside the `cd $TREE` subshell, so bash
# refused the redirection and every leg died with rc=1 before python ran.
# All paths below are absolute.
set -u
ROOT=/home/vgpnk/Projects/shokunin/audio-shokunin
cd "$ROOT"
OUT="$ROOT/corpus/live/r81-baseline"
TREE="$OUT/tree"
FIX="$TREE/corpus/fixtures/measure_audio.py"

snap() { # tag -> one line of frozen state
  printf '%s head=%s fixture_sha256=%s tree_fixture_sha256=%s\n' \
    "$1" "$(git rev-parse --short HEAD)" \
    "$(sha256sum "$ROOT/corpus/fixtures/measure_audio.py" | cut -d' ' -f1)" \
    "$(sha256sum "$FIX" | cut -d' ' -f1)"
}

run_one() { # rundir mode args...
  local dir="$1" mode="$2"; shift 2
  local before after stamp receipt out rc
  before=$(sha256sum "$FIX" | cut -d' ' -f1)
  printf 'CMD %s %s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$mode" "$*" >> "$OUT/$dir/commands.log"
  out=$(cd "$TREE" && python3 corpus/fixtures/measure_audio.py "$@" 2> "$OUT/$dir/$mode.stderr.log")
  rc=$?
  printf '%s\n' "$out" > "$OUT/$dir/$mode.stdout.json"
  echo "EXIT=$rc" >> "$OUT/$dir/$mode.stdout.json"
  after=$(sha256sum "$FIX" | cut -d' ' -f1)
  receipt=$(printf '%s' "$out" | python3 -c 'import json,sys;print(json.load(sys.stdin)["receipt"])' 2>/dev/null || true)
  if [ -n "$receipt" ] && [ -f "$receipt" ]; then
    stamp=$(basename "$(dirname "$receipt")")
    cp "$receipt" "$OUT/$dir/$mode.receipt.json"
    sha256sum "$receipt" >> "$OUT/$dir/receipt-shas.txt"
    printf 'RECEIPT %s %s %s\n' "$mode" "$stamp" "$receipt" >> "$OUT/$dir/commands.log"
  else
    printf 'RECEIPT %s MISSING\n' "$mode" >> "$OUT/$dir/commands.log"
  fi
  printf 'SHA before=%s after=%s rc=%s\n' "$before" "$after" "$rc" >> "$OUT/$dir/commands.log"
}

for leg in a b; do
  dir="runs-$leg"
  mkdir -p "$OUT/$dir"
  snap "pre-run$leg" >> "$OUT/$dir/commands.log"
  run_one "$dir" normal
  run_one "$dir" capture-r78 --probe-capture-r78
  run_one "$dir" capture-r79 --probe-capture-r79
  run_one "$dir" module-r80 --probe-module-r80
  snap "post-run$leg" >> "$OUT/$dir/commands.log"
done
echo ALL_DONE
