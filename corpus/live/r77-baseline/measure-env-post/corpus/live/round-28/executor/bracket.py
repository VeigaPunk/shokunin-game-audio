import sys, pathlib, wave
import numpy as np
sys.path.insert(0, str(pathlib.Path(".shokunin/audio/corpus/fixtures").resolve()))
from measure_audio import measure, SPECS
out=pathlib.Path(".shokunin/audio/corpus/live/round-28/executor")
rate=48000; n=5760; t=np.arange(n)/rate
# Baseline reproduces the source-generated UI chirp formula. Variant changes only chirp coefficient.
for label, coeff in [("base",700.0),("f620",620.0),("f615",615.0),("f610",610.0),("f780",780.0),("f785",785.0),("f790",790.0)]:
    x=.38*np.sin(2*np.pi*(coeff*t+800*t*t))*np.exp(-30*t)
    pcm=np.round(np.clip(x,-1,1)*32767).astype("<i2")
    p=(out/(label+".wav")).resolve()
    with wave.open(str(p),"wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(pcm.tobytes())
    m=measure(label,(.12,250,4000,False),p)
    print(label, coeff, m["duration_s"],m["peak_full_scale"],m["rms_dbfs"],m["spectral_centroid_hz"],m["failures"])
