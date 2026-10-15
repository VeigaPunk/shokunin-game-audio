#!/usr/bin/env bash
# manual recon step 3: load rtp-sink and watch the core log for the module's own lines
set -u
SEAT=/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r99-scout
cd "$SEAT"
export PIPEWIRE_RUNTIME_DIR="$SEAT/run" XDG_RUNTIME_DIR="$SEAT/run"
echo "core pid=$(cat run/core.pid) alive=$(kill -0 $(cat run/core.pid) 2>/dev/null && echo yes || echo no)"
echo "log lines before: $(wc -l < runs/core.log)"
printf 'load-module libpipewire-module-rtp-sink { destination.ip = "127.0.0.1" destination.port = 46100 sess.min-ptime = 1 sess.max-ptime = 1 audio.format = "S16BE" stream.props = { node.name = "r99s_sink" media.class = "Audio/Sink" node.virtual = false node.always-process = true } }\nquit\n' | timeout 8 pw-cli > scratch/load3.out 2>&1
echo "load rc=$? out=$(cat scratch/load3.out | tail -2 | tr '\n' '|')"
sleep 1
echo "log lines after: $(wc -l < runs/core.log)"
echo "--- new log lines mentioning module/rtp/stream:"
grep -iE "rtp|impl-module|stream|error" runs/core.log | tail -25
echo "--- nodes:"
timeout 5 pw-cli ls Node 2>&1 | grep -E "node.name|id [0-9]" | head -12
