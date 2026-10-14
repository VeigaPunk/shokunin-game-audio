import math, struct, wave
from pathlib import Path
import hashlib
p=Path(".shokunin/audio/corpus/live/round-56/alt")
rate=48000; n=5760
samples=[]
for i in range(n):
 t=i/rate
 x=.21*math.sin(2*math.pi*733*t)+.09*math.sin(2*math.pi*1823*t)+.035*math.sin(2*math.pi*3111*t)
 samples.append(max(-32768,min(32767,round(x*32767))))
data=struct.pack("<"+"h"*n,*samples)
def chunk(tag,b): return tag+struct.pack('<I',len(b))+b+(b'\0' if len(b)&1 else b'')
def write(mask,name):
 fmt=struct.pack('<HHIIHHHHI',0xfffe,1,rate,rate*2,2,16,22,16,mask)+bytes.fromhex('0100000000001000800000aa00389b71')
 body=b'WAVE'+chunk(b'fmt ',fmt)+chunk(b'data',data)
 raw=b'RIFF'+struct.pack('<I',len(body))+body
 f=p/name; f.write_bytes(raw); print(name,len(raw),hashlib.sha256(raw).hexdigest())
write(0,'mask0.wav'); write(4,'mask4.wav')
