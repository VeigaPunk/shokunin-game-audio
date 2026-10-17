import importlib.util, json, sys
from pathlib import Path
root=Path(__file__).resolve().parents[4]
src=root/"corpus/fixtures/measure_audio.py"
s=importlib.util.spec_from_file_location("ma",src); ma=importlib.util.module_from_spec(s); s.loader.exec_module(ma)
for f in (Path(__file__).parent/"mono.wav",Path(__file__).parent/"stereo.wav"):
 x=ma.measure("ui",ma.SPECS["ui"],f); print(json.dumps(x,sort_keys=True))
sys.exit(1 if any(ma.measure("ui",ma.SPECS["ui"],f)["failures"] for f in (Path(__file__).parent/"stereo.wav",)) else 0)
