import math, struct, hashlib
from pathlib import Path
p=Path(__file__).parent
rate=48000; n=5760
# 15-bit signed samples are scaled conservatively, then left-aligned in 16-bit containers.
q=[round(8191*(.30*math.sin(2*math.pi*997*i/rate)+.12*math.sin(2*math.pi*1733*i/rate))) for i in range(n)]
samples=[max(-16384,min(16383,x))*2 for x in q]
payload=struct.pack('<'+'h'*n,*samples)
guid=bytes.fromhex('0100000000001000800000aa00389b71')
def wav(valid,name):
    fmt=struct.pack('<HHIIHHHHI',0xfffe,1,rate,rate*2,2,16,22,valid,4)+guid
    body=b'WAVE'+b'fmt '+struct.pack('<I',len(fmt))+fmt+b'data'+struct.pack('<I',len(payload))+payload
    data=b'RIFF'+struct.pack('<I',len(body))+body
    (p/name).write_bytes(data)
for v,name in [(15,'valid15.wav'),(16,'valid16.wav')]: wav(v,name)
for name in ('valid15.wav','valid16.wav'):
 d=(p/name).read_bytes(); print(name,len(d),hashlib.sha256(d).hexdigest())
print('payload bytes',len(payload),'payload sha256',hashlib.sha256(payload).hexdigest(),'sample range',min(samples),max(samples))
