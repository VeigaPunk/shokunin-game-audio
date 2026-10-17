import hashlib, math, struct, wave
from pathlib import Path
import numpy as np
out=Path(__file__).parent
rate=48000; n=5760
i=np.arange(n)
# A distinct two-tone UI pulse with a gentle raised-cosine envelope.
env=np.minimum(1.0, np.minimum(i/96, (n-1-i)/96))
env=np.clip(env,0,1)
x=env*(0.23*np.sin(2*np.pi*733*i/rate)+0.11*np.sin(2*np.pi*1469*i/rate+0.31))
d=np.clip(np.rint(x*128),-128,127).astype(np.int16)
u8=(d+128).astype(np.uint8)
s16=(d.astype(np.int32)*256).astype('<i2')
for name,width,data in [('candidate_pcm8.wav',1,u8.tobytes()),('control_pcm16.wav',2,s16.tobytes())]:
 with wave.open(str(out/name),'wb') as w:
  w.setnchannels(1); w.setsampwidth(width); w.setframerate(rate); w.writeframes(data)
 print(name, 'sha256='+hashlib.sha256((out/name).read_bytes()).hexdigest(), 'bytes='+str((out/name).stat().st_size))
