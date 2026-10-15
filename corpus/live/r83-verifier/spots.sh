#!/usr/bin/env bash
# r83-verifier spot re-derivations — own r83v_<pid> names, /tmp scratch,
# bounded timeouts, name-verified module unload only. No tone to shared
# sinks (silence/prop-legs only on default-routing paths).
set -u
VPID=$$
TAG="r83v_${VPID}"
OUT="/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r83-verifier/spot"
W="/tmp/r83v-work/spot"
mkdir -p "$OUT" "$W"
exec 9>"$OUT/spots.jsonl"
say() { printf '%s\n' "$*" >&9; }

NSA="${TAG}_nsa"; NSB="${TAG}_nsb"; NS44="${TAG}_ns44"
MA=$(pactl load-module module-null-sink sink_name="$NSA" rate=48000 channels=2 channel_map=front-left,front-right sink_properties=device.description="$NSA")
MB=$(pactl load-module module-null-sink sink_name="$NSB" rate=48000 channels=2 channel_map=front-left,front-right sink_properties=device.description="$NSB")
M44=$(pactl load-module module-null-sink sink_name="$NS44" rate=44100 channels=2 channel_map=front-left,front-right sink_properties=device.description="$NS44")
say "{\"setup\":{\"nsa_mod\":$MA,\"nsb_mod\":$MB,\"ns44_mod\":$M44,\"tag\":\"$TAG\"}}"
sleep 0.4

# tag tone via python (48k stereo + 44.1k stereo)
python3 - "$W" <<'PY'
import numpy as np, sys, wave
w = sys.argv[1]
for name, rate in (("tone48", 48000), ("tone44", 44100)):
    n = int(rate * 4)
    t = np.arange(n) / rate
    l = (8192 * np.sin(2 * np.pi * 1000 * t)).astype("<i2")
    r = (8192 * np.sin(2 * np.pi * 1500 * t)).astype("<i2")
    pcm = np.empty(n * 2, dtype="<i2")
    pcm[0::2], pcm[1::2] = l, r
    with wave.open(f"{w}/{name}.wav", "wb") as f:
        f.setnchannels(2); f.setsampwidth(2); f.setframerate(rate)
        f.writeframes(pcm.tobytes())
PY

shot() {  # name, timeout_s, argv...
  local name="$1"; shift; local ts="$1"; shift
  timeout "$ts" "$@" > "$W/$name.out" 2> "$W/$name.err"
  local rc=$?
  say "{\"leg\":\"$name\",\"rc\":$rc,\"stderr\":$(python3 -c "import json,sys;print(json.dumps(open('$W/$name.err',errors='replace').read()[:400]))")}"
}

props_of() { # node-name -> compact props
  pw-dump | python3 -c "
import json,sys
d=json.load(sys.stdin)
for o in d:
    p=o.get('info',{}).get('props',{})
    if p.get('node.name')=='$1':
        keep={k:v for k,v in p.items() if k.startswith(('media.','node.','audio.','channelmap.','resample.','channelmix.','stream.','bogus','target.','adapt.'))}
        print(json.dumps(keep,sort_keys=True))
        break
"
}

# s1: pw-loopback -i '' SIGSEGV
shot segv_i_empty 6 pw-loopback -n "${TAG}_s1" -i ''
# s2: pw-loopback -o ' ' SIGSEGV
shot segv_o_space 6 pw-loopback -n "${TAG}_s2" -o ' '
# s3: pw-cat -P '' SIGSEGV
shot segv_pwcat_P_empty 6 pw-cat -p -P '' "$W/tone48.wav"
# s4: pw-record -P '' SIGSEGV
shot segv_pwrecord_P_empty 6 pw-record -P '' "$W/rec.wav"
# s5: loopback hard error a=b }{ c=d -> rc=255, zero nodes
shot err255_braces 6 pw-loopback -n "${TAG}_s5" -C "$NSA" -i 'a=b }{ c=d' -P "$NSB"
say "{\"leg\":\"s5_nodes\",\"witness\":$(pw-dump | python3 -c "import json,sys;d=json.load(sys.stdin);print(json.dumps([o['info']['props'].get('node.name') for o in d if 's5' in str(o.get('info',{}).get('props',{}).get('node.name',''))]))")}"
# s6: pw-cat -P 'a=b }{ c=d' -> rc=1 syntax error in --properties
shot err1_pwcat 6 pw-cat -p -P 'a=b }{ c=d' --target "$NSB" "$W/tone48.wav"
# s7: silent drop '}{ garbage' -> nodes with defaults
timeout 3 pw-loopback -n "${TAG}_s7" -C "$NSA" -i '}{ garbage' -P "$NSB" > /dev/null 2>&1
say "{\"leg\":\"s7_drop_silent\",\"in_props\":$(props_of "input.${TAG}_s7"),\"out_name\":$(pw-dump | python3 -c "import json,sys;d=json.load(sys.stdin);print(json.dumps([o['info']['props'].get('node.name') for o in d if '${TAG}_s7' in str(o.get('info',{}).get('props',{}).get('node.name',''))]))")}"
# s8: -l -5 uint32 wrap
timeout 3 pw-loopback -n "${TAG}_s8" -C "$NSA" -P "$NSB" -l -5 > /dev/null 2>&1
say "{\"leg\":\"s8_uint32_wrap\",\"in_latency\":$(pw-dump | python3 -c "import json,sys;d=json.load(sys.stdin);print(json.dumps([o['info']['props'].get('node.latency') for o in d if o.get('info',{}).get('props',{}).get('node.name')=='input.${TAG}_s8']))")}"
# s9: resample.disable + 44.1k file -> 48k sink = all-zero monitor
timeout 8 pw-cat -p -P 'resample.disable=true' --target "$NSB" "$W/tone44.wav" > /dev/null 2>&1 &
FEED=$!
timeout 6 pw-record -P stream.capture.sink=true -P node.name="${TAG}_s9tap" --target "$NSB" -n 144000 --rate 48000 --channels 2 --format s16 "$W/s9_mon.wav" > /dev/null 2>&1
wait $FEED 2>/dev/null
python3 - "$W/s9_mon.wav" >&9 <<'PY'
import json,sys,wave,numpy as np
try:
    with wave.open(sys.argv[1],'rb') as f:
        pcm=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').reshape(-1,2)
    seg=pcm[int(48000*0.4):]
    print(json.dumps({"leg":"s9_disable_zerofill","frames":int(len(pcm)),
        "settled_all_zero":bool(np.all(seg==0)),
        "settled_peak":int(np.abs(seg).max()) if len(seg) else -1}))
