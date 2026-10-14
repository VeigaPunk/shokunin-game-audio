import importlib.util, json, sys
from pathlib import Path
p=Path(sys.argv[1]); root=Path(sys.argv[2])
s=importlib.util.spec_from_file_location("measure_audio",root); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
for name in ("pcm8","pcm16"):
 print(json.dumps(m.measure(name,m.SPECS["ui"],p/(name+".wav")),sort_keys=True))
