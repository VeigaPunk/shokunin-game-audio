import importlib.util, json, pathlib, hashlib
module_path=pathlib.Path(".shokunin/audio/corpus/fixtures/measure_audio.py").resolve()
spec=importlib.util.spec_from_file_location("measure_audio", module_path)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
base=m.ROOT/"live/round-45/alt"
for n in (5713,5711):
 p=base/f"alt-ui-{n}.wav"
 result=m.measure("ui",m.SPECS["ui"],p)
 result["sha256"]=hashlib.sha256(p.read_bytes()).hexdigest()
 print(json.dumps(result,sort_keys=True))
