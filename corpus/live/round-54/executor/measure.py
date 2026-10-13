import importlib.util,json
from pathlib import Path
s=importlib.util.spec_from_file_location("m", ".shokunin/audio/corpus/fixtures/measure_audio.py")
m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
p=Path(".shokunin/audio/corpus/live/round-54/executor")
for f in ("pcm32.wav","pcm16.wav"):
 print(json.dumps(m.measure("ui",m.SPECS["ui"],(p/f).resolve())))
