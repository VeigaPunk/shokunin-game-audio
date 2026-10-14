import hashlib, math, struct
from pathlib import Path
import numpy as np
out=Path(__file__).parent
rate=48000; n=5760
t=np.arange(n,dtype=np.float64)/rate
q=np.rint(8191*(.24*np.sin(2*np.pi*997*t)+.09*np.sin(2*np.pi*1633*t))).astype(np.int64)
samples=(q*8).astype("<i2")
payload=samples.tobytes()
guid=bytes.fromhex("0100000000001000800000aa00389b71")
for valid,name in ((13,"valid-13.wav"),(16,"valid-16.wav")):
 fmt=struct.pack("<HHIIHHHHI",0xfffe,1,rate,rate*2,2,16,22,valid,0x4)+guid
 assert len(fmt)==40
 body=b"fmt "+struct.pack("<I",40)+fmt+b"data"+struct.pack("<I",len(payload))+payload
 wav=b"RIFF"+struct.pack("<I",len(body)+4)+b"WAVE"+body
 (out/name).write_bytes(wav)
 print(name,"bytes",len(wav),"wav_sha256",hashlib.sha256(wav).hexdigest())
print("payload_bytes",len(payload),"payload_sha256",hashlib.sha256(payload).hexdigest(),"samples",len(samples),"range",int(samples.min()),int(samples.max()),"all_divisible_by_8",bool(np.all(samples%8==0)))
