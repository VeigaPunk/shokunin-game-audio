import math, struct, wave
from pathlib import Path
out=Path(__file__).parent
rate=48000
for name,freq in (("baseline",60.0),("variant",64.0)):
    with wave.open(str(out/(name+".wav")),"wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate)
        w.writeframes(b"".join(struct.pack("<h",round(0.22*32767*math.sin(2*math.pi*freq*i/rate))) for i in range(rate*2)))
