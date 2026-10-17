#!/usr/bin/env bash
# r79-author formal receipt runs — TWO end-to-end runs of the FROZEN
# artifact (sha256 recorded in frozen-artifact.txt), sequential, in one
# window, with a host-state snapshot before and after each.
set -u
cd /home/vgpnk/Projects/shokunin/audio-shokunin
OUT=corpus/live/r79-author

snapshot() {
  local tag="$1"
  {
    echo "=== $tag $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
    echo "measure_audio.py sha256: $(sha256sum corpus/fixtures/measure_audio.py | cut -d' ' -f1)"
    echo "-- live sibling probe processes --"
    pgrep -af "measure_audio|pw-cat|pw-play|pw-record|pw-loopback|parec" | grep -v pgrep || true
    echo "-- default sink/source --"
    pactl info | grep -E "Default (Sink|Source)" || true
    echo "-- session default source metadata --"
    pw-metadata -n default 0 default.audio.source 2>&1 | tail -1
    echo "-- wpctl default markers --"
    wpctl status 2>/dev/null | sed -n '/Sinks:/,/Streams:/p' | grep -E '^\s*[│├└]*\s*\*|Sources:|Sinks:' | head -8
    echo "-- foreign null sinks/sources --"
    pactl list short sinks | grep -v "alsa_output\|alsa_input" || true
    pactl list short sources | grep -v "alsa_output\|alsa_input" || true
    echo "-- r79 leftovers (nodes/procs/modules) --"
    echo "nodes: $(pw-dump 2>/dev/null | grep -c 'r79lb_\|r79fc_\|r79exp')"
    echo "procs: $(pgrep -cf 'r79lb_|r79fc_|r79exp' || true)"
    echo "modules: $(pactl list short modules | grep -c 'r79lb\|r79exp' || true)"
    echo "-- load --"
    uptime
  } >> "$OUT/host-window.log" 2>&1
}

for leg in B C; do
  snapshot "pre-run$leg"
  python3 corpus/fixtures/measure_audio.py --probe-capture-r79 \
    > "$OUT/r79-run$leg.stdout.json" 2> "$OUT/r79-run$leg.stderr.log"
  echo "EXIT=$?" >> "$OUT/r79-run$leg.stdout.json"
  snapshot "post-run$leg"
done
echo ALL_DONE
