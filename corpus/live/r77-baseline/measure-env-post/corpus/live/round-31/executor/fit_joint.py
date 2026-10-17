# Fit requested centroid ratio in a narrow neighborhood; record every measured coefficient.
import json, wave
import numpy as np
from pathlib import Path
import importlib.util
spec=importlib.util.spec_from_file_location("measure_audio", ".shokunin/audio/corpus/fixtures/measure_audio.py")
ma=importlib.util.module_from_spec(spec); spec.loader.exec_module(ma)
out=Path(".shokunin/audio/corpus/live/round-31/executor").resolve(); rate=48000
base=ma.measure("ui",ma.SPECS["ui"],out/"base.wav")
rows=[]
for k in np.linspace(1.08,1.12,81):
 t=np.arange(6719)/rate; sig=.38*np.sin(2*np.pi*k*(700*t+800*t*t))*np.exp(-30*t)
 pcm=np.round(np.clip(sig,-1,1)*32767).astype("<i2")
 with wave.open(str(out/"variant.wav"),"wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(pcm.tobytes())
 m=ma.measure("ui_alt",(6719/rate,250,4000,False),out/"variant.wav")
 rel=abs(m["spectral_centroid_hz"]-base["spectral_centroid_hz"])/base["spectral_centroid_hz"]
 rows.append({"k":float(k),"m":m,"rel":rel})
eligible=[x for x in rows if 0<x["rel"]<.10 and not x["m"]["failures"]]
best=min(eligible,key=lambda x:abs(x["rel"]-.10))
# Rewrite chosen sample exactly and remeasure.
k=best["k"]; t=np.arange(6719)/rate; sig=.38*np.sin(2*np.pi*k*(700*t+800*t*t))*np.exp(-30*t); pcm=np.round(np.clip(sig,-1,1)*32767).astype("<i2")
with wave.open(str(out/"variant.wav"),"wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(pcm.tobytes())
variant=ma.measure("ui_alt",(6719/rate,250,4000,False),out/"variant.wav")
rel=abs(variant["spectral_centroid_hz"]-base["spectral_centroid_hz"])/base["spectral_centroid_hz"]
result={"base":base,"variant":variant,"selected_k":k,"duration_delta_s":abs(variant["duration_s"]-base["duration_s"]),"centroid_relative_delta":rel,"duration_branch":abs(variant["duration_s"]-base["duration_s"])>=.020,"centroid_branch":rel>=.10,"comparator_pass":abs(variant["duration_s"]-base["duration_s"])>=.020 or rel>=.10,"fit_scan":[{"k":x["k"],"centroid_hz":x["m"]["spectral_centroid_hz"],"relative_delta":x["rel"],"ordinary_failures":x["m"]["failures"]} for x in rows]}
(out/"fit_results.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps({"selected_k":k,"ratio":rel,"duration_delta":result["duration_delta_s"],"branches":[result["duration_branch"],result["centroid_branch"]],"base_failures":base["failures"],"variant_failures":variant["failures"]}))
