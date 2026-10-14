import wave
import numpy as np
from pathlib import Path
r=48000; n=5760; t=np.arange(n)/r
x=(.18*np.sin(2*np.pi*440*t)+.10*np.sin(2*np.pi*1200*t+.2)+.06*np.sin(2*np.pi*2600*t+.7))*np.exp(-t*8)
x=np.round(np.clip(x,-.95,.95)*32767).astype("<i2")
for name,ch,data in (("mono.wav",1,x.tobytes()),("stereo.wav",2,np.column_stack((x,x)).astype("<i2").tobytes())):
 with wave.open(str(Path(__file__).parent/name),"wb") as w:
  w.setnchannels(ch); w.setsampwidth(2); w.setframerate(r); w.writeframes(data)
