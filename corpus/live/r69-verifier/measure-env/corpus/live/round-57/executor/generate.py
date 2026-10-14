import math, struct, hashlib
from pathlib import Path
out=Path(__file__).parent
rate=48000
frames=5760
samples=[round(32767*(.25*math.sin(2*math.pi*1000*i/rate)+.08*math.sin(2*math.pi*1500*i/rate))) for i in range(frames)]
data=struct.pack("<"+"h"*frames,*samples)
guid=bytes.fromhex("0100000000001000800000aa00389b71")
for bits in (15,16):
    fmt=struct.pack("<HHIIHHHHI",0xfffe,1,rate,rate*2,2,16,22,bits,0x4)+guid
    body=b"WAVE"+b"fmt "+struct.pack("<I",len(fmt))+fmt+b"data"+struct.pack("<I",len(data))+data
    wav=b"RIFF"+struct.pack("<I",len(body))+body
    p=out/f"valid-{bits}.wav"
    p.write_bytes(wav)
    print(p, len(wav), hashlib.sha256(wav).hexdigest(),len(data),hashlib.sha256(data).hexdigest())
