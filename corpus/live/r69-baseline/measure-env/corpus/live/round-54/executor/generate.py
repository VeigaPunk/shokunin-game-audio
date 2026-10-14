import wave, struct, math
from pathlib import Path
p=Path(__file__).parent
n=5760; rate=48000
vals=[]
for i in range(n):
 t=i/rate
 x=.25*math.sin(2*math.pi*1000*t)+.08*math.sin(2*math.pi*1500*t)
 vals.append(max(-32768,min(32767,round(x*32767))))
with wave.open(str(p/"pcm16.wav"),"wb") as w:
 w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(b"".join(struct.pack("<h",v) for v in vals))
with open(p/"pcm32.wav","wb") as f:
 data=b"".join(struct.pack("<i",v*65536) for v in vals)
 f.write(b"RIFF"+struct.pack("<I",36+len(data))+b"WAVEfmt "+struct.pack("<IHHIIHH",16,1,1,rate,rate*4,4,32)+b"data"+struct.pack("<I",len(data))+data)
