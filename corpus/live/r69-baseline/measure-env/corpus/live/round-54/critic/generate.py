import numpy as np, struct, wave, hashlib
from pathlib import Path
p=Path(".shokunin/audio/corpus/live/round-54/critic")
n=5760;t=np.arange(n)/48000
s=np.rint((.25*np.sin(2*np.pi*1000*t)+.08*np.sin(2*np.pi*1500*t))*32768).astype("<i2")
x=(s.astype(np.int64)*65536).astype("<i4")
raw=x.tobytes(); fmt=struct.pack("<HHIIHH",1,1,48000,48000*4,4,32)
head=b"RIFF"+struct.pack("<I",4+8+len(fmt)+8+len(raw))+b"WAVEfmt "+struct.pack("<I",16)+fmt+b"data"+struct.pack("<I",len(raw))+raw
(p/"candidate-pcm32.wav").write_bytes(head)
with wave.open(str(p/"control-pcm16.wav"),"wb") as w:
 w.setnchannels(1);w.setsampwidth(2);w.setframerate(48000);w.writeframes(s.tobytes())
for f in p.glob("*.wav"): print(f.name,hashlib.sha256(f.read_bytes()).hexdigest(),f.stat().st_size)
