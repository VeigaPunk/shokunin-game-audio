import math, struct, hashlib
from pathlib import Path
import numpy as np
p=Path(".shokunin/audio/corpus/live/round-58/critic")
rate=48000; n=5760
t=np.arange(n,dtype=np.float64)/rate
s=np.rint(8191*(.30*np.sin(2*np.pi*997*t)+.12*np.sin(2*np.pi*1733*t))).astype(np.int16)*4
payload=s.astype("<i2").tobytes()
guid=bytes.fromhex("0100000000001000800000aa00389b71")
def wav(v):
 fmt=struct.pack("<HHIIHHHHI",0xfffe,1,rate,rate*2,2,16,22,v,4)+guid
 data=b"data"+struct.pack("<I",len(payload))+payload
 body=b"WAVE"+b"fmt "+struct.pack("<I",len(fmt))+fmt+data
 return b"RIFF"+struct.pack("<I",len(body))+body
for v,name in [(14,"valid14.wav"),(16,"valid16.wav")]:
 b=wav(v); (p/name).write_bytes(b); print(name,len(b),hashlib.sha256(b).hexdigest())
print("payload",len(payload),hashlib.sha256(payload).hexdigest(),"range",int(s.min()),int(s.max()),"not_div4",int(np.count_nonzero(s%4)),"frames",len(s))
