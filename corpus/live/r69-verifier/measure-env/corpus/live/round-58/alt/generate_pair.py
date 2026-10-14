from pathlib import Path
import math, struct, hashlib
import numpy as np
p=Path(__file__).parent
rate=48000; n=5760
t=np.arange(n)/rate
q=np.rint(8191*(.22*np.sin(2*np.pi*887*t)+.10*np.sin(2*np.pi*1901*t))).astype(np.int16)
samples=(q*4).astype('<i2')
payload=samples.tobytes()
guid=bytes.fromhex('0100000000001000800000aa00389b71')
for valid in (14,16):
 fmt=struct.pack('<HHIIHHHHI',0xfffe,1,rate,rate*2,2,16,22,valid,4)+guid
 assert len(fmt)==40
 data=b'WAVE'+b'fmt '+struct.pack('<I',len(fmt))+fmt+b'data'+struct.pack('<I',len(payload))+payload
 wav=b'RIFF'+struct.pack('<I',len(data))+data
 (p/f'valid{valid}.wav').write_bytes(wav)
 print(valid,len(wav),hashlib.sha256(wav).hexdigest())
print('payload',len(payload),hashlib.sha256(payload).hexdigest(),'range',samples.min(),samples.max(),'all_div4',bool(np.all(samples%4==0)))
