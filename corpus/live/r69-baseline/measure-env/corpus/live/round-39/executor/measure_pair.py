import importlib.util, json, pathlib, sys
root=pathlib.Path(__file__).resolve().parents[3]
p=pathlib.Path(__file__).parent
spec=importlib.util.spec_from_file_location("measure_audio", root/"fixtures/measure_audio.py")
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
spec2=(2.0,5,200,True)
a=m.measure("baseline",spec2,p/"baseline.wav")
b=m.measure("variant",spec2,p/"variant.wav")
for x in (a,b): x["path"]=pathlib.Path(x["path"]).name
ca=a["spectral_centroid_hz"]; cb=b["spectral_centroid_hz"]
print(json.dumps({"A":a,"B":b,"forward":abs(cb-ca)/ca,"reverse":abs(cb-ca)/cb},indent=2))
