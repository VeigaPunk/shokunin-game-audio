import importlib.util, pathlib, json
p=pathlib.Path(".shokunin/audio/corpus/fixtures/measure_audio.py").resolve()
s=importlib.util.spec_from_file_location("measure_audio",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
for name in ("candidate_pcm24.wav","control_pcm16.wav"):
 q=p.parent.parent / "live/round-51/alt" / name
 r=m.measure(name,(.12,250,4000,False),q)
 print(json.dumps(r,sort_keys=True))
