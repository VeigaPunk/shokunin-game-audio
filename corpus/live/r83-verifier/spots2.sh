#!/usr/bin/env bash
# r83v spots round 2 — mid-run pw-dump sampling for s7/s8, link-gated s11.
set -u
VPID=$$
TAG="r83v_${VPID}"
OUT="/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r83-verifier/spot"
W="/tmp/r83v-work/spot"
mkdir -p "$OUT" "$W"
exec 9>"$OUT/spots2.jsonl"
say() { printf '%s\n' "$*" >&9; }

NSA="${TAG}_nsa"; NSB="${TAG}_nsb"
MA=$(pactl load-module module-null-sink sink_name="$NSA" rate=48000 channels=2 channel_map=front-left,front-right)
MB=$(pactl load-module module-null-sink sink_name="$NSB" rate=48000 channels=2 channel_map=front-left,front-right)
say "{\"setup\":{\"nsa_mod\":$MA,\"nsb_mod\":$MB,\"tag\":\"$TAG\"}}"
sleep 0.5

props_of() {
  pw-dump | python3 -c "
import json,sys
d=json.load(sys.stdin)
for o in d:
    p=o.get('info',{}).get('props',{})
    if p.get('node.name')=='$1':
        keep={k:v for k,v in p.items() if k.startswith(('media.','node.','audio.','channelmap.','resample.','channelmix.','stream.','bogus','target.','adapt.','a'))}
        print(json.dumps(keep,sort_keys=True))
        break
"
}
nodes_named() {
  pw-dump | python3 -c "
import json,sys
d=json.load(sys.stdin)
print(json.dumps([o['info']['props'].get('node.name') for o in d if '$1' in str(o.get('info',{}).get('props',{}).get('node.name',''))]))
"
}

# s7 (fixed): '}{ garbage' silent drop — sample mid-run
timeout 4 pw-loopback -n "${TAG}_s7" -C "$NSA" -i '}{ garbage' -P "$NSB" > "$W/s7.out" 2> "$W/s7.err" &
LB=$!
sleep 1.6
say "{\"leg\":\"s7_drop_silent\",\"in_props\":$(props_of "input.${TAG}_s7"),\"node_names\":$(nodes_named "${TAG}_s7"),\"stderr_empty\":$(python3 -c "print(not open('$W/s7.err').read().strip())")}"
wait $LB 2>/dev/null

# s8 (fixed): -l -5 uint32 wrap — sample mid-run
timeout 4 pw-loopback -n "${TAG}_s8" -C "$NSA" -i stream.capture.sink=true -P "$NSB" -l -5 > "$W/s8.out" 2> "$W/s8.err" &
LB=$!
sleep 1.6
say "{\"leg\":\"s8_uint32_wrap\",\"in_latency\":$(pw-dump | python3 -c "import json,sys;d=json.load(sys.stdin);print(json.dumps([o['info']['props'].get('node.latency') for o in d if o.get('info',{}).get('props',{}).get('node.name')=='input.${TAG}_s8']))")}"
wait $LB 2>/dev/null

# s8b: -l beats -d both orders — node.latency 240/48000 with -l 5 -d 0.25
timeout 4 pw-loopback -n "${TAG}_s8b" -C "$NSA" -i stream.capture.sink=true -P "$NSB" -d 0.25 -l 5 > /dev/null 2>&1 &
LB=$!
sleep 1.6
say "{\"leg\":\"s8b_dl_order\",\"in_latency\":$(pw-dump | python3 -c "import json,sys;d=json.load(sys.stdin);print(json.dumps([o['info']['props'].get('node.latency') for o in d if o.get('info',{}).get('props',{}).get('node.name')=='input.${TAG}_s8b']))")}"
wait $LB 2>/dev/null

