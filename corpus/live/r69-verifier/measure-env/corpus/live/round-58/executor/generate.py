import math, struct, hashlib
from pathlib import Path
import numpy as np
out=Path(__file__).parent
rate=48000; n=5760
# UI-shaped 120 ms two-tone signed PCM16 waveform, quantized to 14-bit left-aligned values.
t=np.arange(n,dtype=np.float64)/rate
x=np.rint((.25*np.sin(2*np.pi*1000*t)+.08*np.sin(2*np.pi*1500*t))*8191).astype(np.int64)
samples=(x*4).astype('<i2')
payload=samples.tobytes()
guid=bytes.fromhex('0100000000001000800000aa00389b71')
def make(vbits,name):
    fmt=struct.pack('<HHIIHHHHI',0xfffe,1,rate,rate*2,2,16,22,vbits,0x4)+guid
    # Above struct layout intentionally inspect fields: cbSize, validbits, mask
    data=b'fmt '+struct.pack('<I',40)+fmt+b'data'+struct.pack('<I',len(payload))+payload
    wav=b'RIFF'+struct.pack('<I',len(data)+4)+b'WAVE'+data
    (out/name).write_bytes(wav)
    print(name,len(wav),'wav_sha256',hashlib.sha256(wav).hexdigest(),'payload_sha256',hashlib.sha256(payload).hexdigest())
make(14,'valid-14.wav'); make(16,'valid-16.wav')
