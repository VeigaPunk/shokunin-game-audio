import json, subprocess, sys
from pathlib import Path
import numpy as np
for p in map(Path, sys.argv[1:]):
    probe=json.loads(subprocess.run(["ffprobe","-v","error","-show_entries","stream=sample_rate,channels,codec_name,bits_per_sample:format=duration","-of","json",str(p)],check=True,capture_output=True).stdout)
    st=probe["streams"][0]; rate=int(st["sample_rate"])
    raw=subprocess.run(["sox",str(p),"-t","f32","-e","floating-point","-"],check=True,capture_output=True).stdout
    x=np.frombuffer(raw,dtype="<f4").astype(np.float64)
    f=np.fft.rfftfreq(len(x),1/rate); a=np.abs(np.fft.rfft(x)); c=float(np.dot(f,a)/a.sum())
    print(json.dumps({"path":str(p),"frames":len(x),"duration_s":float(probe["format"]["duration"]),"sample_rate_hz":rate,"channels":int(st["channels"]),"codec_name":st.get("codec_name"),"bits_per_sample":st.get("bits_per_sample"),"peak":float(np.max(np.abs(x))),"rms":float(np.sqrt(np.mean(x*x))),"spectral_centroid_hz":c}))
