import math, struct, wave
from pathlib import Path
import hashlib
p=Path(__file__).parent
n=5760; rate=48000
samples=[round(32767*(.25*math.sin(2*math.pi*1000*i/rate)+.08*math.sin(2*math.pi*1500*i/rate))) for i in range(n)]
data=struct.pack('<'+'h'*n,*samples)
# Extensible WAVE: fmt payload base + cbSize + valid bits + channel mask + GUID.
guid=bytes.fromhex('0100000000001000800000aa00389b71')
for name,mask in [('mask-0.wav',0),('mask-4.wav',4)]:
    fmt=struct.pack('<HHIIHHH',0xfffe,1,rate,rate*2,2,16,22)+struct.pack('<HI',16,mask)+guid
    assert len(fmt)==40
    body=b'WAVE'+b'fmt '+struct.pack('<I',len(fmt))+fmt+b'data'+struct.pack('<I',len(data))+data
    wav=b'RIFF'+struct.pack('<I',len(body))+body
    (p/name).write_bytes(wav)
    print(name,len(wav),hashlib.sha256(wav).hexdigest(),len(data),hex(mask))
