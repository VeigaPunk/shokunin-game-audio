import importlib.util, json
from pathlib import Path
p=Path(".shokunin/audio/corpus/fixtures/measure_audio.py").resolve()
s=importlib.util.spec_from_file_location("measure_audio",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
out=Path(".shokunin/audio/corpus/live/round-27/executor").resolve()
records={}
for name,secs in (("base",.12),("var6719",6719/48000),("var6720",.14)):
    records[name]=m.measure(name,(secs,250,4000,False),out/(name+".wav"))
base=records["base"]
for name in ("var6719","var6720"):
    v=records[name]; d=abs(v["duration_s"]-base["duration_s"]); c=abs(v["spectral_centroid_hz"]-base["spectral_centroid_hz"])/base["spectral_centroid_hz"]
    print(json.dumps({"pair":name,"duration_delta_s":d,"centroid_relative_delta":c,"distinctness_passed":d>=.020 or c>=.10}))
print(json.dumps(records,indent=2))
