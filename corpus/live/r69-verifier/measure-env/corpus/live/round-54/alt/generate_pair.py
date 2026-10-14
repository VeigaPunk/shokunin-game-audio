import math, struct, wave
from pathlib import Path
import numpy as np
p=Path(__file__).parent
rate=48000
n=5760
t=np.arange(n,dtype=np.float64)/rate
x=0.22*np.sin(2*np.pi*733*t)+0.11*np.sin(2*np.pi*2131*t)+0.035*np.sin(2*np.pi*3217*t)
s=np.rint(x*32767).astype(np.int16)
s32=(s.astype(np.int64)*65536).astype(np.int32)
for name, data, width in [("candidate_pcm32.wav",s32,4),("control_pcm16.wav",s,2)]:
    with wave.open(str(p/name),"wb") as w:
        w.setnchannels(1); w.setsampwidth(width); w.setframerate(rate); w.writeframes(data.astype("<i%d"%width).tobytes())
    import hashlib
    print(name, len((p/name).read_bytes()), hashlib.sha256((p/name).read_bytes()).hexdigest())
