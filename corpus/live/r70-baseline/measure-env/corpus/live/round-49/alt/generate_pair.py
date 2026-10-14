import hashlib, wave
from pathlib import Path
import numpy as np
out=Path(__file__).parent
n=5760
# Deterministic mono transient, defined by sample index; identical PCM payload at each declared rate.
i=np.arange(n,dtype=np.float64)
env=np.sin(np.pi*np.minimum(i/(n*.28),1)/2)**2
x=np.round(np.clip(.28*env*np.sin(2*np.pi*997*i/48000),-1,1)*32767).astype("<i2")
for rate in (48001,48000):
 p=out/f"ui-{rate}.wav"
 with wave.open(str(p),"wb") as w:
  w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(x.tobytes())
 print(p, hashlib.sha256(p.read_bytes()).hexdigest(), hashlib.sha256(x.tobytes()).hexdigest())
