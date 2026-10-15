#!/usr/bin/env bash
# manual recon step 2: sink is loaded; play a tone to it and dump link/negotiation errors
set -u
SEAT=/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r99-scout
cd "$SEAT"
export PIPEWIRE_RUNTIME_DIR="$SEAT/run" XDG_RUNTIME_DIR="$SEAT/run"
echo "--- nodes before play:"
pw-dump 2>/dev/null | python3 -c "
import json,sys
for o in json.load(sys.stdin):
    if o['type'].endswith('Node'):
        i=o['info']; p=i.get('props',{})
        print('NODE',o['id'], p.get('node.name'), p.get('media.class'), 'state=',i.get('state'), i.get('n-input-ports'),i.get('n-output-ports'))
"
MARK=$(wc -l < runs/core.log)
setsid pw-play scratch/tone997_s16_48k_st.wav --target r99s_sink > scratch/play4.out 2> scratch/play4.err &
echo $! > scratch/play4.pid
sleep 2
echo "--- pw-link -l:"; pw-link -l 2>&1 | head -12
echo "--- nodes during play:"
pw-dump 2>/dev/null | python3 -c "
import json,sys
for o in json.load(sys.stdin):
    if o['type'].endswith('Node'):
        i=o['info']; p=i.get('props',{})
        print('NODE',o['id'], p.get('node.name'), p.get('media.class'), 'state=',i.get('state'), i.get('n-input-ports'),i.get('n-output-ports'))
"
echo "--- core log since mark (link/negotiation):"
tail -n +"$MARK" runs/core.log | grep -iE "link|negotiat|format|error" | tail -30