# s11 (fixed): -d 1.0 transport, link-gated loopback, timestamped spawns
timeout 8 pw-loopback -n "${TAG}_s11" -C "$NSA" -i stream.capture.sink=true -P "$NSB" -d 1.0 > /dev/null 2>&1 &
LB=$!
# link-gate: wait until input.<tag> has a producer and output.<tag> a consumer
for i in $(seq 1 60); do
  ok=$(pw-dump | python3 -c "
import json,sys
d=json.load(sys.stdin)
links=[(o['info']['props'].get('link.input.node'),o['info']['props'].get('link.output.node')) for o in d if o.get('type')=='PipeWire:Interface:Link']
names={o['id']:o['info']['props'].get('node.name') for o in d if o.get('type')=='PipeWire:Interface:Node'}
inp=[i for i,(a,b) in enumerate(links) if names.get(b)=='input.${TAG}_s11']
outp=[i for i,(a,b) in enumerate(links) if names.get(a)=='output.${TAG}_s11']
print('yes' if inp and outp else 'no')")
  [ "$ok" = "yes" ] && break
  sleep 0.2
done
echo "s11 link gate: $ok at iter $i" >> "$W/s11.log"
timeout 5 pw-record -P stream.capture.sink=true -P node.name="${TAG}_s11tap" --target "$NSB" -n 192000 --rate 48000 --channels 2 --format s16 "$W/s11_mon.wav" > /dev/null 2>&1 &
TAP=$!
sleep 0.2
T_TAP=$(python3 -c 'import time;print(time.monotonic())')
sleep 0.4
T_FEED=$(python3 -c 'import time;print(time.monotonic())')
timeout 3 pw-cat -p --target "$NSA" "$W/tone48.wav" > /dev/null 2>&1 &
FEED=$!
wait $TAP 2>/dev/null
kill $LB $FEED 2>/dev/null
python3 - "$W/s11_mon.wav" "$T_TAP" "$T_FEED" >&9 <<'PY'
import json,sys,wave,numpy as np
try:
    with wave.open(sys.argv[1],'rb') as f:
        pcm=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').reshape(-1,2)
    nz=np.nonzero(np.max(np.abs(pcm),axis=1)>400)[0]
    onset=float(nz[0])/48000 if len(nz) else None
    lead=float(sys.argv[3])-float(sys.argv[2])
    print(json.dumps({"leg":"s11_d10_transport","frames":int(len(pcm)),
        "onset_in_tap_s":onset,"feed_lead_s":round(lead,3),
        "transport_s":round(onset-lead,3) if onset is not None else None}))
except Exception as e:
    print(json.dumps({"leg":"s11_d10_transport","error":str(e)}))
PY

# control leg for s11: same shape, no -d
timeout 8 pw-loopback -n "${TAG}_s11c" -C "$NSA" -i stream.capture.sink=true -P "$NSB" > /dev/null 2>&1 &
LB=$!
for i in $(seq 1 60); do
  ok=$(pw-dump | python3 -c "
import json,sys
d=json.load(sys.stdin)
links=[(o['info']['props'].get('link.input.node'),o['info']['props'].get('link.output.node')) for o in d if o.get('type')=='PipeWire:Interface:Link']
names={o['id']:o['info']['props'].get('node.name') for o in d if o.get('type')=='PipeWire:Interface:Node'}
inp=[i for i,(a,b) in enumerate(links) if names.get(b)=='input.${TAG}_s11c']
outp=[i for i,(a,b) in enumerate(links) if names.get(a)=='output.${TAG}_s11c']
print('yes' if inp and outp else 'no')")
  [ "$ok" = "yes" ] && break
  sleep 0.2
done
timeout 5 pw-record -P stream.capture.sink=true -P node.name="${TAG}_s11ctap" --target "$NSB" -n 192000 --rate 48000 --channels 2 --format s16 "$W/s11c_mon.wav" > /dev/null 2>&1 &
TAP=$!
sleep 0.2
T_TAP=$(python3 -c 'import time;print(time.monotonic())')
sleep 0.4
T_FEED=$(python3 -c 'import time;print(time.monotonic())')
timeout 3 pw-cat -p --target "$NSA" "$W/tone48.wav" > /dev/null 2>&1 &
FEED=$!
wait $TAP 2>/dev/null
kill $LB $FEED 2>/dev/null
python3 - "$W/s11c_mon.wav" "$T_TAP" "$T_FEED" >&9 <<'PY'
import json,sys,wave,numpy as np
try:
    with wave.open(sys.argv[1],'rb') as f:
        pcm=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').reshape(-1,2)
    nz=np.nonzero(np.max(np.abs(pcm),axis=1)>400)[0]
    onset=float(nz[0])/48000 if len(nz) else None
    lead=float(sys.argv[3])-float(sys.argv[2])
    print(json.dumps({"leg":"s11_ctl","frames":int(len(pcm)),
        "onset_in_tap_s":onset,"feed_lead_s":round(lead,3),
        "transport_s":round(onset-lead,3) if onset is not None else None}))
except Exception as e:
    print(json.dumps({"leg":"s11_ctl","error":str(e)}))
PY

for pair in "$MA:$NSA" "$MB:$NSB"; do
  mid="${pair%%:*}"; sn="${pair##*:}"
  ok=$(pactl list short modules | awk -v m="$mid" -v s="sink_name=$sn" '$1==m && index($0,s){print "yes"}')
  if [ "$ok" = "yes" ]; then pactl unload-module "$mid"; fi
done
sleep 0.4
say "{\"teardown\":{\"r83v_objects_after\":$(pw-dump | python3 -c "import json,sys;d=json.load(sys.stdin);print(json.dumps([o.get('id') for o in d if 'r83v_${VPID}' in json.dumps(o)]))"),\"mods_left\":$(pactl list short modules | grep -c "r83v_${VPID}" || true)}}"
echo "spots2 done $(date -u +%FT%TZ)"