except Exception as e:
    print(json.dumps({"leg":"s9_disable_zerofill","error":str(e)}))
PY
# s10: resample.peaks + mismatch -> |x| artifact (min=0, octave dominant)
timeout 8 pw-cat -p -P 'resample.peaks=true' --target "$NSB" "$W/tone44.wav" > /dev/null 2>&1 &
FEED=$!
timeout 6 pw-record -P stream.capture.sink=true -P node.name="${TAG}_s10tap" --target "$NSB" -n 144000 --rate 48000 --channels 2 --format s16 "$W/s10_mon.wav" > /dev/null 2>&1
wait $FEED 2>/dev/null
python3 - "$W/s10_mon.wav" >&9 <<'PY'
import json,sys,wave,numpy as np
try:
    with wave.open(sys.argv[1],'rb') as f:
        pcm=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').reshape(-1,2)
    seg=pcm[int(48000*0.4):].astype(np.float64)
    def amp_at(c,f,rate=48000):
        x=c*np.hanning(len(c)); k=np.exp(-2j*np.pi*f*np.arange(len(c))/rate)
        return float(4*abs(np.dot(x,k))/len(c))
    out={"leg":"s10_peaks_abs","frames":int(len(pcm))}
    for i,ch in enumerate((seg[:,0],seg[:,1])):
        out[f"ch{i}"]={"min":float(ch.min()),"mean":round(float(ch.mean()),2),
            "neg_frac":round(float(np.mean(ch<0)),4),
            "zero_frac":round(float(np.mean(ch==0)),4),
            "a1k":round(amp_at(ch,1000),1),"a2k":round(amp_at(ch,2000),1),
            "a1_5k":round(amp_at(ch,1500),1),"a3k":round(amp_at(ch,3000),1)}
    print(json.dumps(out))
except Exception as e:
    print(json.dumps({"leg":"s10_peaks_abs","error":str(e)}))
PY
# s11: -d 1.0 real transport delay (light: onset method like fixture)
timeout 5 pw-loopback -n "${TAG}_s11" -C "$NSA" -P "$NSB" -d 1.0 > /dev/null 2>&1 &
LB=$!
sleep 0.8
timeout 4 pw-record -P stream.capture.sink=true -P node.name="${TAG}_s11tap" --target "$NSB" -n 96000 --rate 48000 --channels 2 --format s16 "$W/s11_mon.wav" > /dev/null 2>&1 &
TAP=$!
sleep 0.3; T0=$(python3 -c 'import time;print(time.monotonic())')
timeout 3 pw-cat -p --target "$NSA" "$W/tone48.wav" > /dev/null 2>&1
wait $TAP 2>/dev/null; kill $LB 2>/dev/null
python3 - "$W/s11_mon.wav" "$T0" >&9 <<'PY'
import json,sys,wave,numpy as np,time
try:
    with wave.open(sys.argv[1],'rb') as f:
        pcm=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').reshape(-1,2)
    nz=np.nonzero(np.max(np.abs(pcm),axis=1)>400)[0]
    first=float(nz[0])/48000 if len(nz) else None
    # transport = onset_pos - feed_offset ; feed started ~0.3s after tap spawn,
    # tap spawn ~0.8s after loopback spawn; record tap-relative numbers only
    print(json.dumps({"leg":"s11_d10_transport","first_nonsilent_s":first,
        "note":"tap-relative onset; ~1.0+d feed offset expected if -d real"}))
except Exception as e:
    print(json.dumps({"leg":"s11_d10_transport","error":str(e)}))
PY

# teardown — unload by index, name-verified
for pair in "$MA:$NSA" "$MB:$NSB" "$M44:$NS44"; do
  mid="${pair%%:*}"; sn="${pair##*:}"
  ok=$(pactl list short modules | awk -v m="$mid" -v s="sink_name=$sn" '$1==m && index($0,s){print "yes"}')
  if [ "$ok" = "yes" ]; then pactl unload-module "$mid"; fi
done
sleep 0.4
say "{\"teardown\":{\"r83v_objects_after\":$(pw-dump | python3 -c "import json,sys;d=json.load(sys.stdin);print(json.dumps([o.get('id') for o in d if 'r83v_${VPID}' in json.dumps(o)]))"),\"mods_left\":$(pactl list short modules | grep -c "r83v_${VPID}" || true)}}"
echo "spots done $(date -u +%FT%TZ)"
