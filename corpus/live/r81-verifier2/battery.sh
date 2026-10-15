#!/usr/bin/env bash
# r81-VERIFIER2 battery pass — the r81-baseline seat's 4-command prior
# battery verbatim (normal + capture-r78 + capture-r79 + module-r80),
# ONE pass on the committed folded tree (fold 07c0671, fixture sha
# verified identical at HEAD). Receipts land in corpus/live/runs/ then
# are copied per mode. All runs `timeout 900`, CWD = repo root.
set -u
ROOT=/home/vgpnk/Projects/shokunin/audio-shokunin
cd "$ROOT"
OUT="$ROOT/corpus/live/r81-verifier2/battery"
FIX="$ROOT/corpus/fixtures/measure_audio.py"
mkdir -p "$OUT"

snap() {
  printf '%s head=%s fixture_sha256=%s\n' \
    "$1" "$(git rev-parse --short HEAD)" \
    "$(sha256sum "$FIX" | cut -d' ' -f1)" >> "$OUT/commands.log"
}

run_one() {
  local mode="$1"; shift
  local before after receipt out rc
  before=$(sha256sum "$FIX" | cut -d' ' -f1)
  printf 'CMD %s %s timeout 900 python3 corpus/fixtures/measure_audio.py %s\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$mode" "$*" >> "$OUT/commands.log"
  out=$(timeout 900 python3 "$FIX" "$@" 2> "$OUT/$mode.stderr.log")
  rc=$?
  printf '%s\n' "$out" > "$OUT/$mode.stdout.json"
  echo "EXIT=$rc" >> "$OUT/$mode.stdout.json"
  after=$(sha256sum "$FIX" | cut -d' ' -f1)
  receipt=$(printf '%s' "$out" | python3 -c 'import json,sys;print(json.load(sys.stdin)["receipt"])' 2>/dev/null || true)
  if [ -n "$receipt" ] && [ -f "$receipt" ]; then
    cp "$receipt" "$OUT/$mode.receipt.json"
    sha256sum "$receipt" >> "$OUT/receipt-shas.txt"
    printf 'RECEIPT %s %s\n' "$mode" "$receipt" >> "$OUT/commands.log"
  else
    printf 'RECEIPT %s MISSING\n' "$mode" >> "$OUT/commands.log"
  fi
  printf 'SHA before=%s after=%s rc=%s\n' "$before" "$after" "$rc" >> "$OUT/commands.log"
}

snap "pre-run"
run_one normal
run_one capture-r78 --probe-capture-r78
run_one capture-r79 --probe-capture-r79
run_one module-r80 --probe-module-r80
snap "post-run"
echo VERIFIER2_BATTERY_DONE
