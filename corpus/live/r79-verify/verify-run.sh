#!/usr/bin/env bash
# r79-verifier independent runs. Independent of r79-author/formal-runs.sh:
# fresh snapshots, own output dir, one probe per invocation.
# usage: verify-run.sh <tag> <probe-flag>
set -u
cd /home/vgpnk/Projects/shokunin/audio-shokunin
OUT=corpus/live/r79-verify
TAG="$1"; FLAG="$2"

snapshot() {
  local tag="$1"
  {
    echo "=== $tag $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
    echo "measure_audio.py sha256: $(sha256sum corpus/fixtures/measure_audio.py | cut -d' ' -f1)"
    echo "-- live probe/sibling processes --"
    pgrep -af "measure_audio|pw-cat|pw-play|pw-record|pw-loopback|parec|r86ctl|arecord|aplay" | grep -v pgrep | grep -v "verify-run.sh" || true
    echo "-- default sink/source --"
    pactl info | grep -E "Default (Sink|Source)" || true
    echo "-- session default source metadata --"
    pw-metadata -n default 0 default.audio.source 2>&1 | tail -1
    echo "-- foreign null sinks/sources (non-alsa) --"
    pactl list short sinks | grep -v "alsa_output" || true
    pactl list short sources | grep -v "alsa_" || true
    echo "-- r79 leftovers (nodes/procs/modules) --"
    echo "nodes: $(pw-dump 2>/dev/null | grep -c 'r79lb_\|r79fc_\|r79exp')"
    echo "procs: $(pgrep -cf 'r79lb_|r79fc_|r79exp' || true)"
    echo "modules: $(pactl list short modules | grep -c 'r79lb\|r79exp' || true)"
    echo "-- load --"
    uptime
  } >> "$OUT/host-window-verify.log" 2>&1
}

snapshot "pre-$TAG"
python3 corpus/fixtures/measure_audio.py "$FLAG" \
  > "$OUT/$TAG.stdout.json" 2> "$OUT/$TAG.stderr.log"
echo "EXIT=$?" >> "$OUT/$TAG.stdout.json"
snapshot "post-$TAG"
echo "DONE $TAG"
