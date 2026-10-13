import numpy as np, struct, hashlib, wave
from pathlib import Path
out=Path(".shokunin/audio/corpus/live/round-53/executor"); n=5760; t=np.arange(n)/48000
s=np.rint((.25*np.sin(2*np.pi*1000*t)+.08*np.sin(2*np.pi*1500*t))*32768).astype(np.int16)
f=s.astype("<f4")/32768
raw=f.tobytes(); fmt=struct.pack("<HHIIHH",3,1,48000,48000*4,4,32)
head=b"RIFF"+struct.pack("<I",4+8+len(fmt)+8+len(raw))+b"WAVEfmt "+struct.pack("<I",16)+fmt+b"data"+struct.pack("<I",len(raw))+raw
(out/"float32.wav").write_bytes(head)
with wave.open(str(out/"pcm16.wav"),"wb") as w:
 w.setnchannels(1); w.setsampwidth(2); w.setframerate(48000); w.writeframes(s.astype("<i2").tobytes())
for x in ("float32.wav","pcm16.wav"):
 d=(out/x).read_bytes(); print(x,hashlib.sha256(d).hexdigest(),len(d))
