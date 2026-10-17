import wave
import numpy as np
from pathlib import Path
N=5760
n=np.arange(N,dtype=np.float64)
x=np.rint(9000*np.sin(2*np.pi*1000*n/48000)).astype("<i2")
for name, ch in (("mono",1),("stereo",2)):
    data=x if ch==1 else np.column_stack((x,x)).reshape(-1)
    with wave.open(str(Path(__file__).parent/(name+".wav")),"wb") as w:
        w.setnchannels(ch); w.setsampwidth(2); w.setframerate(48000); w.writeframes(data.tobytes())
print("generated",len(x),"frames per channel")
