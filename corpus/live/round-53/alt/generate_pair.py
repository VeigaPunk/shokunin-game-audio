import hashlib, math, struct, wave
from pathlib import Path
import numpy as np
out=Path(__file__).parent
rate=48000; n=5760
i=np.arange(n,dtype=np.float64)
# Distinct pulsed two-tone, quantize once to signed PCM16, then encode exact normalized values as float32.
env=np.minimum(1.0,np.minimum(i/128.0,(n-1-i)/128.0)); env=np.clip(env,0,1)
x=env*(0.27*np.sin(2*np.pi*887*i/rate+0.17)+0.09*np.sin(2*np.pi*1777*i/rate))
s16=np.clip(np.rint(x*32768),-32768,32767).astype('<i2')
f32=(s16.astype(np.float64)/32768.0).astype('<f4')
pcm=s16.tobytes(); flt=f32.tobytes()
def chunk(tag,data): return tag+struct.pack('<I',len(data))+data+(b'\0' if len(data)&1 else b'')
fmt_pcm=struct.pack('<HHIIHH',1,1,rate,rate*2,2,16)
fmt_flt=struct.pack('<HHIIHH',3,1,rate,rate*4,4,32)
def wav(fmt,data):
 body=chunk(b'fmt ',fmt)+chunk(b'data',data)
 return b'RIFF'+struct.pack('<I',len(body)+4)+b'WAVE'+body
(out/'candidate_float32.wav').write_bytes(wav(fmt_flt,flt))
(out/'control_pcm16.wav').write_bytes(wav(fmt_pcm,pcm))
for name in ('candidate_float32.wav','control_pcm16.wav'):
 b=(out/name).read_bytes(); print(name,'bytes='+str(len(b)),'sha256='+hashlib.sha256(b).hexdigest())
