import importlib.util, json
from pathlib import Path
p=Path(".shokunin/audio/corpus/fixtures/measure_audio.py")
s=importlib.util.spec_from_file_location("measure_audio",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
spec=(2.0,5,200,True)
a=m.measure("ambience_base",spec,Path('/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-37/alt/ambience_base.wav'))
b=m.measure("ambience_alt",spec,Path('/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-37/alt/ambience_alt.wav'))
print(json.dumps({"baseline":a,"variant":b,"duration_delta_s":abs(a["duration_s"]-b["duration_s"]),"centroid_relative_delta":abs(a["spectral_centroid_hz"]-b["spectral_centroid_hz"])/a["spectral_centroid_hz"]},indent=2))
