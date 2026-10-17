#!/usr/bin/env bash
# r80-baseline battery — the file's default `normal` mode plus the r78/r79
# probe entries, executed TWICE (runs-a, runs-b) on the frozen post-r79 tree.
# Every run is receipted: stdout/stderr per command, the canonical receipt
# copied beside it, and the fixture sha256 recorded before/after.
set -u
cd /home/vgpnk/Projects/shokunin/audio-shokunin
OUT=corpus/live/r80-baseline
FIX=corpus/fixtures/measure_audio.py

snap() { # tag -> one line of frozen state
  printf '%s head=%s fixture_sha256=%s\n' \
    "$1" "$(git rev-parse --short HEAD)" "$(sha256sum "$FIX" | cut -d' ' -f1)"
}

run_one() { # rundir mode args...
  local dir="$1" mode="$2"; shift 2
  local before after stamp receipt
  before=$(sha256sum "$FIX" | cut -d' ' -f1)
  printf 'CMD %s %s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$mode" "$*" >> "$OUT/$dir/commands.log"
  python3 corpus/fixtures/measure_audio.py "$@" \
    > "$OUT/$dir/$mode.stdout.json" 2> "$OUT/$dir/$mode.stderr.log"
  local rc=$?
  echo "EXIT=$rc" >> "$OUT/$dir/$mode.stdout.json"
  after=$(sha256sum "$FIX" | cut -d' ' -f1)
  receipt=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["receipt"])' \
            "$OUT/$dir/$mode.stdout.json" 2>/dev/null || true)
  if [ -n "$receipt" ] && [ -f "$receipt" ]; then
    stamp=$(basename "$(dirname "$receipt")")
    cp "$receipt" "$OUT/$dir/$mode.receipt.json"
    sha256sum "$receipt" >> "$OUT/$dir/receipt-shas.txt"
    printf 'RECEIPT %s %s %s\n' "$mode" "$stamp" "$receipt" >> "$OUT/$dir/commands.log"
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
  snap "post-run$leg" >> "$OUT/$dir/commands.log"
done
echo ALL_DONE
