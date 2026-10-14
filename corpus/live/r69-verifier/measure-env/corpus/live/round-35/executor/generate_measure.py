import importlib.util
import pathlib
import wave
import numpy as np

out=pathlib.Path(__file__).parent
rate=48000
n=round(.30*rate)
t=np.arange(n)/rate
# A smooth, exponentially decaying 620 Hz sinusoid with a short deterministic noise onset.
rng=np.random.default_rng(3501)
env=np.sin(np.pi*np.arange(n)/(n-1))**0.35
samples=.28*env*np.sin(2*np.pi*620*t)
samples[:1200] += .035*rng.standard_normal(1200)*np.linspace(1,0,1200)
pcm=np.round(np.clip(samples,-1,1)*32767).astype("<i2")
path=out/"movement_third_candidate.wav"
with wave.open(str(path),"wb") as wav:
    wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(rate); wav.writeframes(pcm.tobytes())
spec=importlib.util.spec_from_file_location("measure_audio", pathlib.Path(".shokunin/audio/corpus/fixtures/measure_audio.py"))
ma=importlib.util.module_from_spec(spec); spec.loader.exec_module(ma)
result=ma.measure("movement_third_candidate",(.30,100,16000,False),path)
print(result)

import hashlib
for name in ("movement", "movement_alt"):
    base=ma.measure(name,(.24 if name=="movement" else .36,100,16000,False))
    rel=abs(result["spectral_centroid_hz"]-base["spectral_centroid_hz"])/base["spectral_centroid_hz"]
    print({"baseline":name,"duration_s":base["duration_s"],"centroid_hz":base["spectral_centroid_hz"],"relative_centroid_delta":rel,"duration_delta_s":abs(result["duration_s"]-base["duration_s"]),"baseline_failures":base["failures"]})
print({"candidate_sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
