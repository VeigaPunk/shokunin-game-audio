import importlib.util, json
from pathlib import Path
p=Path(".shokunin/audio/corpus/fixtures/measure_audio.py")
s=importlib.util.spec_from_file_location("measure_audio",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
candidate=Path(".shokunin/audio/corpus/live/round-35/alt/movement_third_candidate.wav").resolve()
c=m.measure("movement_third_candidate",(.30,100,16000,False),candidate)
b={n:m.measure(n,m.SPECS[n]) for n in ("movement","movement_alt")}
print(json.dumps({"candidate":c,"baselines":b},indent=2))
