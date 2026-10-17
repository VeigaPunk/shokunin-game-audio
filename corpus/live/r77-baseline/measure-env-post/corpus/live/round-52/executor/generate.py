import numpy as np, wave, hashlib
from pathlib import Path
out=Path(__file__).parent
n=5760; rate=48000
x=.25*np.sin(2*np.pi*1000*np.arange(n)/rate)+.08*np.sin(2*np.pi*1500*np.arange(n)/rate)
u=np.clip(np.rint(x*127+128),0,255).astype(np.uint8)
s16=(u.astype(np.int16)-128)*256
(out/'pcm8.wav').write_bytes(b'')
with wave.open(str(out/'pcm8.wav'),'wb') as w:
 w.setnchannels(1);w.setsampwidth(1);w.setframerate(rate);w.writeframes(u.tobytes())
with wave.open(str(out/'pcm16.wav'),'wb') as w:
 w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes(s16.astype('<i2').tobytes())
for p in [out/'pcm8.wav',out/'pcm16.wav']:
 print(p.name,hashlib.sha256(p.read_bytes()).hexdigest(),len(p.read_bytes()))
print('pcm8 stream sha256',hashlib.sha256(u.tobytes()).hexdigest())
print('pcm16 stream sha256',hashlib.sha256(s16.astype('<i2').tobytes()).hexdigest())
