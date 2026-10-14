import math, struct, wave
from pathlib import Path
import numpy as np
p=Path(__file__).parent
rate=48000; n=5760
t=np.arange(n,dtype=np.float64)/rate
x=.25*np.sin(2*np.pi*1000*t)+.08*np.sin(2*np.pi*1500*t)
s=np.rint(x*32767).astype("<i2")
data=s.tobytes()
# standard PCM control
with wave.open(str(p/"pcm16.wav"),"wb") as w:
 w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(data)
# RIFF WAVE_FORMAT_EXTENSIBLE, fmt size 40, PCM subtype GUID
guid=bytes.fromhex("0100000000001000800000aa00389b71")
fmt=struct.pack("<HHIIHHHHI",0xfffe,1,rate,rate*2,2,16,22,16,4)+guid
assert len(fmt)==40
chunks=b"fmt "+struct.pack("<I",len(fmt))+fmt+b"data"+struct.pack("<I",len(data))+data
body=b"WAVE"+chunks
(p/"extensible.wav").write_bytes(b"RIFF"+struct.pack("<I",len(body))+body)
print(len(data),len(fmt),guid.hex())
