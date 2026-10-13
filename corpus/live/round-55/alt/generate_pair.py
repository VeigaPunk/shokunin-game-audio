import math, struct, hashlib
from pathlib import Path
import numpy as np
out=Path(__file__).parent
rate=48000
n=5760
t=np.arange(n,dtype=np.float64)/rate
x=.19*np.sin(2*np.pi*613*t)+.095*np.sin(2*np.pi*1733*t)+.04*np.sin(2*np.pi*2963*t)
s=np.rint(np.clip(x,-1,1)*32767).astype("<i2")
data=s.tobytes()
# Standard 16-byte WAVE_FORMAT_PCM fmt chunk.
fmt=struct.pack("<HHIIHH",1,1,rate,rate*2,2,16)
chunks=b"fmt "+struct.pack("<I",len(fmt))+fmt+b"data"+struct.pack("<I",len(data))+data
standard=b"RIFF"+struct.pack("<I",4+len(chunks))+b"WAVE"+chunks
# WAVEFORMATEXTENSIBLE, PCM subtype, mono front-center speaker mask.
guid=bytes.fromhex("0100000000001000800000aa00389b71")
fmtx=struct.pack("<HHIIHHHHI",0xfffe,1,rate,rate*2,2,16,22,16,0x4)+guid
chunksx=b"fmt "+struct.pack("<I",len(fmtx))+fmtx+b"data"+struct.pack("<I",len(data))+data
extensible=b"RIFF"+struct.pack("<I",4+len(chunksx))+b"WAVE"+chunksx
for name,b in (("standard_pcm16.wav",standard),("extensible_pcm16.wav",extensible)):
 p=out/name;p.write_bytes(b);print(name,len(b),hashlib.sha256(b).hexdigest())
