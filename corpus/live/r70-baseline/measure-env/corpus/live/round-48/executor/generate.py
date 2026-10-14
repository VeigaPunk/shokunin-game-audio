from pathlib import Path
import sys, wave
import numpy as np
out=Path(sys.argv[1]); rate=int(sys.argv[2]); n=5760
# Identical signal samples are generated once on a 48 kHz time grid, independent of output rate.
t=np.arange(n)/48000
x=.28*np.sin(2*np.pi*1000*t)*np.hanning(n)
pcm=np.rint(np.clip(x,-1,1)*32767).astype('<i2')
with wave.open(str(out),'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(pcm.tobytes())
