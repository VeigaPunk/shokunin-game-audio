import importlib.util
from pathlib import Path
p=Path(".shokunin/audio/corpus/fixtures/measure_audio.py")
s=importlib.util.spec_from_file_location("measure_audio", p)
m=importlib.util.module_from_spec(s)
s.loader.exec_module(m)
spec=m.SPECS["ui"]
a=m.measure("ui_clone", spec, Path(".shokunin/audio/corpus/live/round-26/alt/ui_clone.wav").resolve())
b=m.measure("ui_clone_alt", spec, Path(".shokunin/audio/corpus/live/round-26/alt/ui_clone_alt.wav").resolve())
duration_delta=abs(a["duration_s"]-b["duration_s"])
centroid_delta=abs(a["spectral_centroid_hz"]-b["spectral_centroid_hz"])/a["spectral_centroid_hz"]
print({"base_failures":a["failures"],"variant_failures":b["failures"],"duration_delta_s":duration_delta,"centroid_relative_delta":centroid_delta,"distinctness_passed":duration_delta>=.020 or centroid_delta>=.10})
