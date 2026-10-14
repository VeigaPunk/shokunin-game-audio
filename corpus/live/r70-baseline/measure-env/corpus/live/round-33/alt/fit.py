import importlib.util, math, sys, wave
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
# Measure using the project's own helper, not a parallel metric.
spec=importlib.util.spec_from_file_location("measure_audio", ROOT/"fixtures/measure_audio.py")
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
rate=48000; seconds=.20
t=np.arange(round(seconds*rate))/rate
samples=.38*np.sin(2*np.pi*(700*t+800*t*t))*np.exp(-30*t)
pcm=np.round(np.clip(samples,-1,1)*32767).astype("<i2")
out=Path(__file__).parent/"ui_third.wav"
with wave.open(str(out),"wb") as w:
 w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(pcm.tobytes())
specs=(.20,250,4000,False)
rows={}
for name,path,s in (("ui",ROOT/"artifacts/ui.wav",(.12,250,4000,False)),("ui_alt",ROOT/"artifacts/ui_alt.wav",(.16,250,4000,False)),("ui_third",out,specs)):
 rows[name]=mod.measure(name,s,path)
 print(name,rows[name])
for name in ("ui","ui_alt"):
 a,b=rows[name],rows["ui_third"]
 dd=abs(b["duration_s"]-a["duration_s"])
 cr=abs(b["spectral_centroid_hz"]-a["spectral_centroid_hz"])/a["spectral_centroid_hz"]
 print("pair",name,"vs ui_third duration_delta_s",repr(dd),"centroid_relative_delta",repr(cr),"duration_arm",dd>=.020,"centroid_arm",cr>=.10,"OR_pass",dd>=.020 or cr>=.10)
