import math, struct, wave
from pathlib import Path
out=Path(__file__).parent
rate=48000
for name,freq in [("below",200.0),("above",300.0)]:
    n=5760
    frames=[]
    for i in range(n):
        t=i/rate
        env=1.0
        x=0.35*env*math.sin(2*math.pi*freq*t)
        frames.append(max(-32768,min(32767,round(x*32767))))
    with wave.open(str(out/(name+".wav")),"wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate)
        w.writeframes(b"".join(struct.pack("<h",v) for v in frames))
