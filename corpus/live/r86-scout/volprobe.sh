#!/bin/bash
pw-record -P stream.capture.sink=true --target r86ctl_ns mon.wav >/dev/null 2>&1 &
REC=$!
sleep 0.6
pw-play --target r86ctl_ns tone1k.wav >/dev/null 2>&1 &
PLAY=$!
sleep 2.0
eval "$1" >/dev/null 2>&1
wait $PLAY 2>/dev/null
sleep 0.3; kill $REC 2>/dev/null; wait $REC 2>/dev/null
python3 -c "
import numpy as np, wave
w=wave.open('mon.wav'); n=w.getnframes(); d=np.frombuffer(w.readframes(n),np.int16).reshape(-1,2)
wsize=12000
out=[]
for i in range(0,d.shape[0]-wsize,wsize):
    out.append((round(i/48000,2),int(np.abs(d[i:i+wsize,0]).max())))
print(out)"
