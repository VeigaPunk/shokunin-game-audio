#!/usr/bin/env bash
# r81-AUTHOR battery replay — the r81-baseline seat's 4-command prior
# battery (normal + capture-r78 + capture-r79 + module-r80), run TWICE on
# the LIVE tree with the r81-extended fixture. Prior rows = every row in
# these receipts (the gst-r81 family is not part of the battery modes).
# Receipts land in corpus/live/runs/ then are copied per mode.
set -u
ROOT=/home/vgpnk/Projects/shokunin/audio-shokunin
cd "$ROOT"
OUT="$ROOT/corpus/live/r81-author"
FIX="$ROOT/corpus/fixtures/measure_audio.py"

snap() {
  printf '%s head=%s fixture_sha256=%s\n' \
    "$1" "$(git rev-parse --short HEAD)" \
    "$(sha256sum "$FIX" | cut -d' ' -f1)"
}

run_one() {
  local dir="$1" mode="$2"; shift 2
  local before after receipt out rc
  before=$(sha256sum "$FIX" | cut -d' ' -f1)
  printf 'CMD %s %s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$mode" "$*" >> "$OUT/$dir/commands.log"
  out=$(python3 "$FIX" "$@" 2> "$OUT/$dir/$mode.stderr.log")
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
echo AUTHOR_BATTERY_DONE
