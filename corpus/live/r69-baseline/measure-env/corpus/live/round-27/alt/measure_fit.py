import importlib.util, pathlib, json
p=pathlib.Path(".shokunin/audio/corpus/fixtures/measure_audio.py")
s=importlib.util.spec_from_file_location("measure_audio",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
for n,d in (("base",.12),("n6719",6719/48000),("n6720",.14),("tone_base",.12),("tone6719",6719/48000),("tone6720",.14)):
 r=m.measure(n,(d,250,4000,False),pathlib.Path(".shokunin/audio/corpus/live/round-27/alt").resolve()/(n+".wav")); print(n,json.dumps({k:r[k] for k in ("duration_s","peak_full_scale","rms_dbfs","spectral_centroid_hz","failures")}))
