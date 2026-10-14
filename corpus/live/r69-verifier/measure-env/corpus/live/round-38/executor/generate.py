import math,sys,wave
from pathlib import Path
out=Path(__file__).parent
for a in map(float,sys.argv[1:]):
 for name, extra in (("base",0),(f"var_{a:.3f}",a)):
  frames=[]
  for i in range(96000):
   t=i/48000;x=.15*math.sin(2*math.pi*12*t)+.09*math.sin(2*math.pi*36*t)+extra*math.sin(2*math.pi*60*t);frames.append(int(round(x*32767)))
  with wave.open(str(out/(name+".wav")),"wb") as w:
   w.setnchannels(1);w.setsampwidth(2);w.setframerate(48000);w.writeframes(b"".join(x.to_bytes(2,"little",signed=True) for x in frames))
