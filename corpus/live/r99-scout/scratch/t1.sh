#!/usr/bin/env bash
# manual recon step 1: private core (debug 4) + wp, load rtp-sink, play a tone, inspect link failure
set -u
SEAT=/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r99-scout
cd "$SEAT"
export PIPEWIRE_RUNTIME_DIR="$SEAT/run" XDG_RUNTIME_DIR="$SEAT/run"
bash probes/down.sh >/dev/null 2>&1
PIPEWIRE_DEBUG=4 bash probes/up.sh both || exit 1
echo 'load-module libpipewire-module-rtp-sink { destination.ip = "127.0.0.1" destination.port = 46100 sess.min-ptime = 1 sess.max-ptime = 1 audio.format = "S16BE" stream.props = { node.name = "r99s_sink" media.class = "Audio/Sink" node.virtual = false node.always-process = true } }' | pw-cli >/dev/null 2>&1
sleep 0.7
pw-dump 2>/dev/null | python3 -c "
import json,sys
for o in json.load(sys.stdin):
    if o['type'].endswith('Node'):
        i=o['info']; p=i.get('props',{})
        print('NODE',o['id'], p.get('node.name'), p.get('media.class'), 'state=',i.get('state'), i.get('n-input-ports'),i.get('n-output-ports'))
"
setsid pw-play scratch/tone997_s16_48k_st.wav -P node.name=r99s_play > scratch/play3.out 2> scratch/play3.err &
echo $! > scratch/play3.pid
sleep 2
echo "--- pw-link -l:"
pw-link -l 2>&1 | head -20
echo "--- nodes after play:"
pw-dump 2>/dev/null | python3 -c "
import json,sys
for o in json.load(sys.stdin):
    if o['type'].endswith('Node'):
        i=o['info']; p=i.get('props',{})
        print('NODE',o['id'], p.get('node.name'), p.get('media.class'), 'state=',i.get('state'), i.get('n-input-ports'),i.get('n-output-ports'))
"
echo "--- core log (link/error):"
grep -iE "link|negotiat|error|warn" runs/core.log | tail -25
