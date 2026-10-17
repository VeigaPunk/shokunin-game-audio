import subprocess, numpy as np, hashlib, pathlib, json
d=pathlib.Path(__file__).parent
a=[]
for f in ["control_pcm16.wav","candidate_pcm24.wav"]:
 p=d/f; raw=subprocess.run(["sox",str(p),"-t","f32","-e","floating-point","-"],check=True,capture_output=True).stdout
 x=np.frombuffer(raw,dtype="<f4").astype(np.float64); a.append(x)
 print(json.dumps({"file":f,"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"sox_decoded_samples":len(x),"decoded_min":float(x.min()),"decoded_max":float(x.max()),"decoded_rms":float(np.sqrt(np.mean(x*x)))},sort_keys=True))
print("decoded_exact_equal",bool(np.array_equal(a[0],a[1])),"max_abs_difference",float(np.max(np.abs(a[0]-a[1]))))
