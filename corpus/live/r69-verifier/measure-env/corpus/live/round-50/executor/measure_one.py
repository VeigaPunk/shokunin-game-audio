import importlib.util, json, sys
from pathlib import Path
root=Path(__file__).resolve().parents[4]; src=root/"corpus/fixtures/measure_audio.py"
s=importlib.util.spec_from_file_location("ma",src); ma=importlib.util.module_from_spec(s); s.loader.exec_module(ma)
p=Path(sys.argv[1]); out=ma.measure("ui",ma.SPECS["ui"],p); print(json.dumps(out,sort_keys=True)); sys.exit(bool(out["failures"]))
