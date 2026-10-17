import importlib.util,json
from pathlib import Path
p=Path(".shokunin/audio/corpus/fixtures/measure_audio.py").resolve()
s=importlib.util.spec_from_file_location("ma",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
root=m.ROOT; d=root/"live/round-32/executor"
base=m.measure("ui",m.SPECS["ui"],(d/"ui_depth_base.wav").resolve())
variant=m.measure("ui_alt",(6719/48000,250,4000,False),(d/"ui_depth_k1.14.wav").resolve())
delta=abs(variant["duration_s"]-base["duration_s"]); centroid=abs(variant["spectral_centroid_hz"]-base["spectral_centroid_hz"])/base["spectral_centroid_hz"]
print(json.dumps({"base":base,"variant":variant,"duration_delta_s":delta,"centroid_relative_delta":centroid,"duration_branch":delta>=.020,"centroid_branch":centroid>=.10,"comparator_pass":delta>=.020 or centroid>=.10},indent=2))
