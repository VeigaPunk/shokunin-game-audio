import importlib.util, pathlib, wave
import numpy as np
HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[2]
spec=importlib.util.spec_from_file_location("measure_audio", ROOT/"fixtures/measure_audio.py")
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
rate=48000
t=np.arange(round(.40*rate))/rate
# Independent, deterministic tapered 2.2 kHz tone with a short broadband transient.
env=np.exp(-11*t)
samples=.38*np.sin(2*np.pi*2200*t)*env + .045*np.random.default_rng(3401).standard_normal(len(t))*np.exp(-80*t)
pcm=np.round(np.clip(samples,-1,1)*32767).astype("<i2")
out=HERE/"impact_third_candidate.wav"
with wave.open(str(out),"wb") as w:
 w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(pcm.tobytes())
result=m.measure("impact_third_candidate",(.40,50,15000,False),out)
print(result)
