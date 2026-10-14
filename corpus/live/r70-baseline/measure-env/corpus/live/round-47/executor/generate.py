import numpy as np, wave, sys
from pathlib import Path
out=Path(sys.argv[1]); f=float(sys.argv[2]); n=5760; rate=48000
t=np.arange(n)/rate
x=.28*np.sin(2*np.pi*f*t)*np.hanning(n)
y=np.rint(np.clip(x,-1,1)*32767).astype("<i2")
with wave.open(str(out),"wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(y.tobytes())
