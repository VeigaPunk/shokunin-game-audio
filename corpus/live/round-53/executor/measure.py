import sys,json
from pathlib import Path
sys.path.insert(0, ".shokunin/audio/corpus/fixtures")
from measure_audio import measure,SPECS
root=Path(".shokunin/audio/corpus/live/round-53/executor").resolve()
print(json.dumps([measure(x,SPECS["ui"],root/(x+".wav")) for x in ("float32","pcm16")],indent=2))
