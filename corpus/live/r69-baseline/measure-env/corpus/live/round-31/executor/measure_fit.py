import importlib.util, json, wave
from pathlib import Path
import numpy as np
fixture=Path(".shokunin/audio/corpus/fixtures/measure_audio.py")
spec=importlib.util.spec_from_file_location("measure_audio", fixture)
ma=importlib.util.module_from_spec(spec); spec.loader.exec_module(ma)
out=Path(".shokunin/audio/corpus/live/round-31/executor").resolve()
rate=48000
for name,count,k in (("base",5760,1.0),("variant",6719,1.0)):
    t=np.arange(count)/rate
    samples=.38*np.sin(2*np.pi*k*(700*t+800*t*t))*np.exp(-30*t)
    pcm=np.round(np.clip(samples,-1,1)*32767).astype("<i2")
    with wave.open(str(out/(name+".wav")),"wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(pcm.tobytes())
base=ma.measure("ui",ma.SPECS["ui"],out/"base.wav")
fits=[]
for k in [0.90,0.92,0.94,0.95,0.96,0.98,1.02,1.04,1.06,1.08,1.10,1.12]:
    t=np.arange(6719)/rate
    samples=.38*np.sin(2*np.pi*k*(700*t+800*t*t))*np.exp(-30*t)
    pcm=np.round(np.clip(samples,-1,1)*32767).astype("<i2")
    with wave.open(str(out/"variant.wav"),"wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(pcm.tobytes())
    m=ma.measure("ui_alt",(6719/rate,250,4000,False),out/"variant.wav")
    fits.append({"k":k,"measure":m,"rel":abs(m["spectral_centroid_hz"]-base["spectral_centroid_hz"])/base["spectral_centroid_hz"]})
print(json.dumps({"base":base,"fits":fits},indent=2))
