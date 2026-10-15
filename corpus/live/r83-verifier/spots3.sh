#!/usr/bin/env bash
# r83v spots round 3 — corrected link gate for s11 -d transport pair.
set -u
VPID=$$
TAG="r83v_${VPID}"
OUT="/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r83-verifier/spot"
W="/tmp/r83v-work/spot"
mkdir -p "$OUT" "$W"
exec 9>"$OUT/spots3.jsonl"
say() { printf '%s\n' "$*" >&9; }

NSA="${TAG}_nsa"; NSB="${TAG}_nsb"
MA=$(pactl load-module module-null-sink sink_name="$NSA" rate=48000 channels=2 channel_map=front-left,front-right)
MB=$(pactl load-module module-null-sink sink_name="$NSB" rate=48000 channels=2 channel_map=front-left,front-right)
say "{\"setup\":{\"nsa_mod\":$MA,\"nsb_mod\":$MB,\"tag\":\"$TAG\"}}"
sleep 0.5

gate() { # correct ends: input.<tag> gets a PRODUCER (link.in==input), output.<tag> a CONSUMER (link.out==output)
  pw-dump | python3 -c "
import json,sys
d=json.load(sys.stdin)
names={o['id']:o['info']['props'].get('node.name') for o in d if o.get('type')=='PipeWire:Interface:Node'}
inp=outp=False
for o in d:
    if o.get('type')!='PipeWire:Interface:Link': continue
    p=o['info']['props']
    if names.get(p.get('link.input.node'))=='input.$1': inp=True
    if names.get(p.get('link.output.node'))=='output.$1': outp=True
print('yes' if inp and outp else 'no')"
}

onset_leg() { # $1=suffix, extra args...
  local sfx="$1"; shift
  timeout 12 pw-loopback -n "${TAG}_${sfx}" -C "$NSA" -i stream.capture.sink=true -P "$NSB" "$@" > /dev/null 2>&1 &
  local LB=$!
  local ok=no i
  for i in $(seq 1 50); do
    ok=$(gate "${TAG}_${sfx}")
    [ "$ok" = "yes" ] && break
    sleep 0.2
  done
  [ "$ok" != "yes" ] && { say "{\"leg\":\"$sfx\",\"blocked\":\"loopback never linked\",\"gate_iters\":$i}"; kill $LB 2>/dev/null; wait $LB 2>/dev/null; return; }
  timeout 6 pw-record -P stream.capture.sink=true -P node.name="${TAG}_${sfx}tap" --target "$NSB" -n 240000 --rate 48000 --channels 2 --format s16 "$W/${sfx}_mon.wav" > /dev/null 2>&1 &
  local TAP=$!
  sleep 0.2
  local T_TAP=$(python3 -c 'import time;print(time.monotonic())')
  sleep 0.4
  local T_FEED=$(python3 -c 'import time;print(time.monotonic())')
  timeout 5 pw-cat -p --target "$NSA" "$W/tone48.wav" > /dev/null 2>&1 &
  local FEED=$!
  wait $TAP 2>/dev/null
  kill $LB $FEED 2>/dev/null; wait $LB 2>/dev/null
  python3 - "$W/${sfx}_mon.wav" "$T_TAP" "$T_FEED" "$sfx" >&9 <<'PY'
import json,sys,wave,numpy as np
try:
    with wave.open(sys.argv[1],'rb') as f:
        pcm=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').reshape(-1,2)
    nz=np.nonzero(np.max(np.abs(pcm),axis=1)>400)[0]
    onset=float(nz[0])/48000 if len(nz) else None
    lead=float(sys.argv[3])-float(sys.argv[2])
    print(json.dumps({"leg":sys.argv[4],"frames":int(len(pcm)),
        "onset_in_tap_s":onset,"feed_lead_s":round(lead,3),
        "transport_s":round(onset-lead,3) if onset is not None else None}))
except Exception as e:
    print(json.dumps({"leg":sys.argv[4],"error":str(e)}))
PY
}

onset_leg s11c            # control — no -d
onset_leg s11 -d 1.0      # ~+1.0 s transport
onset_leg s11l -l 1000    # -l prop-only control

for pair in "$MA:$NSA" "$MB:$NSB"; do
  mid="${pair%%:*}"; sn="${pair##*:}"
  ok=$(pactl list short modules | awk -v m="$mid" -v s="sink_name=$sn" '$1==m && index($0,s){print "yes"}')
  if [ "$ok" = "yes" ]; then pactl unload-module "$mid"; fi
done
sleep 0.4
say "{\"teardown\":{\"r83v_objects_after\":$(pw-dump | python3 -c "import json,sys;d=json.load(sys.stdin);print(json.dumps([o.get('id') for o in d if 'r83v_${VPID}' in json.dumps(o)]))"),\"mods_left\":$(pactl list short modules | grep -c "r83v_${VPID}" || true)}}"
echo "spots3 done $(date -u +%FT%TZ)"
