import math, struct, hashlib, json
from pathlib import Path
import numpy as np
D=Path(__file__).parent
rate=48000
n=5760
samples=[round(8191*(.24*math.sin(2*math.pi*997*i/rate)+.09*math.sin(2*math.pi*1633*i/rate))) for i in range(n)]
payload=struct.pack('<'+'h'*n,*samples)
guid=bytes.fromhex('0100000000001000800000aa00389b71')
def wav(valid):
    fmt=struct.pack('<HHIIHHHHI',0xfffe,1,rate,rate*2,2,16,22,valid,4)+guid
    # struct includes format tag and extensible body (fmt length exactly 40)
    body=b'WAVE'+b'fmt '+struct.pack('<I',len(fmt))+fmt+b'data'+struct.pack('<I',len(payload))+payload
    return b'RIFF'+struct.pack('<I',len(body))+body
for valid,name in [(0,'valid-0.wav'),(16,'valid-16.wav')]:
    (D/name).write_bytes(wav(valid))
print(json.dumps({'payload_bytes':len(payload),'payload_sha256':hashlib.sha256(payload).hexdigest(),'samples':n,'min':min(samples),'max':max(samples),'all_zero_or_16?':all(-32768<=x<=32767 for x in samples),'wavs':{v:hashlib.sha256(wav(v)).hexdigest() for v in (0,16)}}))
