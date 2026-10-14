import numpy as np, wave, hashlib
from pathlib import Path
out=Path(".shokunin/audio/corpus/live/round-35/alt/movement_third_candidate.wav")
sr=48000; n=14400; t=np.arange(n)/sr
rng=np.random.default_rng(3501)
env=np.sin(np.pi*np.minimum(t/.012,1)/2)**2 * np.exp(-t/0.20)
sig=.52*env*np.sin(2*np.pi*1800*t)
# Short reproducible broadband attack adds non-tonal content.
attack=np.zeros(n); k=int(.012*sr); attack[:k]=rng.normal(0,.07,k)*np.exp(-np.arange(k)/(sr*.003))
sig+=attack
sig*=np.minimum(np.arange(n)/(sr*.002),1)
sig=np.clip(sig,-.9,.9)
pcm=np.round(sig*32767).astype("<i2")
with wave.open(str(out),"wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes())
print({"path":str(out),"frames":len(pcm),"sha256":hashlib.sha256(out.read_bytes()).hexdigest()})
